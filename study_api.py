from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import uuid
from models_with_states import (
    db, User, Deck, Card, UserCardState, StudySession,
    Part, Chapter, Topic
)

study_api = Blueprint('study_api', __name__)

def calculate_next_review(quality, prev_interval, prev_easiness, prev_repetitions):
    """
    Implementation of SuperMemo2 algorithm
    quality: 0-5 (0=complete blackout, 5=perfect recall)
    """
    if quality < 0 or quality > 5:
        raise ValueError("Quality must be between 0 and 5")

    # Update easiness factor
    easiness = prev_easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    easiness = max(1.3, easiness)  # Minimum easiness factor is 1.3

    # Update interval
    if quality < 3:
        # If quality is poor, reset repetitions and start over
        interval = 1
        repetitions = 0
    else:
        # Calculate new interval based on previous performance
        if prev_repetitions == 0:
            interval = 1
        elif prev_repetitions == 1:
            interval = 6
        else:
            interval = round(prev_interval * easiness)
        repetitions = prev_repetitions + 1

    return {
        'interval': interval,
        'easiness': easiness,
        'repetitions': repetitions
    }

@study_api.route('/api/study/start-session', methods=['POST'])
def start_study_session():
    """Start a new study session"""
    data = request.get_json()
    user_id = data.get('user_id')
    deck_id = data.get('deck_id')
    
    if not all([user_id, deck_id]):
        return jsonify({'error': 'user_id and deck_id are required'}), 400
    
    try:
        # Create new study session
        session = StudySession(
            id=uuid.uuid4(),
            user_id=user_id,
            deck_id=deck_id,
            cards_studied=0,
            correct_answers=0
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'session_id': str(session.id),
            'started_at': session.started_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_api.route('/api/study/get-next-cards', methods=['GET'])
def get_next_cards():
    """Get the next batch of cards to study"""
    user_id = request.args.get('user_id')
    deck_id = request.args.get('deck_id')
    limit = int(request.args.get('limit', 10))
    
    if not all([user_id, deck_id]):
        return jsonify({'error': 'user_id and deck_id are required'}), 400
    
    try:
        # Get active cards that are due for review
        now = datetime.utcnow()
        card_states = UserCardState.query.join(Card).filter(
            UserCardState.user_id == user_id,
            Card.deck_id == deck_id,
            UserCardState.is_active == True,
            UserCardState.next_review <= now
        ).limit(limit).all()
        
        cards_data = []
        for state in card_states:
            card = Card.query.get(state.card_id)
            topic = Topic.query.get(card.topic_id)
            chapter = Chapter.query.get(topic.chapter_id)
            part = Part.query.get(chapter.part_id)
            
            cards_data.append({
                'card_id': str(card.id),
                'front': card.front,
                'back': card.back,
                'topic': topic.title,
                'chapter': chapter.title,
                'part': part.title,
                'next_review': state.next_review.isoformat(),
                'interval': state.interval,
                'repetitions': state.repetitions
            })
        
        return jsonify({
            'cards': cards_data,
            'count': len(cards_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_api.route('/api/study/review-card', methods=['POST'])
def review_card():
    """Record a card review and update its state"""
    data = request.get_json()
    user_id = data.get('user_id')
    card_id = data.get('card_id')
    session_id = data.get('session_id')
    quality = data.get('quality')  # 0-5 rating
    
    if not all([user_id, card_id, session_id, quality is not None]):
        return jsonify({'error': 'user_id, card_id, session_id, and quality are required'}), 400
    
    try:
        # Get card state
        card_state = UserCardState.query.filter_by(
            user_id=user_id,
            card_id=card_id
        ).first()
        
        if not card_state:
            return jsonify({'error': 'Card state not found'}), 404
        
        # Calculate new values using SuperMemo2
        new_values = calculate_next_review(
            quality,
            card_state.interval,
            card_state.easiness,
            card_state.repetitions
        )
        
        # Update card state
        card_state.easiness = new_values['easiness']
        card_state.interval = new_values['interval']
        card_state.repetitions = new_values['repetitions']
        card_state.last_review = datetime.utcnow()
        card_state.next_review = datetime.utcnow() + timedelta(days=new_values['interval'])
        
        # Update session statistics
        session = StudySession.query.get(session_id)
        if session:
            session.cards_studied += 1
            if quality >= 4:  # Consider quality 4-5 as correct answers
                session.correct_answers += 1
        
        db.session.commit()
        
        return jsonify({
            'card_id': str(card_id),
            'new_interval': new_values['interval'],
            'new_easiness': new_values['easiness'],
            'new_repetitions': new_values['repetitions'],
            'next_review': card_state.next_review.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_api.route('/api/study/end-session', methods=['POST'])
def end_study_session():
    """End a study session and get statistics"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400
    
    try:
        session = StudySession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        session.ended_at = datetime.utcnow()
        db.session.commit()
        
        # Calculate statistics
        duration = (session.ended_at - session.started_at).total_seconds()
        accuracy = (session.correct_answers / session.cards_studied * 100) if session.cards_studied > 0 else 0
        
        return jsonify({
            'session_id': str(session.id),
            'duration_seconds': duration,
            'cards_studied': session.cards_studied,
            'correct_answers': session.correct_answers,
            'accuracy_percent': accuracy,
            'started_at': session.started_at.isoformat(),
            'ended_at': session.ended_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_api.route('/api/study/progress', methods=['GET'])
def get_study_progress():
    """Get study progress statistics for a deck"""
    user_id = request.args.get('user_id')
    deck_id = request.args.get('deck_id')
    
    if not all([user_id, deck_id]):
        return jsonify({'error': 'user_id and deck_id are required'}), 400
    
    try:
        # Get all cards and their states
        card_states = UserCardState.query.join(Card).filter(
            UserCardState.user_id == user_id,
            Card.deck_id == deck_id
        ).all()
        
        total_cards = len(card_states)
        if total_cards == 0:
            return jsonify({'error': 'No cards found'}), 404
        
        # Calculate statistics
        now = datetime.utcnow()
        stats = {
            'total_cards': total_cards,
            'active_cards': sum(1 for s in card_states if s.is_active),
            'cards_due': sum(1 for s in card_states if s.is_active and s.next_review <= now),
            'cards_learned': sum(1 for s in card_states if s.repetitions > 0),
            'mastered_cards': sum(1 for s in card_states if s.repetitions >= 3),
            'average_easiness': sum(s.easiness for s in card_states) / total_cards,
        }
        
        # Get topic-wise progress
        topics = Topic.query.join(Card).filter(Card.deck_id == deck_id).distinct().all()
        topic_progress = []
        
        for topic in topics:
            topic_states = UserCardState.query.join(Card).filter(
                UserCardState.user_id == user_id,
                Card.topic_id == topic.id
            ).all()
            
            if topic_states:
                topic_progress.append({
                    'topic': topic.title,
                    'total_cards': len(topic_states),
                    'active_cards': sum(1 for s in topic_states if s.is_active),
                    'cards_due': sum(1 for s in topic_states if s.is_active and s.next_review <= now),
                    'mastered_cards': sum(1 for s in topic_states if s.repetitions >= 3),
                    'average_easiness': sum(s.easiness for s in topic_states) / len(topic_states)
                })
        
        return jsonify({
            'overall_stats': stats,
            'topic_progress': topic_progress
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500