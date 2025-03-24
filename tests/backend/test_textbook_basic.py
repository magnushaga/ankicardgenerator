import sys
import os
import pytest
from flask import Flask
from app.models import db, Textbook, Part, Chapter, Topic
import uuid

# Test database configuration
DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:admin@127.0.0.1:5432/anki_test_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'TESTING': True
}

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.config.update(DB_CONFIG)
    
    db.init_app(app)
    return app

@pytest.fixture(scope='function')
def test_client(app):
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_basic_textbook_creation(test_client):
    """Test basic textbook creation and storage"""
    with test_client.application.app_context():
        # Create a simple textbook
        textbook = Textbook(
            id=uuid.uuid4(),
            title='Introduction to Python',
            author='Test Author',
            subject='Computer Science'
        )
        
        # Add to database
        db.session.add(textbook)
        db.session.commit()
        
        # Verify the textbook was saved
        saved_textbook = Textbook.query.filter_by(title='Introduction to Python').first()
        assert saved_textbook is not None
        assert saved_textbook.author == 'Test Author'
        print(f"\nCreated and verified textbook: {saved_textbook.title}")

def test_textbook_with_structure(test_client):
    """Test creating a textbook with parts, chapters, and topics"""
    with test_client.application.app_context():
        # Create textbook
        textbook = Textbook(
            id=uuid.uuid4(),
            title='Python Programming',
            author='Test Author',
            subject='Computer Science'
        )
        db.session.add(textbook)
        db.session.flush()
        
        # Create part
        part = Part(
            id=uuid.uuid4(),
            textbook_id=textbook.id,
            title='Part 1: Basics',
            order_index=0
        )
        db.session.add(part)
        db.session.flush()
        
        # Create chapter
        chapter = Chapter(
            id=uuid.uuid4(),
            part_id=part.id,
            title='Chapter 1: Introduction',
            order_index=0
        )
        db.session.add(chapter)
        db.session.flush()
        
        # Create topic
        topic = Topic(
            id=uuid.uuid4(),
            chapter_id=chapter.id,
            title='What is Python?',
            comment='Introduction to Python programming language',
            order_index=0
        )
        db.session.add(topic)
        
        # Save everything
        db.session.commit()
        
        # Verify the structure
        saved_textbook = Textbook.query.filter_by(title='Python Programming').first()
        assert saved_textbook is not None
        print(f"\nCreated textbook: {saved_textbook.title}")
        
        saved_parts = Part.query.filter_by(textbook_id=saved_textbook.id).all()
        assert len(saved_parts) == 1
        print(f"Created part: {saved_parts[0].title}")
        
        saved_chapters = Chapter.query.filter_by(part_id=saved_parts[0].id).all()
        assert len(saved_chapters) == 1
        print(f"Created chapter: {saved_chapters[0].title}")
        
        saved_topics = Topic.query.filter_by(chapter_id=saved_chapters[0].id).all()
        assert len(saved_topics) == 1
        print(f"Created topic: {saved_topics[0].title}")

def test_api_textbook_creation(test_client):
    """Test creating a textbook through the API"""
    # Test data
    test_data = {
        'textbook_name': 'Python Programming Guide',
        'test_mode': True
    }
    
    # Test analyze endpoint
    response = test_client.post('/api/analyze-textbook', json=test_data)
    assert response.status_code == 200
    analysis = response.get_json()
    print("\nTextbook analysis:", analysis)
    
    # Test structure generation
    response = test_client.post('/api/generate-textbook-structure', json=test_data)
    assert response.status_code == 200
    structure = response.get_json()
    print("\nGenerated structure:", structure)
    
    # Verify database entries
    with test_client.application.app_context():
        textbook = Textbook.query.filter_by(title='Python Programming Guide').first()
        assert textbook is not None
        print(f"\nVerified textbook in database: {textbook.title}") 