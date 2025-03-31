from flask import Blueprint, request, jsonify
from anthropic import Anthropic
import os
import uuid
import json
from datetime import datetime, timedelta
from models import (
    Users, Textbooks, Parts, Chapters, Topics, Decks, Cards,
    StudySessions, CardReviews
)
from supabase import create_client
from dotenv import load_dotenv
import logging
from functools import wraps
import jwt
from jwt.algorithms import RSAAlgorithm
from jwt_verify import requires_scope
from access_control import (
    requires_permission, requires_role, assign_role, remove_role,
    ResourceType, Permission, Role
)
from supabase_config import supabase
from auth_decorators import requires_auth
from study.supermemo2 import SuperMemo2
from subscription_management import SubscriptionManager, SubscriptionTier, SubscriptionStatus

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

api = Blueprint('api', __name__)

# Initialize subscription manager
subscription_manager = SubscriptionManager()

class TextbookAnalyzer:
    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Anthropic client with API key"""
        if not hasattr(self, 'client') or self.client is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            try:
                self.client = Anthropic(api_key=api_key)
            except Exception as e:
                logger.error(f"Error initializing Anthropic client: {e}")
                raise

    def analyze_textbook(self, textbook_name, client=None):
        """Analyze textbook title to determine subject area and requirements"""
        logger.info(f"Analyzing subject area for: {textbook_name}")
        
        if client is None:
            client = self.client
        
        if client is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            client = Anthropic(api_key=api_key)
        
        analysis_prompt = f"""
        Based solely on this textbook title: "{textbook_name}", please:
        
        1. Identify the primary subject area (e.g., mathematics, physics, economics, biology)
        2. Identify any specialized subfields (e.g., organic chemistry, linear algebra, microeconomics)
        3. Determine if this subject typically requires:
        - Mathematical notation (equations, formulas, symbols)
        - Chemical formulas or reactions
        - Biological processes or diagrams
        - Code snippets
        - Historical context
        - Conceptual frameworks
        - Theoretical models
        - Examples or case studies
        - Quotations from key figures
        
        Return your analysis as a JSON object with the following structure:
        {{
            "primary_subject": "subject name",
            "subfields": ["subfield1", "subfield2"],
            "requires_math": true/false,
            "requires_chemistry_notation": true/false,
            "requires_biology_notation": true/false,
            "benefits_from_code": true/false,
            "benefits_from_history": true/false,
            "benefits_from_concepts": true/false,
            "benefits_from_theory": true/false,
            "benefits_from_examples": true/false,
            "benefits_from_quotes": true/false,
            "recommended_focus_areas": ["focus1", "focus2", "focus3"],
            "special_notation_needs": ["need1", "need2"]
        }}
        """
        
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.2,
                system="You are an expert in academic subjects who can identify the subject area and learning requirements of a textbook based on its title. Respond with valid JSON only.",
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            content = response.content[0].text
            
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3]
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3]
                
            analysis = json.loads(content)
            logger.info(f"Successfully analyzed textbook: {textbook_name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing textbook: {e}")
            return {
                "primary_subject": "general",
                "subfields": [],
                "requires_math": True,
                "requires_chemistry_notation": False,
                "requires_biology_notation": False,
                "benefits_from_code": False,
                "benefits_from_history": True,
                "benefits_from_concepts": True,
                "benefits_from_theory": True,
                "benefits_from_examples": True,
                "benefits_from_quotes": True,
                "recommended_focus_areas": ["core concepts", "critical thinking", "applications"],
                "special_notation_needs": []
            }

    def generate_structure(self, textbook_name, test_mode=False):
        """Generate textbook structure using Claude"""
        try:
            structure_prompt = f"""
            Create a detailed structure for the textbook "{textbook_name}".
            
            CRITICAL FORMATTING REQUIREMENTS:
            1. Title Format:
               - Parts must be exactly "Part I: [Title]", "Part II: [Title]", etc.
               - Chapters must be exactly "Chapter 1: [Title]", "Chapter 2: [Title]", etc.
               - DO NOT double-number chapters (NO "Chapter 1: Chapter 3: Title")
               - Keep chapter numbers sequential within each part
               - Topics should have clear titles without numbers

            Example of correct formatting:
            {{
                "parts": [
                    {{
                        "title": "Part I: Fundamentals",
                        "chapters": [
                            {{
                                "title": "Chapter 1: Introduction",
                                "topics": [...]
                            }},
                            {{
                                "title": "Chapter 2: Basic Concepts",
                                "topics": [...]
                            }}
                        ]
                    }}
                ]
            }}

            Requirements:
            1. Include 2-3 main parts
            2. Each part should have 2-3 chapters
            3. Each chapter should have 2-4 topics
            4. Every topic must have:
               - A clear title
               - A comment explaining its importance
               - A card_count between 5-10
               - requires_latex flag indicating if LaTeX is needed
               - latex_type specifying the type of notation needed
            """

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2000,
                temperature=0.3,
                system="""You are an expert in textbook organization. 
                         Respond with valid JSON only. 
                         Ensure parts use Roman numerals (I, II, III).
                         Ensure chapters use continuous Arabic numerals (1, 2, 3, 4...).
                         Never double-number chapters.
                         Maintain consistent formatting throughout.""",
                messages=[
                    {"role": "user", "content": structure_prompt}
                ]
            )
            
            content = response.content[0].text
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3]
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3]
            
            structure = json.loads(content)

            # Fix and verify formatting
            chapter_counter = 1
            for i, part in enumerate(structure['parts']):
                if not part['title'].startswith(f"Part {self._to_roman(i+1)}:"):
                    part['title'] = f"Part {self._to_roman(i+1)}: {part['title'].split(':', 1)[-1].strip()}"
                
                for chapter in part['chapters']:
                    if "Chapter" in chapter['title'].split(":", 1)[-1]:
                        actual_title = chapter['title'].split(":")[-1].strip()
                        chapter['title'] = f"Chapter {chapter_counter}: {actual_title}"
                    else:
                        chapter['title'] = f"Chapter {chapter_counter}: {chapter['title'].split(':', 1)[-1].strip()}"
                    
                    chapter_counter += 1
                    
                    for topic in chapter['topics']:
                        if 'requires_latex' not in topic:
                            topic['requires_latex'] = False
                        if 'latex_type' not in topic:
                            topic['latex_type'] = 'none'

            return structure

        except Exception as e:
            logger.error(f"Error generating structure: {e}")
            if test_mode:
                return {
                    'parts': [
                        {
                            'title': 'Part I: Fundamentals',
                            'chapters': [
                                {
                                    'title': 'Chapter 1: Introduction',
                                    'topics': [
                                        {
                                            'title': 'Basic Concepts',
                                            'comment': 'Foundation of the subject',
                                            'card_count': 5,
                                            'requires_latex': False,
                                            'latex_type': 'none'
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            raise

    def _to_roman(self, num):
        """Helper method to convert numbers to Roman numerals"""
        roman_nums = [
            ('X', 10),
            ('IX', 9),
            ('V', 5),
            ('IV', 4),
            ('I', 1)
        ]
        result = ''
        for roman, value in roman_nums:
            while num >= value:
                result += roman
                num -= value
        return result

    def generate_cards_for_topic(self, topic_title, topic_comment, textbook_name, card_count):
        """Generate flashcards for a specific topic using Claude"""
        try:
            cards_prompt = f"""
            Create {card_count} Anki flashcards for the topic "{topic_title}" from the textbook "{textbook_name}".
            Topic context: {topic_comment}
            
            Return as JSON array of cards:
            [
                {{
                    "question": "Clear, specific question",
                    "answer": "Comprehensive answer"
                }}
            ]
            """

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2000,
                temperature=0.3,
                system="You are an expert in creating educational flashcards. Respond with valid JSON only.",
                messages=[
                    {"role": "user", "content": cards_prompt}
                ]
            )
            
            content = response.content[0].text
            
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3]
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3]
            
            return json.loads(content)

        except Exception as e:
            logger.error(f"Error generating cards: {e}")
            return [
                {
                    "question": f"What is {topic_title}?",
                    "answer": "This is a test card generated in fallback mode."
                },
                {
                    "question": f"Explain the importance of {topic_title}.",
                    "answer": "This is another test card generated in fallback mode."
                }
            ]

@api.route('/api/test', methods=['GET'])
def test():
    """Test endpoint to verify API is working"""
    return jsonify({"message": "API is working!"})

@api.route('/api/protected', methods=['GET'])
@requires_auth
def protected():
    """Test endpoint to verify authentication is working"""
    return jsonify({
        "message": "Protected endpoint is working!",
        "user": request.user
    })

@api.route('/api/user-decks', methods=['GET'])
@requires_auth
def get_user_decks():
    """Get all decks for the authenticated user"""
    try:
        user_id = request.user['sub']
        result = supabase.table('decks').select('*').eq('user_id', user_id).execute()
        
        return jsonify([{
            'id': deck['id'],
            'title': deck['title'],
            'created_at': deck['created_at']
        } for deck in result.data])
        
    except Exception as e:
        logger.error(f"Error getting user decks: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks', methods=['POST'])
@requires_auth
def create_deck():
    """Create a new deck for the authenticated user"""
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
            
        deck_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'title': title,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('decks').insert(deck_data).execute()
        
        return jsonify({
            'id': result.data[0]['id'],
            'title': result.data[0]['title'],
            'created_at': result.data[0]['created_at']
        })
        
    except Exception as e:
        logger.error(f"Error creating deck: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks/<deck_id>', methods=['DELETE'])
@requires_auth
@requires_permission(Permission.DELETE)
def delete_deck(deck_id):
    """Delete a deck"""
    try:
        # Check if user owns the deck
        deck_result = supabase.table('decks').select('*').eq('id', deck_id).execute()
        if not deck_result.data:
            return jsonify({'error': 'Deck not found'}), 404
            
        deck = deck_result.data[0]
        if deck['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Delete the deck
        supabase.table('decks').delete().eq('id', deck_id).execute()
        
        return jsonify({'message': 'Deck deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting deck: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks/<deck_id>/collaborate', methods=['POST'])
@requires_auth
@requires_permission(Permission.SHARE)
def add_collaborator(deck_id):
    """Add a collaborator to a deck"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        role = data.get('role', 'viewer')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
            
        try:
            role_enum = Role(role)
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
            
        result = assign_role(user_id, ResourceType.DECK, deck_id, role_enum)
        if not result:
            return jsonify({'error': 'Failed to assign role'}), 500
            
        return jsonify({
            'id': str(result['id']),
            'role': result['role']
        })
        
    except Exception as e:
        logger.error(f"Error adding collaborator: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks/<deck_id>/collaborate/<user_id>', methods=['DELETE'])
@requires_auth
@requires_permission(Permission.SHARE)
def remove_collaborator(deck_id, user_id):
    """Remove a collaborator from a deck"""
    try:
        success = remove_role(user_id, ResourceType.DECK, deck_id)
        if not success:
            return jsonify({'error': 'Failed to remove collaborator'}), 500
            
        return jsonify({'message': 'Collaborator removed successfully'})
        
    except Exception as e:
        logger.error(f"Error removing collaborator: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks/<deck_id>/edit', methods=['POST'])
@requires_auth
@requires_permission(Permission.WRITE)
def edit_deck(deck_id):
    """Edit a deck"""
    try:
        data = request.get_json()
        # ... existing edit deck logic ...
        
    except Exception as e:
        logger.error(f"Error editing deck: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/live-decks', methods=['POST'])
@requires_auth
def create_live_deck():
    """Create a new live deck from an existing deck"""
    try:
        data = request.get_json()
        deck_id = data.get('deck_id')
        name = data.get('name')
        description = data.get('description')
        
        if not all([deck_id, name]):
            return jsonify({'error': 'deck_id and name are required'}), 400
            
        # Check if user owns the deck
        deck_result = supabase.table('decks').select('*').eq('id', deck_id).execute()
        if not deck_result.data:
            return jsonify({'error': 'Deck not found'}), 404
            
        deck = deck_result.data[0]
        if deck['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Create live deck
        live_deck_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'deck_id': deck_id,
            'name': name,
            'description': description,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('live_decks').insert(live_deck_data).execute()
        
        return jsonify(result.data[0])
        
    except Exception as e:
        logger.error(f"Error creating live deck: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/live-decks/<live_deck_id>/cards', methods=['GET'])
@requires_auth
def get_live_deck_cards(live_deck_id):
    """Get all cards for a live deck with their states"""
    try:
        # Check if user owns the live deck
        live_deck_result = supabase.table('live_decks').select('*').eq('id', live_deck_id).execute()
        if not live_deck_result.data:
            return jsonify({'error': 'Live deck not found'}), 404
            
        live_deck = live_deck_result.data[0]
        if live_deck['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Get cards with their states
        cards_result = supabase.table('user_card_states').select(
            'card_id, is_active, next_review, interval, easiness, repetitions'
        ).eq('live_deck_id', live_deck_id).execute()
        
        return jsonify(cards_result.data)
        
    except Exception as e:
        logger.error(f"Error getting live deck cards: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/live-decks/<live_deck_id>/cards/<card_id>/toggle', methods=['POST'])
@requires_auth
def toggle_card_state(live_deck_id, card_id):
    """Toggle a card's active state in a live deck"""
    try:
        # Check if user owns the live deck
        live_deck_result = supabase.table('live_decks').select('*').eq('id', live_deck_id).execute()
        if not live_deck_result.data:
            return jsonify({'error': 'Live deck not found'}), 404
            
        live_deck = live_deck_result.data[0]
        if live_deck['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Get current card state
        card_state_result = supabase.table('user_card_states').select('*').eq(
            'live_deck_id', live_deck_id
        ).eq('card_id', card_id).execute()
        
        if not card_state_result.data:
            return jsonify({'error': 'Card state not found'}), 404
            
        # Toggle the state
        current_state = card_state_result.data[0]
        new_state = not current_state['is_active']
        
        result = supabase.table('user_card_states').update({
            'is_active': new_state
        }).eq('live_deck_id', live_deck_id).eq('card_id', card_id).execute()
        
        return jsonify({
            'card_id': card_id,
            'is_active': new_state
        })
        
    except Exception as e:
        logger.error(f"Error toggling card state: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/analytics', methods=['GET'])
@requires_auth
def get_learning_analytics():
    """Get learning analytics for the current user"""
    try:
        result = supabase.table('learning_analytics').select('*').eq(
            'user_id', request.user['sub']
        ).execute()
        
        return jsonify(result.data)
        
    except Exception as e:
        logger.error(f"Error getting learning analytics: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/achievements', methods=['GET'])
@requires_auth
def get_achievements():
    """Get all achievements for the current user"""
    try:
        result = supabase.table('achievements').select('*').eq(
            'user_id', request.user['sub']
        ).execute()
        
        return jsonify(result.data)
        
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/reminders', methods=['POST'])
@requires_auth
def create_study_reminder():
    """Create a new study reminder"""
    try:
        data = request.get_json()
        live_deck_id = data.get('live_deck_id')
        reminder_time = data.get('reminder_time')
        days_of_week = data.get('days_of_week')
        notification_type = data.get('notification_type', 'in-app')
        
        if not all([live_deck_id, reminder_time, days_of_week]):
            return jsonify({'error': 'live_deck_id, reminder_time, and days_of_week are required'}), 400
            
        # Check if user owns the live deck
        live_deck_result = supabase.table('live_decks').select('*').eq('id', live_deck_id).execute()
        if not live_deck_result.data:
            return jsonify({'error': 'Live deck not found'}), 404
            
        live_deck = live_deck_result.data[0]
        if live_deck['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        reminder_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'live_deck_id': live_deck_id,
            'reminder_time': reminder_time,
            'days_of_week': days_of_week,
            'notification_type': notification_type,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('study_reminders').insert(reminder_data).execute()
        
        return jsonify(result.data[0])
        
    except Exception as e:
        logger.error(f"Error creating study reminder: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/analyze-textbook', methods=['POST'])
def analyze_textbook():
    """Analyze a textbook's title to determine subject area and requirements"""
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400

    analyzer = TextbookAnalyzer()
    try:
        analysis = analyzer.analyze_textbook(textbook_name)
        return jsonify(analysis)
        
    except Exception as e:
        default_analysis = {
            "primary_subject": "general",
            "subfields": [],
            "requires_math": True,
            "requires_chemistry_notation": False,
            "requires_biology_notation": False,
            "benefits_from_code": False,
            "benefits_from_history": True,
            "benefits_from_concepts": True,
            "benefits_from_theory": True,
            "benefits_from_examples": True,
            "benefits_from_quotes": True,
            "recommended_focus_areas": ["core concepts", "critical thinking", "applications"],
            "special_notation_needs": []
        }
        return jsonify({"error": str(e), "fallback_analysis": default_analysis}), 500

@api.route('/api/generate-textbook-structure', methods=['POST'])
@requires_auth
def generate_textbook_structure():
    """Generate a structured outline for a textbook"""
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    test_mode = data.get('test_mode', False)
    is_public = data.get('is_public', False)
    allow_collaboration = data.get('allow_collaboration', False)
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400

    analyzer = TextbookAnalyzer()
    try:
        structure = analyzer.generate_structure(textbook_name, test_mode)
        
        # Get user ID from request
        user_id = request.user.get('sub')
        if not user_id:
            return jsonify({'error': 'User ID not found'}), 401
            
        # Create database entries in Supabase
        textbook_data = {
            'id': str(uuid.uuid4()),
            'title': textbook_name,
            'author': 'Generated',
            'subject': 'general',
            'created_at': datetime.utcnow().isoformat(),
            'created_by': user_id,
            'is_public': is_public,
            'allow_collaboration': allow_collaboration
        }
        
        result = supabase.table('textbooks').insert(textbook_data).execute()
        textbook_id = result.data[0]['id']
        
        # Create user ownership record
        user_deck_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'textbook_id': textbook_id,
            'is_owner': True,
            'can_edit': True,
            'can_share': True,
            'created_at': datetime.utcnow().isoformat()
        }
        supabase.table('user_decks').insert(user_deck_data).execute()
        
        # Create initial sharing settings if public
        if is_public:
            share_data = {
                'id': str(uuid.uuid4()),
                'textbook_id': textbook_id,
                'shared_by': user_id,
                'share_type': 'public',
                'created_at': datetime.utcnow().isoformat()
            }
            supabase.table('deck_shares').insert(share_data).execute()
        
        # Create initial collaboration settings if enabled
        if allow_collaboration:
            collaboration_data = {
                'id': str(uuid.uuid4()),
                'textbook_id': textbook_id,
                'created_by': user_id,
                'is_active': True,
                'max_collaborators': 5,  # Default max collaborators
                'created_at': datetime.utcnow().isoformat()
            }
            supabase.table('deck_collaborations').insert(collaboration_data).execute()
        
        # Create textbook structure
        for part_idx, part_data in enumerate(structure["parts"]):
            part_data = {
                'id': str(uuid.uuid4()),
                'textbook_id': textbook_id,
                'title': part_data["title"],
                'order_index': part_idx,
                'created_at': datetime.utcnow().isoformat()
            }
            result = supabase.table('parts').insert(part_data).execute()
            part_id = result.data[0]['id']
            
            for chapter_idx, chapter_data in enumerate(part_data["chapters"]):
                chapter_data = {
                    'id': str(uuid.uuid4()),
                    'part_id': part_id,
                    'title': chapter_data["title"],
                    'order_index': chapter_idx,
                    'created_at': datetime.utcnow().isoformat()
                }
                result = supabase.table('chapters').insert(chapter_data).execute()
                chapter_id = result.data[0]['id']
                
                for topic_idx, topic_data in enumerate(chapter_data["topics"]):
                    topic_data = {
                        'id': str(uuid.uuid4()),
                        'chapter_id': chapter_id,
                        'title': topic_data["title"],
                        'comment': topic_data["comment"],
                        'order_index': topic_idx,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    supabase.table('topics').insert(topic_data).execute()
        
        # Return enhanced response with ownership and sharing info
        return jsonify({
            'structure': structure,
            'textbook': {
                'id': textbook_id,
                'title': textbook_name,
                'is_public': is_public,
                'allow_collaboration': allow_collaboration,
                'created_by': user_id,
                'created_at': textbook_data['created_at']
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating textbook structure: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/generate-cards', methods=['POST'])
def generate_cards():
    """Generate flashcards for a specific topic"""
    data = request.get_json()
    topic_id = data.get('topic_id')
    deck_id = data.get('deck_id')
    card_count = data.get('card_count', 5)
    test_mode = data.get('test_mode', False)
    
    if not all([topic_id, deck_id]):
        return jsonify({'error': 'topic_id and deck_id are required'}), 400
        
    if test_mode:
        card_count = min(card_count, 3)

    try:
        # Get topic data from Supabase
        topic_result = supabase.table('topics').select('*').eq('id', topic_id).execute()
        if not topic_result.data:
            return jsonify({'error': 'Topic not found'}), 404
            
        topic = topic_result.data[0]
        
        # Get chapter and textbook data
        chapter_result = supabase.table('chapters').select('*').eq('id', topic['chapter_id']).execute()
        chapter = chapter_result.data[0]
        
        part_result = supabase.table('parts').select('*').eq('id', chapter['part_id']).execute()
        part = part_result.data[0]
        
        textbook_result = supabase.table('textbooks').select('*').eq('id', part['textbook_id']).execute()
        textbook = textbook_result.data[0]
        
        # Generate cards
        analyzer = TextbookAnalyzer()
        cards = analyzer.generate_cards_for_topic(
            topic['title'],
            topic['comment'],
            textbook['title'],
            card_count
        )
        
        # Store cards in Supabase
        created_cards = []
        for card_data in cards:
            card_data = {
                'id': str(uuid.uuid4()),
                'deck_id': deck_id,
                'topic_id': topic_id,
                'front': card_data['question'],
                'back': card_data['answer'],
                'created_at': datetime.utcnow().isoformat(),
                'next_review': datetime.utcnow().isoformat(),
                'interval': 1,
                'easiness': 2.5,
                'repetitions': 0
            }
            result = supabase.table('cards').insert(card_data).execute()
            created_cards.append(result.data[0])
        
        return jsonify(created_cards)
        
    except Exception as e:
        logger.error(f"Error generating cards: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/study-sessions', methods=['POST'])
@requires_auth
def create_study_session():
    """Create a new study session"""
    try:
        data = request.get_json()
        deck_id = data.get('deck_id')
        
        if not deck_id:
            logger.error("No deck_id provided in request")
            return jsonify({'error': 'deck_id is required'}), 400
            
        # Get user from database using Auth0 ID
        user_result = supabase.table('users').select('id').eq('auth0_id', request.user['sub']).execute()
        if not user_result.data:
            logger.error(f"User not found in database for Auth0 ID: {request.user['sub']}")
            return jsonify({'error': 'User not found in database'}), 404
            
        user_id = user_result.data[0]['id']
        logger.info(f"Found user ID: {user_id} for Auth0 ID: {request.user['sub']}")
        
        # Verify deck exists and user has access
        deck_result = supabase.table('decks').select('*, deck_shares(*)').eq('id', deck_id).execute()
        if not deck_result.data:
            logger.error(f"Deck not found: {deck_id}")
            return jsonify({'error': 'Deck not found'}), 404
            
        deck = deck_result.data[0]
        
        # Check if user has access to the deck
        has_access = False
        
        # Check if user owns the deck
        if deck['user_id'] == user_id:
            has_access = True
        # Check if deck is public
        elif deck.get('is_public', False):
            has_access = True
        # Check if deck is shared with user
        elif deck.get('deck_shares'):
            for share in deck['deck_shares']:
                if share['user_id'] == user_id:
                    has_access = True
                    break
        
        if not has_access:
            logger.error(f"User {user_id} does not have access to deck {deck_id}")
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Create study session
        session_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,  # Use database user ID
            'deck_id': deck_id,
            'started_at': datetime.utcnow().isoformat(),
            'cards_studied': 0,
            'correct_answers': 0
        }
        
        logger.info(f"Creating study session: {session_data}")
        result = supabase.table('study_sessions').insert(session_data).execute()
        
        if not result.data:
            logger.error("Failed to create study session")
            return jsonify({'error': 'Failed to create study session'}), 500
            
        logger.info(f"Successfully created study session: {result.data[0]}")
        return jsonify(result.data[0])
        
    except Exception as e:
        logger.error(f"Error creating study session: {e}")
        logger.error("Exception details:", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api.route('/api/study-sessions/<session_id>', methods=['PUT'])
@requires_auth
def end_study_session(session_id):
    """End a study session and calculate statistics"""
    try:
        # Update session in Supabase
        update_data = {
            'ended_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('study_sessions').update(update_data).eq('id', session_id).execute()
        session = result.data[0]
        
        # Get reviews for statistics
        reviews_result = supabase.table('card_reviews').select('*').eq('session_id', session_id).execute()
        reviews = reviews_result.data
        
        # Calculate statistics
        total_cards = len(reviews)
        total_time = sum(r['time_taken'] for r in reviews if r['time_taken'])
        avg_quality = sum(r['quality'] for r in reviews) / total_cards if total_cards else 0
        
        # Update session statistics
        supabase.table('study_sessions').update({
            'cards_studied': total_cards,
            'correct_answers': sum(1 for r in reviews if r['quality'] >= 3)
        }).eq('id', session_id).execute()
        
        return jsonify({
            'sessionId': str(session['id']),
            'startedAt': session['started_at'],
            'endedAt': session['ended_at'],
            'statistics': {
                'totalCards': total_cards,
                'totalTimeMs': total_time,
                'averageQuality': avg_quality
            }
        })
        
    except Exception as e:
        logger.error(f"Error ending study session: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks/<deck_id>/due-cards', methods=['GET'])
@requires_auth
def get_due_cards(deck_id):
    """Get cards that are due for review"""
    try:
        # Get user from database using Auth0 ID
        user_result = supabase.table('users').select('id').eq('auth0_id', request.user['sub']).execute()
        if not user_result.data:
            logger.error(f"User not found in database for Auth0 ID: {request.user['sub']}")
            return jsonify({'error': 'User not found in database'}), 404
            
        user_id = user_result.data[0]['id']
        logger.info(f"Found user ID: {user_id} for Auth0 ID: {request.user['sub']}")
            
        # First verify the deck exists and user has access
        deck_result = supabase.table('decks').select('*, deck_shares(*)').eq('id', deck_id).execute()
        if not deck_result.data:
            logger.error(f"Deck not found: {deck_id}")
            return jsonify({'error': 'Deck not found'}), 404
            
        deck = deck_result.data[0]
        
        # Check if user has access to the deck
        has_access = False
        
        # Check if user owns the deck
        if deck['user_id'] == user_id:
            has_access = True
        # Check if deck is public
        elif deck.get('is_public', False):
            has_access = True
        # Check if deck is shared with user
        elif deck.get('deck_shares'):
            for share in deck['deck_shares']:
                if share['user_id'] == user_id:
                    has_access = True
                    break
        
        if not has_access:
            logger.error(f"User {user_id} does not have access to deck {deck_id}")
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Get all cards for the deck with their states
        now = datetime.utcnow().isoformat()
        result = supabase.table('cards').select(
            'id, front, back, next_review, interval, easiness, repetitions'
        ).eq('deck_id', deck_id).lte('next_review', now).execute()
        
        # Format the response
        cards = []
        for card in result.data:
            card_data = {
                'id': str(card['id']),
                'front': card['front'],
                'back': card['back'],
                'nextReview': card['next_review'],
                'interval': card['interval'],
                'easiness': card['easiness'],
                'repetitions': card['repetitions']
            }
            cards.append(card_data)
            
        logger.info(f"Found {len(cards)} due cards for deck {deck_id}")
        return jsonify(cards)
        
    except Exception as e:
        logger.error(f"Error getting due cards: {e}")
        logger.error("Exception details:", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api.route('/api/review-card', methods=['POST'])
@requires_auth
def review_card():
    """Record a card review with SuperMemo2 algorithm"""
    try:
        data = request.get_json()
        card_id = data.get('card_id')
        session_id = data.get('session_id')
        quality = data.get('quality')
        time_taken = data.get('time_taken')
        
        if not all([card_id, session_id, quality is not None]):
            logger.error("Missing required fields in review request")
            return jsonify({'error': 'card_id, session_id, and quality are required'}), 400
        
        # Get user from database using Auth0 ID
        user_result = supabase.table('users').select('id').eq('auth0_id', request.user['sub']).execute()
        if not user_result.data:
            logger.error(f"User not found in database for Auth0 ID: {request.user['sub']}")
            return jsonify({'error': 'User not found in database'}), 404
            
        user_id = user_result.data[0]['id']
        logger.info(f"Found user ID: {user_id} for Auth0 ID: {request.user['sub']}")
        
        # Get card data from Supabase
        card_result = supabase.table('cards').select('*, decks!inner(*)').eq('id', card_id).execute()
        if not card_result.data:
            logger.error(f"Card not found: {card_id}")
            return jsonify({'error': 'Card not found'}), 404
            
        card = card_result.data[0]
        
        # Verify user has access to the deck
        if card['decks']['user_id'] != user_id:
            logger.error(f"User {user_id} does not have access to card {card_id}")
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Apply SuperMemo2 algorithm
        sm2 = SuperMemo2()
        new_easiness, new_interval, new_repetitions = sm2.calculate_values(
            quality,
            card['easiness'],
            card['interval'],
            card['repetitions']
        )
        
        # Update card in Supabase
        update_data = {
            'interval': new_interval,
            'easiness': new_easiness,
            'repetitions': new_repetitions,
            'next_review': (datetime.utcnow() + timedelta(days=new_interval)).isoformat()
        }
        
        logger.info(f"Updating card {card_id} with new values: {update_data}")
        result = supabase.table('cards').update(update_data).eq('id', card_id).execute()
        updated_card = result.data[0]
        
        # Record the review
        review_data = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'card_id': card_id,
            'quality': quality,
            'time_taken': time_taken,
            'created_at': datetime.utcnow().isoformat(),
            'prev_easiness': card['easiness'],
            'prev_interval': card['interval'],
            'prev_repetitions': card['repetitions'],
            'new_easiness': new_easiness,
            'new_interval': new_interval,
            'new_repetitions': new_repetitions
        }
        
        logger.info(f"Recording review: {review_data}")
        supabase.table('card_reviews').insert(review_data).execute()
        
        return jsonify({
            'cardId': str(updated_card['id']),
            'nextReview': updated_card['next_review'],
            'interval': updated_card['interval'],
            'easiness': updated_card['easiness'],
            'repetitions': updated_card['repetitions']
        })
        
    except Exception as e:
        logger.error(f"Error recording card review: {e}")
        logger.error("Exception details:", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api.route('/api/search-decks', methods=['GET'])
@requires_auth
def search_decks():
    """Search for decks with authentication"""
    try:
        query = request.args.get('q', '')
        logger.info(f"Searching decks with query: {query}")
        
        # Log the entire request object for debugging
        logger.info("Request object: %s", request.__dict__)
        logger.info("Request user object: %s", getattr(request, 'user', None))
        
        # Get user info from the JWT token
        if not hasattr(request, 'user'):
            logger.error("No user information found in request")
            return jsonify({"error": "User information not found"}), 401
            
        user_id = request.user.get('sub')
        if not user_id:
            logger.error("No user ID found in token")
            return jsonify({"error": "User ID not found"}), 401
            
        logger.info(f"Searching decks for user: {user_id}")
        
        # Search decks in Supabase
        result = supabase.table('decks').select('*').ilike('title', f'%{query}%').execute()
        
        if not result.data:
            logger.info("No decks found matching query")
            return jsonify([])
            
        # Format the response
        decks = []
        for deck in result.data:
            deck_data = {
                'id': deck['id'],
                'title': deck['title'],
                'user_id': deck['user_id'],
                'created_at': deck['created_at'],
                'cards': []  # You can populate this with actual cards if needed
            }
            decks.append(deck_data)
            
        logger.info(f"Found {len(decks)} decks matching query")
        return jsonify(decks)
        
    except Exception as e:
        logger.error(f"Error searching decks: {e}")
        logger.error("Exception details:", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api.route('/api/live-decks/<live_deck_id>/parts', methods=['POST'])
@requires_auth
@requires_permission('can_edit')
def add_part_to_live_deck(live_deck_id):
    """Add a new part to a live deck"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        order_index = data.get('order_index')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
            
        # Get the deck ID from the live deck
        live_deck_result = supabase.table('live_decks').select('deck_id').eq('id', live_deck_id).execute()
        if not live_deck_result.data:
            return jsonify({'error': 'Live deck not found'}), 404
            
        deck_id = live_deck_result.data[0]['deck_id']
        
        # Get the next order index if not provided
        if order_index is None:
            last_part = supabase.table('parts').select('order_index').eq('deck_id', deck_id).order('order_index', desc=True).limit(1).execute()
            order_index = (last_part.data[0]['order_index'] + 1) if last_part.data else 0
            
        part_data = {
            'id': str(uuid.uuid4()),
            'deck_id': deck_id,
            'title': title,
            'description': description,
            'order_index': order_index,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('parts').insert(part_data).execute()
        
        return jsonify({
            'id': str(result.data[0]['id']),
            'title': result.data[0]['title'],
            'description': result.data[0]['description'],
            'order_index': result.data[0]['order_index']
        })
        
    except Exception as e:
        logger.error(f"Error adding part: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/parts/<part_id>/chapters', methods=['POST'])
@requires_auth
@requires_permission('can_edit')
def add_chapter_to_part(part_id):
    """Add a new chapter to a part"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        order_index = data.get('order_index')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
            
        # Get the next order index if not provided
        if order_index is None:
            last_chapter = supabase.table('chapters').select('order_index').eq('part_id', part_id).order('order_index', desc=True).limit(1).execute()
            order_index = (last_chapter.data[0]['order_index'] + 1) if last_chapter.data else 0
            
        chapter_data = {
            'id': str(uuid.uuid4()),
            'part_id': part_id,
            'title': title,
            'description': description,
            'order_index': order_index,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('chapters').insert(chapter_data).execute()
        
        return jsonify({
            'id': str(result.data[0]['id']),
            'title': result.data[0]['title'],
            'description': result.data[0]['description'],
            'order_index': result.data[0]['order_index']
        })
        
    except Exception as e:
        logger.error(f"Error adding chapter: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/chapters/<chapter_id>/topics', methods=['POST'])
@requires_auth
@requires_permission('can_edit')
def add_topic_to_chapter(chapter_id):
    """Add a new topic to a chapter"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        order_index = data.get('order_index')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
            
        # Get the next order index if not provided
        if order_index is None:
            last_topic = supabase.table('topics').select('order_index').eq('chapter_id', chapter_id).order('order_index', desc=True).limit(1).execute()
            order_index = (last_topic.data[0]['order_index'] + 1) if last_topic.data else 0
            
        topic_data = {
            'id': str(uuid.uuid4()),
            'chapter_id': chapter_id,
            'title': title,
            'description': description,
            'order_index': order_index,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('topics').insert(topic_data).execute()
        
        return jsonify({
            'id': str(result.data[0]['id']),
            'title': result.data[0]['title'],
            'description': result.data[0]['description'],
            'order_index': result.data[0]['order_index']
        })
        
    except Exception as e:
        logger.error(f"Error adding topic: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/topics/<topic_id>/cards', methods=['POST'])
@requires_auth
@requires_permission('can_edit')
def add_card_to_topic(topic_id):
    """Add a new card to a topic"""
    try:
        data = request.get_json()
        front = data.get('front')
        back = data.get('back')
        card_type = data.get('card_type', 'basic')
        media_urls = data.get('media_urls', [])
        tags = data.get('tags', [])
        difficulty = data.get('difficulty', 'medium')
        notes = data.get('notes')
        
        if not all([front, back]):
            return jsonify({'error': 'front and back are required'}), 400
            
        card_data = {
            'id': str(uuid.uuid4()),
            'topic_id': topic_id,
            'front': front,
            'back': back,
            'card_type': card_type,
            'media_urls': media_urls,
            'tags': tags,
            'difficulty': difficulty,
            'notes': notes,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('cards').insert(card_data).execute()
        
        return jsonify({
            'id': str(result.data[0]['id']),
            'front': result.data[0]['front'],
            'back': result.data[0]['back'],
            'card_type': result.data[0]['card_type'],
            'media_urls': result.data[0]['media_urls'],
            'tags': result.data[0]['tags'],
            'difficulty': result.data[0]['difficulty'],
            'notes': result.data[0]['notes']
        })
        
    except Exception as e:
        logger.error(f"Error adding card: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks/<deck_id>/cards', methods=['GET'])
@requires_auth
@requires_permission(Permission.READ)
def get_deck_cards(deck_id):
    """Get all cards for a specific deck with their context"""
    try:
        logger.info(f"Fetching cards for deck {deck_id}")
        logger.info(f"User ID: {request.user['sub']}")
        
        # First, verify the deck exists and user has access
        deck_result = supabase.table('decks').select('*').eq('id', deck_id).execute()
        if not deck_result.data:
            logger.error(f"Deck {deck_id} not found")
            return jsonify({"error": "Deck not found"}), 404
            
        deck = deck_result.data[0]
        logger.info(f"Found deck: {deck['title']}")
        
        # Check if user has access to this deck
        user_role = get_user_role(request.user['sub'], ResourceType.DECK, deck_id)
        if not user_role:
            logger.error(f"User {request.user['sub']} does not have access to deck {deck_id}")
            return jsonify({"error": "Unauthorized access to deck"}), 403
            
        logger.info(f"User role for deck: {user_role.value}")
        
        # Get all parts for the deck
        parts_result = supabase.table('parts').select('*').eq('deck_id', deck_id).order('order_index').execute()
        if not parts_result.data:
            logger.info(f"No parts found for deck {deck_id}")
            return jsonify([])
            
        # Initialize the response structure
        deck_structure = {
            'id': deck_id,
            'title': deck['title'],
            'parts': []
        }
        
        # For each part, get its chapters
        for part in parts_result.data:
            part_data = {
                'id': part['id'],
                'title': part['title'],
                'chapters': []
            }
            
            # Get chapters for this part
            chapters_result = supabase.table('chapters').select('*').eq('part_id', part['id']).order('order_index').execute()
            
            for chapter in chapters_result.data:
                chapter_data = {
                    'id': chapter['id'],
                    'title': chapter['title'],
                    'topics': []
                }
                
                # Get topics for this chapter
                topics_result = supabase.table('topics').select('*').eq('chapter_id', chapter['id']).order('order_index').execute()
                
                for topic in topics_result.data:
                    topic_data = {
                        'id': topic['id'],
                        'title': topic['title'],
                        'cards': []
                    }
                    
                    # Get cards for this topic
                    cards_result = supabase.table('cards').select('*').eq('topic_id', topic['id']).execute()
                    
                    for card in cards_result.data:
                        card_data = {
                            'id': card['id'],
                            'front': card['front'],
                            'back': card['back'],
                            'created_at': card['created_at']
                        }
                        topic_data['cards'].append(card_data)
                    
                    chapter_data['topics'].append(topic_data)
                
                part_data['chapters'].append(chapter_data)
            
            deck_structure['parts'].append(part_data)
            
        logger.info(f"Successfully fetched deck structure with {len(deck_structure['parts'])} parts")
        return jsonify(deck_structure)
        
    except Exception as e:
        logger.error(f"Error fetching deck cards: {str(e)}")
        logger.error("Exception details:", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api.route('/api/course-materials', methods=['POST'])
@requires_auth
def upload_course_material():
    """Upload a new course material"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Get additional metadata from form data
        title = request.form.get('title')
        description = request.form.get('description')
        material_type = request.form.get('material_type')
        tags = request.form.getlist('tags')
        metadata = json.loads(request.form.get('metadata', '{}'))
        
        if not all([title, material_type]):
            return jsonify({'error': 'title and material_type are required'}), 400
            
        # TODO: Implement file upload to storage (e.g., S3, Supabase Storage)
        # For now, we'll just store the file path
        file_path = f"course_materials/{request.user['sub']}/{file.filename}"
        
        material_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'title': title,
            'description': description,
            'material_type': material_type,
            'file_path': file_path,
            'file_size': 0,  # TODO: Get actual file size
            'mime_type': file.content_type,
            'tags': tags,
            'metadata': metadata
        }
        
        result = supabase.table('course_materials').insert(material_data).execute()
        
        return jsonify(result.data[0])
        
    except Exception as e:
        logger.error(f"Error uploading course material: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/course-materials', methods=['GET'])
@requires_auth
def get_course_materials():
    """Get all course materials for the current user"""
    try:
        result = supabase.table('course_materials').select('*').eq(
            'user_id', request.user['sub']
        ).execute()
        
        return jsonify(result.data)
        
    except Exception as e:
        logger.error(f"Error getting course materials: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/course-materials/<material_id>', methods=['DELETE'])
@requires_auth
def delete_course_material(material_id):
    """Delete a course material"""
    try:
        # Check if user owns the material
        material_result = supabase.table('course_materials').select('*').eq('id', material_id).execute()
        if not material_result.data:
            return jsonify({'error': 'Material not found'}), 404
            
        material = material_result.data[0]
        if material['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Delete the material
        supabase.table('course_materials').delete().eq('id', material_id).execute()
        
        return jsonify({'message': 'Material deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting course material: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/study-resources', methods=['POST'])
@requires_auth
def create_study_resource():
    """Create a new study resource"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        resource_type = data.get('resource_type')
        source_material_id = data.get('source_material_id')
        tags = data.get('tags', [])
        metadata = data.get('metadata', {})
        
        if not all([title, content, resource_type]):
            return jsonify({'error': 'title, content, and resource_type are required'}), 400
            
        # If source_material_id is provided, verify it exists and user owns it
        if source_material_id:
            material_result = supabase.table('course_materials').select('*').eq('id', source_material_id).execute()
            if not material_result.data:
                return jsonify({'error': 'Source material not found'}), 404
                
            material = material_result.data[0]
            if material['user_id'] != request.user['sub']:
                return jsonify({'error': 'Unauthorized'}), 403
        
        resource_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'title': title,
            'content': content,
            'resource_type': resource_type,
            'source_material_id': source_material_id,
            'tags': tags,
            'metadata': metadata
        }
        
        result = supabase.table('study_resources').insert(resource_data).execute()
        
        return jsonify(result.data[0])
        
    except Exception as e:
        logger.error(f"Error creating study resource: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/study-resources', methods=['GET'])
@requires_auth
def get_study_resources():
    """Get all study resources for the current user"""
    try:
        result = supabase.table('study_resources').select('*').eq(
            'user_id', request.user['sub']
        ).execute()
        
        return jsonify(result.data)
        
    except Exception as e:
        logger.error(f"Error getting study resources: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/study-resources/<resource_id>', methods=['DELETE'])
@requires_auth
def delete_study_resource(resource_id):
    """Delete a study resource"""
    try:
        # Check if user owns the resource
        resource_result = supabase.table('study_resources').select('*').eq('id', resource_id).execute()
        if not resource_result.data:
            return jsonify({'error': 'Resource not found'}), 404
            
        resource = resource_result.data[0]
        if resource['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Delete the resource
        supabase.table('study_resources').delete().eq('id', resource_id).execute()
        
        return jsonify({'message': 'Resource deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting study resource: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/generate-resource', methods=['POST'])
@requires_auth
def generate_study_resource():
    """Generate a study resource from course material using GPT"""
    try:
        data = request.get_json()
        material_id = data.get('material_id')
        generation_type = data.get('generation_type')
        prompt = data.get('prompt')
        
        if not all([material_id, generation_type, prompt]):
            return jsonify({'error': 'material_id, generation_type, and prompt are required'}), 400
            
        # Verify material exists and user owns it
        material_result = supabase.table('course_materials').select('*').eq('id', material_id).execute()
        if not material_result.data:
            return jsonify({'error': 'Material not found'}), 404
            
        material = material_result.data[0]
        if material['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Create a study resource first
        resource_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'title': f"Generated {generation_type} for {material['title']}",
            'content': None,  # Will be updated after generation
            'resource_type': generation_type,
            'source_material_id': material_id
        }
        
        resource_result = supabase.table('study_resources').insert(resource_data).execute()
        resource = resource_result.data[0]
        
        # Create generation record
        generation_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'resource_id': resource['id'],
            'status': 'pending',
            'generation_type': generation_type,
            'prompt': prompt
        }
        
        generation_result = supabase.table('resource_generations').insert(generation_data).execute()
        generation = generation_result.data[0]
        
        # TODO: Implement actual GPT generation
        # For now, return a mock response
        return jsonify({
            'resource': resource,
            'generation': generation,
            'message': 'Generation started'
        })
        
    except Exception as e:
        logger.error(f"Error generating study resource: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/generations/<generation_id>', methods=['GET'])
@requires_auth
def get_generation_status(generation_id):
    """Get the status of a resource generation"""
    try:
        result = supabase.table('resource_generations').select('*').eq('id', generation_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Generation not found'}), 404
            
        generation = result.data[0]
        if generation['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        return jsonify(generation)
        
    except Exception as e:
        logger.error(f"Error getting generation status: {e}")
        return jsonify({"error": str(e)}), 500

# Create subscription routes blueprint
subscription_routes = Blueprint('subscription_routes', __name__)

# Register subscription routes with the main api blueprint
api.register_blueprint(subscription_routes, url_prefix='/subscriptions')

# Subscription routes
@subscription_routes.route('/', methods=['POST'])
@requires_auth
def create_subscription():
    """Create a new subscription"""
    try:
        data = request.get_json()
        tier = data.get('tier')
        payment_method_id = data.get('payment_method_id')
        
        if not tier or not payment_method_id:
            return jsonify({"error": "Missing required fields"}), 400
            
        try:
            tier_enum = SubscriptionTier(tier)
        except ValueError:
            return jsonify({"error": "Invalid subscription tier"}), 400
            
        result = subscription_manager.create_subscription(
            user_id=request.user['sub'],
            tier=tier_enum,
            payment_method_id=payment_method_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        return jsonify({"error": "Failed to create subscription"}), 500

@subscription_routes.route('/<subscription_id>', methods=['PUT'])
@requires_auth
def update_subscription(subscription_id):
    """Update an existing subscription"""
    try:
        data = request.get_json()
        tier = data.get('tier')
        
        if not tier:
            return jsonify({"error": "Missing tier"}), 400
            
        try:
            tier_enum = SubscriptionTier(tier)
        except ValueError:
            return jsonify({"error": "Invalid subscription tier"}), 400
            
        result = subscription_manager.update_subscription(
            subscription_id=subscription_id,
            tier=tier_enum
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        return jsonify({"error": "Failed to update subscription"}), 500

@subscription_routes.route('/<subscription_id>', methods=['DELETE'])
@requires_auth
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        result = subscription_manager.cancel_subscription(subscription_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        return jsonify({"error": "Failed to cancel subscription"}), 500

@subscription_routes.route('/current', methods=['GET'])
@requires_auth
def get_current_subscription():
    """Get user's current subscription"""
    try:
        subscription = subscription_manager.get_subscription(request.user['sub'])
        if subscription:
            return jsonify(subscription)
        return jsonify({"tier": "free"})
        
    except Exception as e:
        logger.error(f"Error getting current subscription: {e}")
        return jsonify({"error": "Failed to get subscription"}), 500

@subscription_routes.route('/features', methods=['GET'])
@requires_auth
def get_subscription_features():
    """Get available features for user's subscription tier"""
    try:
        tier = subscription_manager.get_subscription_tier(request.user['sub'])
        features = subscription_manager.has_feature_access(request.user['sub'])
        return jsonify({
            "tier": tier.value,
            "features": features
        })
        
    except Exception as e:
        logger.error(f"Error getting subscription features: {e}")
        return jsonify({"error": "Failed to get subscription features"}), 500

@subscription_routes.route('/webhook', methods=['POST'])
def handle_stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        event = request.get_json()
        result = subscription_manager.handle_webhook(event)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return jsonify({"error": "Failed to handle webhook"}), 500 