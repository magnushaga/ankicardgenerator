from datetime import datetime
import uuid

class StudyNote:
    """
    Model class for study_notes table.
    Represents a note that can be linked to either a course or a textbook.
    """
    def __init__(self, id=None, user_id=None, title=None, content=None, 
                 source_type=None, source_id=None, tags=None, is_public=False, 
                 metadata=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.content = content or {}  # JSONB field for rich text content
        self.source_type = source_type  # 'course' or 'textbook'
        self.source_id = source_id
        self.tags = tags or []
        self.is_public = is_public
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'tags': self.tags,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class NoteContentVersion:
    def __init__(self, id=None, note_id=None, content=None, version_number=None, 
                 created_by=None, metadata=None):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.content = content  # TipTap.js compatible JSON
        self.version_number = version_number
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'content': self.content,
            'version_number': self.version_number,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class NoteMedia:
    def __init__(self, id=None, note_id=None, media_type=None, url=None, 
                 metadata=None, created_by=None):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.media_type = media_type
        self.url = url
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.created_by = created_by

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'media_type': self.media_type,
            'url': self.url,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Course:
    def __init__(self, id=None, title=None, description=None, created_by=None, 
                 is_public=False, metadata=None):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.created_by = created_by
        self.is_public = is_public
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CourseSection:
    def __init__(self, id=None, course_id=None, parent_section_id=None, 
                 title=None, description=None, order_index=None):
        self.id = id or str(uuid.uuid4())
        self.course_id = course_id
        self.parent_section_id = parent_section_id
        self.title = title
        self.description = description
        self.order_index = order_index
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'parent_section_id': self.parent_section_id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CourseSectionNote:
    def __init__(self, id=None, section_id=None, note_id=None, order_index=None):
        self.id = id or str(uuid.uuid4())
        self.section_id = section_id
        self.note_id = note_id
        self.order_index = order_index
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'note_id': self.note_id,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class NotePermission:
    def __init__(self, id=None, note_id=None, user_id=None, permission_level=None, 
                 granted_by=None, expires_at=None, is_active=True):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.user_id = user_id
        self.permission_level = permission_level
        self.granted_by = granted_by
        self.granted_at = datetime.utcnow()
        self.expires_at = expires_at
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'user_id': self.user_id,
            'permission_level': self.permission_level,
            'granted_by': self.granted_by,
            'granted_at': self.granted_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CoursePermission:
    def __init__(self, id=None, course_id=None, user_id=None, permission_level=None, 
                 granted_by=None, expires_at=None, is_active=True):
        self.id = id or str(uuid.uuid4())
        self.course_id = course_id
        self.user_id = user_id
        self.permission_level = permission_level
        self.granted_by = granted_by
        self.granted_at = datetime.utcnow()
        self.expires_at = expires_at
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'permission_level': self.permission_level,
            'granted_by': self.granted_by,
            'granted_at': self.granted_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class NoteCollaborationSession:
    def __init__(self, id=None, note_id=None, user_id=None, session_end=None):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.user_id = user_id
        self.session_start = datetime.utcnow()
        self.session_end = session_end
        self.last_activity = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'user_id': self.user_id,
            'session_start': self.session_start.isoformat(),
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'last_activity': self.last_activity.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class NoteActivityLog:
    def __init__(self, id=None, note_id=None, user_id=None, activity_type=None, 
                 details=None):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.user_id = user_id
        self.activity_type = activity_type
        self.details = details or {}
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class NoteComment:
    def __init__(self, id=None, note_id=None, user_id=None, parent_comment_id=None, 
                 content=None, is_resolved=False):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.user_id = user_id
        self.parent_comment_id = parent_comment_id
        self.content = content
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_resolved = is_resolved

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'user_id': self.user_id,
            'parent_comment_id': self.parent_comment_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_resolved': self.is_resolved
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data) 