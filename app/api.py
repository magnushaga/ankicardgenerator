from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import json
from anthropic import Anthropic
from datetime import datetime
from models import db, Textbook, Part, Chapter, Topic, Deck, Card, StudySession, CardReview
from supermemo2 import update_card_review

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
                print(f"Error initializing Anthropic client: {e}")
                raise

    def analyze_textbook(self, textbook_name, client=None):
        """
        Use Claude API to analyze a textbook's title and determine its subject area,
        specialized formatting needs, and appropriate focus areas.
        """
        print(f"Analyzing subject area for: {textbook_name}")
        
        # Use self.client if no client is provided
        if client is None:
            client = self.client
        
        # Ensure we have a client
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
            
            # Remove any markdown code blocks if present
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3]
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3]
                
            analysis = json.loads(content)
            print(f"Successfully analyzed textbook: {textbook_name}")
            return analysis
            
        except Exception as e:
            print(f"Error analyzing textbook: {e}")
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
            # Create the structure prompt
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
                    }},
                    {{
                        "title": "Part II: Advanced Topics",
                        "chapters": [
                            {{
                                "title": "Chapter 3: Advanced Features",
                                "topics": [...]
                            }},
                            {{
                                "title": "Chapter 4: Best Practices",
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

            # Make API call with updated system prompt
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
            
            # Extract and parse the JSON from the response
            content = response.content[0].text
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3]
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3]
            
            structure = json.loads(content)

            # Fix and verify formatting
            chapter_counter = 1  # Keep track of chapter numbers across all parts
            for i, part in enumerate(structure['parts']):
                # Fix part numbering
                if not part['title'].startswith(f"Part {self._to_roman(i+1)}:"):
                    part['title'] = f"Part {self._to_roman(i+1)}: {part['title'].split(':', 1)[-1].strip()}"
                
                # Fix chapter numbering
                for chapter in part['chapters']:
                    # Remove any double chapter numbering
                    if "Chapter" in chapter['title'].split(":", 1)[-1]:
                        # Extract the actual title after any chapter numbers
                        actual_title = chapter['title'].split(":")[-1].strip()
                        chapter['title'] = f"Chapter {chapter_counter}: {actual_title}"
                    else:
                        # Just ensure the chapter number is correct
                        chapter['title'] = f"Chapter {chapter_counter}: {chapter['title'].split(':', 1)[-1].strip()}"
                    
                    chapter_counter += 1
                    
                    # Ensure each topic has required fields
                    for topic in chapter['topics']:
                        if 'requires_latex' not in topic:
                            topic['requires_latex'] = False
                        if 'latex_type' not in topic:
                            topic['latex_type'] = 'none'

            return structure

        except Exception as e:
            print(f"Error generating structure: {e}")
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
            
            # Remove markdown code blocks if present
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3]
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3]
            
            return json.loads(content)

        except Exception as e:
            print(f"Error generating cards: {e}")
            # Return fallback cards for test mode
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

@api.route('/')
def test_route():
    return jsonify({'message': 'Flask backend is working!'})

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
        # Return default analysis as fallback
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
    test_mode = data.get('test_mode', False)  # New parameter
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400

    analyzer = TextbookAnalyzer()
    try:
        structure = analyzer.generate_structure(textbook_name, test_mode)
        
        # Create database entries
        textbook = Textbook(
            id=uuid.uuid4(),
            title=textbook_name,
            author="Generated",
            subject="general"
        )
        db.session.add(textbook)
        
        for part_idx, part_data in enumerate(structure["parts"]):
            part = Part(
                id=uuid.uuid4(),
                textbook_id=textbook.id,
                title=part_data["title"],
                order_index=part_idx
            )
            db.session.add(part)
            
            for chapter_idx, chapter_data in enumerate(part_data["chapters"]):
                chapter = Chapter(
                    id=uuid.uuid4(),
                    part_id=part.id,
                    title=chapter_data["title"],
                    order_index=chapter_idx
                )
                db.session.add(chapter)
                
                for topic_idx, topic_data in enumerate(chapter_data["topics"]):
                    topic = Topic(
                        id=uuid.uuid4(),
                        chapter_id=chapter.id,
                        title=topic_data["title"],
                        comment=topic_data["comment"],
                        order_index=topic_idx
                    )
                    db.session.add(topic)
        
        db.session.commit()
        return jsonify(structure)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api.route('/api/generate-cards', methods=['POST'])
def generate_cards():
    """Generate flashcards for a specific topic"""
    data = request.get_json()
    topic_id = data.get('topic_id')
    deck_id = data.get('deck_id')
    card_count = data.get('card_count', 5)
    test_mode = data.get('test_mode', False)  # New parameter
    
    if not all([topic_id, deck_id]):
        return jsonify({'error': 'topic_id and deck_id are required'}), 400
        
    # Override card count in test mode
    if test_mode:
        card_count = min(card_count, 3)  # Limit to maximum 3 cards in test mode

    try:
        topic = Topic.query.get_or_404(topic_id)
        chapter = Chapter.query.get_or_404(topic.chapter_id)
        part = Part.query.get_or_404(chapter.part_id)
        textbook = Textbook.query.get_or_404(part.textbook_id)
        
        # Generate cards prompt
        cards_prompt = f"""
        Create {card_count} {'simple test' if test_mode else ''} Anki flashcards for the topic "{topic.title}" from the textbook "{textbook.title}".
        
        TOPIC CONTEXT: {topic.comment}
        CHAPTER: {chapter.title}
        PART: {part.title}
        
        {'Keep the cards basic and straightforward for testing purposes.' if test_mode else ''}
        
        Format your response as a JSON array of card objects:
        [
            {{
                "front": "[Clear, specific question]",
                "back": "[Comprehensive answer with appropriate notation]"
            }}
        ]
        """
        
        content = get_anthropic_completion(cards_prompt, max_tokens=4000, temperature=0.3)
        
        # Clean up JSON string
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3]
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3]
            
        cards_data = json.loads(content)
        
        # Create cards in database
        created_cards = []
        for card_data in cards_data:
            card = Card(
                id=uuid.uuid4(),
                deck_id=deck_id,
                topic_id=topic_id,
                front=card_data["front"],
                back=card_data["back"]
            )
            db.session.add(card)
            created_cards.append({
                "id": str(card.id),
                "front": card.front,
                "back": card.back
            })
        
        db.session.commit()
        return jsonify(created_cards)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api.route('/api/review-card', methods=['POST'])
def review_card():
    """Record a card review with SuperMemo2 algorithm"""
    data = request.get_json()
    card_id = data.get('card_id')
    session_id = data.get('session_id')
    quality = data.get('quality')  # 0-5 rating
    time_taken = data.get('time_taken')  # milliseconds
    
    if not all([card_id, session_id, quality is not None]):
        return jsonify({'error': 'card_id, session_id, and quality are required'}), 400
        
    try:
        card = Card.query.get_or_404(card_id)
        
        # Update card using SuperMemo2
        prev_values, new_values = update_card_review(card, quality)
        
        # Record the review
        review = CardReview(
            id=uuid.uuid4(),
            session_id=session_id,
            card_id=card_id,
            quality=quality,
            time_taken=time_taken,
            prev_easiness=prev_values['easiness'],
            prev_interval=prev_values['interval'],
            prev_repetitions=prev_values['repetitions'],
            new_easiness=new_values['easiness'],
            new_interval=new_values['interval'],
            new_repetitions=new_values['repetitions']
        )
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'cardId': str(card.id),
            'nextReview': card.next_review.isoformat(),
            'interval': card.interval,
            'easiness': card.easiness,
            'repetitions': card.repetitions
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api.route('/api/study-sessions', methods=['POST'])
def create_study_session():
    """Create a new study session"""
    data = request.get_json()
    deck_id = data.get('deck_id')
    
    if not deck_id:
        return jsonify({'error': 'deck_id is required'}), 400
        
    try:
        session = StudySession(
            id=uuid.uuid4(),
            deck_id=deck_id
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'sessionId': str(session.id),
            'deckId': str(session.deck_id),
            'startedAt': session.started_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api.route('/api/study-sessions/<session_id>', methods=['PUT'])
def end_study_session(session_id):
    """End a study session"""
    try:
        session = StudySession.query.get_or_404(session_id)
        session.ended_at = datetime.utcnow()
        db.session.commit()
        
        # Calculate statistics
        reviews = CardReview.query.filter_by(session_id=session_id).all()
        total_cards = len(reviews)
        total_time = sum(r.time_taken for r in reviews if r.time_taken)
        avg_quality = sum(r.quality for r in reviews) / total_cards if total_cards else 0
        
        return jsonify({
            'sessionId': str(session.id),
            'startedAt': session.started_at.isoformat(),
            'endedAt': session.ended_at.isoformat(),
            'statistics': {
                'totalCards': total_cards,
                'totalTimeMs': total_time,
                'averageQuality': avg_quality
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api.route('/api/decks/<deck_id>/due-cards', methods=['GET'])
def get_due_cards(deck_id):
    """Get cards that are due for review"""
    try:
        now = datetime.utcnow()
        cards = Card.query.filter(
            Card.deck_id == deck_id,
            Card.next_review <= now
        ).all()
        
        return jsonify([{
            'id': str(card.id),
            'front': card.front,
            'back': card.back,
            'nextReview': card.next_review.isoformat(),
            'interval': card.interval,
            'easiness': card.easiness,
            'repetitions': card.repetitions
        } for card in cards])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500