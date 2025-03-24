from anthropic import Anthropic
import os
import json

class TextbookAnalyzer:
    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        if not hasattr(self, 'client') or self.client is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            try:
                self.client = Anthropic(api_key=api_key)
            except Exception as e:
                print(f"Error initializing Anthropic client: {e}")
                raise

    # Copy all the TextbookAnalyzer methods from api.py
    # analyze_textbook, generate_structure, generate_cards_for_topic, etc. 