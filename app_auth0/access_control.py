from functools import wraps
from flask import request, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv
import logging
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, List
from subscription_management import SubscriptionManager, SubscriptionTier, TIER_FEATURES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client with service role key
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Missing Supabase credentials")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

class ResourceType(Enum):
    DECK = 'deck'
    LIVE_DECK = 'live_deck'
    PART = 'part'
    CHAPTER = 'chapter'
    TOPIC = 'topic'
    CARD = 'card'
    STUDY_SESSION = 'study_session'
    USER = 'user'

class Permission(Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    SHARE = 'share'
    ADMIN = 'admin'
    CREATE_LIVE_DECK = 'create_live_deck'
    EDIT_LIVE_DECK = 'edit_live_deck'
    USE_AI_FEATURES = 'use_ai_features'
    USE_MEDIA = 'use_media'
    USE_ANALYTICS = 'use_analytics'
    USE_EXPORT = 'use_export'
    USE_IMPORT = 'use_import'
    USE_API = 'use_api'
    USE_PRIORITY_SUPPORT = 'use_priority_support'

class Role(Enum):
    OWNER = 'owner'
    EDITOR = 'editor'
    VIEWER = 'viewer'
    ADMIN = 'admin'

# Initialize subscription manager
subscription_manager = SubscriptionManager()

def get_user_role(user_id: str, resource_type: ResourceType, resource_id: str) -> Optional[Role]:
    """Get user's role for a specific resource"""
    try:
        logger.info(f"Getting role for user {user_id} on {resource_type.value} {resource_id}")
        
        # First get the user's UUID from our database
        user_result = supabase.table('users').select('id').eq('auth0_id', user_id).execute()
        if not user_result.data:
            logger.error(f"User with Auth0 ID {user_id} not found in database")
            return None
            
        db_user_id = user_result.data[0]['id']
        logger.info(f"Found database user ID {db_user_id} for Auth0 user {user_id}")
        
        if resource_type == ResourceType.DECK:
            # Check if user owns the deck
            deck_result = supabase.table('decks').select('*').eq('id', resource_id).execute()
            if not deck_result.data:
                logger.error(f"Deck {resource_id} not found")
                return None
                
            deck = deck_result.data[0]
            if deck['user_id'] == db_user_id:
                logger.info(f"User {db_user_id} is owner of deck {resource_id}")
                return Role.OWNER
            
            # Check collaboration role
            collab_result = supabase.table('deck_collaborations').select('*').eq(
                'deck_id', resource_id
            ).eq('user_id', db_user_id).execute()
            
            if collab_result.data:
                role = Role(collab_result.data[0]['role'])
                logger.info(f"User {db_user_id} has {role.value} role on deck {resource_id}")
                return role
            
            logger.error(f"User {db_user_id} has no access to deck {resource_id}")
            return None
            
        elif resource_type == ResourceType.LIVE_DECK:
            # Check if user owns the live deck
            live_deck_result = supabase.table('live_decks').select('*').eq('id', resource_id).execute()
            if live_deck_result.data and live_deck_result.data[0]['user_id'] == db_user_id:
                return Role.OWNER
            
            return None
            
        elif resource_type in [ResourceType.PART, ResourceType.CHAPTER, ResourceType.TOPIC, ResourceType.CARD]:
            # Get the parent deck ID
            deck_id = get_parent_deck_id(resource_type, resource_id)
            if deck_id:
                return get_user_role(user_id, ResourceType.DECK, deck_id)
            
            return None
            
        return None
        
    except Exception as e:
        logger.error(f"Error getting user role: {e}")
        logger.error("Exception details:", exc_info=True)
        return None

def get_parent_deck_id(resource_type: ResourceType, resource_id: str) -> Optional[str]:
    """Get the parent deck ID for a resource"""
    try:
        if resource_type == ResourceType.PART:
            result = supabase.table('parts').select('deck_id').eq('id', resource_id).execute()
        elif resource_type == ResourceType.CHAPTER:
            result = supabase.table('chapters').select('part_id').eq('id', resource_id).execute()
            if result.data:
                part_result = supabase.table('parts').select('deck_id').eq('id', result.data[0]['part_id']).execute()
                return part_result.data[0]['deck_id'] if part_result.data else None
        elif resource_type == ResourceType.TOPIC:
            result = supabase.table('topics').select('chapter_id').eq('id', resource_id).execute()
            if result.data:
                chapter_result = supabase.table('chapters').select('part_id').eq('id', result.data[0]['chapter_id']).execute()
                if chapter_result.data:
                    part_result = supabase.table('parts').select('deck_id').eq('id', chapter_result.data[0]['part_id']).execute()
                    return part_result.data[0]['deck_id'] if part_result.data else None
        elif resource_type == ResourceType.CARD:
            result = supabase.table('cards').select('topic_id').eq('id', resource_id).execute()
            if result.data:
                topic_result = supabase.table('topics').select('chapter_id').eq('id', result.data[0]['topic_id']).execute()
                if topic_result.data:
                    chapter_result = supabase.table('chapters').select('part_id').eq('id', topic_result.data[0]['chapter_id']).execute()
                    if chapter_result.data:
                        part_result = supabase.table('parts').select('deck_id').eq('id', chapter_result.data[0]['part_id']).execute()
                        return part_result.data[0]['deck_id'] if part_result.data else None
        
        return None
    except Exception as e:
        logger.error(f"Error getting parent deck ID: {e}")
        return None

def has_permission(user_id: str, resource_type: ResourceType, resource_id: str, required_permission: Permission) -> bool:
    """Check if user has the required permission for a resource"""
    try:
        # First get the user's UUID from our database
        user_result = supabase.table('users').select('id').eq('auth0_id', user_id).execute()
        if not user_result.data:
            logger.error(f"User with Auth0 ID {user_id} not found in database")
            return False
            
        db_user_id = user_result.data[0]['id']
        logger.info(f"Found database user ID {db_user_id} for Auth0 user {user_id}")

        # First check subscription-based permissions
        if required_permission in [
            Permission.CREATE_LIVE_DECK,
            Permission.EDIT_LIVE_DECK,
            Permission.USE_AI_FEATURES,
            Permission.USE_MEDIA,
            Permission.USE_ANALYTICS,
            Permission.USE_EXPORT,
            Permission.USE_IMPORT,
            Permission.USE_API,
            Permission.USE_PRIORITY_SUPPORT
        ]:
            feature = required_permission.value.replace('use_', '')
            return subscription_manager.has_feature_access(db_user_id, feature)

        # Then check role-based permissions
        role = get_user_role(user_id, resource_type, resource_id)
        if not role:
            return False

        # Map permissions to roles
        role_permissions = {
            Role.OWNER: {
                Permission.READ: True,
                Permission.WRITE: True,
                Permission.DELETE: True,
                Permission.SHARE: True,
                Permission.ADMIN: True
            },
            Role.EDITOR: {
                Permission.READ: True,
                Permission.WRITE: True,
                Permission.DELETE: False,
                Permission.SHARE: True,
                Permission.ADMIN: False
            },
            Role.VIEWER: {
                Permission.READ: True,
                Permission.WRITE: False,
                Permission.DELETE: False,
                Permission.SHARE: False,
                Permission.ADMIN: False
            },
            Role.ADMIN: {
                Permission.READ: True,
                Permission.WRITE: True,
                Permission.DELETE: True,
                Permission.SHARE: True,
                Permission.ADMIN: True
            }
        }

        return role_permissions[role].get(required_permission, False)

    except Exception as e:
        logger.error(f"Error checking permission: {e}")
        logger.error("Exception details:", exc_info=True)
        return False

def requires_permission(permission: Permission):
    """Decorator to require specific permissions for routes"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                logger.info(f"Checking permission {permission.value} for user {request.user['sub']}")
                
                # Get resource type and ID from route parameters
                resource_type = None
                resource_id = None
                
                # Extract resource type and ID from route parameters
                if 'deck_id' in kwargs:
                    resource_type = ResourceType.DECK
                    resource_id = kwargs['deck_id']
                elif 'live_deck_id' in kwargs:
                    resource_type = ResourceType.LIVE_DECK
                    resource_id = kwargs['live_deck_id']
                elif 'part_id' in kwargs:
                    resource_type = ResourceType.PART
                    resource_id = kwargs['part_id']
                elif 'chapter_id' in kwargs:
                    resource_type = ResourceType.CHAPTER
                    resource_id = kwargs['chapter_id']
                elif 'topic_id' in kwargs:
                    resource_type = ResourceType.TOPIC
                    resource_id = kwargs['topic_id']
                elif 'card_id' in kwargs:
                    resource_type = ResourceType.CARD
                    resource_id = kwargs['card_id']
                
                if not resource_type or not resource_id:
                    logger.error("Could not determine resource type or ID from route parameters")
                    return jsonify({"error": "Invalid resource"}), 400
                
                logger.info(f"Checking permission {permission.value} for {resource_type.value} {resource_id}")
                
                # Check if user has the required permission
                if not has_permission(request.user['sub'], resource_type, resource_id, permission):
                    logger.error(f"User {request.user['sub']} does not have {permission.value} permission for {resource_type.value} {resource_id}")
                    return jsonify({"error": "Insufficient permissions"}), 403
                
                logger.info(f"Permission check passed for user {request.user['sub']}")
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Error in permission check: {e}")
                logger.error("Exception details:", exc_info=True)
                return jsonify({"error": "Internal server error"}), 500
                
        return decorated
    return decorator

def requires_role(role: Role):
    """Decorator to require specific role for routes"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({"error": "No authenticated user"}), 401

            user_id = request.user['sub']
            resource_type = kwargs.get('resource_type')
            resource_id = kwargs.get('resource_id')

            if not resource_type or not resource_id:
                return jsonify({"error": "Resource type and ID required"}), 400

            try:
                resource_type_enum = ResourceType(resource_type)
                required_role = Role(role)
            except ValueError:
                return jsonify({"error": "Invalid resource type or role"}), 400

            user_role = get_user_role(user_id, resource_type_enum, resource_id)
            if not user_role or user_role != required_role:
                return jsonify({"error": "Insufficient role"}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator

def assign_role(user_id: str, resource_type: ResourceType, resource_id: str, role: Role) -> bool:
    """Assign a role to a user for a resource"""
    try:
        if resource_type == ResourceType.DECK:
            # Check if user already has a role
            collab_result = supabase.table('deck_collaborations').select('*').eq(
                'deck_id', resource_id
            ).eq('user_id', user_id).execute()

            if collab_result.data:
                # Update existing role
                result = supabase.table('deck_collaborations').update({
                    'role': role.value,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('deck_id', resource_id).eq('user_id', user_id).execute()
            else:
                # Create new collaboration
                result = supabase.table('deck_collaborations').insert({
                    'id': str(uuid.uuid4()),
                    'deck_id': resource_id,
                    'user_id': user_id,
                    'role': role.value,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }).execute()

            return True if result.data else False

        return False

    except Exception as e:
        logger.error(f"Error assigning role: {e}")
        return False

def remove_role(user_id: str, resource_type: ResourceType, resource_id: str) -> bool:
    """Remove a user's role for a resource"""
    try:
        if resource_type == ResourceType.DECK:
            result = supabase.table('deck_collaborations').delete().eq(
                'deck_id', resource_id
            ).eq('user_id', user_id).execute()

            return True if result.data else False

        return False

    except Exception as e:
        logger.error(f"Error removing role: {e}")
        return False 