from datetime import datetime, date
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, Float, Date, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class SubjectCategories(Base):
    """Model class for subject_categories table."""
    __tablename__ = 'subject_categories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationships
    children = relationship("SubjectCategories", backref=relationship.backref('parent', remote_side=[id]))
    content_relationships = relationship("ContentSubjectRelationships", back_populates="subject")

    def __init__(self, id=None, name=None, description=None, parent_id=None, level=None, created_at=None, updated_at=None):
        """Initialize a new SubjectCategory."""
        self.id = str(id) if id else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.parent_id = str(parent_id) if parent_id else None
        self.level = level
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        """Convert instance to dictionary."""
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
        """Create instance from dictionary."""
        if 'id' in data and isinstance(data['id'], str):
            data['id'] = uuid.UUID(data['id'])
        if 'parent_id' in data and isinstance(data['parent_id'], str):
            data['parent_id'] = uuid.UUID(data['parent_id'])
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class SubjectSubcategories(Base):
    """Model class for subject_subcategories table."""
    __tablename__ = 'subject_subcategories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    # Add relationships
    category = relationship("SubjectCategories", back_populates="subcategories")
    content_relationships = relationship("ContentSubjectRelationships", back_populates="subcategory")

    def __init__(self, id=None, category_id=None, name=None, description=None, created_at=None, updated_at=None, metadata=None):
        """Initialize a new SubjectSubcategory."""
        self.id = str(id) if id else str(uuid.uuid4())
        self.category_id = str(category_id) if category_id else None
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = metadata or {}

    def to_dict(self):
        """Convert instance to dictionary."""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary."""
        return cls(**data)

class ContentSubjectRelationships(Base):
    """Model class for content_subject_relationships table."""
    __tablename__ = 'content_subject_relationships'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_type_id = Column(UUID(as_uuid=True), nullable=False)  # References content_types table
    content_id = Column(UUID(as_uuid=True), nullable=False)
    subject_id = Column(UUID(as_uuid=True), nullable=False)
    subject_type = Column(String(50), nullable=False)  # category, subcategory
    relationship_type = Column(String(50), nullable=False)  # primary, secondary, prerequisite
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

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
    study_preferences = Column(JSONB)  # Study time, notification preferences, etc.
    institution_id = Column(UUID(as_uuid=True), ForeignKey('educational_institutions.id'))
    department_id = Column(UUID(as_uuid=True), ForeignKey('institution_departments.id'))
    role = Column(String(50))  # student, instructor, admin
    stripe_customer_id = Column(String(255))
    picture = Column(String(1024))
    metadata = Column(JSONB)

class Courses(Base):
    """Model class for courses table - Top level container for educational content."""
    __tablename__ = 'courses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    code = Column(String(50))  # Course code (e.g., CS101)
    description = Column(Text)
    subject_area = Column(String(255))
    level = Column(String(50))  # undergraduate, graduate, professional
    credits = Column(Integer)
    institution_id = Column(UUID(as_uuid=True), ForeignKey('educational_institutions.id'))
    department_id = Column(UUID(as_uuid=True), ForeignKey('institution_departments.id'))
    instructor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    is_public = Column(Boolean, default=False)
    status = Column(String(50), default='active')  # active, archived, draft
    start_date = Column(Date)
    end_date = Column(Date)
    language = Column(String(50))
    difficulty_level = Column(Integer)
    avg_rating = Column(Float)
    num_ratings = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    main_subject_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    subcategory_ids = Column(ARRAY(UUID(as_uuid=True)))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)
    prerequisites = Column(ARRAY(UUID(as_uuid=True)))  # Array of course IDs

class CourseEnrollments(Base):
    """Model class for course_enrollments table - Manages student enrollments and access."""
    __tablename__ = 'course_enrollments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role = Column(String(50), nullable=False)  # student, teaching_assistant, auditor
    status = Column(String(50), default='active')  # active, completed, dropped
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    grade = Column(String(10))
    access_level = Column(Integer, default=1)  # Custom access levels (1-5)
    last_accessed = Column(DateTime)
    progress = Column(Float, default=0)  # Overall course progress
    metadata = Column(JSONB)

class CourseContent(Base):
    """Model class for course_content table - Manages course-based study materials."""
    __tablename__ = 'course_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    source_textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbook_content.id'))  # If migrated from textbook
    content_type = Column(String(50))  # original, migrated, hybrid
    difficulty_level = Column(Integer)
    language = Column(String(50))
    main_subject_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    subcategory_ids = Column(ARRAY(UUID(as_uuid=True)))
    total_modules = Column(Integer, default=0)
    total_sections = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseModules(Base):
    """Model class for course_modules table - Module-level organization for courses."""
    __tablename__ = 'course_modules'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('course_content.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    source_part_id = Column(UUID(as_uuid=True), ForeignKey('textbook_parts.id'))  # If migrated from textbook
    is_active = Column(Boolean, default=True)
    total_sections = Column(Integer, default=0)
    prerequisites = Column(ARRAY(UUID(as_uuid=True)))  # Required modules
    learning_objectives = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseSections(Base):
    """Model class for course_sections table - Section-level organization for courses."""
    __tablename__ = 'course_sections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey('course_modules.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    source_chapter_id = Column(UUID(as_uuid=True), ForeignKey('textbook_chapters.id'))  # If migrated from textbook
    content_type = Column(String(50))  # lecture, practice, assessment
    is_active = Column(Boolean, default=True)
    total_items = Column(Integer, default=0)
    prerequisites = Column(ARRAY(UUID(as_uuid=True)))  # Required sections
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class ContentMigrations(Base):
    """Model class for content_migrations table - Tracks content migration processes."""
    __tablename__ = 'content_migrations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    source_id = Column(UUID(as_uuid=True), nullable=False)  # textbook_id
    source_type = Column(String(50), nullable=False)  # textbook, external
    target_id = Column(UUID(as_uuid=True), nullable=False)  # course_id
    target_type = Column(String(50), nullable=False)  # course
    status = Column(String(50), default='pending')  # pending, in_progress, completed, failed
    progress = Column(Float, default=0)
    error_log = Column(JSONB)
    migration_settings = Column(JSONB)  # Configuration for the migration
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LiveCourseContent(Base):
    """Model class for live_course_content table - Active course study content."""
    __tablename__ = 'live_course_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('course_content.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(String(50))  # deck, notes, quiz
    is_active = Column(Boolean, default=True)
    active_modules = Column(Integer, default=0)
    active_sections = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class LiveCourseModules(Base):
    """Model class for live_course_modules table - Active modules for course study."""
    __tablename__ = 'live_course_modules'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_content_id = Column(UUID(as_uuid=True), ForeignKey('live_course_content.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('course_modules.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class LiveCourseSections(Base):
    """Model class for live_course_sections table - Active sections for course study."""
    __tablename__ = 'live_course_sections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_module_id = Column(UUID(as_uuid=True), ForeignKey('live_course_modules.id'), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseFiles(Base):
    """Model class for course_files table - Manages uploaded course materials."""
    __tablename__ = 'course_files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('content_modules.id'))
    content_id = Column(UUID(as_uuid=True), ForeignKey('course_content.id'))
    title = Column(String(255), nullable=False)
    file_type = Column(String(50))  # pdf, ppt, doc, video, etc.
    file_path = Column(String(1024))
    file_size = Column(Integer)
    mime_type = Column(String(255))
    upload_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    visibility = Column(String(50), default='enrolled')  # public, enrolled, restricted
    processing_error = Column(Text)
    ocr_text = Column(Text)  # Extracted text content
    thumbnail_path = Column(String(1024))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)  # For storing additional extracted content

class CourseParts(Base):
    """Model class for course_parts table - Top-level organization of course content."""
    __tablename__ = 'course_parts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    source_textbook_id = Column(UUID(as_uuid=True))  # For migrated content
    last_modified = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)

class CourseChapters(Base):
    """Model class for course_chapters table - Subdivides parts into chapters."""
    __tablename__ = 'course_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id = Column(UUID(as_uuid=True), ForeignKey('course_parts.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    source_chapter_id = Column(UUID(as_uuid=True))  # For migrated content
    last_modified = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)

class CourseTopics(Base):
    """Model class for course_topics table - Subdivides chapters into topics."""
    __tablename__ = 'course_topics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('course_chapters.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    source_topic_id = Column(UUID(as_uuid=True))  # For migrated content
    last_modified = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)

class ContentAccess(Base):
    """Model class for content_access table - Fine-grained access control."""
    __tablename__ = 'content_access'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False)  # Can reference various content tables
    content_type = Column(String(50), nullable=False)  # course, module, file, deck
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    access_type = Column(String(50), nullable=False)  # view, edit, manage
    granted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)

class ContentCollaborators(Base):
    """Model class for content_collaborators table - Manages shared content editing."""
    __tablename__ = 'content_collaborators'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content_type = Column(String(50), nullable=False)  # course, module, deck
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role = Column(String(50), nullable=False)  # editor, reviewer, viewer
    permissions = Column(JSONB)  # Detailed permission settings
    invited_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudyProgress(Base):
    """Model class for study_progress table - Tracks learning progress."""
    __tablename__ = 'study_progress'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content_type = Column(String(50), nullable=False)  # module, deck, card
    status = Column(String(50))  # not_started, in_progress, completed
    progress = Column(Float)  # Percentage complete
    last_accessed = Column(DateTime)
    time_spent = Column(Integer)  # Time spent in seconds
    mastery_level = Column(Float)  # 0-1 scale
    review_count = Column(Integer, default=0)
    next_review_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class ContentReviews(Base):
    """Model class for content_reviews table - User reviews for course content."""
    __tablename__ = 'content_reviews'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content_type = Column(String(50), nullable=False)  # course, deck, module
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    rating = Column(Integer)  # 1-5 scale
    review_text = Column(Text)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TextbookContent(Base):
    """Model class for textbook_content table - Manages textbook-based study materials."""
    __tablename__ = 'textbook_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    author = Column(String(255))
    description = Column(Text)
    content_type = Column(String(50))  # textbook, notes, summary
    file_path = Column(String(1024))
    is_public = Column(Boolean, default=False)
    difficulty_level = Column(Integer)
    language = Column(String(50))
    main_subject_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    subcategory_ids = Column(ARRAY(UUID(as_uuid=True)))
    total_parts = Column(Integer, default=0)
    total_chapters = Column(Integer, default=0)
    total_topics = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class TextbookParts(Base):
    """Model class for textbook_parts table - Top-level textbook organization."""
    __tablename__ = 'textbook_parts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbook_content.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    total_chapters = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class TextbookChapters(Base):
    """Model class for textbook_chapters table - Chapter-level organization."""
    __tablename__ = 'textbook_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id = Column(UUID(as_uuid=True), ForeignKey('textbook_parts.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    total_topics = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class TextbookTopics(Base):
    """Model class for textbook_topics table - Topic-level organization."""
    __tablename__ = 'textbook_topics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('textbook_chapters.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    total_cards = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class ContentMigrationMappings(Base):
    """Model class for content_migration_mappings table - Detailed migration tracking."""
    __tablename__ = 'content_migration_mappings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    migration_id = Column(UUID(as_uuid=True), ForeignKey('content_migrations.id'), nullable=False)
    source_id = Column(UUID(as_uuid=True), nullable=False)
    source_type = Column(String(50), nullable=False)  # textbook_part, chapter, topic
    target_id = Column(UUID(as_uuid=True), nullable=False)
    target_type = Column(String(50), nullable=False)  # course_part, module, section
    status = Column(String(50), default='pending')
    confidence_score = Column(Float)  # For AI-assisted mappings
    mapping_data = Column(JSONB)  # Stores specific mapping details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LiveTextbookContent(Base):
    """Model class for live_textbook_content table - Active textbook study content."""
    __tablename__ = 'live_textbook_content'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbook_content.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(String(50))  # deck, notes, quiz
    is_active = Column(Boolean, default=True)
    active_parts = Column(Integer, default=0)
    active_chapters = Column(Integer, default=0)
    active_topics = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class LiveTextbookParts(Base):
    """Model class for live_textbook_parts table - Active parts for textbook study."""
    __tablename__ = 'live_textbook_parts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_content_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_content.id'), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey('textbook_parts.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class LiveTextbookChapters(Base):
    """Model class for live_textbook_chapters table - Active chapters for textbook study."""
    __tablename__ = 'live_textbook_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_part_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_parts.id'), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('textbook_chapters.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class LiveTextbookTopics(Base):
    """Model class for live_textbook_topics table - Active topics for textbook study."""
    __tablename__ = 'live_textbook_topics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_chapter_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_chapters.id'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('textbook_topics.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class StudyPreferences(Base):
    """Model class for study_preferences table - User study settings and preferences."""
    __tablename__ = 'study_preferences'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    preferred_study_time = Column(JSONB)  # Daily study schedule
    notification_preferences = Column(JSONB)  # Study reminders and alerts
    study_goals = Column(JSONB)  # Daily/weekly goals
    preferred_content_type = Column(String(50))  # textbook or course
    spaced_repetition_settings = Column(JSONB)  # SRS algorithm settings
    ui_preferences = Column(JSONB)  # UI/UX preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonalizedTextbooks(Base):
    """Model class for personalized_textbooks table - User-specific textbook customizations."""
    __tablename__ = 'personalized_textbooks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    original_textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbook_content.id'), nullable=False)
    title = Column(String(255), nullable=False)  # Can be customized
    description = Column(Text)
    is_public = Column(Boolean, default=False)  # Allow sharing customizations
    version = Column(Integer, default=1)  # Track major revisions
    fork_type = Column(String(50))  # full, partial, reference
    structure_changes = Column(JSONB)  # Track structural modifications
    custom_metadata = Column(JSONB)  # User-specific metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonalizedParts(Base):
    """Model class for personalized_parts table - Customized textbook parts."""
    __tablename__ = 'personalized_parts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personalized_textbook_id = Column(UUID(as_uuid=True), ForeignKey('personalized_textbooks.id'), nullable=False)
    original_part_id = Column(UUID(as_uuid=True), ForeignKey('textbook_parts.id'))  # Null if newly created
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_custom = Column(Boolean, default=False)  # True if user-created
    custom_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonalizedChapters(Base):
    """Model class for personalized_chapters table - Customized textbook chapters."""
    __tablename__ = 'personalized_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personalized_part_id = Column(UUID(as_uuid=True), ForeignKey('personalized_parts.id'), nullable=False)
    original_chapter_id = Column(UUID(as_uuid=True), ForeignKey('textbook_chapters.id'))  # Null if newly created
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_custom = Column(Boolean, default=False)  # True if user-created
    custom_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonalizedTopics(Base):
    """Model class for personalized_topics table - Customized textbook topics."""
    __tablename__ = 'personalized_topics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personalized_chapter_id = Column(UUID(as_uuid=True), ForeignKey('personalized_chapters.id'), nullable=False)
    original_topic_id = Column(UUID(as_uuid=True), ForeignKey('textbook_topics.id'))  # Null if newly created
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_custom = Column(Boolean, default=False)  # True if user-created
    custom_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentCustomizations(Base):
    """Model class for content_customizations table - Tracks changes to content structure."""
    __tablename__ = 'content_customizations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personalized_textbook_id = Column(UUID(as_uuid=True), ForeignKey('personalized_textbooks.id'), nullable=False)
    customization_type = Column(String(50))  # move, merge, split, add, remove
    source_id = Column(UUID(as_uuid=True))  # Original content ID
    source_type = Column(String(50))  # part, chapter, topic
    target_id = Column(UUID(as_uuid=True))  # New content ID
    target_type = Column(String(50))  # part, chapter, topic
    change_data = Column(JSONB)  # Details of the change
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_reverted = Column(Boolean, default=False)
    revert_reason = Column(Text)

class SharedCustomizations(Base):
    """Model class for shared_customizations table - Manages sharing of content customizations."""
    __tablename__ = 'shared_customizations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personalized_textbook_id = Column(UUID(as_uuid=True), ForeignKey('personalized_textbooks.id'), nullable=False)
    shared_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    shared_with = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    access_level = Column(String(50))  # view, edit, clone
    share_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    metadata = Column(JSONB)

class CustomizationComments(Base):
    """Model class for customization_comments table - Allows discussions on content changes."""
    __tablename__ = 'customization_comments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customization_id = Column(UUID(as_uuid=True), ForeignKey('content_customizations.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('customization_comments.id'))
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Decks(Base):
    """Model class for decks table."""
    __tablename__ = 'decks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    main_subject_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    subcategory_ids = Column(ARRAY(UUID(as_uuid=True)))
    source_textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbook_content.id'))
    content_type_id = Column(UUID(as_uuid=True))  # References content_types table
    total_cards = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    metadata = Column(JSONB)

class DeckShares(Base):
    """Model class for deck_shares table."""
    __tablename__ = 'deck_shares'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = Column(UUID(as_uuid=True), ForeignKey('decks.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    shared_at = Column(DateTime, default=datetime.utcnow)
    access_level = Column(String(50), default='view')  # view, edit, clone
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB)

class StudySessions(Base):
    """Model class for study_sessions table."""
    __tablename__ = 'study_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    deck_id = Column(UUID(as_uuid=True), ForeignKey('decks.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    cards_studied = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    session_duration = Column(Integer)  # Duration in seconds
    average_response_time = Column(Float)  # Average time per card in seconds
    session_type = Column(String(50))  # review, learn, practice
    difficulty_level = Column(Integer)
    metadata = Column(JSONB)

class TextbookReviews(Base):
    """Model class for textbook_reviews table."""
    __tablename__ = 'textbook_reviews'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbook_content.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    rating = Column(Integer)  # 1-5 scale
    review_text = Column(Text)
    helpful_count = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)
    is_verified_purchase = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseUploads(Base):
    """Model class for course_uploads table - Manages and tracks uploaded course materials."""
    __tablename__ = 'course_uploads'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('course_modules.id'))
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.id'))
    upload_type = Column(String(50))  # lecture_notes, slides, textbook, assignment, etc.
    content_format = Column(String(50))  # pdf, doc, video, audio, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(1024))
    file_size = Column(Integer)
    mime_type = Column(String(255))
    original_filename = Column(String(255))
    processing_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    processing_error = Column(Text)
    extracted_text = Column(Text)  # OCR or extracted content
    content_structure = Column(JSONB)  # Detected structure (headings, sections, etc.)
    ai_analysis = Column(JSONB)  # AI-generated insights, summaries, etc.
    visibility = Column(String(50), default='enrolled')  # public, enrolled, restricted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseContentMappings(Base):
    """Model class for course_content_mappings table - Maps uploaded content to course structure."""
    __tablename__ = 'course_content_mappings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey('course_uploads.id'), nullable=False)
    content_type = Column(String(50))  # module, section, topic, resource
    content_id = Column(UUID(as_uuid=True))  # References various content tables
    mapping_type = Column(String(50))  # auto, manual, verified
    confidence_score = Column(Float)  # AI-determined relevance (0-1)
    page_numbers = Column(ARRAY(Integer))  # For PDF/document mappings
    time_codes = Column(JSONB)  # For video/audio content
    extracted_content = Column(Text)  # Relevant extracted content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseResources(Base):
    """Model class for course_resources table - Organizes supplementary course materials."""
    __tablename__ = 'course_resources'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('course_modules.id'))
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.id'))
    upload_id = Column(UUID(as_uuid=True), ForeignKey('course_uploads.id'))
    resource_type = Column(String(50))  # reading, reference, example, template
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)
    order_index = Column(Integer)
    is_required = Column(Boolean, default=False)
    visibility = Column(String(50), default='enrolled')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseAssessments(Base):
    """Model class for course_assessments table - Manages course-related assessments."""
    __tablename__ = 'course_assessments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('course_modules.id'))
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.id'))
    assessment_type = Column(String(50))  # quiz, exam, assignment, project
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    content = Column(JSONB)  # Questions, rubrics, etc.
    total_points = Column(Float)
    passing_score = Column(Float)
    due_date = Column(DateTime)
    time_limit = Column(Integer)  # In minutes
    attempts_allowed = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class CourseProgress(Base):
    """Model class for course_progress table - Tracks detailed student progress."""
    __tablename__ = 'course_progress'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('course_modules.id'))
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.id'))
    content_type = Column(String(50))  # module, section, resource, assessment
    content_id = Column(UUID(as_uuid=True))
    status = Column(String(50))  # not_started, in_progress, completed
    progress = Column(Float, default=0)
    score = Column(Float)  # For assessments
    time_spent = Column(Integer)  # In seconds
    last_accessed = Column(DateTime)
    completion_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

class ContentGenerationQueue(Base):
    """Model class for content_generation_queue table - Manages AI content generation tasks."""
    __tablename__ = 'content_generation_queue'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey('course_uploads.id'), nullable=False)
    generation_type = Column(String(50))  # cards, summary, quiz, notes
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    priority = Column(Integer, default=0)
    parameters = Column(JSONB)  # Generation parameters
    progress = Column(Float, default=0)
    error_log = Column(Text)
    result_id = Column(UUID(as_uuid=True))  # Reference to generated content
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine) 