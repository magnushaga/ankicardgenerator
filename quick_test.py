from flask import Flask
import json
import uuid
from models_with_states import db
from api_test import test_api

def setup_test_app():
    """Create and configure the test Flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_flashcards.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Register the test API blueprint
    app.register_blueprint(test_api)
    
    # Initialize the database
    db.init_app(app)
    
    return app

def run_test():
    """Run a quick test of the flashcard system"""
    app = setup_test_app()
    
    with app.app_context():
        # Create the database tables
        db.create_all()
        
        # Create a test user ID
        test_user_id = str(uuid.uuid4())
        
        print("\n=== Starting Flashcard System Test ===\n")
        
        # 1. Generate test textbook with 40 cards
        with app.test_client() as client:
            print("1. Generating test textbook and cards...")
            response = client.post('/api/test/generate-textbook',
                                json={'user_id': test_user_id})
            
            if response.status_code == 200:
                data = json.loads(response.data)
                deck_id = data['deck']['id']
                
                print(f"\nSuccess!")
                print(f"Textbook: {data['textbook']['title']}")
                print(f"Deck: {data['deck']['name']}")
                print(f"Cards created: {data['cards_created']}")
                print("\nSample cards:")
                for card in data['sample_cards']:
                    print(f"\nTopic: {card['topic']}")
                    print(f"Q: {card['front']}")
                    print(f"A: {card['back']}")
                
                # 2. Get deck statistics
                print("\n2. Getting deck statistics...")
                response = client.get(f'/api/test/get-deck-stats/{deck_id}',
                                   query_string={'user_id': test_user_id})
                
                if response.status_code == 200:
                    stats = json.loads(response.data)
                    print("\nDeck Statistics:")
                    print(f"Total cards: {stats['total_cards']}")
                    print(f"Active cards: {stats['active_cards']}")
                    print(f"Due cards: {stats['due_cards']}")
                    print("\nBy Topic:")
                    for topic in stats['topic_stats']:
                        print(f"\n{topic['topic']}:")
                        print(f"  Total: {topic['total_cards']}")
                        print(f"  Active: {topic['active_cards']}")
                        print(f"  Due: {topic['due_cards']}")
                
                # 3. Get due cards
                print("\n3. Getting due cards...")
                response = client.get(f'/api/test/get-due-cards/{deck_id}',
                                   query_string={'user_id': test_user_id})
                
                if response.status_code == 200:
                    due_data = json.loads(response.data)
                    print(f"\nDue cards: {due_data['count']}")
                    if due_data['due_cards']:
                        print("\nFirst few due cards:")
                        for card in due_data['due_cards'][:3]:
                            print(f"\nTopic: {card['topic']}")
                            print(f"Q: {card['front']}")
                            print(f"A: {card['back']}")
                            print(f"Next review: {card['next_review']}")
            else:
                print(f"Error: {response.data}")

if __name__ == '__main__':
    run_test()