from flask import Blueprint, request, jsonify
from anthropic import Anthropic
import os
import uuid
import json
from datetime import datetime
from models import (
    User, Textbook, Part, Chapter, Topic, Deck, Card,
    StudySession, CardReview
)
from supabase_config import supabase
import logging
from functools import wraps
import jwt
from jwt.algorithms import RSAAlgorithm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401
        
        try:
            token = auth_header.split(' ')[1]
            # Verify the token with Auth0
            jwks_url = f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/jwks.json'
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"]
            )
            request.user = payload
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
    return decorated

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

@api.route('/api/review-card', methods=['POST'])
def review_card():
    """Record a card review with SuperMemo2 algorithm"""
    data = request.get_json()
    card_id = data.get('card_id')
    session_id = data.get('session_id')
    quality = data.get('quality')
    time_taken = data.get('time_taken')
    
    if not all([card_id, session_id, quality is not None]):
        return jsonify({'error': 'card_id, session_id, and quality are required'}), 400
        
    try:
        # Get card data from Supabase
        card_result = supabase.table('cards').select('*').eq('id', card_id).execute()
        if not card_result.data:
            return jsonify({'error': 'Card not found'}), 404
            
        card = card_result.data[0]
        
        # Update card using SuperMemo2 algorithm
        # This is a simplified version - you might want to implement the full algorithm
        new_interval = card['interval'] * (1 + (quality - 3) * 0.1)
        new_easiness = max(1.3, card['easiness'] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        new_repetitions = card['repetitions'] + 1
        
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

@api.route('/api/study-sessions', methods=['POST'])
def create_study_session():
    """Create a new study session"""
    data = request.get_json()
    deck_id = data.get('deck_id')
    
    if not deck_id:
        return jsonify({'error': 'deck_id is required'}), 400
        
    try:
        session_data = {
            'id': str(uuid.uuid4()),
            'deck_id': deck_id,
            'started_at': datetime.utcnow().isoformat()
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
def end_study_session(session_id):
    """End a study session"""
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
def get_due_cards(deck_id):
    """Get cards that are due for review"""
    try:
        now = datetime.utcnow().isoformat()
        result = supabase.table('cards').select('*').eq('deck_id', deck_id).lte('next_review', now).execute()
        
        return jsonify([{
            'id': str(card['id']),
            'front': card['front'],
            'back': card['back'],
            'nextReview': card['next_review'],
            'interval': card['interval'],
            'easiness': card['easiness'],
            'repetitions': card['repetitions']
        } for card in result.data])
        
    except Exception as e:
        logger.error(f"Error getting due cards: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/search-decks', methods=['GET'])
@requires_auth
def search_decks():
    """Search for decks by title and return with cards"""
    query = request.args.get('q', '')
    
    try:
        # Get user info from Supabase
        user_result = supabase.table('users').select('*').eq('auth0_id', request.user['sub']).execute()
        
        if not user_result.data or len(user_result.data) == 0:
            return jsonify({"error": "User not found"}), 404
            
        user = user_result.data[0]
        
        # Search for decks
        decks_result = supabase.table('decks').select('*').ilike('title', f'%{query}%').execute()
        
        if not decks_result.data:
            return jsonify([])
            
        # Get cards for each deck
        decks = []
        for deck in decks_result.data:
            cards_result = supabase.table('cards').select('*').eq('deck_id', deck['id']).execute()
            cards = []
            
            if cards_result.data:
                for card in cards_result.data:
                    # Get topic info for each card
                    topic_result = supabase.table('topics').select('*').eq('id', card['topic_id']).execute()
                    topic = topic_result.data[0] if topic_result.data else None
                    
                    # Get chapter info
                    chapter_result = supabase.table('chapters').select('*').eq('id', topic['chapter_id']).execute() if topic else None
                    chapter = chapter_result.data[0] if chapter_result and chapter_result.data else None
                    
                    # Get part info
                    part_result = supabase.table('parts').select('*').eq('id', chapter['part_id']).execute() if chapter else None
                    part = part_result.data[0] if part_result and part_result.data else None
                    
                    cards.append({
                        'id': card['id'],
                        'front': card['front'],
                        'back': card['back'],
                        'partTitle': part['title'] if part else None,
                        'chapterTitle': chapter['title'] if chapter else None,
                        'topicTitle': topic['title'] if topic else None
                    })
            
            decks.append({
                'id': deck['id'],
                'title': deck['title'],
                'cards': cards
            })
        
        return jsonify(decks)
        
    except Exception as e:
        logger.error(f"Error searching decks: {str(e)}")
        return jsonify({"error": str(e)}), 500 