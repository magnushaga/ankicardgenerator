from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event, text
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Profile fields
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    preferences = db.Column(db.JSON, default=dict)
    
    # Relationships
    decks = db.relationship('Deck', backref='owner', lazy=True)
    textbooks = db.relationship('Textbook', backref='owner', lazy=True)
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'fullName': self.full_name,
            'bio': self.bio,
            'createdAt': self.created_at.isoformat(),
            'lastLogin': self.last_login.isoformat() if self.last_login else None,
            'preferences': self.preferences
        }

class Textbook(db.Model):
    __tablename__ = 'textbooks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    # Search fields
    description = db.Column(db.Text)
    tags = db.Column(db.JSON, default=list)  # List of subject tags
    difficulty_level = db.Column(db.String(20))  # e.g., 'beginner', 'intermediate', 'advanced'
    language = db.Column(db.String(10), default='en')  # ISO language code
    
    # Metadata
    total_cards = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0.0)
    num_ratings = db.Column(db.Integer, default=0)
    
    # Relationships
    parts = db.relationship('Part', backref='textbook', lazy=True, cascade='all, delete-orphan')
    decks = db.relationship('Deck', backref='textbook', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('TextbookReview', backref='textbook', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'userId': str(self.user_id),
            'title': self.title,
            'author': self.author,
            'subject': self.subject,
            'description': self.description,
            'tags': self.tags,
            'difficultyLevel': self.difficulty_level,
            'language': self.language,
            'isPublic': self.is_public,
            'uploadedAt': self.uploaded_at.isoformat(),
            'totalCards': self.total_cards,
            'avgRating': self.avg_rating,
            'numRatings': self.num_ratings
        }

class TextbookReview(db.Model):
    __tablename__ = 'textbook_reviews'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = db.Column(UUID(as_uuid=True), db.ForeignKey('textbooks.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'textbookId': str(self.textbook_id),
            'userId': str(self.user_id),
            'rating': self.rating,
            'comment': self.comment,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = db.Column(UUID(as_uuid=True), db.ForeignKey('textbooks.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='part', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id = db.Column(UUID(as_uuid=True), db.ForeignKey('parts.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Relationships
    topics = db.relationship('Topic', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    
    # Relationships
    cards = db.relationship('Card', backref='topic', lazy=True, cascade='all, delete-orphan')

class Deck(db.Model):
    __tablename__ = 'decks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = db.Column(UUID(as_uuid=True), db.ForeignKey('textbooks.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cards = db.relationship('Card', backref='deck', lazy=True, cascade='all, delete-orphan')

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    topic_id = db.Column(UUID(as_uuid=True), db.ForeignKey('topics.id'), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # SuperMemo2 algorithm fields
    easiness = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=1)  # in days
    repetitions = db.Column(db.Integer, default=0)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
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