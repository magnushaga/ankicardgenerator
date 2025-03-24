from datetime import datetime
from .extensions import db
from sqlalchemy.dialects.postgresql import UUID
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Association table for deck sharing
deck_shares = db.Table('deck_shares',
    db.Column('deck_id', UUID(as_uuid=True), db.ForeignKey('decks.id'), primary_key=True),
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True),
    db.Column('shared_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Remove all other relationships except decks
    decks = db.relationship('Deck', back_populates='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'createdAt': self.created_at.isoformat()
        }

class Deck(db.Model):
    __tablename__ = 'decks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Update relationship to use back_populates instead of backref
    user = db.relationship('User', back_populates='decks')
    parts = db.relationship('Part', back_populates='deck', lazy=True, cascade='all, delete-orphan')

class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Update relationship to use back_populates
    deck = db.relationship('Deck', back_populates='parts')
    chapters = db.relationship('Chapter', back_populates='part', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id = db.Column(UUID(as_uuid=True), db.ForeignKey('parts.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Update relationship to use back_populates
    part = db.relationship('Part', back_populates='chapters')
    topics = db.relationship('Topic', back_populates='chapter', lazy=True, cascade='all, delete-orphan')

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Update relationship to use back_populates
    chapter = db.relationship('Chapter', back_populates='topics')
    cards = db.relationship('Card', back_populates='topic', lazy=True, cascade='all, delete-orphan')

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = db.Column(UUID(as_uuid=True), db.ForeignKey('topics.id'), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Update relationship to use back_populates
    topic = db.relationship('Topic', back_populates='cards')

class UserCardState(db.Model):
    """Tracks the state of each card for each user"""
    __tablename__ = 'user_card_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    card_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cards.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SuperMemo2 algorithm fields
    easiness = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=1)  # in days
    repetitions = db.Column(db.Integer, default=0)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    last_review = db.Column(db.DateTime)

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
    # Statistics
    cards_studied = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    
    # Relationships
    reviews = db.relationship('CardReview', backref='session', lazy=True, cascade='all, delete-orphan')

class CardReview(db.Model):
    __tablename__ = 'card_reviews'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('study_sessions.id'), nullable=False)
    card_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cards.id'), nullable=False)
    quality = db.Column(db.Integer, nullable=False)  # 0-5 rating
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_taken = db.Column(db.Integer)  # milliseconds
    
    # Previous state
    prev_easiness = db.Column(db.Float)
    prev_interval = db.Column(db.Integer)
    prev_repetitions = db.Column(db.Integer)
    
    # New state
    new_easiness = db.Column(db.Float)
    new_interval = db.Column(db.Integer)
    new_repetitions = db.Column(db.Integer)

class TextbookReview(db.Model):
    __tablename__ = 'textbook_reviews'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = db.Column(UUID(as_uuid=True), db.ForeignKey('textbooks.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Change this to use backref instead of back_populates
    textbook = db.relationship('Textbook', backref='reviews')
    user = db.relationship('User', backref='textbook_reviews')

class Textbook(db.Model):
    __tablename__ = 'textbooks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    # Search fields
    tags = db.Column(db.JSON, default=list)
    difficulty_level = db.Column(db.String(20))
    language = db.Column(db.String(10), default='en')
    
    # Metadata
    total_cards = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0.0)
    num_ratings = db.Column(db.Integer, default=0)