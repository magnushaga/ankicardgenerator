from flask import Blueprint, request, jsonify
from app.models import db, User, Deck, Part, Chapter, Topic, Card
from .. import api  # Import from the main api.py
import os

# Create the blueprint
bp = Blueprint('api', __name__)

# Import the TextbookAnalyzer from the main api.py
TextbookAnalyzer = api.TextbookAnalyzer

@bp.route('/api/generate-deck', methods=['POST'])
def generate_deck():
    """Generate a new deck from a textbook"""
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400
        
    try:
        # Initialize analyzer
        analyzer = TextbookAnalyzer()
        
        # Analyze textbook
        analysis = analyzer.analyze_textbook(textbook_name)
        
        # Generate structure
        structure = analyzer.generate_structure(analysis)
        
        # Create test user (using environment variable)
        test_user = User.query.filter_by(email=os.getenv('TEST_USER_EMAIL')).first()
        if not test_user:
            test_user = User(
                email=os.getenv('TEST_USER_EMAIL', 'test@example.com'),
                username=os.getenv('TEST_USERNAME', 'testuser')
            )
            test_user.set_password(os.getenv('TEST_PASSWORD', 'testpassword'))
            db.session.add(test_user)
            db.session.commit()

        # Create deck
        deck = Deck(
            user_id=test_user.id,
            title=textbook_name
        )
        db.session.add(deck)
        db.session.flush()

        # Create content hierarchy
        for part_idx, part_data in enumerate(structure['parts']):
            part = Part(
                deck_id=deck.id,
                title=part_data['title'],
                order_index=part_idx
            )
            db.session.add(part)
            db.session.flush()

            for chapter_idx, chapter_data in enumerate(part_data['chapters']):
                chapter = Chapter(
                    part_id=part.id,
                    title=chapter_data['title'],
                    order_index=chapter_idx
                )
                db.session.add(chapter)
                db.session.flush()

                for topic_idx, topic_data in enumerate(chapter_data['topics']):
                    topic = Topic(
                        chapter_id=chapter.id,
                        title=topic_data['title'],
                        order_index=topic_idx
                    )
                    db.session.add(topic)
                    db.session.flush()

                    # Generate cards for topic
                    cards = analyzer.generate_cards_for_topic(
                        topic_data['title'],
                        chapter_data['title'],
                        part_data['title'],
                        card_count=3
                    )
                    
                    for card_data in cards:
                        card = Card(
                            topic_id=topic.id,
                            front=card_data['question'],
                            back=card_data['answer']
                        )
                        db.session.add(card)

        db.session.commit()
        return jsonify({
            'message': 'Deck generated successfully',
            'deckId': str(deck.id)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Import routes at the bottom to avoid circular imports
from . import routes  # if you have a routes.py file 