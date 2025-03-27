from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import json
import anthropic
from datetime import datetime
from models import db, Textbook, Part, Chapter, Topic, Deck, Card, StudySession, CardReview
from supermemo2 import update_card_review

api = Blueprint('api', __name__)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your-api-key-here')

def get_anthropic_completion(prompt, max_tokens=1000, temperature=0.2):
    """Helper function to get completions from Anthropic's API"""
    import httpx
    
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "content-type": "application/json",
    }
    
    data = {
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant: ",
        "model": "claude-2",
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature,
    }
    
    response = httpx.post(
        "https://api.anthropic.com/v1/complete",
        headers=headers,
        json=data,
        timeout=30.0
    )
    
    if response.status_code != 200:
        raise Exception(f"Error from Anthropic API: {response.text}")
        
    return response.json()["completion"]

@api.route('/')
def test_route():
    return jsonify({'message': 'Flask backend is working!'})

@api.route('/api/analyze-course', methods=['POST'])
def analyze_course():
    """Analyze a course's title to determine subject area and requirements"""
    data = request.get_json()
    course_name = data.get('course_name')
    
    if not course_name:
        return jsonify({'error': 'course_name is required'}), 400

    analysis_prompt = f"""
    Based solely on this course title: "{course_name}", please:
    
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
        content = get_anthropic_completion(analysis_prompt)
        
        # Remove any markdown code blocks if present
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3]
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3]
            
        analysis = json.loads(content)
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
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400

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
        content = get_anthropic_completion(analysis_prompt)
        
        # Remove any markdown code blocks if present
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3]
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3]
            
        analysis = json.loads(content)
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

@api.route('/api/generate-course-structure', methods=['POST'])
def generate_course_structure():
    """Generate a structured outline for a course"""
    data = request.get_json()
    course_name = data.get('course_name')
    
    if not course_name:
        return jsonify({'error': 'course_name is required'}), 400

    # First get the analysis
    try:
        analysis_response = get_anthropic_completion(
            f'Analyze this course title: "{course_name}" and return a JSON with primary_subject, subfields, and requirements.'
        )
        analysis = json.loads(analysis_response)
    except Exception as e:
        analysis = {
            "primary_subject": "general",
            "subfields": [],
            "requires_math": True
        }

    # Generate structure prompt based on analysis
    structure_prompt = f"""
    You are an expert in course organization. Please create a comprehensive nested structure for the course "{course_name}".
    
    Based on my analysis, this appears to be a {analysis["primary_subject"]} course
    """
    
    if analysis.get("subfields"):
        subfields = ", ".join(analysis["subfields"])
        structure_prompt += f" with focus on {subfields}"
    
    structure_prompt += ".\n\n"
    
    # Add subject-specific instructions
    if analysis.get("requires_math") or analysis["primary_subject"] in ["mathematics", "physics"]:
        structure_prompt += """
        For this mathematics-focused content:
        - Each topic includes progression from definitions to theorems to applications
        - Include problem-solving strategies and proof techniques
        - Note where specific mathematical tools are essential
        """

    # Add format requirements
    structure_prompt += """
    Format your response as a JSON object that follows this structure exactly:
    
    {
        "topics": [
            {
                "title": "[Topic Title]",
                "comment": "[Focus/importance of this topic]",
                "card_count": 5
            }
        ]
    }
    """
    
    try:
        content = get_anthropic_completion(structure_prompt, max_tokens=4000, temperature=0.3)
        
        # Clean up JSON string
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3]
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3]
            
        structure = json.loads(content)
        
        # Create database entries
        course = Course(
            id=uuid.uuid4(),
            title=course_name,
            user_id=1,  # Assuming a default user for now
            description=analysis["primary_subject"]
        )
        db.session.add(course)
        
        for topic_idx, topic_data in enumerate(structure["topics"]):
            topic = Topic(
                id=uuid.uuid4(),
                course_id=course.id,
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
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    test_mode = data.get('test_mode', False)  # New parameter
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400

    # First get the analysis
    try:
        analysis_response = get_anthropic_completion(
            f'Analyze this textbook title: "{textbook_name}" and return a JSON with primary_subject, subfields, and requirements.'
        )
        analysis = json.loads(analysis_response)
    except Exception as e:
        analysis = {
            "primary_subject": "general",
            "subfields": [],
            "requires_math": True
        }

    # Modify structure prompt based on test mode
    structure_prompt = f"""
    You are an expert in textbook organization. Please create a {'simplified test version with 1-2 topics per chapter' if test_mode else 'comprehensive'} nested structure for the textbook "{textbook_name}".
    
    Based on my analysis, this appears to be a {analysis["primary_subject"]} textbook
    """
    
    if analysis.get("subfields"):
        subfields = ", ".join(analysis["subfields"])
        structure_prompt += f" with focus on {subfields}"
    
    structure_prompt += ".\n\n"
    
    # Add subject-specific instructions
    if analysis.get("requires_math") or analysis["primary_subject"] in ["mathematics", "physics"]:
        structure_prompt += """
        For this mathematics-focused content:
        - Each topic includes progression from definitions to theorems to applications
        - Include problem-solving strategies and proof techniques
        - Note where specific mathematical tools are essential
        """

    # Modify format requirements for test mode
    if test_mode:
        structure_prompt += """
        For test mode, please create a minimal structure with:
        - 1 part
        - 2 chapters
        - 1-2 topics per chapter
        - 2-3 cards per topic
        """

    # Add format requirements
    structure_prompt += """
    Format your response as a JSON object that follows this structure exactly:
    
    {
        "parts": [
            {
                "title": "Part I: [Part Title]",
                "chapters": [
                    {
                        "title": "Chapter 1: [Chapter Title]",
                        "topics": [
                            {
                                "title": "[Topic Title]",
                                "comment": "[Focus/importance of this topic]",
                                "card_count": 5
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    
    try:
        content = get_anthropic_completion(structure_prompt, max_tokens=4000, temperature=0.3)
        
        # Clean up JSON string
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3]
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3]
            
        structure = json.loads(content)
        
        # Create database entries
        textbook = Textbook(
            id=uuid.uuid4(),
            title=textbook_name,
            author="Generated",
            subject=analysis["primary_subject"]
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

@api.route('/api/generate-course-cards', methods=['POST'])
def generate_course_cards():
    """Generate flashcards for a specific course topic"""
    data = request.get_json()
    topic_id = data.get('topic_id')
    deck_id = data.get('deck_id')
    card_count = data.get('card_count', 5)
    
    if not all([topic_id, deck_id]):
        return jsonify({'error': 'topic_id and deck_id are required'}), 400
        
    try:
        topic = Topic.query.get_or_404(topic_id)
        course = Course.query.get_or_404(topic.course_id)
        
        # Generate cards prompt
        cards_prompt = f"""
        Create {card_count} Anki flashcards for the topic "{topic.title}" from the course "{course.title}".
        
        TOPIC CONTEXT: {topic.comment}
        COURSE CONTENT: {course.content}
        COURSE ATTACHMENTS: {', '.join(course.attachments)}
        
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
        
        # Determine if the card is from a textbook or a course
        if card.topic.chapter:
            # Textbook-based card
            prev_values, new_values = update_card_review(card, quality)
        else:
            # Course-based card
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