from flask import Blueprint, request, jsonify, current_app
from ..models import (
    db, User, Deck, Textbook, Part, Chapter, Topic, Card,
    LiveDeck, UserCardState, StudySession, CardReview,
    LearningAnalytics, DeckCollaboration, Achievement,
    StudyReminder, DeckExport, ContentReport, APILog
)
from ..api_backup.api_backup import TextbookAnalyzer
from sqlalchemy import text
import uuid
from datetime import datetime
import logging
from functools import wraps
import time
from ..supabase_config import supabase

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

def log_api_call(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        response = f(*args, **kwargs)
        end_time = time.time()
        
        # Log API call
        log = APILog(
            user_id=request.user.id if hasattr(request, 'user') else None,
            endpoint=request.endpoint,
            method=request.method,
            status_code=response[1] if isinstance(response, tuple) else 200,
            response_time=int((end_time - start_time) * 1000)  # Convert to milliseconds
        )
        db.session.add(log)
        db.session.commit()
        
        return response
    return decorated_function

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
            
        token = auth_header.split(' ')[1]
        try:
            # Verify the token with Supabase
            user = supabase.auth.get_user(token)
            # Get or create user in our database
            current_user = User.get_or_create_from_supabase(user)
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated

@api_bp.route('/api/test', methods=['GET'])
def test():
    logger.info("Test endpoint accessed")
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        response = {
            "status": "success",
            "message": "API is working!",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(f"Sending response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        response = {
            "status": "error",
            "message": "API is working but database connection failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.error(f"Sending error response: {response}")
        return jsonify(response), 500

@api_bp.route('/api/generate-deck', methods=['POST'])
def generate_deck():
    """Generate a deck from a textbook name and save to PostgreSQL"""
    data = request.get_json()
    textbook_name = data.get('textbook_name')
    
    if not textbook_name:
        return jsonify({'error': 'textbook_name is required'}), 400
        
    try:
        # Initialize analyzer
        analyzer = TextbookAnalyzer()
        
        # Step 1: Analyze textbook
        print("\nAnalyzing textbook...")
        analysis = analyzer.analyze_textbook(textbook_name)
        
        # Step 2: Generate structure
        print("\nGenerating structure...")
        structure = analyzer.generate_structure(textbook_name)
        
        # Step 3: Create database entries
        print("\nCreating database entries...")
        
        # Create test user with unique email
        print("\n1. Creating test user...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user = User(
            email=f'test_{timestamp}@example.com',
            username=f'test_user_{timestamp}'
        )
        test_user.set_password('testpassword')
        db.session.add(test_user)
        db.session.flush()

        # Create deck
        print("\n2. Creating deck...")
        deck = Deck(
            user_id=test_user.id,
            title=textbook_name
        )
        db.session.add(deck)
        db.session.flush()
        
        all_cards = {}
        # Create parts, chapters, topics
        for part_idx, part_data in enumerate(structure['parts']):
            print(f"\nCreating part: {part_data['title']}")
            part = Part(
                deck_id=deck.id,
                title=part_data['title'],
                order_index=part_idx
            )
            db.session.add(part)
            db.session.flush()

            for chapter_idx, chapter_data in enumerate(part_data['chapters']):
                print(f"  Creating chapter: {chapter_data['title']}")
                chapter = Chapter(
                    part_id=part.id,
                    title=chapter_data['title'],
                    order_index=chapter_idx
                )
                db.session.add(chapter)
                db.session.flush()

                for topic_idx, topic_data in enumerate(chapter_data['topics']):
                    print(f"    Creating topic: {topic_data['title']}")
                    topic = Topic(
                        chapter_id=chapter.id,
                        title=topic_data['title'],
                        order_index=topic_idx
                    )
                    db.session.add(topic)
                    db.session.flush()

                    # Generate cards for this topic
                    print(f"      Generating cards for topic: {topic_data['title']}")
                    cards = analyzer.generate_cards_for_topic(
                        topic_data['title'],
                        topic_data.get('comment', ''),
                        textbook_name,
                        topic_data.get('card_count', 3)
                    )
                    
                    # Store cards in database
                    topic_cards = []
                    for card_data in cards:
                        card = Card(
                            topic_id=topic.id,
                            front=card_data['question'],
                            back=card_data['answer']
                        )
                        db.session.add(card)
                        topic_cards.append({
                            'front': card.front,
                            'back': card.back
                        })
                    all_cards[str(topic.id)] = topic_cards

        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'message': 'Deck generated successfully',
            'deck': {
                'id': str(deck.id),
                'title': deck.title,
                'user_id': str(test_user.id)
            },
            'analysis': analysis,
            'structure': structure,
            'cards': all_cards
        })
        
    except Exception as e:
        print(f"Error generating deck: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/textbooks', methods=['GET'])
def get_textbooks():
    """Get all generated textbooks"""
    try:
        textbooks = Textbook.query.all()
        return jsonify([{
            'id': str(textbook.id),
            'title': textbook.title,
            'author': textbook.author,
            'subject': textbook.subject
        } for textbook in textbooks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/search-decks', methods=['GET'])
def search_decks():
    """Search for decks by title and return with cards"""
    query = request.args.get('q', '')
    
    try:
        decks = Deck.query.filter(Deck.title.ilike(f'%{query}%')).all()
        
        result = []
        for deck in decks:
            cards = []
            # Get all cards from the deck structure
            for part in deck.parts:
                for chapter in part.chapters:
                    for topic in chapter.topics:
                        topic_cards = Card.query.filter_by(topic_id=topic.id).all()
                        cards.extend([{
                            'id': str(card.id),
                            'front': card.front,
                            'back': card.back,
                            'partTitle': part.title,
                            'chapterTitle': chapter.title,
                            'topicTitle': topic.title
                        } for card in topic_cards])
            
            result.append({
                'id': str(deck.id),
                'title': deck.title,
                'cards': cards
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/live-decks', methods=['POST'])
@log_api_call
def create_live_deck():
    """Create a new live deck from an existing deck"""
    data = request.get_json()
    deck_id = data.get('deck_id')
    name = data.get('name')
    description = data.get('description')
    
    if not all([deck_id, name]):
        return jsonify({'error': 'deck_id and name are required'}), 400
        
    try:
        # Create live deck
        live_deck = LiveDeck(
            user_id=request.user.id,
            deck_id=deck_id,
            name=name,
            description=description
        )
        db.session.add(live_deck)
        db.session.flush()
        
        # Initialize card states
        deck = Deck.query.get_or_404(deck_id)
        for part in deck.parts:
            for chapter in part.chapters:
                for topic in chapter.topics:
                    for card in topic.cards:
                        card_state = UserCardState(
                            user_id=request.user.id,
                            live_deck_id=live_deck.id,
                            card_id=card.id,
                            is_active=True
                        )
                        db.session.add(card_state)
        
        db.session.commit()
        return jsonify(live_deck.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/live-decks/<live_deck_id>/cards', methods=['GET'])
@log_api_call
def get_live_deck_cards(live_deck_id):
    """Get all cards for a live deck with their states"""
    try:
        live_deck = LiveDeck.query.get_or_404(live_deck_id)
        if live_deck.user_id != request.user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        cards = []
        for card_state in live_deck.card_states:
            card = card_state.card
            cards.append({
                'id': str(card.id),
                'front': card.front,
                'back': card.back,
                'is_active': card_state.is_active,
                'next_review': card_state.next_review.isoformat() if card_state.next_review else None,
                'interval': card_state.interval,
                'easiness': card_state.easiness,
                'repetitions': card_state.repetitions,
                'card_type': card.card_type,
                'media_urls': card.media_urls,
                'tags': card.tags,
                'difficulty': card.difficulty,
                'notes': card.notes
            })
            
        return jsonify(cards)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/live-decks/<live_deck_id>/cards/<card_id>/toggle', methods=['POST'])
@log_api_call
def toggle_card_state(live_deck_id, card_id):
    """Toggle a card's active state in a live deck"""
    try:
        card_state = UserCardState.query.filter_by(
            live_deck_id=live_deck_id,
            card_id=card_id,
            user_id=request.user.id
        ).first_or_404()
        
        card_state.is_active = not card_state.is_active
        db.session.commit()
        
        return jsonify({
            'card_id': str(card_id),
            'is_active': card_state.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/analytics', methods=['GET'])
@log_api_call
def get_learning_analytics():
    """Get learning analytics for the current user"""
    try:
        analytics = LearningAnalytics.query.filter_by(
            user_id=request.user.id
        ).all()
        
        return jsonify([{
            'live_deck_id': str(a.live_deck_id),
            'preferred_study_time': a.preferred_study_time,
            'average_session_duration': a.average_session_duration,
            'cards_per_session': a.cards_per_session,
            'mastery_level': a.mastery_level,
            'weak_areas': a.weak_areas,
            'strong_areas': a.strong_areas,
            'preferred_card_types': a.preferred_card_types,
            'study_consistency': a.study_consistency
        } for a in analytics])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/achievements', methods=['GET'])
@log_api_call
def get_achievements():
    """Get all achievements for the current user"""
    try:
        achievements = Achievement.query.filter_by(
            user_id=request.user.id
        ).all()
        
        return jsonify([{
            'id': str(a.id),
            'type': a.type,
            'title': a.title,
            'description': a.description,
            'earned_at': a.earned_at.isoformat(),
            'metadata': a.metadata
        } for a in achievements])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/reminders', methods=['POST'])
@log_api_call
def create_study_reminder():
    """Create a new study reminder"""
    data = request.get_json()
    live_deck_id = data.get('live_deck_id')
    reminder_time = data.get('reminder_time')
    days_of_week = data.get('days_of_week')
    notification_type = data.get('notification_type', 'in-app')
    
    if not all([live_deck_id, reminder_time, days_of_week]):
        return jsonify({'error': 'live_deck_id, reminder_time, and days_of_week are required'}), 400
        
    try:
        reminder = StudyReminder(
            user_id=request.user.id,
            live_deck_id=live_deck_id,
            reminder_time=datetime.strptime(reminder_time, '%H:%M').time(),
            days_of_week=days_of_week,
            notification_type=notification_type
        )
        db.session.add(reminder)
        db.session.commit()
        
        return jsonify({
            'id': str(reminder.id),
            'reminder_time': reminder.reminder_time.strftime('%H:%M'),
            'days_of_week': reminder.days_of_week,
            'notification_type': reminder.notification_type
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/decks/<deck_id>/export', methods=['POST'])
@log_api_call
def export_deck(deck_id):
    """Export a deck in various formats"""
    data = request.get_json()
    format = data.get('format', 'anki')
    settings = data.get('settings', {})
    
    if not format:
        return jsonify({'error': 'format is required'}), 400
        
    try:
        # Create export record
        export = DeckExport(
            deck_id=deck_id,
            user_id=request.user.id,
            format=format,
            settings=settings
        )
        db.session.add(export)
        db.session.flush()
        
        # TODO: Implement actual export logic based on format
        # This would involve generating the appropriate file
        # and storing it somewhere accessible
        
        export.file_url = f"/exports/{export.id}.{format}"  # Placeholder
        db.session.commit()
        
        return jsonify({
            'id': str(export.id),
            'format': export.format,
            'file_url': export.file_url
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/reports', methods=['POST'])
@log_api_call
def create_content_report():
    """Report inappropriate content"""
    data = request.get_json()
    content_type = data.get('content_type')
    content_id = data.get('content_id')
    reason = data.get('reason')
    description = data.get('description')
    
    if not all([content_type, content_id, reason]):
        return jsonify({'error': 'content_type, content_id, and reason are required'}), 400
        
    try:
        report = ContentReport(
            reporter_id=request.user.id,
            content_type=content_type,
            content_id=content_id,
            reason=reason,
            description=description
        )
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'id': str(report.id),
            'status': report.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/decks/<deck_id>/collaborate', methods=['POST'])
@log_api_call
def add_collaborator(deck_id):
    """Add a collaborator to a deck"""
    data = request.get_json()
    user_id = data.get('user_id')
    role = data.get('role', 'viewer')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
        
    try:
        # Check if user has permission to add collaborators
        deck = Deck.query.get_or_404(deck_id)
        if deck.user_id != request.user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        collaboration = DeckCollaboration(
            deck_id=deck_id,
            user_id=user_id,
            role=role,
            can_edit=role in ['owner', 'editor'],
            can_share=role in ['owner', 'editor'],
            can_delete=role == 'owner'
        )
        db.session.add(collaboration)
        db.session.commit()
        
        return jsonify({
            'id': str(collaboration.id),
            'role': collaboration.role
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/live-decks/<live_deck_id>/parts', methods=['POST'])
@log_api_call
def add_part_to_live_deck(live_deck_id):
    """Add a new part to a live deck"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    order_index = data.get('order_index')
    
    if not title:
        return jsonify({'error': 'title is required'}), 400
        
    try:
        live_deck = LiveDeck.query.get_or_404(live_deck_id)
        if live_deck.user_id != request.user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Get the next order index if not provided
        if order_index is None:
            last_part = Part.query.filter_by(deck_id=live_deck.deck_id).order_by(Part.order_index.desc()).first()
            order_index = (last_part.order_index + 1) if last_part else 0
            
        part = Part(
            deck_id=live_deck.deck_id,
            title=title,
            description=description,
            order_index=order_index
        )
        db.session.add(part)
        db.session.commit()
        
        return jsonify({
            'id': str(part.id),
            'title': part.title,
            'description': part.description,
            'order_index': part.order_index
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/parts/<part_id>/chapters', methods=['POST'])
@log_api_call
def add_chapter_to_part(part_id):
    """Add a new chapter to a part"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    order_index = data.get('order_index')
    
    if not title:
        return jsonify({'error': 'title is required'}), 400
        
    try:
        part = Part.query.get_or_404(part_id)
        live_deck = LiveDeck.query.get_or_404(part.deck_id)
        if live_deck.user_id != request.user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Get the next order index if not provided
        if order_index is None:
            last_chapter = Chapter.query.filter_by(part_id=part_id).order_by(Chapter.order_index.desc()).first()
            order_index = (last_chapter.order_index + 1) if last_chapter else 0
            
        chapter = Chapter(
            part_id=part_id,
            title=title,
            description=description,
            order_index=order_index
        )
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({
            'id': str(chapter.id),
            'title': chapter.title,
            'description': chapter.description,
            'order_index': chapter.order_index
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/chapters/<chapter_id>/topics', methods=['POST'])
@log_api_call
def add_topic_to_chapter(chapter_id):
    """Add a new topic to a chapter"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    order_index = data.get('order_index')
    
    if not title:
        return jsonify({'error': 'title is required'}), 400
        
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        part = Part.query.get_or_404(chapter.part_id)
        live_deck = LiveDeck.query.get_or_404(part.deck_id)
        if live_deck.user_id != request.user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Get the next order index if not provided
        if order_index is None:
            last_topic = Topic.query.filter_by(chapter_id=chapter_id).order_by(Topic.order_index.desc()).first()
            order_index = (last_topic.order_index + 1) if last_topic else 0
            
        topic = Topic(
            chapter_id=chapter_id,
            title=title,
            description=description,
            order_index=order_index
        )
        db.session.add(topic)
        db.session.commit()
        
        return jsonify({
            'id': str(topic.id),
            'title': topic.title,
            'description': topic.description,
            'order_index': topic.order_index
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/topics/<topic_id>/cards', methods=['POST'])
@log_api_call
def add_card_to_topic(topic_id):
    """Add a new card to a topic"""
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
        
    try:
        topic = Topic.query.get_or_404(topic_id)
        chapter = Chapter.query.get_or_404(topic.chapter_id)
        part = Part.query.get_or_404(chapter.part_id)
        live_deck = LiveDeck.query.get_or_404(part.deck_id)
        if live_deck.user_id != request.user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Create the card
        card = Card(
            topic_id=topic_id,
            front=front,
            back=back,
            card_type=card_type,
            media_urls=media_urls,
            tags=tags,
            difficulty=difficulty,
            notes=notes
        )
        db.session.add(card)
        db.session.flush()
        
        # Create card state for the live deck
        card_state = UserCardState(
            user_id=request.user.id,
            live_deck_id=live_deck.id,
            card_id=card.id,
            is_active=True
        )
        db.session.add(card_state)
        db.session.commit()
        
        return jsonify({
            'id': str(card.id),
            'front': card.front,
            'back': card.back,
            'card_type': card.card_type,
            'media_urls': card.media_urls,
            'tags': card.tags,
            'difficulty': card.difficulty,
            'notes': card.notes,
            'is_active': card_state.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/live-decks/<live_deck_id>/structure', methods=['GET'])
@log_api_call
def get_live_deck_structure(live_deck_id):
    """Get the complete structure of a live deck"""
    try:
        live_deck = LiveDeck.query.get_or_404(live_deck_id)
        if live_deck.user_id != request.user.id:
            return jsonify({"error": "Unauthorized"}), 403
            
        structure = []
        for part in live_deck.deck.parts:
            part_data = {
                'id': str(part.id),
                'title': part.title,
                'description': part.description,
                'order_index': part.order_index,
                'chapters': []
            }
            
            for chapter in part.chapters:
                chapter_data = {
                    'id': str(chapter.id),
                    'title': chapter.title,
                    'description': chapter.description,
                    'order_index': chapter.order_index,
                    'topics': []
                }
                
                for topic in chapter.topics:
                    topic_data = {
                        'id': str(topic.id),
                        'title': topic.title,
                        'description': topic.description,
                        'order_index': topic.order_index,
                        'cards': []
                    }
                    
                    for card in topic.cards:
                        card_state = UserCardState.query.filter_by(
                            live_deck_id=live_deck_id,
                            card_id=card.id,
                            user_id=request.user.id
                        ).first()
                        
                        if card_state:
                            topic_data['cards'].append({
                                'id': str(card.id),
                                'front': card.front,
                                'back': card.back,
                                'card_type': card.card_type,
                                'media_urls': card.media_urls,
                                'tags': card.tags,
                                'difficulty': card.difficulty,
                                'notes': card.notes,
                                'is_active': card_state.is_active,
                                'next_review': card_state.next_review.isoformat() if card_state.next_review else None,
                                'interval': card_state.interval,
                                'easiness': card_state.easiness,
                                'repetitions': card_state.repetitions
                            })
                    
                    chapter_data['topics'].append(topic_data)
                
                part_data['chapters'].append(chapter_data)
            
            structure.append(part_data)
            
        return jsonify(structure)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login with Supabase"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
        
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        # Get or create user in our database
        user = User.get_or_create_from_supabase(auth_response.user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'user': user.to_dict(),
            'session': auth_response.session
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@api_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Sign up with Supabase"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    
    if not all([email, password, username]):
        return jsonify({'error': 'Email, password, and username are required'}), 400
        
    try:
        # Sign up with Supabase
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password
        })
        
        # Create user in our database
        user = User(
            id=auth_response.user.id,
            email=email,
            username=username,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'user': user.to_dict(),
            'session': auth_response.session
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout(current_user):
    """Logout from Supabase"""
    try:
        supabase.auth.sign_out()
        return jsonify({'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user(current_user):
    """Get current user information"""
    return jsonify(current_user.to_dict()) 