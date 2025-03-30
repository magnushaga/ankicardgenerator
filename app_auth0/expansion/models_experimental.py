from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class StudyGroup:
    def __init__(self, id, name, description, created_by, is_public=False, max_members=50):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_by = created_by
        self.is_public = is_public
        self.max_members = max_members
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'is_public': self.is_public,
            'max_members': self.max_members,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class StudyGroupMember:
    def __init__(self, group_id, user_id, role='member'):
        self.group_id = group_id
        self.user_id = user_id
        self.role = role  # admin, moderator, member
        self.joined_at = datetime.utcnow()

    def to_dict(self):
        return {
            'group_id': self.group_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat()
        }

class GroupStudySession:
    def __init__(self, id, group_id, title, description, scheduled_start, scheduled_end):
        self.id = id or str(uuid.uuid4())
        self.group_id = group_id
        self.title = title
        self.description = description
        self.scheduled_start = scheduled_start
        self.scheduled_end = scheduled_end
        self.status = 'scheduled'  # scheduled, active, completed, cancelled
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'title': self.title,
            'description': self.description,
            'scheduled_start': self.scheduled_start.isoformat(),
            'scheduled_end': self.scheduled_end.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class StudySessionParticipant:
    def __init__(self, session_id, user_id, status='pending'):
        self.session_id = session_id
        self.user_id = user_id
        self.status = status  # pending, accepted, declined
        self.joined_at = None
        self.left_at = None

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'status': self.status,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'left_at': self.left_at.isoformat() if self.left_at else None
        }

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

class PracticeExam:
    def __init__(self, id, user_id, title, description, source_material_id, questions, time_limit=None, passing_score=None, is_public=False):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.source_material_id = source_material_id
        self.questions = questions  # JSONB array of questions
        self.time_limit = time_limit  # in minutes
        self.passing_score = passing_score
        self.is_public = is_public
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'source_material_id': self.source_material_id,
            'questions': self.questions,
            'time_limit': self.time_limit,
            'passing_score': self.passing_score,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ExamAttempt:
    def __init__(self, id, exam_id, user_id, score=None, answers=None, started_at=None, completed_at=None, status='in_progress'):
        self.id = id or str(uuid.uuid4())
        self.exam_id = exam_id
        self.user_id = user_id
        self.score = score
        self.answers = answers  # JSONB array of answers
        self.started_at = started_at or datetime.utcnow()
        self.completed_at = completed_at
        self.status = status  # in_progress, completed, abandoned
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'exam_id': self.exam_id,
            'user_id': self.user_id,
            'score': self.score,
            'answers': self.answers,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class StudyAnalytics:
    def __init__(self, id, user_id, date, study_time=None, cards_studied=None, notes_created=None, exams_taken=None, topics_mastered=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.date = date
        self.study_time = study_time  # in minutes
        self.cards_studied = cards_studied
        self.notes_created = notes_created
        self.exams_taken = exams_taken
        self.topics_mastered = topics_mastered
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'study_time': self.study_time,
            'cards_studied': self.cards_studied,
            'notes_created': self.notes_created,
            'exams_taken': self.exams_taken,
            'topics_mastered': self.topics_mastered,
            'created_at': self.created_at.isoformat()
        }

class LearningPath:
    def __init__(self, id, user_id, title, description, materials, estimated_duration=None, difficulty_level=None, is_public=False):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.materials = materials  # JSONB array of material IDs and their order
        self.estimated_duration = estimated_duration  # in hours
        self.difficulty_level = difficulty_level
        self.is_public = is_public
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'materials': self.materials,
            'estimated_duration': self.estimated_duration,
            'difficulty_level': self.difficulty_level,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LearningPathProgress:
    def __init__(self, path_id, user_id, completed_materials=None, current_material_index=0, started_at=None, last_accessed_at=None, status='in_progress'):
        self.path_id = path_id
        self.user_id = user_id
        self.completed_materials = completed_materials or []  # JSONB array
        self.current_material_index = current_material_index
        self.started_at = started_at or datetime.utcnow()
        self.last_accessed_at = last_accessed_at
        self.status = status  # in_progress, completed, abandoned

    def to_dict(self):
        return {
            'path_id': self.path_id,
            'user_id': self.user_id,
            'completed_materials': self.completed_materials,
            'current_material_index': self.current_material_index,
            'started_at': self.started_at.isoformat(),
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'status': self.status
        } 