import os
from flask import Flask
from app.models import db, User, Deck, Part, Chapter, Topic, Card
import json
import pathlib
from sqlalchemy import text
import sys
import logging

# Set up logging to help us debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the project root directory and content directory
ROOT_DIR = pathlib.Path(__file__).parent
CONTENT_DIR = ROOT_DIR / 'saved_content' / 'python_intro'

# Verify content files exist
def verify_content_files():
    required_files = ['analysis.json', 'structure.json', 'cards.json']
    missing_files = []
    
    for file in required_files:
        if not (CONTENT_DIR / file).exists():
            missing_files.append(file)
    
    if missing_files:
        raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")
    
    print("All required content files found!")

# Create Flask app
app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:admin@localhost:5432/anki_test_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TESTING': True
})

# Initialize database
db.init_app(app)

def reset_database():
    """Reset database by dropping and recreating all tables"""
    with app.app_context():
        try:
            # Drop all tables using CASCADE
            db.session.execute(text('DROP TABLE IF EXISTS cards CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS topics CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS chapters CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS parts CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS decks CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS users CASCADE'))
            
            db.session.commit()
            
            # Create all tables
            db.create_all()
            print("Database reset complete")
            
        except Exception as e:
            print(f"Error resetting database: {e}")
            db.session.rollback()
            raise

def load_content():
    """Load the saved content files"""
    try:
        # Load structure (which contains the hierarchy)
        with open(CONTENT_DIR / 'structure.json', 'r') as f:
            structure = json.load(f)
            print("Loaded structure.json")

        # Load cards
        with open(CONTENT_DIR / 'cards.json', 'r') as f:
            cards = json.load(f)
            print("Loaded cards.json")

        return structure, cards
    except Exception as e:
        print(f"Error loading content: {e}")
        raise

def insert_into_database(structure, cards):
    """Insert the loaded content into the database"""
    with app.app_context():
        try:
            print("\n=== Starting Database Insertion ===")
            
            # Create test user
            print("\n1. Creating test user...")
            test_user = User(
                email='test@example.com',
                username='testuser'
            )
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            print(f"Created user: {test_user.username}")

            # Create deck
            print("\n2. Creating deck...")
            deck = Deck(
                user_id=test_user.id,
                title="Introduction to Python"
            )
            db.session.add(deck)
            db.session.flush()
            print(f"Created deck: {deck.title}")

            # Create content hierarchy
            print("\n3. Creating content hierarchy...")
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

                        # Get cards for this topic
                        topic_id = f"{part_data['title']}_{chapter_data['title']}_{topic_data['title']}".replace(' ', '_')
                        topic_cards = cards.get(topic_id, [])
                        
                        print(f"      Adding {len(topic_cards)} cards")
                        for card_data in topic_cards:
                            card = Card(
                                topic_id=topic.id,
                                front=card_data['question'],
                                back=card_data['answer']
                            )
                            db.session.add(card)

            # Commit all changes
            db.session.commit()
            print("\nAll content committed to database successfully!")

            # Print summary
            print("\n=== Database Content Summary ===")
            parts = Part.query.filter_by(deck_id=deck.id).all()
            print(f"Total parts: {len(parts)}")
            
            total_chapters = 0
            total_topics = 0
            total_cards = 0
            
            for part in parts:
                print(f"\nPart: {part.title}")
                chapters = Chapter.query.filter_by(part_id=part.id).all()
                total_chapters += len(chapters)
                
                for chapter in chapters:
                    print(f"  Chapter: {chapter.title}")
                    topics = Topic.query.filter_by(chapter_id=chapter.id).all()
                    total_topics += len(topics)
                    
                    for topic in topics:
                        cards = Card.query.filter_by(topic_id=topic.id).all()
                        total_cards += len(cards)
                        print(f"    Topic: {topic.title} (Cards: {len(cards)})")
            
            print("\n=== Final Statistics ===")
            print(f"Total parts: {len(parts)}")
            print(f"Total chapters: {total_chapters}")
            print(f"Total topics: {total_topics}")
            print(f"Total cards: {total_cards}")

        except Exception as e:
            print(f"Error in database insertion: {e}")
            db.session.rollback()
            raise

def cleanup_models():
    """Remove any lingering textbook_reviews references"""
    if hasattr(User, 'textbook_reviews'):
        logger.debug("Removing textbook_reviews from User model")
        delattr(User, 'textbook_reviews')
    
    # Print all attributes of User model for debugging
    logger.debug("User model attributes: %s", dir(User))

if __name__ == '__main__':
    try:
        # Add cleanup before any database operations
        cleanup_models()
        
        # Step 1: Verify content files exist
        print("\n=== Verifying Content Files ===")
        verify_content_files()
        
        # Step 2: Reset database
        print("\n=== Resetting Database ===")
        reset_database()
        
        # Step 3: Load content
        print("\n=== Loading Content Files ===")
        structure, cards = load_content()
        
        # Step 4: Insert into database
        insert_into_database(structure, cards)
        
    except Exception as e:
        print(f"\nError: {e}")
        logger.exception("Detailed error information:") 