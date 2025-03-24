import sys
import os
import pytest
from flask import Flask
from app.models import db, User, Deck, Textbook, Part, Chapter, Topic, Card, StudySession, CardReview
from app.api import api
import json
import uuid
from datetime import datetime

# Test database configuration
TEST_DB_CONFIG = {
    'user': 'postgres',
    'password': 'admin',
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'anki_test_db'
}

TEST_DATABASE_URL = f"postgresql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['database']}"

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URL,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'ANTHROPIC_API_KEY': 'test-key'
    })
    
    # Initialize the app with SQLAlchemy
    db.init_app(app)
    app.register_blueprint(api)
    
    return app

@pytest.fixture(scope='function')
def test_client(app):
    with app.app_context():
        db.create_all()
        
        # Create test user
        test_user = User(
            id=uuid.uuid4(),
            email='test@example.com',
            username='testuser',
            full_name='Test User'
        )
        test_user.set_password('testpass')
        db.session.add(test_user)
        
        # Create test deck
        test_deck = Deck(
            id=uuid.uuid4(),
            owner_id=test_user.id,
            name='Test Deck',
            description='Test deck for automated testing'
        )
        db.session.add(test_deck)
        
        db.session.commit()
        
        yield app.test_client()
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(test_client):
    with test_client.application.app_context():
        return User.query.filter_by(username='testuser').first()

@pytest.fixture
def test_deck(test_client):
    with test_client.application.app_context():
        return Deck.query.first()

def test_database_connection(test_client):
    """Test database connection"""
    with test_client.application.app_context():
        try:
            db.session.execute('SELECT 1')
            db.session.commit()
            assert True
        except Exception as e:
            assert False, f"Database connection failed: {str(e)}"

def test_create_textbook_and_structure(test_client, mocker):
    """Test creating a textbook and its structure"""
    # Mock Anthropic API calls
    mock_completion = mocker.patch('app.api.get_anthropic_completion')
    
    # Mock analysis response
    mock_completion.return_value = json.dumps({
        "primary_subject": "Computer Science",
        "subfields": ["Programming", "Python"],
        "requires_math": False,
        "benefits_from_code": True,
        "recommended_focus_areas": ["Python basics"]
    })

    # Test analyze textbook
    response = test_client.post('/api/analyze-textbook', json={
        'textbook_name': 'Python Programming',
        'test_mode': True
    })
    
    assert response.status_code == 200
    analysis = response.get_json()
    print("\nAnalysis Response:", json.dumps(analysis, indent=2))
    assert analysis['primary_subject'] == 'Computer Science'

    # Mock structure response
    mock_completion.return_value = json.dumps({
        "parts": [{
            "title": "Part I: Basics",
            "chapters": [{
                "title": "Chapter 1: Introduction",
                "topics": [{
                    "title": "What is Python?",
                    "comment": "Basic introduction",
                    "card_count": 3
                }]
            }]
        }]
    })

    # Test generate structure
    response = test_client.post('/api/generate-textbook-structure', json={
        'textbook_name': 'Python Programming',
        'test_mode': True
    })
    
    assert response.status_code == 200
    structure = response.get_json()
    print("\nStructure Response:", json.dumps(structure, indent=2))

    # Verify database entries
    with test_client.application.app_context():
        # Check textbook was created
        textbook = Textbook.query.filter_by(title='Python Programming').first()
        assert textbook is not None
        print("\nTextbook created:", textbook.title)

        # Check part was created
        part = Part.query.filter_by(textbook_id=textbook.id).first()
        assert part is not None
        assert part.title == "Part I: Basics"
        print("Part created:", part.title)

        # Check chapter was created
        chapter = Chapter.query.filter_by(part_id=part.id).first()
        assert chapter is not None
        assert chapter.title == "Chapter 1: Introduction"
        print("Chapter created:", chapter.title)

        # Check topic was created
        topic = Topic.query.filter_by(chapter_id=chapter.id).first()
        assert topic is not None
        assert topic.title == "What is Python?"
        print("Topic created:", topic.title)

def test_generate_cards(test_client, mocker):
    """Test card generation"""
    # First create a textbook structure
    with test_client.application.app_context():
        # Create test textbook
        textbook = Textbook(
            id=uuid.uuid4(),
            title='Test Python Book',
            author='Test Author',
            subject='Computer Science'
        )
        db.session.add(textbook)

        # Create test part
        part = Part(
            id=uuid.uuid4(),
            textbook_id=textbook.id,
            title='Test Part',
            order_index=0
        )
        db.session.add(part)

        # Create test chapter
        chapter = Chapter(
            id=uuid.uuid4(),
            part_id=part.id,
            title='Test Chapter',
            order_index=0
        )
        db.session.add(chapter)

        # Create test topic
        topic = Topic(
            id=uuid.uuid4(),
            chapter_id=chapter.id,
            title='Test Topic',
            comment='Test comment',
            order_index=0
        )
        db.session.add(topic)

        # Create test deck
        deck = Deck(
            id=uuid.uuid4(),
            name='Test Deck',
            description='Test Description'
        )
        db.session.add(deck)
        db.session.commit()

        # Mock card generation response
        mock_completion = mocker.patch('app.api.get_anthropic_completion')
        mock_completion.return_value = json.dumps([
            {
                "front": "What is Python?",
                "back": "Python is a programming language"
            },
            {
                "front": "Who created Python?",
                "back": "Guido van Rossum"
            }
        ])

        # Test generate cards
        response = test_client.post('/api/generate-cards', json={
            'topic_id': str(topic.id),
            'deck_id': str(deck.id),
            'test_mode': True
        })
        
        assert response.status_code == 200
        cards = response.get_json()
        print("\nGenerated Cards:", json.dumps(cards, indent=2))

        # Verify cards in database
        db_cards = Card.query.filter_by(deck_id=deck.id).all()
        assert len(db_cards) > 0
        print(f"\nNumber of cards created: {len(db_cards)}")
        for card in db_cards:
            print(f"Card: {card.front} -> {card.back}")

def test_error_handling(test_client):
    """Test API error handling"""
    # Test missing textbook name
    response = test_client.post('/api/analyze-textbook', json={})
    assert response.status_code == 400
    
    # Test invalid topic_id
    response = test_client.post('/api/generate-cards', json={
        'topic_id': str(uuid.uuid4()),
        'deck_id': str(uuid.uuid4())
    })
    assert response.status_code == 404

def test_study_session(test_client, test_user, test_deck):
    """Test study session creation and card review"""
    # Create study session
    response = test_client.post('/api/study-sessions', json={
        'deck_id': str(test_deck.id)
    })
    assert response.status_code == 200
    session_data = response.get_json()
    session_id = session_data['sessionId']

    # Create a test card
    with test_client.application.app_context():
        card = Card(
            id=uuid.uuid4(),
            deck_id=test_deck.id,
            topic_id=uuid.uuid4(),  # Dummy topic ID
            front='Test question',
            back='Test answer'
        )
        db.session.add(card)
        db.session.commit()

        # Review the card
        response = test_client.post('/api/review-card', json={
            'card_id': str(card.id),
            'session_id': session_id,
            'quality': 4,
            'time_taken': 1000
        })
        assert response.status_code == 200
        review_data = response.get_json()
        assert 'cardId' in review_data
        assert 'nextReview' in review_data

def test_due_cards(test_client, test_deck):
    """Test getting due cards"""
    response = test_client.get(f'/api/decks/{str(test_deck.id)}/due-cards')
    assert response.status_code == 200
    cards = response.get_json()
    assert isinstance(cards, list)

if __name__ == '__main__':
    pytest.main(['-v']) 