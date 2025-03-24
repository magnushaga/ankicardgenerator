import os
from flask import Flask
from app.models import db, User, Deck, Part, Chapter, Topic, Card
import json
import pathlib

# Get the project root directory
ROOT_DIR = pathlib.Path(__file__).parent
CONTENT_DIR = ROOT_DIR / 'saved_content' / 'python_intro'

# Create Flask app
app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:admin@localhost:5432/anki_test_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TESTING': True
})

# Initialize database
db.init_app(app)

def load_saved_content():
    """Load saved content from files"""
    # Load analysis
    with open(CONTENT_DIR / 'analysis.json', 'r') as f:
        analysis = json.load(f)
    
    # Load structure
    with open(CONTENT_DIR / 'structure.json', 'r') as f:
        structure = json.load(f)
    
    # Load cards
    with open(CONTENT_DIR / 'cards.json', 'r') as f:
        cards = json.load(f)
    
    return analysis, structure, cards

def insert_into_database():
    """Insert the saved content into the database"""
    with app.app_context():
        try:
            print("\n=== Starting Database Insertion ===")
            
            # Load content
            analysis, structure, cards_data = load_saved_content()
            
            # Step 1: Create test user
            print("\n1. Creating test user...")
            test_user = User(
                email='test@example.com',
                username='testuser'
            )
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            print(f"Created user: {test_user.username}")

            # Step 2: Create deck
            print("\n2. Creating deck...")
            deck = Deck(
                user_id=test_user.id,
                title="Introduction to Python"
            )
            db.session.add(deck)
            db.session.flush()
            print(f"Created deck: {deck.title}")

            # Step 3: Create content hierarchy
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
                        topic_cards = cards_data.get(topic_id, [])
                        
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
            print(f"Total parts created: {len(parts)}")
            
            for part in parts:
                print(f"\nPart: {part.title}")
                chapters = Chapter.query.filter_by(part_id=part.id).all()
                print(f"Chapters in this part: {len(chapters)}")
                
                for chapter in chapters:
                    print(f"  Chapter: {chapter.title}")
                    topics = Topic.query.filter_by(chapter_id=chapter.id).all()
                    print(f"  Topics in this chapter: {len(topics)}")
                    
                    for topic in topics:
                        cards = Card.query.filter_by(topic_id=topic.id).all()
                        print(f"    Topic: {topic.title} (Cards: {len(cards)})")

        except Exception as e:
            print(f"Error in database insertion: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    try:
        # Reset database
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("Database reset complete")
        
        # Insert content
        insert_into_database()
        
    except Exception as e:
        print(f"Test failed: {e}") 