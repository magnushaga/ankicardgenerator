from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User:
    def __init__(self, id, email, username, auth0_id=None):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.username = username
        self.auth0_id = auth0_id
        self.created_at = datetime.utcnow()
        self.last_login = datetime.utcnow()

    @staticmethod
    def from_auth0_claims(claims):
        return User(
            id=None,  # Supabase will generate this
            email=claims['email'],
            username=claims.get('nickname', claims['email'].split('@')[0]),
            auth0_id=claims['sub']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'auth0_id': self.auth0_id,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat()
        }

class TestUser:
    def __init__(self, id, email, username, auth0_id=None, test_group=None, test_data=None):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.username = username
        self.auth0_id = auth0_id
        self.test_group = test_group
        self.test_data = test_data or {}
        self.created_at = datetime.utcnow()
        self.last_login = datetime.utcnow()
        self.is_active = True
        self.email_verified = False

    @staticmethod
    def from_auth0_claims(claims):
        return TestUser(
            id=None,  # Supabase will generate this
            email=claims['email'],
            username=claims.get('nickname', claims['email'].split('@')[0]),
            auth0_id=claims['sub'],
            email_verified=claims.get('email_verified', False)
        )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'auth0_id': self.auth0_id,
            'test_group': self.test_group,
            'test_data': self.test_data,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat(),
            'is_active': self.is_active,
            'email_verified': self.email_verified
        }

class Textbook:
    def __init__(self, id, title, author, subject):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.author = author
        self.subject = subject
        self.created_at = datetime.utcnow()

class Part:
    def __init__(self, id, textbook_id, title, order_index):
        self.id = id or str(uuid.uuid4())
        self.textbook_id = textbook_id
        self.title = title
        self.order_index = order_index

class Chapter:
    def __init__(self, id, part_id, title, order_index):
        self.id = id or str(uuid.uuid4())
        self.part_id = part_id
        self.title = title
        self.order_index = order_index

class Topic:
    def __init__(self, id, chapter_id, title, comment, order_index):
        self.id = id or str(uuid.uuid4())
        self.chapter_id = chapter_id
        self.title = title
        self.comment = comment
        self.order_index = order_index

class Deck:
    def __init__(self, id, user_id, title):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.created_at = datetime.utcnow()

class Card:
    def __init__(self, id, deck_id, topic_id, front, back):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.topic_id = topic_id
        self.front = front
        self.back = back
        self.created_at = datetime.utcnow()
        self.next_review = datetime.utcnow()
        self.interval = 1
        self.easiness = 2.5
        self.repetitions = 0

class StudySession:
    def __init__(self, id, deck_id):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.started_at = datetime.utcnow()
        self.ended_at = None

class CardReview:
    def __init__(self, id, session_id, card_id, quality, time_taken):
        self.id = id or str(uuid.uuid4())
        self.session_id = session_id
        self.card_id = card_id
        self.quality = quality
        self.time_taken = time_taken
        self.created_at = datetime.utcnow()
        self.prev_easiness = None
        self.prev_interval = None
        self.prev_repetitions = None
        self.new_easiness = None
        self.new_interval = None
        self.new_repetitions = None 