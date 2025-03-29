from functools import wraps
from flask import request, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv
import logging

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

def get_user_permissions(user_id, resource_type, resource_id):
    """Get user's permissions for a specific resource"""
    try:
        if resource_type == 'deck':
            # Check if user owns the deck
            deck_result = supabase.table('decks').select('*').eq('id', resource_id).execute()
            if deck_result.data and deck_result.data[0]['user_id'] == user_id:
                return {'owner': True, 'can_edit': True, 'can_share': True, 'can_delete': True}
            
            # Check collaboration permissions
            collab_result = supabase.table('deck_collaborations').select('*').eq(
                'deck_id', resource_id
            ).eq('user_id', user_id).execute()
            
            if collab_result.data:
                return {
                    'owner': False,
                    'can_edit': collab_result.data[0]['can_edit'],
                    'can_share': collab_result.data[0]['can_share'],
                    'can_delete': collab_result.data[0]['can_delete']
                }
            
            return {'owner': False, 'can_edit': False, 'can_share': False, 'can_delete': False}
            
        elif resource_type == 'live_deck':
            # Check if user owns the live deck
            live_deck_result = supabase.table('live_decks').select('*').eq('id', resource_id).execute()
            if live_deck_result.data and live_deck_result.data[0]['user_id'] == user_id:
                return {'owner': True, 'can_edit': True, 'can_share': True, 'can_delete': True}
            
            return {'owner': False, 'can_edit': False, 'can_share': False, 'can_delete': False}
            
        elif resource_type in ['part', 'chapter', 'topic', 'card']:
            # Get the parent deck ID
            if resource_type == 'part':
                part_result = supabase.table('parts').select('deck_id').eq('id', resource_id).execute()
                if not part_result.data:
                    return None
                deck_id = part_result.data[0]['deck_id']
            elif resource_type == 'chapter':
                chapter_result = supabase.table('chapters').select('part_id').eq('id', resource_id).execute()
                if not chapter_result.data:
                    return None
                part_result = supabase.table('parts').select('deck_id').eq('id', chapter_result.data[0]['part_id']).execute()
                if not part_result.data:
                    return None
                deck_id = part_result.data[0]['deck_id']
            elif resource_type == 'topic':
                topic_result = supabase.table('topics').select('chapter_id').eq('id', resource_id).execute()
                if not topic_result.data:
                    return None
                chapter_result = supabase.table('chapters').select('part_id').eq('id', topic_result.data[0]['chapter_id']).execute()
                if not chapter_result.data:
                    return None
                part_result = supabase.table('parts').select('deck_id').eq('id', chapter_result.data[0]['part_id']).execute()
                if not part_result.data:
                    return None
                deck_id = part_result.data[0]['deck_id']
            else:  # card
                card_result = supabase.table('cards').select('topic_id').eq('id', resource_id).execute()
                if not card_result.data:
                    return None
                topic_result = supabase.table('topics').select('chapter_id').eq('id', card_result.data[0]['topic_id']).execute()
                if not topic_result.data:
                    return None
                chapter_result = supabase.table('chapters').select('part_id').eq('id', topic_result.data[0]['chapter_id']).execute()
                if not chapter_result.data:
                    return None
                part_result = supabase.table('parts').select('deck_id').eq('id', chapter_result.data[0]['part_id']).execute()
                if not part_result.data:
                    return None
                deck_id = part_result.data[0]['deck_id']
            
            # Get permissions for the parent deck
            return get_user_permissions(user_id, 'deck', deck_id)
            
        return None
        
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        return None

def requires_permission(permission):
    """Decorator to require specific permissions for routes"""
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
                
            permissions = get_user_permissions(user_id, resource_type, resource_id)
            if not permissions:
                return jsonify({"error": "Resource not found"}), 404
                
            if not permissions.get(permission, False):
                return jsonify({"error": "Insufficient permissions"}), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

def requires_ownership(f):
    """Decorator to require resource ownership"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'user'):
            return jsonify({"error": "No authenticated user"}), 401
            
        user_id = request.user['sub']
        resource_type = kwargs.get('resource_type')
        resource_id = kwargs.get('resource_id')
        
        if not resource_type or not resource_id:
            return jsonify({"error": "Resource type and ID required"}), 400
            
        permissions = get_user_permissions(user_id, resource_type, resource_id)
        if not permissions:
            return jsonify({"error": "Resource not found"}), 404
            
        if not permissions.get('owner', False):
            return jsonify({"error": "Resource ownership required"}), 403
            
        return f(*args, **kwargs)
    return decorated 