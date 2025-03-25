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
    
    id = db.Column(db.String(36), primary_key=True)  # Supabase UUID
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    preferred_study_time = db.Column(db.String(50))
    notification_preferences = db.Column(db.JSON)
    study_goals = db.Column(db.JSON)
    
    # Relationships
    decks = db.relationship('Deck', backref='creator', lazy=True)
    live_decks = db.relationship('LiveDeck', backref='owner', lazy=True)
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)
    analytics = db.relationship('LearningAnalytics', backref='user', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)
    reminders = db.relationship('StudyReminder', backref='user', lazy=True)
    
    @classmethod
    def get_or_create_from_supabase(cls, supabase_user):
        """Get or create a user from Supabase auth data"""
        user = cls.query.get(supabase_user.id)
        if not user:
            user = cls(
                id=supabase_user.id,
                email=supabase_user.email,
                username=supabase_user.email.split('@')[0],  # Default username from email
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
        return user
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'preferred_study_time': self.preferred_study_time,
            'notification_preferences': self.notification_preferences,
            'study_goals': self.study_goals
        }

class Deck(db.Model):
    """Base deck model that represents the original deck"""
    __tablename__ = 'decks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Version tracking
    version = db.Column(db.Integer, default=1)
    parent_version_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=True)
    
    # Statistics
    total_cards = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', back_populates='decks')
    parts = db.relationship('Part', back_populates='deck', lazy=True, cascade='all, delete-orphan')
    live_decks = db.relationship('LiveDeck', back_populates='deck', lazy=True)
    parent_version = db.relationship('Deck', remote_side=[id], backref='child_versions')

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'is_public': self.is_public,
            'version': self.version,
            'total_cards': self.total_cards,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LiveDeck(db.Model):
    """Represents a user's active version of a deck with their card preferences"""
    __tablename__ = 'live_decks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)  # User's custom name for this version
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistics
    active_cards = db.Column(db.Integer, default=0)
    
    # Relationships
    deck = db.relationship('Deck', back_populates='live_decks')
    card_states = db.relationship('UserCardState', back_populates='live_deck', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'active_cards': self.active_cards,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deck = db.relationship('Deck', back_populates='parts')
    chapters = db.relationship('Chapter', back_populates='part', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id = db.Column(UUID(as_uuid=True), db.ForeignKey('parts.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    part = db.relationship('Part', back_populates='chapters')
    topics = db.relationship('Topic', back_populates='chapter', lazy=True, cascade='all, delete-orphan')

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = db.relationship('Chapter', back_populates='topics')
    cards = db.relationship('Card', back_populates='topic', lazy=True, cascade='all, delete-orphan')

class Card(db.Model):
    """Base card model that represents the original card"""
    __tablename__ = 'cards'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = db.Column(UUID(as_uuid=True), db.ForeignKey('topics.id'), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topic = db.relationship('Topic', back_populates='cards')
    user_states = db.relationship('UserCardState', back_populates='card', lazy=True)

class UserCardState(db.Model):
    """Tracks the state of each card for each user in their live deck"""
    __tablename__ = 'user_card_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    live_deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('live_decks.id'), nullable=False)
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
    
    # Relationships
    user = db.relationship('User', back_populates='card_states')
    live_deck = db.relationship('LiveDeck', back_populates='card_states')
    card = db.relationship('Card', back_populates='user_states')

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    live_deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('live_decks.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
    # Statistics
    cards_studied = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', back_populates='study_sessions')
    live_deck = db.relationship('LiveDeck', backref='study_sessions')
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

class LearningAnalytics(db.Model):
    """Tracks learning analytics for users"""
    __tablename__ = 'learning_analytics'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    live_deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('live_decks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Study preferences
    preferred_study_time = db.Column(db.String(5))  # HH:MM format
    average_session_duration = db.Column(db.Integer)  # in minutes
    cards_per_session = db.Column(db.Integer)
    
    # Performance metrics
    mastery_level = db.Column(db.Float)  # 0-100
    weak_areas = db.Column(db.JSON)  # List of topic IDs
    strong_areas = db.Column(db.JSON)  # List of topic IDs
    
    # Learning style
    preferred_card_types = db.Column(db.JSON)  # List of preferred card types
    study_consistency = db.Column(db.Float)  # 0-100

class DeckCollaboration(db.Model):
    """Manages collaboration on decks"""
    __tablename__ = 'deck_collaborations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # owner, editor, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Permissions
    can_edit = db.Column(db.Boolean, default=False)
    can_share = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)

class Achievement(db.Model):
    """Tracks user achievements"""
    __tablename__ = 'achievements'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # streak, mastery, creation, etc.
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    achievement_data = db.Column(db.JSON)  # Additional achievement data

class StudyReminder(db.Model):
    """Manages study reminders"""
    __tablename__ = 'study_reminders'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    live_deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('live_decks.id'), nullable=False)
    reminder_time = db.Column(db.Time, nullable=False)  # HH:MM format
    days_of_week = db.Column(db.JSON, nullable=False)  # List of days (0-6)
    notification_type = db.Column(db.String(20), default='in-app')  # in-app, email, push
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class DeckExport(db.Model):
    """Tracks deck exports"""
    __tablename__ = 'deck_exports'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    format = db.Column(db.String(20), nullable=False)  # anki, csv, pdf
    settings = db.Column(db.JSON)  # Export settings
    file_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class ContentReport(db.Model):
    """Tracks content reports"""
    __tablename__ = 'content_reports'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # deck, card, comment
    content_id = db.Column(UUID(as_uuid=True), nullable=False)
    reason = db.Column(db.String(50), nullable=False)  # inappropriate, copyright, spam
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

class APILog(db.Model):
    """Logs API usage"""
    __tablename__ = 'api_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    endpoint = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response_time = db.Column(db.Integer)  # milliseconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
