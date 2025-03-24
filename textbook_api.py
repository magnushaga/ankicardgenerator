from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from models_with_states import (
    db, User, Textbook, Part, Chapter, Topic, Deck, Card,
    UserPartState, UserChapterState, UserTopicState, UserCardState
)

textbook_api = Blueprint('textbook_api', __name__)

@textbook_api.route('/api/textbooks', methods=['POST'])
def create_textbook():
    """Create a new textbook with initial structure"""
    data = request.get_json()
    required_fields = ['title', 'author', 'subject', 'user_id']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Required fields: {", ".join(required_fields)}'}), 400
        
    try:
        # Create textbook
        textbook = Textbook(
            id=uuid.uuid4(),
            user_id=data['user_id'],
            title=data['title'],
            author=data['author'],
            subject=data['subject'],
            description=data.get('description', ''),
            tags=data.get('tags', []),
            difficulty_level=data.get('difficulty_level', 'intermediate'),
            language=data.get('language', 'en')
        )
        db.session.add(textbook)
        db.session.flush()  # Get the ID without committing
        
        # Create initial deck
        deck = Deck(
            id=uuid.uuid4(),
            owner_id=data['user_id'],
            name=f"{data['title']} - Main Deck",
            description=f"Main deck for {data['title']}",
            textbook_id=textbook.id
        )
        db.session.add(deck)
        
        db.session.commit()
        
        return jsonify({
            'textbook_id': str(textbook.id),
            'deck_id': str(deck.id),
            'message': 'Textbook and initial deck created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@textbook_api.route('/api/textbooks/<textbook_id>/structure', methods=['POST'])
def add_textbook_structure():
    """Add parts, chapters, and topics to a textbook"""
    data = request.get_json()
    textbook_id = data.get('textbook_id')
    user_id = data.get('user_id')
    structure = data.get('structure')
    
    if not all([textbook_id, user_id, structure]):
        return jsonify({'error': 'textbook_id, user_id, and structure are required'}), 400
    
    try:
        textbook = Textbook.query.get_or_404(textbook_id)
        deck = Deck.query.filter_by(textbook_id=textbook_id).first()
        
        if not deck:
            return jsonify({'error': 'No deck found for this textbook'}), 404
        
        # Add parts, chapters, and topics
        for part_idx, part_data in enumerate(structure['parts']):
            part = Part(
                id=uuid.uuid4(),
                deck_id=deck.id,
                title=part_data['title'],
                order_index=part_idx
            )
            db.session.add(part)
            db.session.flush()
            
            # Create user part state
            part_state = UserPartState(
                user_id=user_id,
                part_id=part.id,
                is_active=True
            )
            db.session.add(part_state)
            
            for chapter_idx, chapter_data in enumerate(part_data['chapters']):
                chapter = Chapter(
                    id=uuid.uuid4(),
                    part_id=part.id,
                    title=chapter_data['title'],
                    order_index=chapter_idx
                )
                db.session.add(chapter)
                db.session.flush()
                
                # Create user chapter state
                chapter_state = UserChapterState(
                    user_id=user_id,
                    chapter_id=chapter.id,
                    is_active=True
                )
                db.session.add(chapter_state)
                
                for topic_idx, topic_data in enumerate(chapter_data['topics']):
                    topic = Topic(
                        id=uuid.uuid4(),
                        chapter_id=chapter.id,
                        title=topic_data['title'],
                        comment=topic_data.get('comment', ''),
                        order_index=topic_idx
                    )
                    db.session.add(topic)
                    db.session.flush()
                    
                    # Create user topic state
                    topic_state = UserTopicState(
                        user_id=user_id,
                        topic_id=topic.id,
                        is_active=True
                    )
                    db.session.add(topic_state)
        
        db.session.commit()
        return jsonify({'message': 'Textbook structure created successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@textbook_api.route('/api/textbooks/<textbook_id>/cards', methods=['POST'])
def generate_textbook_cards():
    """Generate cards for a textbook topic"""
    data = request.get_json()
    user_id = data.get('user_id')
    topic_id = data.get('topic_id')
    cards_data = data.get('cards')  # List of {front, back} objects
    
    if not all([user_id, topic_id, cards_data]):
        return jsonify({'error': 'user_id, topic_id, and cards_data are required'}), 400
    
    try:
        topic = Topic.query.get_or_404(topic_id)
        chapter = Chapter.query.get_or_404(topic.chapter_id)
        part = Part.query.get_or_404(chapter.part_id)
        deck = Deck.query.get_or_404(part.deck_id)
        
        created_cards = []
        for card_data in cards_data:
            # Create card
            card = Card(
                id=uuid.uuid4(),
                deck_id=deck.id,
                topic_id=topic_id,
                front=card_data['front'],
                back=card_data['back']
            )
            db.session.add(card)
            db.session.flush()
            
            # Create user card state
            card_state = UserCardState(
                user_id=user_id,
                card_id=card.id,
                is_active=True
            )
            db.session.add(card_state)
            
            created_cards.append({
                'id': str(card.id),
                'front': card.front,
                'back': card.back
            })
        
        db.session.commit()
        return jsonify(created_cards)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@textbook_api.route('/api/textbooks/<textbook_id>/state', methods=['GET'])
def get_textbook_state(textbook_id):
    """Get the complete state of a textbook for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        # Get textbook and its deck
        textbook = Textbook.query.get_or_404(textbook_id)
        deck = Deck.query.filter_by(textbook_id=textbook_id).first()
        
        if not deck:
            return jsonify({'error': 'No deck found for this textbook'}), 404
        
        # Get all parts with their states
        parts = Part.query.filter_by(deck_id=deck.id).all()
        parts_data = []
        
        for part in parts:
            part_state = UserPartState.query.filter_by(
                user_id=user_id,
                part_id=part.id
            ).first()
            
            chapters_data = []
            for chapter in Chapter.query.filter_by(part_id=part.id).all():
                chapter_state = UserChapterState.query.filter_by(
                    user_id=user_id,
                    chapter_id=chapter.id
                ).first()
                
                topics_data = []
                for topic in Topic.query.filter_by(chapter_id=chapter.id).all():
                    topic_state = UserTopicState.query.filter_by(
                        user_id=user_id,
                        topic_id=topic.id
                    ).first()
                    
                    # Get cards for this topic
                    cards = Card.query.filter_by(topic_id=topic.id).all()
                    cards_data = []
                    
                    for card in cards:
                        card_state = UserCardState.query.filter_by(
                            user_id=user_id,
                            card_id=card.id
                        ).first()
                        
                        cards_data.append({
                            'id': str(card.id),
                            'front': card.front,
                            'back': card.back,
                            'is_active': card_state.is_active if card_state else True,
                            'next_review': card_state.next_review.isoformat() if card_state and card_state.next_review else None,
                            'easiness': card_state.easiness if card_state else 2.5,
                            'interval': card_state.interval if card_state else 1,
                            'repetitions': card_state.repetitions if card_state else 0
                        })
                    
                    topics_data.append({
                        'id': str(topic.id),
                        'title': topic.title,
                        'comment': topic.comment,
                        'is_active': topic_state.is_active if topic_state else True,
                        'cards': cards_data
                    })
                
                chapters_data.append({
                    'id': str(chapter.id),
                    'title': chapter.title,
                    'is_active': chapter_state.is_active if chapter_state else True,
                    'topics': topics_data
                })
            
            parts_data.append({
                'id': str(part.id),
                'title': part.title,
                'is_active': part_state.is_active if part_state else True,
                'chapters': chapters_data
            })
        
        return jsonify({
            'textbook': {
                'id': str(textbook.id),
                'title': textbook.title,
                'author': textbook.author,
                'subject': textbook.subject
            },
            'deck_id': str(deck.id),
            'parts': parts_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@textbook_api.route('/api/textbooks/<textbook_id>/toggle-state', methods=['POST'])
def toggle_item_state():
    """Toggle the active state of a part, chapter, topic, or card"""
    data = request.get_json()
    user_id = data.get('user_id')
    item_type = data.get('item_type')  # 'part', 'chapter', 'topic', or 'card'
    item_id = data.get('item_id')
    is_active = data.get('is_active', True)
    
    if not all([user_id, item_type, item_id]):
        return jsonify({'error': 'user_id, item_type, and item_id are required'}), 400
    
    if item_type not in ['part', 'chapter', 'topic', 'card']:
        return jsonify({'error': 'Invalid item_type'}), 400
    
    try:
        # Map item types to their state models
        state_models = {
            'part': UserPartState,
            'chapter': UserChapterState,
            'topic': UserTopicState,
            'card': UserCardState
        }
        
        StateModel = state_models[item_type]
        state = StateModel.query.filter_by(
            user_id=user_id,
            f"{item_type}_id"=item_id
        ).first()
        
        if not state:
            # Create new state if it doesn't exist
            state = StateModel(
                user_id=user_id,
                f"{item_type}_id": item_id,
                is_active=is_active
            )
            db.session.add(state)
        else:
            state.is_active = is_active
            state.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'item_type': item_type,
            'item_id': str(item_id),
            'is_active': state.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500