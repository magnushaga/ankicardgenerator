from flask import Blueprint, request, jsonify, current_app
from ..models import db, User, Deck, Textbook, Part, Chapter, Topic, Card
from ..api_backup.api_backup import TextbookAnalyzer
from sqlalchemy import text
import uuid
from datetime import datetime
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/api/test', methods=['GET'])
def test():
    logger.info("Test endpoint accessed")
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        response = {
            "status": "success",
            "message": "API is working!",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(f"Sending response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        response = {
            "status": "error",
            "message": "API is working but database connection failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.error(f"Sending error response: {response}")
        return jsonify(response), 500

@api_bp.route('/api/generate-deck', methods=['POST'])
def generate_deck():
    """Generate a deck from a textbook name and save to PostgreSQL"""
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400
        
    try:
        # Initialize analyzer
        analyzer = TextbookAnalyzer()
        
        # Step 1: Analyze textbook
        print("\nAnalyzing textbook...")
        analysis = analyzer.analyze_textbook(textbook_name)
        
        # Step 2: Generate structure
        print("\nGenerating structure...")
        structure = analyzer.generate_structure(textbook_name)
        
        # Step 3: Create database entries
        print("\nCreating database entries...")
        
        # Create test user with unique email
        print("\n1. Creating test user...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user = User(
            email=f'test_{timestamp}@example.com',
            username=f'test_user_{timestamp}'
        )
        test_user.set_password('testpassword')
        db.session.add(test_user)
        db.session.flush()

        # Create deck
        print("\n2. Creating deck...")
        deck = Deck(
            user_id=test_user.id,
            title=textbook_name
        )
        db.session.add(deck)
        db.session.flush()
        
        all_cards = {}
        # Create parts, chapters, topics
        for part_idx, part_data in enumerate(structure['parts']):
            print(f"\nCreating part: {part_data['title']}")
            part = Part(
                deck_id=deck.id,
                title=part_data['title'],
                order_index=part_idx
            )
            db.session.add(part)
            db.session.flush()

            for chapter_idx, chapter_data in enumerate(part_data['chapters']):
                print(f"  Creating chapter: {chapter_data['title']}")
                chapter = Chapter(
                    part_id=part.id,
                    title=chapter_data['title'],
                    order_index=chapter_idx
                )
                db.session.add(chapter)
                db.session.flush()

                for topic_idx, topic_data in enumerate(chapter_data['topics']):
                    print(f"    Creating topic: {topic_data['title']}")
                    topic = Topic(
                        chapter_id=chapter.id,
                        title=topic_data['title'],
                        order_index=topic_idx
                    )
                    db.session.add(topic)
                    db.session.flush()

                    # Generate cards for this topic
                    print(f"      Generating cards for topic: {topic_data['title']}")
                    cards = analyzer.generate_cards_for_topic(
                        topic_data['title'],
                        topic_data.get('comment', ''),
                        textbook_name,
                        topic_data.get('card_count', 3)
                    )
                    
                    # Store cards in database
                    topic_cards = []
                    for card_data in cards:
                        card = Card(
                            topic_id=topic.id,
                            front=card_data['question'],
                            back=card_data['answer']
                        )
                        db.session.add(card)
                        topic_cards.append({
                            'front': card.front,
                            'back': card.back
                        })
                    all_cards[str(topic.id)] = topic_cards

        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'message': 'Deck generated successfully',
            'deck': {
                'id': str(deck.id),
                'title': deck.title,
                'user_id': str(test_user.id)
            },
            'analysis': analysis,
            'structure': structure,
            'cards': all_cards
        })
        
    except Exception as e:
        print(f"Error generating deck: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/textbooks', methods=['GET'])
def get_textbooks():
    """Get all generated textbooks"""
    try:
        textbooks = Textbook.query.all()
        return jsonify([{
            'id': str(textbook.id),
            'title': textbook.title,
            'author': textbook.author,
            'subject': textbook.subject
        } for textbook in textbooks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/search-decks', methods=['GET'])
def search_decks():
    """Search for decks by title and return with cards"""
    query = request.args.get('q', '')
    
    try:
        decks = Deck.query.filter(Deck.title.ilike(f'%{query}%')).all()
        
        result = []
        for deck in decks:
            cards = []
            # Get all cards from the deck structure
            for part in deck.parts:
                for chapter in part.chapters:
                    for topic in chapter.topics:
                        topic_cards = Card.query.filter_by(topic_id=topic.id).all()
                        cards.extend([{
                            'id': str(card.id),
                            'front': card.front,
                            'back': card.back,
                            'partTitle': part.title,
                            'chapterTitle': chapter.title,
                            'topicTitle': topic.title
                        } for card in topic_cards])
            
            result.append({
                'id': str(deck.id),
                'title': deck.title,
                'cards': cards
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 