import os
from dotenv import load_dotenv
from flask import Flask
from app.api import TextbookAnalyzer
from app.models import db, User, Deck, Part, Chapter, Topic, Card
import pathlib
import json

# Get the project root directory
ROOT_DIR = pathlib.Path(__file__).parent
print(f"Looking for .env file in: {ROOT_DIR}")
load_dotenv(ROOT_DIR / '.env')

# Create Flask app
app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:admin@localhost:5432/anki_test_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TESTING': True
})

# Initialize database
db.init_app(app)

def test_content_generation():
    """First test the Claude API content generation"""
    print("\n=== Testing Content Generation ===")
    
    analyzer = TextbookAnalyzer()
    
    # Step 1: Analyze the textbook
    print("\n1. Analyzing 'Introduction to Python'...")
    analysis = analyzer.analyze_textbook("Introduction to Python")
    print("\nAnalysis Results:")
    print(json.dumps(analysis, indent=2))
    
    # Step 2: Generate structure
    print("\n2. Generating textbook structure...")
    structure = analyzer.generate_structure("Introduction to Python")
    print("\nGenerated Structure:")
    print(json.dumps(structure, indent=2))
    
    # Step 3: Generate sample cards for first topic
    print("\n3. Testing card generation...")
    if structure and 'parts' in structure:
        first_part = structure['parts'][0]
        if 'chapters' in first_part:
            first_chapter = first_part['chapters'][0]
            if 'topics' in first_chapter:
                first_topic = first_chapter['topics'][0]
                print(f"\nGenerating cards for topic: {first_topic['title']}")
                cards = analyzer.generate_cards_for_topic(
                    topic_title=first_topic['title'],
                    topic_comment=first_topic.get('comment', ''),
                    textbook_name="Introduction to Python",
                    card_count=3
                )
                print("\nSample Cards:")
                print(json.dumps(cards, indent=2))
    
    return structure

def insert_into_database(structure):
    """Insert the generated content into the database"""
    with app.app_context():
        try:
            print("\n=== Starting Database Insertion ===")
            
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
            analyzer = TextbookAnalyzer()
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

                        # Generate cards for this topic
                        print(f"      Generating cards for topic: {topic.title}")
                        cards_data = analyzer.generate_cards_for_topic(
                            topic_title=topic.title,
                            topic_comment=topic_data.get('comment', ''),
                            textbook_name="Introduction to Python",
                            card_count=3
                        )

                        for card_data in cards_data:
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
        # First test content generation
        print("\n=== Phase 1: Content Generation ===")
        structure = test_content_generation()
        
        # If content generation is successful, proceed with database insertion
        if structure:
            print("\n=== Phase 2: Database Insertion ===")
            # Reset database
            with app.app_context():
                db.drop_all()
                db.create_all()
                print("Database reset complete")
            
            # Insert content into database
            insert_into_database(structure)
            
    except Exception as e:
        print(f"Test failed: {e}") 