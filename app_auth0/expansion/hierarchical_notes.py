from datetime import datetime
import uuid

class StudyNote:
    def __init__(self, id, user_id, title, content, source_material_id=None, tags=None, is_public=False):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.content = content
        self.source_material_id = source_material_id
        self.tags = tags or []
        self.is_public = is_public
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'source_material_id': self.source_material_id,
            'tags': self.tags,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class NotePart:
    def __init__(self, id, note_id, title, description, order_index):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.title = title
        self.description = description
        self.order_index = order_index
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class NoteChapter:
    def __init__(self, id, part_id, title, description, order_index):
        self.id = id or str(uuid.uuid4())
        self.part_id = part_id
        self.title = title
        self.description = description
        self.order_index = order_index
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'part_id': self.part_id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class NoteTopic:
    def __init__(self, id, chapter_id, title, content, order_index):
        self.id = id or str(uuid.uuid4())
        self.chapter_id = chapter_id
        self.title = title
        self.content = content
        self.order_index = order_index
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'title': self.title,
            'content': self.content,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class NoteShare:
    def __init__(self, id, note_id, shared_with, permission='view', expires_at=None):
        self.id = id or str(uuid.uuid4())
        self.note_id = note_id
        self.shared_with = shared_with
        self.permission = permission  # view, edit
        self.shared_at = datetime.utcnow()
        self.expires_at = expires_at
        self.is_active = True

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'shared_with': self.shared_with,
            'permission': self.permission,
            'shared_at': self.shared_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

class NotePartShare:
    def __init__(self, id, part_id, shared_with, permission='view', expires_at=None):
        self.id = id or str(uuid.uuid4())
        self.part_id = part_id
        self.shared_with = shared_with
        self.permission = permission
        self.shared_at = datetime.utcnow()
        self.expires_at = expires_at
        self.is_active = True

    def to_dict(self):
        return {
            'id': self.id,
            'part_id': self.part_id,
            'shared_with': self.shared_with,
            'permission': self.permission,
            'shared_at': self.shared_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

class NoteChapterShare:
    def __init__(self, id, chapter_id, shared_with, permission='view', expires_at=None):
        self.id = id or str(uuid.uuid4())
        self.chapter_id = chapter_id
        self.shared_with = shared_with
        self.permission = permission
        self.shared_at = datetime.utcnow()
        self.expires_at = expires_at
        self.is_active = True

    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'shared_with': self.shared_with,
            'permission': self.permission,
            'shared_at': self.shared_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

class NoteTopicShare:
    def __init__(self, id, topic_id, shared_with, permission='view', expires_at=None):
        self.id = id or str(uuid.uuid4())
        self.topic_id = topic_id
        self.shared_with = shared_with
        self.permission = permission
        self.shared_at = datetime.utcnow()
        self.expires_at = expires_at
        self.is_active = True

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'shared_with': self.shared_with,
            'permission': self.permission,
            'shared_at': self.shared_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        } 