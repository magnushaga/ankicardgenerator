from datetime import datetime, date
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, Float, Date, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

# Admin Tables
class AdminRoles(Base):
    """Model class for admin_roles table."""
    __tablename__ = 'admin_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminPermissions(Base):
    """Model class for admin_permissions table."""
    __tablename__ = 'admin_permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminRolePermissions(Base):
    """Model class for admin_role_permissions table."""
    __tablename__ = 'admin_role_permissions'

    role_id = Column(UUID(as_uuid=True), ForeignKey('admin_roles.id'), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('admin_permissions.id'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAdminRoles(Base):
    """Model class for user_admin_roles table."""
    __tablename__ = 'user_admin_roles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('admin_roles.id'), primary_key=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminAuditLogs(Base):
    """Model class for admin_audit_logs table."""
    __tablename__ = 'admin_audit_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSONB)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

class EducationalInstitutions(Base):
    """Model class for educational_institutions table."""
    __tablename__ = 'educational_institutions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # university, college, high_school
    country = Column(String(100))
    city = Column(String(100))
    website = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InstitutionDepartments(Base):
    """Model class for institution_departments table."""
    __tablename__ = 'institution_departments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey('educational_institutions.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    children = relationship("SubjectCategories", backref=backref('parent', remote_side=[id]))
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
    meta_data = Column(JSONB)

    # Add relationships
    category = relationship("SubjectCategories", back_populates="subcategories")
    content_relationships = relationship("ContentSubjectRelationships", back_populates="subcategory")

    def __init__(self, id=None, category_id=None, name=None, description=None, created_at=None, updated_at=None, meta_data=None):
        """Initialize a new SubjectSubcategory."""
        self.id = str(id) if id else str(uuid.uuid4())
        self.category_id = str(category_id) if category_id else None
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
        self.meta_data = meta_data or {}

    def to_dict(self):
        """Convert instance to dictionary."""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'meta_data': self.meta_data
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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)
    node_comments = relationship('NodeComments', back_populates='user', cascade='all, delete-orphan')
    uploads = relationship('CourseUploads', back_populates='user', cascade='all, delete-orphan')
    notes = relationship('Notes', back_populates='user', cascade='all, delete-orphan')
    live_notes = relationship('LiveNotes', back_populates='user', cascade='all, delete-orphan')
    live_decks = relationship('LiveDecks', back_populates='user', cascade='all, delete-orphan')
    card_reviews = relationship('CardReviews', back_populates='user', cascade='all, delete-orphan')

class Courses(Base):
    """Model class for courses table - Represents educational courses."""
    __tablename__ = 'courses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    institution_id = Column(UUID(as_uuid=True), ForeignKey('educational_institutions.id'))
    department_id = Column(UUID(as_uuid=True), ForeignKey('institution_departments.id'))
    subject_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    subcategory_ids = Column(ARRAY(UUID(as_uuid=True)))
    course_code = Column(String(50))
    semester = Column(String(50))
    year = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    institution = relationship('EducationalInstitutions', back_populates='courses')
    department = relationship('InstitutionDepartments', back_populates='courses')
    subject = relationship('SubjectCategories', back_populates='courses')
    content = relationship('CourseContent', back_populates='course', cascade='all, delete-orphan')
    enrolled_students = relationship('CourseEnrollments', back_populates='course', cascade='all, delete-orphan')

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
    meta_data = Column(JSONB)

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
    total_nodes = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    nodes = relationship('ContentNode', back_populates='course', cascade='all, delete-orphan')
    live_content = relationship('LiveCourseContent', back_populates='course', cascade='all, delete-orphan')

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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)

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
    active_nodes = Column(Integer, default=0)
    version = Column(Integer, default=1)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey('live_course_content.id'))
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    course = relationship('CourseContent', back_populates='live_content')
    parent_version = relationship('LiveCourseContent', remote_side=[id], backref='child_versions')
    live_nodes = relationship('LiveContentNode', back_populates='live_course', cascade='all, delete-orphan')
    notes = relationship('LiveNotes', back_populates='course_content', lazy=True)
    decks = relationship('LiveDecks', back_populates='course_content', lazy=True)

class LiveCourseModules(Base):
    """Model class for live_course_modules table - Active modules for course study."""
    __tablename__ = 'live_course_modules'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_content_id = Column(UUID(as_uuid=True), ForeignKey('live_course_content.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('course_modules.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

class LiveCourseSections(Base):
    """Model class for live_course_sections table - Active sections for course study."""
    __tablename__ = 'live_course_sections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_module_id = Column(UUID(as_uuid=True), ForeignKey('live_course_modules.id'), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey('course_sections.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

class CourseFiles(Base):
    """Model class for course_files table - Files associated with courses."""
    __tablename__ = 'course_files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(1024), nullable=False)
    file_type = Column(String(50))  # pdf, doc, ppt, etc.
    file_size = Column(Integer)  # Size in bytes
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    course = relationship('Courses', backref='files')
    content_nodes = relationship('ContentNode', back_populates='file', cascade='all, delete-orphan')
    live_content_nodes = relationship('LiveContentNode', back_populates='file', cascade='all, delete-orphan')

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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)

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
    bucket_name = Column(String(255), nullable=False, default='textbook-materials')  # Supabase storage bucket
    storage_path = Column(String(1024), nullable=False)  # Path within the bucket
    file_path = Column(String(1024), nullable=False)  # Full URL or path to access the file
    is_public = Column(Boolean, default=False)
    difficulty_level = Column(Integer)
    language = Column(String(50))
    main_subject_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    subcategory_ids = Column(ARRAY(UUID(as_uuid=True)))
    total_parts = Column(Integer, default=0)
    total_chapters = Column(Integer, default=0)
    total_topics = Column(Integer, default=0)
    storage_provider = Column(String(50), default='supabase')  # For future extensibility
    storage_metadata = Column(JSONB)  # For Supabase-specific metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)
    # New fields for conversion tracking
    converted_from = Column(UUID(as_uuid=True))  # ID of the live content this was converted from
    conversion_date = Column(DateTime)  # When the conversion happened
    conversion_meta_data = Column(JSONB)  # Additional conversion details

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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)

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
    meta_data = Column(JSONB)
    live_notes = relationship('LiveNotes', back_populates='topic', lazy=True)

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
    version = Column(Integer, default=1)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_content.id'))
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    parent_version = relationship('LiveTextbookContent', remote_side=[id], backref='child_versions')
    parts = relationship('LiveTextbookParts', back_populates='live_content', lazy=True)
    chapters = relationship('LiveTextbookChapters', back_populates='live_content', lazy=True)
    topics = relationship('LiveTextbookTopics', back_populates='live_content', lazy=True)
    notes = relationship('LiveNotes', back_populates='textbook_content', lazy=True)
    decks = relationship('LiveDecks', back_populates='textbook_content', lazy=True)

class LiveTextbookParts(Base):
    """Model class for live_textbook_parts table - Active parts for textbook study."""
    __tablename__ = 'live_textbook_parts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_content_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_content.id'), nullable=False)
    part_id = Column(UUID(as_uuid=True), ForeignKey('textbook_parts.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

class LiveTextbookChapters(Base):
    """Model class for live_textbook_chapters table - Active chapters for textbook study."""
    __tablename__ = 'live_textbook_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_part_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_parts.id'), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('textbook_chapters.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

class LiveTextbookTopics(Base):
    """Model class for live_textbook_topics table - Active topics for textbook study."""
    __tablename__ = 'live_textbook_topics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_chapter_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_chapters.id'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('textbook_topics.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

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

class Decks(Base):
    """Model class for decks table - Collection of flashcards."""
    __tablename__ = 'decks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    user = relationship('Users', back_populates='decks')
    node = relationship('ContentNode', back_populates='decks')
    cards = relationship('Cards', back_populates='deck', cascade='all, delete-orphan')
    live_versions = relationship('LiveDecks', back_populates='deck', cascade='all, delete-orphan')

class Cards(Base):
    """Model for individual flashcards."""
    __tablename__ = 'cards'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = Column(UUID(as_uuid=True), ForeignKey('decks.id'), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    deck = relationship('Decks', back_populates='cards')
    node = relationship('ContentNode', back_populates='cards')
    live_versions = relationship('LiveCards', back_populates='card', cascade='all, delete-orphan')

    def get_node_path(self):
        """Get the full path of nodes this card belongs to."""
        return self.node.get_node_path()

class NodeTypes(Base):
    """Model class for node_types table."""
    __tablename__ = 'node_types'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    nodes = relationship('ContentNode', back_populates='node_type')

class ContentNode(Base):
    """Model class for content_nodes table - Base model for hierarchical content organization."""
    __tablename__ = 'content_nodes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbook_content.id'))
    course_id = Column(UUID(as_uuid=True), ForeignKey('course_content.id'))
    parent_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'))
    node_type_id = Column(UUID(as_uuid=True), ForeignKey('node_types.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    level = Column(Integer)  # 1=Part, 2=Chapter, 3=Topic, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)
    
    # Optional relationships for course content types
    assignment_id = Column(UUID(as_uuid=True), ForeignKey('assignments.id'))
    quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.id'))
    discussion_topic_id = Column(UUID(as_uuid=True), ForeignKey('discussion_topics.id'))
    announcement_id = Column(UUID(as_uuid=True), ForeignKey('announcements.id'))
    file_id = Column(UUID(as_uuid=True), ForeignKey('course_files.id'))
    content_type = Column(String(50))  # assignment, quiz, discussion, announcement, file, etc.

    # Relationships
    textbook = relationship('TextbookContent', back_populates='nodes')
    course = relationship('CourseContent', back_populates='nodes')
    parent = relationship('ContentNode', remote_side=[id], backref='children')
    node_type = relationship('NodeType', back_populates='nodes')
    decks = relationship('Decks', back_populates='node', cascade='all, delete-orphan')
    cards = relationship('Cards', back_populates='node', cascade='all, delete-orphan')
    notes = relationship('Notes', back_populates='node', cascade='all, delete-orphan')
    live_notes = relationship('LiveNotes', back_populates='node', cascade='all, delete-orphan')
    comments = relationship('NodeComments', back_populates='node', cascade='all, delete-orphan')
    resources = relationship('CourseResources', back_populates='node', cascade='all, delete-orphan')
    uploads = relationship('CourseUploads', back_populates='node', cascade='all, delete-orphan')
    live_versions = relationship('LiveContentNode', back_populates='node', cascade='all, delete-orphan')
    live_decks = relationship('LiveDecks', back_populates='node', cascade='all, delete-orphan')
    live_cards = relationship('LiveCards', back_populates='node', cascade='all, delete-orphan')
    
    # New relationships for course content types
    assignment = relationship('Assignments', back_populates='content_nodes')
    quiz = relationship('Quizzes', back_populates='content_nodes')
    discussion_topic = relationship('DiscussionTopics', back_populates='content_nodes')
    announcement = relationship('Announcements', back_populates='content_nodes')
    file = relationship('CourseFiles', back_populates='content_nodes')

class NodeComments(Base):
    """Model class for node_comments table - Allows discussions on content nodes at any level."""
    __tablename__ = 'node_comments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('node_comments.id'))
    is_resolved = Column(Boolean, default=False)
    comment_type = Column(String(50))  # feedback, question, suggestion, discussion
    level = Column(Integer)  # Matches the node's level (1=part, 2=chapter, 3=topic, etc.)
    meta_data = Column(JSONB)  # For additional comment data like attachments, mentions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    node = relationship('ContentNode', back_populates='comments')
    user = relationship('Users', back_populates='node_comments')
    parent = relationship('NodeComments', remote_side=[id], backref='replies')

class CourseUploads(Base):
    """Model class for course_uploads table - Manages uploaded files for courses."""
    __tablename__ = 'course_uploads'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    bucket_name = Column(String(255), nullable=False, default='course-materials')  # Supabase storage bucket
    storage_path = Column(String(1024), nullable=False)  # Path within the bucket
    file_path = Column(String(1024), nullable=False)  # Full URL or path to access the file
    file_type = Column(String(50))  # pdf, doc, image, video, etc.
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(255))
    upload_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    processing_error = Column(Text)
    visibility = Column(String(50), default='enrolled')  # public, enrolled, restricted
    storage_provider = Column(String(50), default='supabase')  # For future extensibility
    storage_metadata = Column(JSONB)  # For Supabase-specific metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    node = relationship('ContentNode', back_populates='uploads')
    user = relationship('Users', back_populates='uploads')
    resources = relationship('CourseResources', back_populates='upload')

class CourseResources(Base):
    """Model class for course_resources table - Organizes supplementary course materials."""
    __tablename__ = 'course_resources'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
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
    meta_data = Column(JSONB)

    # Relationships
    node = relationship('ContentNode', back_populates='resources')
    upload = relationship('CourseUploads', back_populates='resources')

class LiveContentNode(Base):
    """Model class for live_content_nodes table - Active version of content nodes."""
    __tablename__ = 'live_content_nodes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey('live_textbook_content.id'))
    course_id = Column(UUID(as_uuid=True), ForeignKey('live_course_content.id'))
    parent_id = Column(UUID(as_uuid=True), ForeignKey('live_content_nodes.id'))
    node_type_id = Column(UUID(as_uuid=True), ForeignKey('node_types.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer)
    level = Column(Integer)  # 1=Part, 2=Chapter, 3=Topic, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)
    
    # Optional relationships for course content types
    assignment_id = Column(UUID(as_uuid=True), ForeignKey('assignments.id'))
    quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.id'))
    discussion_topic_id = Column(UUID(as_uuid=True), ForeignKey('discussion_topics.id'))
    announcement_id = Column(UUID(as_uuid=True), ForeignKey('announcements.id'))
    file_id = Column(UUID(as_uuid=True), ForeignKey('course_files.id'))
    content_type = Column(String(50))  # assignment, quiz, discussion, announcement, file, etc.

    # Relationships
    node = relationship('ContentNode', back_populates='live_versions')
    textbook = relationship('LiveTextbookContent', back_populates='nodes')
    course = relationship('LiveCourseContent', back_populates='nodes')
    parent = relationship('LiveContentNode', remote_side=[id], backref='children')
    node_type = relationship('NodeType', back_populates='live_nodes')
    live_decks = relationship('LiveDecks', back_populates='node', cascade='all, delete-orphan')
    live_cards = relationship('LiveCards', back_populates='node', cascade='all, delete-orphan')
    live_notes = relationship('LiveNotes', back_populates='node', cascade='all, delete-orphan')
    
    # New relationships for course content types
    assignment = relationship('Assignments', back_populates='live_content_nodes')
    quiz = relationship('Quizzes', back_populates='live_content_nodes')
    discussion_topic = relationship('DiscussionTopics', back_populates='live_content_nodes')
    announcement = relationship('Announcements', back_populates='live_content_nodes')
    file = relationship('CourseFiles', back_populates='live_content_nodes')

class Notes(Base):
    """Model class for notes table - Enhanced to link with content nodes."""
    __tablename__ = 'notes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
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
    meta_data = Column(JSONB)

    # Relationships
    user = relationship('Users', back_populates='notes')
    node = relationship('ContentNode', back_populates='notes')
    parent = relationship('Notes', remote_side=[id], backref='children')
    versions = relationship('NoteVersions', back_populates='note', cascade='all, delete-orphan')
    collaborators = relationship('NoteCollaborators', back_populates='note', cascade='all, delete-orphan')
    tags_rel = relationship('NoteTags', back_populates='note', cascade='all, delete-orphan')
    references_from = relationship('NoteReferences', 
                                 foreign_keys='NoteReferences.source_note_id',
                                 back_populates='source_note',
                                 cascade='all, delete-orphan')
    references_to = relationship('NoteReferences',
                               foreign_keys='NoteReferences.target_note_id',
                               back_populates='target_note')
    live_versions = relationship('LiveNotes', back_populates='note', cascade='all, delete-orphan')

class LiveNotes(Base):
    """Model class for live_notes table - Active study versions of notes."""
    __tablename__ = 'live_notes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey('notes.id'), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    format = Column(String(50), default='markdown')
    tags = Column(ARRAY(String))
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey('live_notes.id'))
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    difficulty_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    note = relationship('Notes', back_populates='live_versions')
    node = relationship('ContentNode', back_populates='live_notes')
    user = relationship('Users', back_populates='live_notes')
    parent_version = relationship('LiveNotes', remote_side=[id], backref='child_versions')
    live_deck_notes = relationship('LiveDeckNotes', back_populates='note', cascade='all, delete-orphan')

class LiveDecks(Base):
    """Model class for live_decks table - Active study versions of decks."""
    __tablename__ = 'live_decks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = Column(UUID(as_uuid=True), ForeignKey('decks.id'), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey('live_decks.id'))
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    difficulty_level = Column(Integer)
    study_mode = Column(String(50))  # normal, review, exam
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    deck = relationship('Decks', back_populates='live_versions')
    node = relationship('ContentNode', back_populates='live_decks')
    user = relationship('Users', back_populates='live_decks')
    parent_version = relationship('LiveDecks', remote_side=[id], backref='child_versions')
    cards = relationship('LiveCards', back_populates='live_deck', cascade='all, delete-orphan')
    notes = relationship('LiveDeckNotes', back_populates='live_deck', cascade='all, delete-orphan')

class LiveCards(Base):
    """Model class for live_cards table - Active study versions of cards."""
    __tablename__ = 'live_cards'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey('cards.id'), nullable=False)
    live_deck_id = Column(UUID(as_uuid=True), ForeignKey('live_decks.id'), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey('content_nodes.id'), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey('live_cards.id'))
    progress = Column(Float, default=0)
    last_studied = Column(DateTime)
    next_review = Column(DateTime)
    ease_factor = Column(Float, default=2.5)  # For spaced repetition
    study_count = Column(Integer, default=0)
    difficulty_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    card = relationship('Cards', back_populates='live_versions')
    live_deck = relationship('LiveDecks', back_populates='cards')
    node = relationship('ContentNode', back_populates='live_cards')
    parent_version = relationship('LiveCards', remote_side=[id], backref='child_versions')
    reviews = relationship('CardReviews', back_populates='live_card', cascade='all, delete-orphan')

class LiveDeckNotes(Base):
    """Model class for live_deck_notes table - Links notes to live decks."""
    __tablename__ = 'live_deck_notes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_deck_id = Column(UUID(as_uuid=True), ForeignKey('live_decks.id'), nullable=False)
    note_id = Column(UUID(as_uuid=True), ForeignKey('live_notes.id'), nullable=False)
    order_index = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    live_deck = relationship('LiveDecks', back_populates='notes')
    note = relationship('LiveNotes', back_populates='live_deck_notes')

class CardReviews(Base):
    """Model class for card_reviews table - Tracks review history for live cards."""
    __tablename__ = 'card_reviews'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    live_card_id = Column(UUID(as_uuid=True), ForeignKey('live_cards.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    quality = Column(Integer)  # 0-5 rating of recall quality
    time_taken = Column(Integer)  # Time taken to answer in seconds
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    prev_easiness = Column(Float)
    prev_interval = Column(Integer)
    prev_repetitions = Column(Integer)
    new_easiness = Column(Float)
    new_interval = Column(Integer)
    new_repetitions = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    live_card = relationship('LiveCards', back_populates='reviews')
    user = relationship('Users', back_populates='card_reviews')

# Subscription Tables
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

# Communication Tools
class Announcements(Base):
    """Model class for announcements table - System-wide and course-specific announcements."""
    __tablename__ = 'announcements'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))  # Null for system-wide announcements
    priority = Column(String(20), default='normal')  # low, normal, high, urgent
    is_pinned = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    publish_at = Column(DateTime, default=datetime.utcnow)
    expire_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    author = relationship('Users', backref='announcements')
    course = relationship('Courses', backref='announcements')
    read_status = relationship('AnnouncementReadStatus', back_populates='announcement', cascade='all, delete-orphan')
    content_nodes = relationship('ContentNode', back_populates='announcement', cascade='all, delete-orphan')
    live_content_nodes = relationship('LiveContentNode', back_populates='announcement', cascade='all, delete-orphan')

class AnnouncementReadStatus(Base):
    """Model class for announcement_read_status table - Tracks which users have read announcements."""
    __tablename__ = 'announcement_read_status'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey('announcements.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    announcement = relationship('Announcements', back_populates='read_status')
    user = relationship('Users', backref='announcement_reads')

class DiscussionForums(Base):
    """Model class for discussion_forums table - Course discussion boards."""
    __tablename__ = 'discussion_forums'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_announcement = Column(Boolean, default=False)  # If true, only instructors can post
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    course = relationship('Courses', backref='discussion_forums')
    topics = relationship('DiscussionTopics', back_populates='forum', cascade='all, delete-orphan')

class DiscussionTopics(Base):
    """Model class for discussion_topics table - Topics within forums."""
    __tablename__ = 'discussion_topics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forum_id = Column(UUID(as_uuid=True), ForeignKey('discussion_forums.id'), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    forum = relationship('DiscussionForums', back_populates='topics')
    author = relationship('Users', backref='discussion_topics')
    replies = relationship('DiscussionReplies', back_populates='topic', cascade='all, delete-orphan')
    content_nodes = relationship('ContentNode', back_populates='discussion_topic', cascade='all, delete-orphan')
    live_content_nodes = relationship('LiveContentNode', back_populates='discussion_topic', cascade='all, delete-orphan')

class DiscussionReplies(Base):
    """Model class for discussion_replies table - Replies to discussion topics."""
    __tablename__ = 'discussion_replies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('discussion_topics.id'), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('discussion_replies.id'))  # For nested replies
    content = Column(Text, nullable=False)
    is_solution = Column(Boolean, default=False)  # Marked as solution by instructor
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    topic = relationship('DiscussionTopics', back_populates='replies')
    author = relationship('Users', backref='discussion_replies')
    parent = relationship('DiscussionReplies', remote_side=[id], backref='children')

class DirectMessages(Base):
    """Model class for direct_messages table - Private messaging between users."""
    __tablename__ = 'direct_messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    sender = relationship('Users', foreign_keys=[sender_id], backref='sent_messages')
    recipient = relationship('Users', foreign_keys=[recipient_id], backref='received_messages')

# Assessment and Grading System
class Assignments(Base):
    """Model class for assignments table - Course assignments."""
    __tablename__ = 'assignments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    points_possible = Column(Float)
    assignment_type = Column(String(50))  # file_upload, text_entry, external_tool, etc.
    submission_type = Column(String(50))  # individual, group
    group_category_id = Column(UUID(as_uuid=True), ForeignKey('group_categories.id'))
    is_published = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    course = relationship('Courses', backref='assignments')
    group_category = relationship('GroupCategories', backref='assignments')
    submissions = relationship('AssignmentSubmissions', back_populates='assignment', cascade='all, delete-orphan')
    content_nodes = relationship('ContentNode', back_populates='assignment', cascade='all, delete-orphan')
    live_content_nodes = relationship('LiveContentNode', back_populates='assignment', cascade='all, delete-orphan')

class AssignmentSubmissions(Base):
    """Model class for assignment_submissions table - Student submissions for assignments."""
    __tablename__ = 'assignment_submissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey('assignments.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'))  # For group submissions
    submission_type = Column(String(50))  # file_upload, text_entry, external_tool, etc.
    content = Column(Text)  # For text submissions
    file_path = Column(String(1024))  # For file submissions
    external_url = Column(String(1024))  # For external tool submissions
    submitted_at = Column(DateTime, default=datetime.utcnow)
    is_late = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    assignment = relationship('Assignments', back_populates='submissions')
    user = relationship('Users', backref='assignment_submissions')
    group = relationship('Groups', backref='assignment_submissions')
    grades = relationship('AssignmentGrades', back_populates='submission', cascade='all, delete-orphan')

class AssignmentGrades(Base):
    """Model class for assignment_grades table - Grades for assignment submissions."""
    __tablename__ = 'assignment_grades'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('assignment_submissions.id'), nullable=False)
    grader_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    score = Column(Float)
    feedback = Column(Text)
    is_final = Column(Boolean, default=False)
    graded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    submission = relationship('AssignmentSubmissions', back_populates='grades')
    grader = relationship('Users', backref='assignment_grades_given')

class Quizzes(Base):
    """Model class for quizzes table - Course quizzes and tests."""
    __tablename__ = 'quizzes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    quiz_type = Column(String(50))  # practice_quiz, assignment, graded_survey, survey
    time_limit = Column(Integer)  # Time limit in minutes, null for no limit
    due_date = Column(DateTime)
    points_possible = Column(Float)
    is_published = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    course = relationship('Courses', backref='quizzes')
    questions = relationship('QuizQuestions', back_populates='quiz', cascade='all, delete-orphan')
    attempts = relationship('QuizAttempts', back_populates='quiz', cascade='all, delete-orphan')
    content_nodes = relationship('ContentNode', back_populates='quiz', cascade='all, delete-orphan')
    live_content_nodes = relationship('LiveContentNode', back_populates='quiz', cascade='all, delete-orphan')

class QuizQuestions(Base):
    """Model class for quiz_questions table - Questions for quizzes."""
    __tablename__ = 'quiz_questions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.id'), nullable=False)
    question_type = Column(String(50))  # multiple_choice, true_false, short_answer, essay, etc.
    question_text = Column(Text, nullable=False)
    points_possible = Column(Float)
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    quiz = relationship('Quizzes', back_populates='questions')
    answers = relationship('QuizAnswers', back_populates='question', cascade='all, delete-orphan')
    responses = relationship('QuizResponses', back_populates='question', cascade='all, delete-orphan')

class QuizAnswers(Base):
    """Model class for quiz_answers table - Possible answers for quiz questions."""
    __tablename__ = 'quiz_answers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('quiz_questions.id'), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    question = relationship('QuizQuestions', back_populates='answers')

class QuizAttempts(Base):
    """Model class for quiz_attempts table - Student attempts at quizzes."""
    __tablename__ = 'quiz_attempts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    score = Column(Float)
    is_late = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    quiz = relationship('Quizzes', back_populates='attempts')
    user = relationship('Users', backref='quiz_attempts')
    responses = relationship('QuizResponses', back_populates='attempt', cascade='all, delete-orphan')

class QuizResponses(Base):
    """Model class for quiz_responses table - Student responses to quiz questions."""
    __tablename__ = 'quiz_responses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey('quiz_questions.id'), nullable=False)
    answer_id = Column(UUID(as_uuid=True), ForeignKey('quiz_answers.id'))  # For multiple choice
    response_text = Column(Text)  # For text responses
    is_correct = Column(Boolean)
    points_earned = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    attempt = relationship('QuizAttempts', back_populates='responses')
    question = relationship('QuizQuestions', back_populates='responses')
    answer = relationship('QuizAnswers', backref='responses')

# Analytics and Reporting
class AnalyticsEvents(Base):
    """Model class for analytics_events table - Tracks user interactions for analytics."""
    __tablename__ = 'analytics_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    event_type = Column(String(100), nullable=False)  # page_view, content_interaction, etc.
    event_data = Column(JSONB, nullable=False)  # Detailed event data
    session_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('Users', backref='analytics_events')

class ContentAnalytics(Base):
    """Model class for content_analytics table - Aggregated analytics for content."""
    __tablename__ = 'content_analytics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    content_type = Column(String(50), nullable=False)  # course, module, deck, etc.
    view_count = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    average_time_spent = Column(Integer, default=0)  # In seconds
    completion_rate = Column(Float, default=0)  # 0-1 scale
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

class UserAnalytics(Base):
    """Model class for user_analytics table - Aggregated analytics for users."""
    __tablename__ = 'user_analytics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    total_time_spent = Column(Integer, default=0)  # In seconds
    content_interaction_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0)  # 0-1 scale
    last_active = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    user = relationship('Users', backref='analytics')

# Integration Capabilities
class ExternalIntegrations(Base):
    """Model class for external_integrations table - Manages third-party integrations."""
    __tablename__ = 'external_integrations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)  # google, microsoft, zoom, etc.
    integration_type = Column(String(50))  # calendar, drive, meeting, etc.
    is_active = Column(Boolean, default=True)
    config = Column(JSONB)  # Integration configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

class UserIntegrations(Base):
    """Model class for user_integrations table - User-specific integration settings."""
    __tablename__ = 'user_integrations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    integration_id = Column(UUID(as_uuid=True), ForeignKey('external_integrations.id'), nullable=False)
    is_enabled = Column(Boolean, default=True)
    access_token = Column(String(1024))
    refresh_token = Column(String(1024))
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    user = relationship('Users', backref='integrations')
    integration = relationship('ExternalIntegrations', backref='user_integrations')

# Mobile and Accessibility
class UserDevices(Base):
    """Model class for user_devices table - Tracks user devices for mobile support."""
    __tablename__ = 'user_devices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    device_id = Column(String(255), nullable=False)
    device_type = Column(String(50))  # mobile, tablet, desktop
    device_name = Column(String(255))
    last_active = Column(DateTime)
    push_token = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    user = relationship('Users', backref='devices')

class AccessibilityPreferences(Base):
    """Model class for accessibility_preferences table - User accessibility settings."""
    __tablename__ = 'accessibility_preferences'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    high_contrast = Column(Boolean, default=False)
    font_size = Column(String(20), default='medium')  # small, medium, large
    screen_reader = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    user = relationship('Users', backref='accessibility_preferences')

# Administrative Tools
class SystemSettings(Base):
    """Model class for system_settings table - Global system configuration."""
    __tablename__ = 'system_settings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    updater = relationship('Users', backref='updated_settings')

class SystemLogs(Base):
    """Model class for system_logs table - System-wide logging."""
    __tablename__ = 'system_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)  # info, warning, error, critical
    category = Column(String(50))  # auth, content, system, etc.
    message = Column(Text, nullable=False)
    details = Column(JSONB)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('Users', backref='system_logs')

# Group Management
class GroupCategories(Base):
    """Model class for group_categories table - Categories for grouping students."""
    __tablename__ = 'group_categories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    group_limit = Column(Integer)  # Maximum number of students per group
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    course = relationship('Courses', backref='group_categories')
    groups = relationship('Groups', back_populates='category', cascade='all, delete-orphan')

class Groups(Base):
    """Model class for groups table - Student groups for collaborative work."""
    __tablename__ = 'groups'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('group_categories.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    category = relationship('GroupCategories', back_populates='groups')
    members = relationship('GroupMembers', back_populates='group', cascade='all, delete-orphan')

class GroupMembers(Base):
    """Model class for group_members table - Members of student groups."""
    __tablename__ = 'group_members'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role = Column(String(50), default='member')  # leader, member
    joined_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSONB)

    # Relationships
    group = relationship('Groups', back_populates='members')
    user = relationship('Users', backref='group_memberships')

def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine) 