import unittest
from flask import Flask
from flask_testing import TestCase
import json
import uuid
from datetime import datetime, timedelta

from models_with_states import db
from api_test import test_api

class FlashcardSystemTest(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the test API blueprint
        app.register_blueprint(test_api)
        
        return app

    def setUp(self):
        db.create_all()
        self.test_user_id = str(uuid.uuid4())

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_complete_flashcard_workflow(self):
        """Test the complete workflow of creating and using flashcards"""
        
        # 1. Generate test textbook with 40 cards
        response = self.client.post('/api/test/generate-textbook',
                                  json={'user_id': self.test_user_id})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('textbook', data)
        self.assertIn('deck', data)
        self.assertEqual(data['cards_created'], 40)
        
        deck_id = data['deck']['id']
        
        # 2. Get deck statistics
        response = self.client.get(f'/api/test/get-deck-stats/{deck_id}',
                                 query_string={'user_id': self.test_user_id})
        self.assertEqual(response.status_code, 200)
        
        stats = json.loads(response.data)
        self.assertEqual(stats['total_cards'], 40)
        self.assertEqual(stats['active_cards'], 40)
        self.assertEqual(len(stats['topic_stats']), 8)  # 8 topics
        
        # 3. Get due cards
        response = self.client.get(f'/api/test/get-due-cards/{deck_id}',
                                 query_string={'user_id': self.test_user_id})
        self.assertEqual(response.status_code, 200)
        
        due_cards = json.loads(response.data)
        self.assertIn('due_cards', due_cards)
        
        print("\nTest Results:")
        print(f"Textbook created: {data['textbook']['title']}")
        print(f"Deck created: {data['deck']['name']}")
        print(f"Total cards created: {data['cards_created']}")
        print("\nDeck Statistics:")
        print(f"Total cards: {stats['total_cards']}")
        print(f"Active cards: {stats['active_cards']}")
        print(f"Due cards: {stats['due_cards']}")
        print("\nTopic Statistics:")
        for topic in stats['topic_stats']:
            print(f"Topic: {topic['topic']}")
            print(f"  Cards: {topic['total_cards']}")
            print(f"  Active: {topic['active_cards']}")
            print(f"  Due: {topic['due_cards']}")

if __name__ == '__main__':
    unittest.main()