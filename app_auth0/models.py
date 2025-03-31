from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Decks:
    """
    Model class for decks table.
    """

    def __init__(self, id=None, user_id=None, title=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Textbooks:
    """
    Model class for textbooks table.
    """

    def __init__(self, id=None, user_id=None, title=None, author=None, subject=None, description=None, file_path=None, uploaded_at=None, is_public=None, tags=None, difficulty_level=None, language=None, total_cards=None, avg_rating=None, num_ratings=None):
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

class Parts:
    """
    Model class for parts table.
    """

    def __init__(self, id=None, deck_id=None, title=None, order_index=None):
        self.id = id or str(uuid.uuid4())
        self.deck_id = deck_id
        self.title = title
        self.order_index = order_index

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'title': self.title,
            'order_index': self.order_index,
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

class Chapters:
    """
    Model class for chapters table.
    """

    def __init__(self, id=None, part_id=None, title=None, order_index=None):
        self.id = id or str(uuid.uuid4())
        self.part_id = part_id
        self.title = title
        self.order_index = order_index

    def to_dict(self):
        return {
            'id': self.id,
            'part_id': self.part_id,
            'title': self.title,
            'order_index': self.order_index,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Users:
    """
    Model class for users table.
    """

    def __init__(self, id=None, email=None, username=None, auth0_id=None, created_at=None, last_login=None, is_active=None, email_verified=None, preferred_study_time=None, notification_preferences=None, study_goals=None, picture=None):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.username = username
        self.auth0_id = auth0_id
        self.created_at = created_at
        self.last_login = last_login
        self.is_active = is_active
        self.email_verified = email_verified
        self.preferred_study_time = preferred_study_time
        self.notification_preferences = notification_preferences
        self.study_goals = study_goals
        self.picture = picture

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'auth0_id': self.auth0_id,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'preferred_study_time': self.preferred_study_time,
            'notification_preferences': self.notification_preferences,
            'study_goals': self.study_goals,
            'picture': self.picture
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Topics:
    """
    Model class for topics table.
    """

    def __init__(self, id=None, chapter_id=None, title=None, order_index=None):
        self.id = id or str(uuid.uuid4())
        self.chapter_id = chapter_id
        self.title = title
        self.order_index = order_index

    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'title': self.title,
            'order_index': self.order_index,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

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

class Cards:
    """
    Model class for cards table.
    """

    def __init__(self, id=None, topic_id=None, front=None, back=None, created_at=None, media_urls=None):
        self.id = id or str(uuid.uuid4())
        self.topic_id = topic_id
        self.front = front
        self.back = back
        self.created_at = created_at
        self.media_urls = media_urls

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'front': self.front,
            'back': self.back,
            'created_at': self.created_at,
            'media_urls': self.media_urls,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class MediaFiles:
    """
    Model class for media_files table.
    """

    def __init__(self, id=None, user_id=None, file_name=None, file_type=None, file_size=None, mime_type=None, storage_path=None, thumbnail_path=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.mime_type = mime_type
        self.storage_path = storage_path
        self.thumbnail_path = thumbnail_path
        self.created_at = created_at
        self.updated_at = updated_at

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
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class MediaAssociations:
    """
    Model class for media_associations table.
    """

    def __init__(self, id=None, media_file_id=None, associated_type=None, associated_id=None, position=None, context=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.media_file_id = media_file_id
        self.associated_type = associated_type
        self.associated_id = associated_id
        self.position = position
        self.context = context
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'media_file_id': self.media_file_id,
            'associated_type': self.associated_type,
            'associated_id': self.associated_id,
            'position': self.position,
            'context': self.context,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

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

class CourseMaterials:
    """
    Model class for course_materials table.
    """

    def __init__(self, id=None, user_id=None, title=None, description=None, material_type=None, file_path=None, file_size=None, mime_type=None, tags=None, metadata=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.material_type = material_type
        self.file_path = file_path
        self.file_size = file_size
        self.mime_type = mime_type
        self.tags = tags
        self.metadata = metadata
        self.created_at = created_at
        self.updated_at = updated_at

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
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class StudyResources:
    """
    Model class for study_resources table.
    """

    def __init__(self, id=None, user_id=None, title=None, content=None, resource_type=None, source_material_id=None, tags=None, metadata=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.content = content
        self.resource_type = resource_type
        self.source_material_id = source_material_id
        self.tags = tags
        self.metadata = metadata
        self.created_at = created_at
        self.updated_at = updated_at

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
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ResourceGenerations:
    """
    Model class for resource_generations table.
    """

    def __init__(self, id=None, user_id=None, resource_id=None, status=None, generation_type=None, prompt=None, result=None, error=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.resource_id = resource_id
        self.status = status
        self.generation_type = generation_type
        self.prompt = prompt
        self.result = result
        self.error = error
        self.created_at = created_at
        self.updated_at = updated_at

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
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class LiveDecks:
    """
    Model class for live_decks table.
    """

    def __init__(self, id=None, user_id=None, deck_id=None, name=None, description=None, created_at=None, updated_at=None, active_cards=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.deck_id = deck_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
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
            'active_cards': self.active_cards,
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

class ContentReports:
    """
    Model class for content_reports table.
    """

    def __init__(self, id=None, reporter_id=None, content_type=None, content_id=None, reason=None, description=None, status=None, created_at=None, resolved_at=None):
        self.id = id or str(uuid.uuid4())
        self.reporter_id = reporter_id
        self.content_type = content_type
        self.content_id = content_id
        self.reason = reason
        self.description = description
        self.status = status
        self.created_at = created_at
        self.resolved_at = resolved_at

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'reason': self.reason,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'resolved_at': self.resolved_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

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

class Subscriptions:
    """
    Model class for subscriptions table.
    """

    def __init__(self, id=None, user_id=None, tier=None, status=None, current_period_start=None, current_period_end=None, stripe_customer_id=None, stripe_subscription_id=None, canceled_at=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.tier = tier
        self.status = status
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.canceled_at = canceled_at
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tier': self.tier,
            'status': self.status,
            'current_period_start': self.current_period_start,
            'current_period_end': self.current_period_end,
            'stripe_customer_id': self.stripe_customer_id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'canceled_at': self.canceled_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class SubscriptionHistory:
    """
    Model class for subscription_history table.
    """

    def __init__(self, id=None, subscription_id=None, previous_tier=None, new_tier=None, previous_status=None, new_status=None, change_reason=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.subscription_id = subscription_id
        self.previous_tier = previous_tier
        self.new_tier = new_tier
        self.previous_status = previous_status
        self.new_status = new_status
        self.change_reason = change_reason
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'previous_tier': self.previous_tier,
            'new_tier': self.new_tier,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'change_reason': self.change_reason,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class SubscriptionUsage:
    """
    Model class for subscription_usage table.
    """

    def __init__(self, id=None, user_id=None, feature=None, usage_count=None, last_used_at=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.feature = feature
        self.usage_count = usage_count
        self.last_used_at = last_used_at
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'feature': self.feature,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
