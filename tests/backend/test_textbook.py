import sys
import os
# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from app import create_app, db
from app.models import Textbook, Part, Chapter, Topic, TextbookReview, User
import uuid
from datetime import datetime

# Test database configuration
DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:admin@127.0.0.1:5432/anki_test_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TESTING': True
}

@pytest.fixture(scope='session')
def app():
    app = create_app(DB_CONFIG)
    return app

@pytest.fixture(scope='function')
def test_client(app):
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_create_textbook(test_client):
    """Test creating a textbook with its structure"""
    with test_client.application.app_context():
        # Create a textbook
        textbook = Textbook(
            id=uuid.uuid4(),
            title='Introduction to Python',
            author='Test Author',
            subject='Computer Science',
            description='A test textbook',
            tags=['python', 'programming'],
            difficulty_level='beginner',
            language='en'
        )
        db.session.add(textbook)
        db.session.flush()

        # Create a part
        part = Part(
            id=uuid.uuid4(),
            textbook_id=textbook.id,
            title='Part 1: Basics',
            order_index=0
        )
        db.session.add(part)
        db.session.flush()

        # Create a chapter
        chapter = Chapter(
            id=uuid.uuid4(),
            part_id=part.id,
            title='Chapter 1: Introduction',
            order_index=0
        )
        db.session.add(chapter)
        db.session.flush()

        # Create topics
        topics = [
            Topic(
                id=uuid.uuid4(),
                chapter_id=chapter.id,
                title=f'Topic {i}: {title}',
                comment=f'Test comment for {title}',
                order_index=i
            )
            for i, title in enumerate([
                'What is Python?',
                'Installing Python',
                'Basic Syntax'
            ])
        ]
        for topic in topics:
            db.session.add(topic)

        # Commit all changes
        db.session.commit()

        # Verify the data was saved
        saved_textbook = Textbook.query.filter_by(title='Introduction to Python').first()
        assert saved_textbook is not None
        print(f"\nCreated textbook: {saved_textbook.title}")

        saved_part = Part.query.filter_by(textbook_id=saved_textbook.id).first()
        assert saved_part is not None
        print(f"Created part: {saved_part.title}")

        saved_chapter = Chapter.query.filter_by(part_id=saved_part.id).first()
        assert saved_chapter is not None
        print(f"Created chapter: {saved_chapter.title}")

        saved_topics = Topic.query.filter_by(chapter_id=saved_chapter.id).all()
        assert len(saved_topics) == 3
        for topic in saved_topics:
            print(f"Created topic: {topic.title}")

def test_query_textbook_structure(test_client):
    """Test querying the complete textbook structure"""
    # First create a textbook with structure
    test_create_textbook(test_client)

    with test_client.application.app_context():
        # Query the textbook and its structure
        textbook = Textbook.query.filter_by(title='Introduction to Python').first()
        assert textbook is not None

        # Get all parts
        parts = Part.query.filter_by(textbook_id=textbook.id).order_by(Part.order_index).all()
        for part in parts:
            print(f"\nPart: {part.title}")
            
            # Get chapters for each part
            chapters = Chapter.query.filter_by(part_id=part.id).order_by(Chapter.order_index).all()
            for chapter in chapters:
                print(f"  Chapter: {chapter.title}")
                
                # Get topics for each chapter
                topics = Topic.query.filter_by(chapter_id=chapter.id).order_by(Topic.order_index).all()
                for topic in topics:
                    print(f"    Topic: {topic.title}")
                    print(f"      Comment: {topic.comment}")

def test_update_textbook(test_client):
    """Test updating textbook information"""
    with test_client.application.app_context():
        # First create a textbook
        test_create_textbook(test_client)

        # Update the textbook
        textbook = Textbook.query.filter_by(title='Introduction to Python').first()
        textbook.title = 'Python Programming: Updated Edition'
        textbook.description = 'Updated description'
        db.session.commit()

        # Verify the update
        updated_textbook = Textbook.query.get(textbook.id)
        assert updated_textbook.title == 'Python Programming: Updated Edition'
        print(f"\nUpdated textbook title to: {updated_textbook.title}")

def test_create_textbook_with_review(test_client):
    """Test creating a textbook with a review"""
    with test_client.application.app_context():
        # Create a test user first
        user = User(
            id=uuid.uuid4(),
            email='test@example.com',
            username='testuser',
            full_name='Test User'
        )
        db.session.add(user)
        db.session.flush()

        # Create a textbook
        textbook = Textbook(
            id=uuid.uuid4(),
            title='Introduction to Python',
            author='Test Author',
            subject='Computer Science',
            description='A test textbook',
            tags=['python', 'programming'],
            difficulty_level='beginner',
            language='en'
        )
        db.session.add(textbook)
        db.session.flush()

        # Add a review
        review = TextbookReview(
            id=uuid.uuid4(),
            textbook_id=textbook.id,
            user_id=user.id,
            rating=5,
            comment='Great textbook!'
        )
        db.session.add(review)
        db.session.commit()

        # Verify the data
        saved_textbook = Textbook.query.filter_by(title='Introduction to Python').first()
        assert saved_textbook is not None
        assert len(saved_textbook.reviews) == 1
        assert saved_textbook.reviews[0].rating == 5 