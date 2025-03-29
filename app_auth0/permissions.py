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

def has_permission(permission):
    """Decorator to check if user has specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({"error": "No authenticated user"}), 401

            user_id = request.user['sub']
            
            # Get user's role and permissions
            user_result = supabase.table('users').select('role').eq('auth0_id', user_id).execute()
            if not user_result.data:
                return jsonify({"error": "User not found"}), 404
                
            user_role = user_result.data[0].get('role', 'user')
            
            # Admin has all permissions
            if user_role == 'admin':
                return f(*args, **kwargs)
            
            # Check specific permissions
            if permission == 'manage_decks':
                # Check if user owns the deck or has collaboration access
                deck_id = kwargs.get('deck_id')
                if deck_id:
                    deck_result = supabase.table('decks').select('user_id').eq('id', deck_id).execute()
                    if not deck_result.data:
                        return jsonify({"error": "Deck not found"}), 404
                        
                    if deck_result.data[0]['user_id'] != user_id:
                        # Check collaboration
                        collab_result = supabase.table('deck_collaborations').select('*').eq(
                            'deck_id', deck_id
                        ).eq('user_id', user_id).execute()
                        
                        if not collab_result.data or not collab_result.data[0].get('can_edit'):
                            return jsonify({"error": "Insufficient permissions"}), 403
                
            elif permission == 'manage_live_decks':
                # Check if user owns the live deck
                live_deck_id = kwargs.get('live_deck_id')
                if live_deck_id:
                    live_deck_result = supabase.table('live_decks').select('user_id').eq('id', live_deck_id).execute()
                    if not live_deck_result.data:
                        return jsonify({"error": "Live deck not found"}), 404
                        
                    if live_deck_result.data[0]['user_id'] != user_id:
                        return jsonify({"error": "Insufficient permissions"}), 403
                
            elif permission == 'manage_content':
                # Check if user owns the content (part, chapter, topic)
                content_id = kwargs.get('content_id')
                content_type = kwargs.get('content_type')
                
                if content_id and content_type:
                    # Get the deck_id for the content
                    if content_type == 'part':
                        content_result = supabase.table('parts').select('deck_id').eq('id', content_id).execute()
                    elif content_type == 'chapter':
                        content_result = supabase.table('chapters').select('part_id').eq('id', content_id).execute()
                        if content_result.data:
                            part_result = supabase.table('parts').select('deck_id').eq('id', content_result.data[0]['part_id']).execute()
                            content_result = part_result
                    elif content_type == 'topic':
                        content_result = supabase.table('topics').select('chapter_id').eq('id', content_id).execute()
                        if content_result.data:
                            chapter_result = supabase.table('chapters').select('part_id').eq('id', content_result.data[0]['chapter_id']).execute()
                            if chapter_result.data:
                                part_result = supabase.table('parts').select('deck_id').eq('id', chapter_result.data[0]['part_id']).execute()
                                content_result = part_result
                    
                    if not content_result.data:
                        return jsonify({"error": f"{content_type} not found"}), 404
                        
                    deck_id = content_result.data[0]['deck_id']
                    
                    # Check deck ownership
                    deck_result = supabase.table('decks').select('user_id').eq('id', deck_id).execute()
                    if not deck_result.data:
                        return jsonify({"error": "Deck not found"}), 404
                        
                    if deck_result.data[0]['user_id'] != user_id:
                        # Check collaboration
                        collab_result = supabase.table('deck_collaborations').select('*').eq(
                            'deck_id', deck_id
                        ).eq('user_id', user_id).execute()
                        
                        if not collab_result.data or not collab_result.data[0].get('can_edit'):
                            return jsonify({"error": "Insufficient permissions"}), 403
                
            elif permission == 'share_deck':
                # Check if user owns the deck
                deck_id = kwargs.get('deck_id')
                if deck_id:
                    deck_result = supabase.table('decks').select('user_id').eq('id', deck_id).execute()
                    if not deck_result.data:
                        return jsonify({"error": "Deck not found"}), 404
                        
                    if deck_result.data[0]['user_id'] != user_id:
                        # Check collaboration
                        collab_result = supabase.table('deck_collaborations').select('*').eq(
                            'deck_id', deck_id
                        ).eq('user_id', user_id).execute()
                        
                        if not collab_result.data or not collab_result.data[0].get('can_share'):
                            return jsonify({"error": "Insufficient permissions"}), 403
                
            elif permission == 'study':
                # Check if user owns the live deck or has access to the deck
                live_deck_id = kwargs.get('live_deck_id')
                if live_deck_id:
                    live_deck_result = supabase.table('live_decks').select('user_id, deck_id').eq('id', live_deck_id).execute()
                    if not live_deck_result.data:
                        return jsonify({"error": "Live deck not found"}), 404
                        
                    if live_deck_result.data[0]['user_id'] != user_id:
                        # Check if user has access to the original deck
                        deck_id = live_deck_result.data[0]['deck_id']
                        deck_result = supabase.table('decks').select('user_id').eq('id', deck_id).execute()
                        if not deck_result.data:
                            return jsonify({"error": "Deck not found"}), 404
                            
                        if deck_result.data[0]['user_id'] != user_id:
                            # Check collaboration
                            collab_result = supabase.table('deck_collaborations').select('*').eq(
                                'deck_id', deck_id
                            ).eq('user_id', user_id).execute()
                            
                            if not collab_result.data:
                                return jsonify({"error": "Insufficient permissions"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator 