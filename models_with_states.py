from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event, text
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

# Association table for deck sharing
deck_shares = db.Table('deck_shares',
    db.Column('deck_id', UUID(as_uuid=True), db.ForeignKey('decks.id'), primary_key=True),
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True),
    db.Column('shared_at', db.DateTime, default=datetime.utcnow)
)

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
    owned_decks = db.relationship('Deck', backref='owner', foreign_keys='Deck.owner_id', lazy=True)
    shared_decks = db.relationship('Deck', secondary=deck_shares, backref='shared_with', lazy=True)
    textbooks = db.relationship('Textbook', backref='owner', lazy=True)
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)
    
    # State tracking relationships
    part_states = db.relationship('UserPartState', backref='user', lazy=True)
    chapter_states = db.relationship('UserChapterState', backref='user', lazy=True)
    topic_states = db.relationship('UserTopicState', backref='user', lazy=True)
    card_states = db.relationship('UserCardState', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Textbook(db.Model):
    __tablename__ = 'textbooks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    tags = db.Column(db.JSON, default=list)
    difficulty_level = db.Column(db.String(20))
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Deck(db.Model):
    __tablename__ = 'decks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    # For forked decks
    parent_deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=True)
    forked_at = db.Column(db.DateTime)
    
    # Optional textbook association
    textbook_id = db.Column(UUID(as_uuid=True), db.ForeignKey('textbooks.id'), nullable=True)
    
    # Relationships
    parts = db.relationship('Part', backref='deck', lazy=True, cascade='all, delete-orphan')
    child_decks = db.relationship('Deck', backref=db.backref('parent_deck', remote_side=[id]))
    cards = db.relationship('Card', backref='deck', lazy=True)

    def fork_for_user(self, user_id):
        """Create a copy of this deck for another user"""
        forked_deck = Deck(
            owner_id=user_id,
            name=f"{self.name} (Forked)",
            description=self.description,
            parent_deck_id=self.id,
            forked_at=datetime.utcnow()
        )
        return forked_deck

class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='part', lazy=True, cascade='all, delete-orphan')
    states = db.relationship('UserPartState', backref='part', lazy=True)

class UserPartState(db.Model):
    __tablename__ = 'user_part_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    part_id = db.Column(UUID(as_uuid=True), db.ForeignKey('parts.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'part_id', name='uq_user_part_state'),)

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id = db.Column(UUID(as_uuid=True), db.ForeignKey('parts.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    topics = db.relationship('Topic', backref='chapter', lazy=True, cascade='all, delete-orphan')
    states = db.relationship('UserChapterState', backref='chapter', lazy=True)

class UserChapterState(db.Model):
    __tablename__ = 'user_chapter_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chapters.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'chapter_id', name='uq_user_chapter_state'),)

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cards = db.relationship('Card', backref='topic', lazy=True, cascade='all, delete-orphan')
    states = db.relationship('UserTopicState', backref='topic', lazy=True)

class UserTopicState(db.Model):
    __tablename__ = 'user_topic_states'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(UUID(as_uuid=True), db.ForeignKey('topics.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'topic_id', name='uq_user_topic_state'),)

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('decks.id'), nullable=False)
    topic_id = db.Column(UUID(as_uuid=True), db.ForeignKey('topics.id'), nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    states = db.relationship('UserCardState', backref='card', lazy=True)

class UserCardState(db.Model):
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
    
    __table_args__ = (db.UniqueConstraint('user_id', 'card_id', name='uq_user_card_state'),)

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

def get_state_by_type(state_type, user_id, item_id):
    """Helper function to get state by type"""
    state_models = {
        'part': UserPartState,
        'chapter': UserChapterState,
        'topic': UserTopicState,
        'card': UserCardState
    }
    
    if state_type not in state_models:
        raise ValueError(f"Invalid state type: {state_type}")
        
    StateModel = state_models[state_type]
    filter_kwargs = {
        'user_id': user_id,
        f'{state_type}_id': item_id
    }
    
    return StateModel.query.filter_by(**filter_kwargs).first()

def toggle_state(state_type, user_id, item_id, is_active):
    """Toggle the active state of an item"""
    state = get_state_by_type(state_type, user_id, item_id)
    
    if not state:
        state_models = {
            'part': UserPartState,
            'chapter': UserChapterState,
            'topic': UserTopicState,
            'card': UserCardState
        }
        StateModel = state_models[state_type]
        
        kwargs = {
            'user_id': user_id,
            f'{state_type}_id': item_id,
            'is_active': is_active
        }
        state = StateModel(**kwargs)
        db.session.add(state)
    else:
        state.is_active = is_active
        state.updated_at = datetime.utcnow()
    
    db.session.commit()
    return state