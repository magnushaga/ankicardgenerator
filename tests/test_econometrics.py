import os
from flask import Flask
from app.models import db, User, Deck, Part, Chapter, Topic, Card
from app.api import TextbookAnalyzer
import json
import pathlib
from dotenv import load_dotenv

# Get the project root directory
ROOT_DIR = pathlib.Path(__file__).parent
SAVE_DIR = ROOT_DIR / 'saved_content' / 'econometrics'

# Create save directory if it doesn't exist
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:admin@localhost:5432/anki_test_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TESTING': True
})

# Initialize database
db.init_app(app)

def generate_and_save_content():
    """Generate content using the TextbookAnalyzer and save to files"""
    try:
        print("\n=== Generating Content ===")
        analyzer = TextbookAnalyzer()
        
        # Step 1: Analyze textbook
        print("\nAnalyzing textbook...")
        analysis = analyzer.analyze_textbook("Introductory Econometrics by Wooldridge")
        
        # Save analysis
        with open(SAVE_DIR / 'analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        print("Saved analysis.json")

        # Step 2: Generate structure
        print("\nGenerating structure...")
        structure = analyzer.generate_structure(analysis)
        
        # Save structure
        with open(SAVE_DIR / 'structure.json', 'w') as f:
            json.dump(structure, f, indent=2)
        print("Saved structure.json")

        # Step 3: Generate cards for each topic
        print("\nGenerating cards...")
        all_cards = {}
        
        for part in structure['parts']:
            for chapter in part['chapters']:
                for topic in chapter['topics']:
                    topic_id = f"{part['title']}_{chapter['title']}_{topic['title']}".replace(' ', '_')
                    print(f"Generating cards for topic: {topic['title']}")
                    
                    cards = analyzer.generate_cards_for_topic(
                        topic['title'],
                        chapter['title'],
                        part['title'],
                        card_count=3
                    )
                    all_cards[topic_id] = cards

        # Save cards
        with open(SAVE_DIR / 'cards.json', 'w') as f:
            json.dump(all_cards, f, indent=2)
        print("Saved cards.json")

        return structure, all_cards

    except Exception as e:
        print(f"Error generating content: {e}")
        raise

def insert_into_database(structure, cards):
    """Insert the generated content into the database"""
    with app.app_context():
        try:
            print("\n=== Starting Database Insertion ===")
            
            # Create test user
            print("\n1. Creating test user...")
            test_user = User(
                email='econometrics@example.com',  # Changed email to avoid conflicts
                username='econometrics_user'       # Changed username to avoid conflicts
            )
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()

            # Create deck
            print("\n2. Creating deck...")
            deck = Deck(
                user_id=test_user.id,
                title="Introductory Econometrics"
            )
            db.session.add(deck)
            db.session.flush()

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

if __name__ == '__main__':
    try:
        # Step 1: Generate and save content
        print("\n=== Generating Content ===")
        structure, cards = generate_and_save_content()
        
        # Step 2: Insert into database
        print("\n=== Inserting Content into Database ===")
        insert_into_database(structure, cards)
        
    except Exception as e:
        print(f"\nError: {e}") 