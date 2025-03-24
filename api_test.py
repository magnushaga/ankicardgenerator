from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime, timedelta
from models_with_states import (
    db, User, Textbook, Part, Chapter, Topic, Deck, Card,
    UserPartState, UserChapterState, UserTopicState, UserCardState
)

test_api = Blueprint('test_api', __name__)

@test_api.route('/api/test/generate-textbook', methods=['POST'])
def generate_test_textbook():
    """Generate a test textbook with structure and 40 cards"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        # Create test textbook
        textbook = Textbook(
            id=uuid.uuid4(),
            user_id=user_id,
            title="Test Physics Textbook",
            author="Test Author",
            subject="Physics",
            description="A test textbook for physics with comprehensive coverage",
            tags=["physics", "mechanics", "thermodynamics", "test"],
            difficulty_level="intermediate",
            language="en"
        )
        db.session.add(textbook)
        db.session.flush()

        # Create main deck
        deck = Deck(
            id=uuid.uuid4(),
            owner_id=user_id,
            name="Physics Fundamentals",
            description="Main deck for Physics fundamentals",
            textbook_id=textbook.id
        )
        db.session.add(deck)
        db.session.flush()

        # Create structure (2 parts, 2 chapters each, 2 topics each = 8 topics total)
        # We'll create 5 cards per topic = 40 cards total
        parts_data = [
            {
                "title": "Part 1: Classical Mechanics",
                "chapters": [
                    {
                        "title": "Chapter 1: Kinematics",
                        "topics": [
                            {
                                "title": "Linear Motion",
                                "comment": "Fundamental concepts of velocity and acceleration"
                            },
                            {
                                "title": "Projectile Motion",
                                "comment": "Two-dimensional motion under gravity"
                            }
                        ]
                    },
                    {
                        "title": "Chapter 2: Dynamics",
                        "topics": [
                            {
                                "title": "Newton's Laws",
                                "comment": "The three fundamental laws of motion"
                            },
                            {
                                "title": "Forces",
                                "comment": "Different types of forces and their effects"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Part 2: Thermodynamics",
                "chapters": [
                    {
                        "title": "Chapter 3: Heat",
                        "topics": [
                            {
                                "title": "Temperature and Heat",
                                "comment": "Basic concepts of thermal physics"
                            },
                            {
                                "title": "Heat Transfer",
                                "comment": "Mechanisms of heat transfer"
                            }
                        ]
                    },
                    {
                        "title": "Chapter 4: Laws of Thermodynamics",
                        "topics": [
                            {
                                "title": "First Law",
                                "comment": "Conservation of energy in thermal systems"
                            },
                            {
                                "title": "Second Law",
                                "comment": "Entropy and irreversible processes"
                            }
                        ]
                    }
                ]
            }
        ]

        # Create parts, chapters, and topics with their states
        topics_created = []
        for part_idx, part_data in enumerate(parts_data):
            part = Part(
                id=uuid.uuid4(),
                deck_id=deck.id,
                title=part_data['title'],
                order_index=part_idx
            )
            db.session.add(part)
            db.session.flush()

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
                        comment=topic_data['comment'],
                        order_index=topic_idx
                    )
                    db.session.add(topic)
                    db.session.flush()

                    topic_state = UserTopicState(
                        user_id=user_id,
                        topic_id=topic.id,
                        is_active=True
                    )
                    db.session.add(topic_state)
                    topics_created.append(topic)

        # Generate 5 cards for each topic (40 cards total)
        cards_created = []
        for topic in topics_created:
            for i in range(5):
                card = Card(
                    id=uuid.uuid4(),
                    deck_id=deck.id,
                    topic_id=topic.id,
                    front=f"Question {i+1} about {topic.title}",
                    back=f"Answer {i+1} for {topic.title}"
                )
                db.session.add(card)
                db.session.flush()

                # Create card state with random intervals
                card_state = UserCardState(
                    user_id=user_id,
                    card_id=card.id,
                    is_active=True,
                    easiness=2.5,
                    interval=1,
                    repetitions=0,
                    next_review=datetime.utcnow() + timedelta(days=1)
                )
                db.session.add(card_state)
                
                cards_created.append({
                    'id': str(card.id),
                    'topic': topic.title,
                    'front': card.front,
                    'back': card.back
                })

        db.session.commit()

        return jsonify({
            'textbook': {
                'id': str(textbook.id),
                'title': textbook.title
            },
            'deck': {
                'id': str(deck.id),
                'name': deck.name
            },
            'structure': parts_data,
            'cards_created': len(cards_created),
            'sample_cards': cards_created[:5]  # Show first 5 cards as sample
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_api.route('/api/test/get-deck-stats/<deck_id>', methods=['GET'])
def get_deck_stats(deck_id):
    """Get statistics about a deck"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        deck = Deck.query.get_or_404(deck_id)
        
        # Get all cards and their states
        cards = Card.query.filter_by(deck_id=deck_id).all()
        card_states = UserCardState.query.filter_by(
            user_id=user_id
        ).filter(
            UserCardState.card_id.in_([card.id for card in cards])
        ).all()
        
        # Calculate statistics
        total_cards = len(cards)
        active_cards = sum(1 for state in card_states if state.is_active)
        due_cards = sum(1 for state in card_states 
                       if state.is_active and state.next_review <= datetime.utcnow())
        
        # Get topic statistics
        topics = Topic.query.join(Card).filter(Card.deck_id == deck_id).distinct().all()
        topic_stats = []
        
        for topic in topics:
            topic_cards = Card.query.filter_by(topic_id=topic.id).all()
            topic_states = UserCardState.query.filter_by(
                user_id=user_id
            ).filter(
                UserCardState.card_id.in_([card.id for card in topic_cards])
            ).all()
            
            topic_stats.append({
                'topic': topic.title,
                'total_cards': len(topic_cards),
                'active_cards': sum(1 for state in topic_states if state.is_active),
                'due_cards': sum(1 for state in topic_states 
                               if state.is_active and state.next_review <= datetime.utcnow())
            })
        
        return jsonify({
            'deck_id': str(deck_id),
            'name': deck.name,
            'total_cards': total_cards,
            'active_cards': active_cards,
            'due_cards': due_cards,
            'topic_stats': topic_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@test_api.route('/api/test/get-due-cards/<deck_id>', methods=['GET'])
def get_due_cards(deck_id):
    """Get all cards due for review"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        # Get all active cards that are due
        card_states = UserCardState.query.join(Card).filter(
            UserCardState.user_id == user_id,
            Card.deck_id == deck_id,
            UserCardState.is_active == True,
            UserCardState.next_review <= datetime.utcnow()
        ).all()
        
        due_cards = []
        for state in card_states:
            card = Card.query.get(state.card_id)
            topic = Topic.query.get(card.topic_id)
            
            due_cards.append({
                'card_id': str(card.id),
                'topic': topic.title,
                'front': card.front,
                'back': card.back,
                'next_review': state.next_review.isoformat(),
                'interval': state.interval,
                'easiness': state.easiness,
                'repetitions': state.repetitions
            })
        
        return jsonify({
            'deck_id': str(deck_id),
            'due_cards': due_cards,
            'count': len(due_cards)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500