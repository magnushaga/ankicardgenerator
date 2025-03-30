from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User:
    def __init__(self, id, email, username, auth0_id=None):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.username = username
        self.auth0_id = auth0_id
        self.created_at = datetime.utcnow()
        self.last_login = datetime.utcnow()

    @staticmethod
    def from_auth0_claims(claims):
        return User(
            id=None,  # Supabase will generate this
            email=claims['email'],
            username=claims.get('nickname', claims['email'].split('@')[0]),
            auth0_id=claims['sub']
        )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'auth0_id': self.auth0_id,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat()
        }
    
class Textbook:
    def __init__(self, id, title, author, subject):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.author = author
        self.subject = subject
        self.created_at = datetime.utcnow()

class Part:
    def __init__(self, id, textbook_id, title, order_index):
        self.id = id or str(uuid.uuid4())
        self.textbook_id = textbook_id
        self.title = title
        self.order_index = order_index

class Chapter:
    def __init__(self, id, part_id, title, order_index):
        self.id = id or str(uuid.uuid4())
        self.part_id = part_id
        self.title = title
        self.order_index = order_index

class Topic:
    def __init__(self, id, chapter_id, title, comment, order_index):
        self.id = id or str(uuid.uuid4())
        self.chapter_id = chapter_id
        self.title = title
        self.comment = comment
        self.order_index = order_index

class Deck:
    def __init__(self, id, user_id, title):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.created_at = datetime.utcnow()

class Card:
    def __init__(self, id, deck_id, topic_id, front, back, media_urls=None):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.topic_id = topic_id
        self.front = front
        self.back = back
        self.media_urls = media_urls or []  # List of URLs to media files
        self.created_at = datetime.utcnow()
        self.next_review = datetime.utcnow()
        self.interval = 1
        self.easiness = 2.5
        self.repetitions = 0

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'topic_id': self.topic_id,
            'front': self.front,
            'back': self.back,
            'media_urls': self.media_urls,
            'created_at': self.created_at.isoformat(),
            'next_review': self.next_review.isoformat(),
            'interval': self.interval,
            'easiness': self.easiness,
            'repetitions': self.repetitions
        }

class StudySession:
    def __init__(self, id, deck_id):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.started_at = datetime.utcnow()
        self.ended_at = None

class CardReview:
    def __init__(self, id, session_id, card_id, quality, time_taken):
        self.id = id or str(uuid.uuid4())
        self.session_id = session_id
        self.card_id = card_id
        self.quality = quality
        self.time_taken = time_taken
        self.created_at = datetime.utcnow()
        self.prev_easiness = None
        self.prev_interval = None
        self.prev_repetitions = None
        self.new_easiness = None
        self.new_interval = None
        self.new_repetitions = None

class MediaFile:
    def __init__(self, id, user_id, file_name, file_type, file_size, mime_type, storage_path, thumbnail_path=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.file_name = file_name
        self.file_type = file_type  # image, video, audio, document, etc.
        self.file_size = file_size
        self.mime_type = mime_type
        self.storage_path = storage_path
        self.thumbnail_path = thumbnail_path
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'storage_path': self.storage_path,
            'thumbnail_path': self.thumbnail_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MediaAssociation:
    def __init__(self, id, media_file_id, associated_type, associated_id, position=None, context=None):
        self.id = id or str(uuid.uuid4())
        self.media_file_id = media_file_id
        self.associated_type = associated_type  # 'card', 'note', 'topic', etc.
        self.associated_id = associated_id
        self.position = position  # For ordering multiple media items
        self.context = context  # Additional context about how the media is used
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'media_file_id': self.media_file_id,
            'associated_type': self.associated_type,
            'associated_id': self.associated_id,
            'position': self.position,
            'context': self.context,
            'created_at': self.created_at.isoformat()
        }

class CourseMaterial:
    def __init__(self, id, user_id, title, description, material_type, file_path, file_size, mime_type, tags=None, metadata=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.material_type = material_type  # lecture_notes, exam, textbook, etc.
        self.file_path = file_path
        self.file_size = file_size
        self.mime_type = mime_type
        self.tags = tags or []
        self.metadata = metadata or {}  # Additional metadata like course name, semester, etc.
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'material_type': self.material_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class StudyResource:
    def __init__(self, id, user_id, title, content, resource_type, source_material_id=None, tags=None, metadata=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.content = content  # The actual content (text, structured data, etc.)
        self.resource_type = resource_type  # summary, flashcards, practice_questions, etc.
        self.source_material_id = source_material_id  # Reference to original course material
        self.tags = tags or []
        self.metadata = metadata or {}  # Additional metadata like difficulty, topics covered, etc.
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'resource_type': self.resource_type,
            'source_material_id': self.source_material_id,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ResourceGeneration:
    def __init__(self, id, user_id, resource_id, status, generation_type, prompt, result=None, error=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.resource_id = resource_id
        self.status = status  # pending, completed, failed
        self.generation_type = generation_type  # flashcards, summary, practice_questions, etc.
        self.prompt = prompt  # The prompt used for generation
        self.result = result  # The generated content
        self.error = error  # Any error message if generation failed
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'status': self.status,
            'generation_type': self.generation_type,
            'prompt': self.prompt,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 