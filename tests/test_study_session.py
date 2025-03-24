from flask import Flask
import json
import random
from datetime import datetime
from models_with_states import db
from study_api import study_api

def setup_test_app():
    """Create and configure the test Flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_flashcards.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Register the study API blueprint
    app.register_blueprint(study_api)
    
    db.init_app(app)
    return app

def simulate_study_session(client, user_id, deck_id):
    """Simulate a complete study session"""
    print("\n=== Starting Study Session ===\n")
    
    # 1. Start a study session
    print("1. Starting new session...")
    response = client.post('/api/study/start-session',
                         json={'user_id': user_id, 'deck_id': deck_id})
    
    if response.status_code != 200:
        print(f"Error: {response.data}")
        return
    
    session_data = json.loads(response.data)
    session_id = session_data['session_id']
    print(f"Session started: {session_id}")
    
    # 2. Get cards to study
    print("\n2. Getting cards to study...")
    response = client.get(f'/api/study/get-next-cards?user_id={user_id}&deck_id={deck_id}&limit=5')
    
    if response.status_code != 200:
        print(f"Error: {response.data}")
        return
    
    cards_data = json.loads(response.data)
    print(f"Retrieved {cards_data['count']} cards")
    
    # 3. Review each card
    print("\n3. Reviewing cards...")
    for card in cards_data['cards']:
        # Simulate user review with random quality (3-5 for better learning progress)
        quality = random.randint(3, 5)
        
        print(f"\nReviewing card from topic: {card['topic']}")
        print(f"Q: {card['front']}")
        print(f"A: {card['back']}")
        print(f"Quality rating: {quality}")
        
        response = client.post('/api/study/review-card',
                            json={
                                'user_id': user_id,
                                'card_id': card['card_id'],
                                'session_id': session_id,
                                'quality': quality
                            })
        
        if response.status_code != 200:
            print(f"Error: {response.data}")
            continue
        
        review_data = json.loads(response.data)
        print(f"Next review in {review_data['new_interval']} days")
    
    # 4. End the session
    print("\n4. Ending session...")
    response = client.post('/api/study/end-session',
                         json={'session_id': session_id})
    
    if response.status_code != 200:
        print(f"Error: {response.data}")
        return
    
    session_stats = json.loads(response.data)
    print("\nSession Statistics:")
    print(f"Duration: {session_stats['duration_seconds']:.1f} seconds")
    print(f"Cards studied: {session_stats['cards_studied']}")
    print(f"Correct answers: {session_stats['correct_answers']}")
    print(f"Accuracy: {session_stats['accuracy_percent']:.1f}%")
    
    # 5. Get overall progress
    print("\n5. Getting overall progress...")
    response = client.get(f'/api/study/progress?user_id={user_id}&deck_id={deck_id}')
    
    if response.status_code != 200:
        print(f"Error: {response.data}")
        return
    
    progress_data = json.loads(response.data)
    print("\nOverall Progress:")
    stats = progress_data['overall_stats']
    print(f"Total cards: {stats['total_cards']}")
    print(f"Active cards: {stats['active_cards']}")
    print(f"Cards due: {stats['cards_due']}")
    print(f"Cards learned: {stats['cards_learned']}")
    print(f"Mastered cards: {stats['mastered_cards']}")
    print(f"Average easiness: {stats['average_easiness']:.2f}")
    
    print("\nProgress by Topic:")
    for topic in progress_data['topic_progress']:
        print(f"\n{topic['topic']}:")
        print(f"  Total cards: {topic['total_cards']}")
        print(f"  Active cards: {topic['active_cards']}")
        print(f"  Cards due: {topic['cards_due']}")
        print(f"  Mastered cards: {topic['mastered_cards']}")
        print(f"  Average easiness: {topic['average_easiness']:.2f}")

def run_test():
    """Run a complete test of the study system"""
    app = setup_test_app()
    
    with app.app_context():
        # Get the first user and deck from the database
        from models_with_states import User, Deck
        user = User.query.first()
        deck = Deck.query.first()
        
        if not user or not deck:
            print("Error: No user or deck found. Please run test_physics_deck.py first.")
            return
        
        with app.test_client() as client:
            # Simulate multiple study sessions
            for i in range(2):
                print(f"\n=== Study Session {i+1} ===")
                simulate_study_session(client, str(user.id), str(deck.id))

if __name__ == '__main__':
    run_test()