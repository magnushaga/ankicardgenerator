from flask import Blueprint, request, jsonify
from anthropic import Anthropic
import os
import uuid
import json
from datetime import datetime, timedelta
from models import (
    User, Textbook, Part, Chapter, Topic, Deck, Card,
    StudySession, CardReview
)
from supabase import create_client
from dotenv import load_dotenv
import logging
from functools import wraps
import jwt
from jwt.algorithms import RSAAlgorithm
from jwt_verify import requires_scope
from permissions import requires_permission, requires_ownership
from supabase_config import supabase
from auth_decorators import requires_auth  # Import the auth decorator from the new module
from study.supermemo2 import SuperMemo2

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
def delete_deck(deck_id):
    """Delete a deck (if user owns it)"""
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
@requires_permission('can_share')
def add_collaborator(deck_id):
    """Add a collaborator to a deck"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        role = data.get('role', 'viewer')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
            
        # Set permissions based on role
        permissions = {
            'owner': {'can_edit': True, 'can_share': True, 'can_delete': True},
            'editor': {'can_edit': True, 'can_share': True, 'can_delete': False},
            'viewer': {'can_edit': False, 'can_share': False, 'can_delete': False}
        }
        
        if role not in permissions:
            return jsonify({'error': 'Invalid role'}), 400
            
        collaboration_data = {
            'id': str(uuid.uuid4()),
            'deck_id': deck_id,
            'user_id': user_id,
            'role': role,
            **permissions[role],
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('deck_collaborations').insert(collaboration_data).execute()
        
        return jsonify({
            'id': str(result.data[0]['id']),
            'role': result.data[0]['role']
        })
        
    except Exception as e:
        logger.error(f"Error adding collaborator: {e}")
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
def generate_textbook_structure():
    """Generate a structured outline for a textbook"""
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    test_mode = data.get('test_mode', False)
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400

    analyzer = TextbookAnalyzer()
    try:
        structure = analyzer.generate_structure(textbook_name, test_mode)
        
        # Create database entries in Supabase
        textbook_data = {
            'id': str(uuid.uuid4()),
            'title': textbook_name,
            'author': 'Generated',
            'subject': 'general',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('textbooks').insert(textbook_data).execute()
        textbook_id = result.data[0]['id']
        
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
        
        return jsonify(structure)
        
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
            return jsonify({'error': 'deck_id is required'}), 400
            
        # Create study session
        session_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'deck_id': deck_id,
            'started_at': datetime.utcnow().isoformat(),
            'ended_at': None,
            'cards_studied': 0,
            'correct_answers': 0
        }
        
        result = supabase.table('study_sessions').insert(session_data).execute()
        
        return jsonify({
            'sessionId': str(result.data[0]['id']),
            'deckId': str(result.data[0]['deck_id']),
            'startedAt': result.data[0]['started_at']
        })
        
    except Exception as e:
        logger.error(f"Error creating study session: {e}")
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
        # First verify the deck exists and user has access
        deck_result = supabase.table('decks').select('*').eq('id', deck_id).execute()
        if not deck_result.data:
            return jsonify({'error': 'Deck not found'}), 404
            
        deck = deck_result.data[0]
        if deck['user_id'] != request.user['sub']:
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
            
        return jsonify(cards)
        
    except Exception as e:
        logger.error(f"Error getting due cards: {e}")
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
            return jsonify({'error': 'card_id, session_id, and quality are required'}), 400
        
        # Get card data from Supabase
        card_result = supabase.table('cards').select('*').eq('id', card_id).execute()
        if not card_result.data:
            return jsonify({'error': 'Card not found'}), 404
            
        card = card_result.data[0]
        
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
def get_deck_cards(deck_id):
    """Get all cards for a specific deck with their context"""
    try:
        logger.info(f"Fetching cards for deck {deck_id}")
        
        # First, verify the deck exists and user has access
        deck_result = supabase.table('decks').select('*').eq('id', deck_id).execute()
        if not deck_result.data:
            logger.error(f"Deck {deck_id} not found")
            return jsonify({"error": "Deck not found"}), 404
            
        deck = deck_result.data[0]
        
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