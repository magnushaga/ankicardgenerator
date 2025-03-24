import os
from dotenv import load_dotenv
from app.api import TextbookAnalyzer
import json
import pathlib

# Get the project root directory
ROOT_DIR = pathlib.Path(__file__).parent
print(f"Looking for .env file in: {ROOT_DIR}")
load_dotenv(ROOT_DIR / '.env')

# Verify API key
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables!")
print(f"API key loaded successfully: {api_key[:10]}...")

def test_python_content_generation():
    """Test analyzing and generating content for Introduction to Python"""
    print("\n=== Starting Python Content Generation Test ===")
    
    # Initialize analyzer
    analyzer = TextbookAnalyzer()
    
    # Step 1: Analyze textbook
    print("\n1. Analyzing 'Introduction to Python'...")
    analysis = analyzer.analyze_textbook("Introduction to Python")
    print("\nAnalysis Results:")
    print(json.dumps(analysis, indent=2))
    
    # Step 2: Generate structure
    print("\n2. Generating textbook structure...")
    structure = analyzer.generate_structure("Introduction to Python")
    print("\nGenerated Structure:")
    print(json.dumps(structure, indent=2))
    
    # Step 3: Generate sample cards for first topic
    if structure and 'parts' in structure:
        first_part = structure['parts'][0]
        if 'chapters' in first_part:
            first_chapter = first_part['chapters'][0]
            if 'topics' in first_chapter:
                first_topic = first_chapter['topics'][0]
                
                print(f"\n3. Generating cards for topic: {first_topic['title']}")
                cards = analyzer.generate_cards_for_topic(
                    topic_title=first_topic['title'],
                    topic_comment=first_topic.get('comment', 'Introduction to Python basics'),
                    textbook_name="Introduction to Python",
                    card_count=3
                )
                print("\nGenerated Cards:")
                print(json.dumps(cards, indent=2))
    
    print("\n=== Content Generation Complete ===")

if __name__ == '__main__':
    try:
        test_python_content_generation()
    except Exception as e:
        print(f"Error in test: {e}")
        raise 