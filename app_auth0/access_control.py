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
from permission_store import permission_store, Permission, ResourceType

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

def get_user_role(user_id: str) -> str:
    """Get the role of a user."""
    try:
        # Check if user has admin permission on any resource
        for resource_type in ResourceType:
            if permission_store.has_permission(user_id, resource_type.value, "*", Permission.ADMIN):
                return "admin"
        return "user"
    except Exception as e:
        logger.error(f"Error getting user role: {str(e)}")
        return "user"

def get_parent_deck_id(resource_type: str, resource_id: str) -> str:
    """Get the parent deck ID for a resource."""
    # This function would typically query the database to get the parent deck ID
    # For now, we'll return None as we're using in-memory storage
    return None

def has_permission(user_id: str, resource_type: str, resource_id: str, permission: Permission) -> bool:
    """Check if a user has a specific permission on a resource."""
    return permission_store.has_permission(user_id, resource_type, resource_id, permission)

def requires_permission(permission: Permission, resource_type: str = None, resource_id: str = None):
    """Decorator to check if a user has the required permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get user ID from the request
                user_id = request.user_id if hasattr(request, 'user_id') else None
                if not user_id:
                    logger.error("No user ID found in request")
                    return jsonify({"error": "Unauthorized"}), 401

                # If resource_type and resource_id are not provided, try to get them from kwargs
                actual_resource_type = resource_type or kwargs.get('resource_type')
                actual_resource_id = resource_id or kwargs.get('resource_id')

                # Check if user has the required permission
                if permission_store.has_permission(user_id, actual_resource_type, actual_resource_id, permission):
                    return f(*args, **kwargs)
                else:
                    logger.warning(f"User {user_id} does not have permission {permission} on {actual_resource_type}:{actual_resource_id}")
                    return jsonify({"error": "Forbidden"}), 403

            except Exception as e:
                logger.error(f"Error checking permission: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        return decorated_function
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

            user_role = get_user_role(user_id)
            if not user_role or user_role != required_role.value:
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