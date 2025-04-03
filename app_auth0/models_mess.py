from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class SubjectCategories:
    """
    Model class for subject_categories table.
    """
    def __init__(self, id=None, name=None, description=None, parent_id=None, level=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.level = level
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'level': self.level,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class SubjectSubcategories:
    """
    Model class for subject_subcategories table.
    """
    def __init__(self, id=None, category_id=None, name=None, description=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.category_id = category_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ContentSubjectRelationships:
    """
    Model class for content_subject_relationships table.
    """
    def __init__(self, id=None, content_type_id=None, content_id=None, subject_id=None, 
                 subject_type=None, relationship_type=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.content_type_id = content_type_id  # References content_types table
        self.content_id = content_id
        self.subject_id = subject_id
        self.subject_type = subject_type
        self.relationship_type = relationship_type
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'content_type_id': self.content_type_id,
            'content_id': self.content_id,
            'subject_id': self.subject_id,
            'subject_type': self.subject_type,
            'relationship_type': self.relationship_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Textbooks:
    """
    Model class for textbooks table.
    """

    def __init__(self, id=None, user_id=None, title=None, author=None, subject=None, description=None, file_path=None, uploaded_at=None, is_public=None, tags=None, difficulty_level=None, language=None, total_cards=None, avg_rating=None, num_ratings=None, main_subject_id=None, subcategory_ids=None, content_type_id=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.author = author
        self.subject = subject
        self.description = description
        self.file_path = file_path
        self.uploaded_at = uploaded_at
        self.is_public = is_public
        self.tags = tags
        self.difficulty_level = difficulty_level
        self.language = language
        self.total_cards = total_cards
        self.avg_rating = avg_rating
        self.num_ratings = num_ratings
        self.main_subject_id = main_subject_id
        self.subcategory_ids = subcategory_ids or []
        self.content_type_id = content_type_id  # References content_types table (default: textbook type)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'author': self.author,
            'subject': self.subject,
            'description': self.description,
            'file_path': self.file_path,
            'uploaded_at': self.uploaded_at,
            'is_public': self.is_public,
            'tags': self.tags,
            'difficulty_level': self.difficulty_level,
            'language': self.language,
            'total_cards': self.total_cards,
            'avg_rating': self.avg_rating,
            'num_ratings': self.num_ratings,
            'main_subject_id': self.main_subject_id,
            'subcategory_ids': self.subcategory_ids,
            'content_type_id': self.content_type_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class DeckShares:
    """
    Model class for deck_shares table.
    """

    def __init__(self, id=None, deck_id=None, user_id=None, shared_at=None):
        self.deck_id = deck_id
        self.user_id = user_id
        self.shared_at = shared_at

    def to_dict(self):
        return {
            'deck_id': self.deck_id,
            'user_id': self.user_id,
            'shared_at': self.shared_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class StudySessions:
    """
    Model class for study_sessions table.
    """

    def __init__(self, id=None, user_id=None, deck_id=None, started_at=None, ended_at=None, cards_studied=None, correct_answers=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.deck_id = deck_id
        self.started_at = started_at
        self.ended_at = ended_at
        self.cards_studied = cards_studied
        self.correct_answers = correct_answers

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'deck_id': self.deck_id,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'cards_studied': self.cards_studied,
            'correct_answers': self.correct_answers,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Decks:
    """
    Model class for decks table.
    """

    def __init__(self, id=None, user_id=None, title=None, created_at=None, is_active=None, 
                 last_modified=None, modified_by=None, main_subject_id=None, subcategory_ids=None, 
                 source_textbook_id=None, content_type_id=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by
        self.main_subject_id = main_subject_id
        self.subcategory_ids = subcategory_ids or []
        self.source_textbook_id = source_textbook_id
        self.content_type_id = content_type_id  # References content_types table (default: deck type)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
            'main_subject_id': self.main_subject_id,
            'subcategory_ids': self.subcategory_ids,
            'source_textbook_id': self.source_textbook_id,
            'content_type_id': self.content_type_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class TextbookReviews:
    """
    Model class for textbook_reviews table.
    """

    def __init__(self, id=None, textbook_id=None, user_id=None, rating=None, comment=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.textbook_id = textbook_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'textbook_id': self.textbook_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class AdminRoles(Base):
    """Model class for admin_roles table."""
    __tablename__ = 'admin_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserCardStates:
    """
    Model class for user_card_states table.
    """

    def __init__(self, id=None, user_id=None, card_id=None, is_active=None, created_at=None, updated_at=None, easiness=None, interval=None, repetitions=None, next_review=None, last_review=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.card_id = card_id
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.easiness = easiness
        self.interval = interval
        self.repetitions = repetitions
        self.next_review = next_review
        self.last_review = last_review

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'card_id': self.card_id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'easiness': self.easiness,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'next_review': self.next_review,
            'last_review': self.last_review,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CardReviews:
    """
    Model class for card_reviews table.
    """

    def __init__(self, id=None, session_id=None, card_id=None, quality=None, reviewed_at=None, time_taken=None, prev_easiness=None, prev_interval=None, prev_repetitions=None, new_easiness=None, new_interval=None, new_repetitions=None):
        self.id = id or str(uuid.uuid4())
        self.session_id = session_id
        self.card_id = card_id
        self.quality = quality
        self.reviewed_at = reviewed_at
        self.time_taken = time_taken
        self.prev_easiness = prev_easiness
        self.prev_interval = prev_interval
        self.prev_repetitions = prev_repetitions
        self.new_easiness = new_easiness
        self.new_interval = new_interval
        self.new_repetitions = new_repetitions

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'card_id': self.card_id,
            'quality': self.quality,
            'reviewed_at': self.reviewed_at,
            'time_taken': self.time_taken,
            'prev_easiness': self.prev_easiness,
            'prev_interval': self.prev_interval,
            'prev_repetitions': self.prev_repetitions,
            'new_easiness': self.new_easiness,
            'new_interval': self.new_interval,
            'new_repetitions': self.new_repetitions,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class AdminPermissions(Base):
    """Model class for admin_permissions table."""
    __tablename__ = 'admin_permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminRolePermissions(Base):
    """Model class for admin_role_permissions table."""
    __tablename__ = 'admin_role_permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey('admin_roles.id'), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('admin_permissions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAdminRoles(Base):
    """Model class for user_admin_roles table."""
    __tablename__ = 'user_admin_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('admin_roles.id'), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminAuditLogs(Base):
    """Model class for admin_audit_logs table."""
    __tablename__ = 'admin_audit_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(255))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSONB)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

class Users(Base):
    """Model class for users table."""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True)
    auth0_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    preferred_study_time = Column(JSONB)
    notification_preferences = Column(JSONB)
    study_goals = Column(JSONB)
    stripe_customer_id = Column(String(255))
    picture = Column(String(1024))

class MediaFiles(Base):
    """Model class for media_files table."""
    __tablename__ = 'media_files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    mime_type = Column(String(255))
    storage_path = Column(String(1024))
    thumbnail_path = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MediaAssociations(Base):
    """Model class for media_associations table."""
    __tablename__ = 'media_associations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey('media_files.id'), nullable=False)
    associated_type = Column(String(50), nullable=False)
    associated_id = Column(UUID(as_uuid=True), nullable=False)
    position = Column(Integer)
    context = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserDecks:
    """
    Model class for user_decks table.
    """

    def __init__(self, id=None, user_id=None, deck_id=None, name=None, description=None, created_at=None, updated_at=None, total_cards=None, active_cards=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.deck_id = deck_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
        self.total_cards = total_cards
        self.active_cards = active_cards

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'deck_id': self.deck_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'total_cards': self.total_cards,
            'active_cards': self.active_cards,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Parts:
    """
    Model class for parts table.
    """

    def __init__(self, id=None, deck_id=None, title=None, order_index=None, is_active=None, last_modified=None, modified_by=None):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.title = title
        self.order_index = order_index
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'title': self.title,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CourseMaterials:
    """
    Model class for course_materials table.
    """

    def __init__(self, id=None, user_id=None, title=None, description=None, content_type_id=None, 
                 file_path=None, file_size=None, mime_type=None, tags=None, metadata=None, 
                 created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.content_type_id = content_type_id  # References content_types table
        self.file_path = file_path
        self.file_size = file_size
        self.mime_type = mime_type
        self.tags = tags
        self.metadata = metadata
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'content_type_id': self.content_type_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class StudyResources(Base):
    """Model class for study_resources table."""
    __tablename__ = 'study_resources'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    content_type_id = Column(UUID(as_uuid=True), ForeignKey('content_types.id'))
    source_material_id = Column(UUID(as_uuid=True))
    tags = Column(ARRAY(String))
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResourceGenerations(Base):
    """Model class for resource_generations table."""
    __tablename__ = 'resource_generations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey('study_resources.id'), nullable=False)
    status = Column(String(50))
    generation_type = Column(String(50))
    prompt = Column(Text)
    result = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Chapters:
    """
    Model class for chapters table.
    """

    def __init__(self, id=None, part_id=None, title=None, order_index=None, is_active=None, last_modified=None, modified_by=None):
        self.id = id or str(uuid.uuid4())
        self.part_id = part_id
        self.title = title
        self.order_index = order_index
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by

    def to_dict(self):
        return {
            'id': self.id,
            'part_id': self.part_id,
            'title': self.title,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Topics:
    """
    Model class for topics table.
    """

    def __init__(self, id=None, chapter_id=None, title=None, order_index=None, is_active=None, last_modified=None, modified_by=None):
        self.id = id or str(uuid.uuid4())
        self.chapter_id = chapter_id
        self.title = title
        self.order_index = order_index
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by

    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'title': self.title,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Cards:
    """
    Model class for cards table.
    """

    def __init__(self, id=None, topic_id=None, front=None, back=None, created_at=None, media_urls=None, is_active=None, last_modified=None, modified_by=None):
        self.id = id or str(uuid.uuid4())
        self.topic_id = topic_id
        self.front = front
        self.back = back
        self.created_at = created_at
        self.media_urls = media_urls
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'front': self.front,
            'back': self.back,
            'created_at': self.created_at,
            'media_urls': self.media_urls,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class LiveDeckParts:
    """
    Model class for live_deck_parts table.
    """

    def __init__(self, id=None, live_deck_id=None, part_id=None, is_active=None, last_modified=None, modified_by=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.live_deck_id = live_deck_id
        self.part_id = part_id
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'live_deck_id': self.live_deck_id,
            'part_id': self.part_id,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class LiveDeckChapters:
    """
    Model class for live_deck_chapters table.
    """

    def __init__(self, id=None, live_deck_part_id=None, chapter_id=None, is_active=None, last_modified=None, modified_by=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.live_deck_part_id = live_deck_part_id
        self.chapter_id = chapter_id
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'live_deck_part_id': self.live_deck_part_id,
            'chapter_id': self.chapter_id,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class LiveDecks:
    """
    Model class for live_decks table.
    """

    def __init__(self, id=None, user_id=None, deck_id=None, name=None, description=None, created_at=None, updated_at=None, active_cards=None, main_subject_id=None, subcategory_ids=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.deck_id = deck_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
        self.active_cards = active_cards
        self.main_subject_id = main_subject_id
        self.subcategory_ids = subcategory_ids or []

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'deck_id': self.deck_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'active_cards': self.active_cards,
            'main_subject_id': self.main_subject_id,
            'subcategory_ids': self.subcategory_ids
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class LiveDeckTopics:
    """
    Model class for live_deck_topics table.
    """

    def __init__(self, id=None, live_deck_chapter_id=None, topic_id=None, is_active=None, last_modified=None, modified_by=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.live_deck_chapter_id = live_deck_chapter_id
        self.topic_id = topic_id
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'live_deck_chapter_id': self.live_deck_chapter_id,
            'topic_id': self.topic_id,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class LiveDeckCards:
    """
    Model class for live_deck_cards table.
    """

    def __init__(self, id=None, live_deck_topic_id=None, card_id=None, is_active=None, last_modified=None, modified_by=None, created_at=None, media_urls=None):
        self.id = id or str(uuid.uuid4())
        self.live_deck_topic_id = live_deck_topic_id
        self.card_id = card_id
        self.is_active = is_active if is_active is not None else True
        self.last_modified = last_modified or datetime.utcnow()
        self.modified_by = modified_by
        self.created_at = created_at or datetime.utcnow()
        self.media_urls = media_urls or []

    def to_dict(self):
        return {
            'id': self.id,
            'live_deck_topic_id': self.live_deck_topic_id,
            'card_id': self.card_id,
            'is_active': self.is_active,
            'last_modified': self.last_modified,
            'modified_by': self.modified_by,
            'created_at': self.created_at,
            'media_urls': self.media_urls,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class LearningAnalytics:
    """
    Model class for learning_analytics table.
    """

    def __init__(self, id=None, user_id=None, live_deck_id=None, created_at=None, updated_at=None, preferred_study_time=None, average_session_duration=None, cards_per_session=None, mastery_level=None, weak_areas=None, strong_areas=None, preferred_card_types=None, study_consistency=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.live_deck_id = live_deck_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.preferred_study_time = preferred_study_time
        self.average_session_duration = average_session_duration
        self.cards_per_session = cards_per_session
        self.mastery_level = mastery_level
        self.weak_areas = weak_areas
        self.strong_areas = strong_areas
        self.preferred_card_types = preferred_card_types
        self.study_consistency = study_consistency

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'live_deck_id': self.live_deck_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'preferred_study_time': self.preferred_study_time,
            'average_session_duration': self.average_session_duration,
            'cards_per_session': self.cards_per_session,
            'mastery_level': self.mastery_level,
            'weak_areas': self.weak_areas,
            'strong_areas': self.strong_areas,
            'preferred_card_types': self.preferred_card_types,
            'study_consistency': self.study_consistency,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class DeckCollaborations:
    """
    Model class for deck_collaborations table.
    """

    def __init__(self, id=None, deck_id=None, user_id=None, role=None, created_at=None, can_edit=None, can_share=None, can_delete=None):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.user_id = user_id
        self.role = role
        self.created_at = created_at
        self.can_edit = can_edit
        self.can_share = can_share
        self.can_delete = can_delete

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'user_id': self.user_id,
            'role': self.role,
            'created_at': self.created_at,
            'can_edit': self.can_edit,
            'can_share': self.can_share,
            'can_delete': self.can_delete,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Achievements:
    """
    Model class for achievements table.
    """

    def __init__(self, id=None, user_id=None, type=None, title=None, description=None, earned_at=None, achievement_data=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.type = type
        self.title = title
        self.description = description
        self.earned_at = earned_at
        self.achievement_data = achievement_data

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'earned_at': self.earned_at,
            'achievement_data': self.achievement_data,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class StudyReminders:
    """
    Model class for study_reminders table.
    """

    def __init__(self, id=None, user_id=None, live_deck_id=None, reminder_time=None, days_of_week=None, notification_type=None, created_at=None, is_active=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.live_deck_id = live_deck_id
        self.reminder_time = reminder_time
        self.days_of_week = days_of_week
        self.notification_type = notification_type
        self.created_at = created_at
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'live_deck_id': self.live_deck_id,
            'reminder_time': self.reminder_time,
            'days_of_week': self.days_of_week,
            'notification_type': self.notification_type,
            'created_at': self.created_at,
            'is_active': self.is_active,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class DeckExports:
    """
    Model class for deck_exports table.
    """

    def __init__(self, id=None, deck_id=None, user_id=None, format=None, settings=None, file_url=None, created_at=None, completed_at=None):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.user_id = user_id
        self.format = format
        self.settings = settings
        self.file_url = file_url
        self.created_at = created_at
        self.completed_at = completed_at

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'user_id': self.user_id,
            'format': self.format,
            'settings': self.settings,
            'file_url': self.file_url,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ContentRatings:
    """
    Model class for content_ratings table.
    Handles ratings for various types of content (decks, notes, courses, etc.).
    """
    def __init__(self, id=None, user_id=None, content_type_id=None, content_id=None, 
                 rating=None, review_text=None, helpful_count=None, created_at=None, 
                 updated_at=None, is_verified=None, institution_id=None, department_id=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.content_type_id = content_type_id  # References content_types table
        self.content_id = content_id
        self.rating = rating  # 1-5 scale
        self.review_text = review_text
        self.helpful_count = helpful_count or 0
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.is_verified = is_verified if is_verified is not None else False
        self.institution_id = institution_id
        self.department_id = department_id

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type_id': self.content_type_id,
            'content_id': self.content_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_verified': self.is_verified,
            'institution_id': self.institution_id,
            'department_id': self.department_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class RatingCategories:
    """
    Model class for rating_categories table.
    Defines different aspects that can be rated for different content types.
    """
    def __init__(self, id=None, name=None, description=None, content_type_id=None, 
                 is_active=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name  # e.g., 'Clarity', 'Accuracy', 'Usefulness'
        self.description = description
        self.content_type_id = content_type_id  # References content_types table
        self.is_active = is_active if is_active is not None else True
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'content_type_id': self.content_type_id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ContentTypes(Base):
    """Model class for content_types table."""
    __tablename__ = 'content_types'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentTypeRelationships(Base):
    """Model class for content_type_relationships table."""
    __tablename__ = 'content_type_relationships'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_type_id = Column(UUID(as_uuid=True), ForeignKey('content_types.id'), nullable=False)
    child_type_id = Column(UUID(as_uuid=True), ForeignKey('content_types.id'), nullable=False)
    relationship_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentReports(Base):
    """Model class for content_reports table."""
    __tablename__ = 'content_reports'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content_type_id = Column(UUID(as_uuid=True), ForeignKey('content_types.id'), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    reason = Column(String(255))
    description = Column(Text)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class ApiLogs:
    """
    Model class for api_logs table.
    """

    def __init__(self, id=None, user_id=None, endpoint=None, method=None, status_code=None, response_time=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.endpoint = endpoint
        self.method = method
        self.status_code = status_code
        self.response_time = response_time
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Subscriptions(Base):
    """Model class for subscriptions table."""
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    tier = Column(String(50))
    status = Column(String(50))
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    canceled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SubscriptionUsage(Base):
    """Model class for subscription_usage table."""
    __tablename__ = 'subscription_usage'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    feature = Column(String(255))
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EducationalInstitutions:
    """
    Model class for educational_institutions table.
    Represents schools, universities, and other educational institutions.
    """
    def __init__(self, id=None, name=None, type=None, country=None, city=None, 
                 website=None, description=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.type = type  # e.g., 'university', 'high_school', 'college'
        self.country = country
        self.city = city
        self.website = website
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'country': self.country,
            'city': self.city,
            'website': self.website,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class InstitutionDepartments:
    """
    Model class for institution_departments table.
    Represents departments or faculties within educational institutions.
    """
    def __init__(self, id=None, institution_id=None, name=None, description=None, 
                 created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.institution_id = institution_id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'institution_id': self.institution_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class UserInstitutionAffiliations:
    """
    Model class for user_institution_affiliations table.
    Tracks user affiliations with educational institutions.
    """
    def __init__(self, id=None, user_id=None, institution_id=None, department_id=None,
                 role=None, start_date=None, end_date=None, is_active=None, 
                 created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.institution_id = institution_id
        self.department_id = department_id
        self.role = role  # e.g., 'student', 'faculty', 'staff'
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active if is_active is not None else True
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'institution_id': self.institution_id,
            'department_id': self.department_id,
            'role': self.role,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class DeckInstitutionAssociations:
    """
    Model class for deck_institution_associations table.
    Associates decks with specific institutions and departments.
    """
    def __init__(self, id=None, deck_id=None, institution_id=None, department_id=None,
                 association_type=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.institution_id = institution_id
        self.department_id = department_id
        self.association_type = association_type  # e.g., 'official', 'community'
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'institution_id': self.institution_id,
            'department_id': self.department_id,
            'association_type': self.association_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Notes(Base):
    """Model class for notes table - Enhanced to link with course content."""
    __tablename__ = 'notes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    content_id = Column(UUID(as_uuid=True), ForeignKey('course_content.id'))
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('content_chapters.id'))
    title = Column(String(255), nullable=False)
    content = Column(Text)
    format = Column(String(50), default='markdown')
    tags = Column(ARRAY(String))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('notes.id'))
    version = Column(Integer, default=1)
    is_deleted = Column(Boolean, default=False)
    metadata = Column(JSONB)

class NoteVersions(Base):
    """Model class for note_versions table."""
    __tablename__ = 'note_versions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    change_summary = Column(String(500))
    metadata = Column(JSONB)

class NoteCollaborators(Base):
    """Model class for note_collaborators table."""
    __tablename__ = 'note_collaborators'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    permission_level = Column(String(50))
    invited_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NoteTags(Base):
    """Model class for note_tags table."""
    __tablename__ = 'note_tags'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id', ondelete='CASCADE'), nullable=False)
    tag = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

class NoteReferences(Base):
    """Model class for note_references table."""
    __tablename__ = 'note_references'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id', ondelete='CASCADE'), nullable=False)
    target_note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id'), nullable=False)
    reference_type = Column(String(50))
    context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

class Courses(Base):
    """Model class for courses table - Top level container for educational content."""
    __tablename__ = 'courses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subject_area = Column(String(255))
    level = Column(String(50))  # e.g., 'undergraduate', 'graduate', 'professional'
    institution_id = Column(UUID(as_uuid=True), ForeignKey('educational_institutions.id'))
    department_id = Column(UUID(as_uuid=True), ForeignKey('institution_departments.id'))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)
    tags = Column(ARRAY(String))

class CourseContent(Base):
    """Model class for course_content table - Organizes different types of content within a course."""
    __tablename__ = 'course_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    content_type = Column(String(50))  # 'textbook', 'lecture_slides', 'notes', 'exam'
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class ContentChapters(Base):
    """Model class for content_chapters table - Subdivides course content into chapters."""
    __tablename__ = 'content_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('course_content.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    file_path = Column(String(1024))  # For PDF chapters or other files
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentSections(Base):
    """Model class for content_sections table - Further subdivides chapters into sections."""
    __tablename__ = 'content_sections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('content_chapters.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudyMaterials(Base):
    """Model class for study_materials table - Stores various types of study content."""
    __tablename__ = 'study_materials'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    content_type = Column(String(50))  # 'notes', 'summary', 'practice_questions', 'flashcards'
    title = Column(String(255), nullable=False)
    content = Column(Text)
    file_path = Column(String(1024))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class ExamContent(Base):
    """Model class for exam_content table - Stores exam-related materials."""
    __tablename__ = 'exam_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    exam_type = Column(String(50))  # 'practice', 'past_exam', 'quiz'
    content = Column(Text)
    solutions = Column(Text)
    file_path = Column(String(1024))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class SemesterPlans(Base):
    """Model class for semester_plans table - Organizes course content by semester."""
    __tablename__ = 'semester_plans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)  # e.g., "Spring 2024"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey('educational_institutions.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)  # For additional semester-specific settings

class SemesterCourses(Base):
    """Model class for semester_courses table - Links courses to semesters."""
    __tablename__ = 'semester_courses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semester_id = Column(UUID(as_uuid=True), ForeignKey('semester_plans.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    schedule_data = Column(JSONB)  # Class schedule, office hours, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeeklyPlans(Base):
    """Model class for weekly_plans table - Organizes content by week."""
    __tablename__ = 'weekly_plans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semester_id = Column(UUID(as_uuid=True), ForeignKey('semester_plans.id'), nullable=False)
    week_number = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text)
    learning_objectives = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeeklyContent(Base):
    """Model class for weekly_content table - Links content to specific weeks."""
    __tablename__ = 'weekly_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    week_id = Column(UUID(as_uuid=True), ForeignKey('weekly_plans.id'), nullable=False)
    content_type = Column(String(50))  # 'lecture', 'reading', 'assignment', 'exam'
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserUploads(Base):
    """Model class for user_uploads table - Stores uploaded content with metadata."""
    __tablename__ = 'user_uploads'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    week_id = Column(UUID(as_uuid=True), ForeignKey('weekly_plans.id'))
    upload_type = Column(String(50))  # 'lecture_notes', 'slides', 'textbook', 'assignment'
    file_path = Column(String(1024))
    file_type = Column(String(50))
    file_size = Column(Integer)
    title = Column(String(255))
    description = Column(Text)
    metadata = Column(JSONB)  # Store OCR text, extracted content, etc.
    processing_status = Column(String(50))  # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentMappings(Base):
    """Model class for content_mappings table - Maps uploaded content to course structure."""
    __tablename__ = 'content_mappings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey('user_uploads.id'), nullable=False)
    content_type = Column(String(50))  # 'part', 'chapter', 'topic', 'section'
    content_id = Column(UUID(as_uuid=True))  # References various content tables
    relevance_score = Column(Float)  # AI-determined relevance (0-1)
    mapping_type = Column(String(50))  # 'auto', 'manual', 'verified'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIGeneratedContent(Base):
    """Model class for ai_generated_content table - Stores AI-generated study materials."""
    __tablename__ = 'ai_generated_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    upload_id = Column(UUID(as_uuid=True), ForeignKey('user_uploads.id'))
    content_type = Column(String(50))  # 'summary', 'flashcards', 'quiz', 'study_guide'
    title = Column(String(255))
    content = Column(Text)
    metadata = Column(JSONB)  # Store generation parameters, model used, etc.
    source_content_ids = Column(ARRAY(UUID(as_uuid=True)))  # References to source materials
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudyMaterialOrganization(Base):
    """Model class for study_material_organization table - Custom organization of study materials."""
    __tablename__ = 'study_material_organization'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('study_material_organization.id'))
    title = Column(String(255))
    organization_type = Column(String(50))  # 'folder', 'collection', 'topic'
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudyMaterialItems(Base):
    """Model class for study_material_items table - Links content to organization structure."""
    __tablename__ = 'study_material_items'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('study_material_organization.id'), nullable=False)
    content_type = Column(String(50))  # 'upload', 'ai_generated', 'note', 'deck'
    content_id = Column(UUID(as_uuid=True))
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentLocations(Base):
    """Model class for content_locations table - Flexible content organization structure."""
    __tablename__ = 'content_locations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('content_locations.id'))
    level_type = Column(String(50), nullable=False)  # 'part', 'chapter', 'topic', 'section', 'custom'
    order_index = Column(Integer)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FlexibleContentMappings(Base):
    """Model class for flexible_content_mappings table - Maps content to locations."""
    __tablename__ = 'flexible_content_mappings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content_type = Column(String(50), nullable=False)  # 'upload', 'note', 'deck', 'ai_generated'
    location_id = Column(UUID(as_uuid=True), ForeignKey('content_locations.id'))
    confidence_score = Column(Float)
    mapping_type = Column(String(50), nullable=False)  # 'auto', 'manual', 'suggested'
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentRelationships(Base):
    """Model class for content_relationships table - Links related content."""
    __tablename__ = 'content_relationships'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_content_id = Column(UUID(as_uuid=True), nullable=False)
    target_content_id = Column(UUID(as_uuid=True), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # 'related', 'prerequisite', 'continuation'
    strength = Column(Float)  # AI-determined relationship strength
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentTags(Base):
    """Model class for content_tags table - Flexible content tagging."""
    __tablename__ = 'content_tags'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content_type = Column(String(50), nullable=False)
    tag = Column(String(100), nullable=False)
    tag_type = Column(String(50))  # 'topic', 'skill', 'concept'
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def init_db(engine):
    Base.metadata.create_all(engine)
