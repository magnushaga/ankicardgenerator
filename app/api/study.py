from flask import jsonify, request
from app.models import db, Card, UserCardState, StudySession, CardReview
from app.study.supermemo2 import SuperMemo2
from . import api
import os
from datetime import datetime

@api.route('/api/study/start', methods=['POST'])
def start_study_session():
    """Start a new study session"""
    data = request.get_json()
    deck_id = data.get('deck_id')
    
    if not deck_id:
        return jsonify({'error': 'deck_id is required'}), 400
    
    try:
        user_id = os.getenv('TEST_USER_ID')
        
        session = StudySession(
            user_id=user_id,
            deck_id=deck_id,
            started_at=datetime.utcnow()
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'sessionId': str(session.id),
            'startedAt': session.started_at.isoformat()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/api/study/next-card', methods=['GET'])
def get_next_card():
    """Get the next card to study"""
    deck_id = request.args.get('deck_id')
    session_id = request.args.get('session_id')
    
    if not all([deck_id, session_id]):
        return jsonify({'error': 'deck_id and session_id are required'}), 400
    
    try:
        user_id = os.getenv('TEST_USER_ID')
        
        # Get next card based on SuperMemo2 algorithm
        next_card = Card.query.join(Topic).join(Chapter).join(Part).filter(
            Part.deck_id == deck_id
        ).outerjoin(
            UserCardState,
            (UserCardState.card_id == Card.id) & (UserCardState.user_id == user_id)
        ).filter(
            (UserCardState.next_review <= datetime.utcnow()) | 
            (UserCardState.id.is_(None))
        ).order_by(
            UserCardState.next_review.asc().nullsfirst()
        ).first()
        
        if not next_card:
            return jsonify({'message': 'No more cards to review'})
        
        return jsonify({
            'cardId': str(next_card.id),
            'front': next_card.front,
            'back': next_card.back
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/study/review', methods=['POST'])
def submit_review():
    """Submit a card review"""
    data = request.get_json()
    card_id = data.get('card_id')
    session_id = data.get('session_id')
    quality = data.get('quality')
    time_taken = data.get('time_taken')
    
    if not all([card_id, session_id, quality is not None]):
        return jsonify({'error': 'card_id, session_id, and quality are required'}), 400
    
    try:
        user_id = os.getenv('TEST_USER_ID')
        
        # Get or create user card state
        user_card_state = UserCardState.query.filter_by(
            user_id=user_id,
            card_id=card_id
        ).first()
        
        if not user_card_state:
            user_card_state = UserCardState(
                user_id=user_id,
                card_id=card_id
            )
            db.session.add(user_card_state)
        
        # Update using SuperMemo2
        prev_values, new_values = SuperMemo2.update_user_card_state(
            user_card_state,
            quality,
            time_taken
        )
        
        # Record review
        review = CardReview(
            session_id=session_id,
            card_id=card_id,
            user_card_state_id=user_card_state.id,
            quality=quality,
            time_taken=time_taken,
            **prev_values,
            **new_values
        )
        db.session.add(review)
        
        db.session.commit()
        return jsonify(new_values)
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 