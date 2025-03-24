import os
from dotenv import load_dotenv
from app.api import TextbookAnalyzer
import json
import pathlib

# Get the project root directory
ROOT_DIR = pathlib.Path(__file__).parent
print(f"Looking for .env file in: {ROOT_DIR}")
load_dotenv(ROOT_DIR / '.env')

# Create directory for saved content
CONTENT_DIR = ROOT_DIR / 'saved_content' / 'python_intro'
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

def save_content_to_files():
    """Generate content from Claude API and save to files"""
    print("\n=== Generating and Saving Content ===")
    
    analyzer = TextbookAnalyzer()
    
    # Step 1: Generate and save analysis
    print("\n1. Analyzing 'Introduction to Python'...")
    analysis = analyzer.analyze_textbook("Introduction to Python")
    with open(CONTENT_DIR / 'analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    print("Analysis saved to analysis.json")
    
    # Step 2: Generate and save structure
    print("\n2. Generating textbook structure...")
    structure = analyzer.generate_structure("Introduction to Python")
    with open(CONTENT_DIR / 'structure.json', 'w') as f:
        json.dump(structure, f, indent=2)
    print("Structure saved to structure.json")
    
    # Step 3: Generate and save cards for each topic
    print("\n3. Generating cards for all topics...")
    all_cards = {}
    
    for part in structure['parts']:
        for chapter in part['chapters']:
            for topic in chapter['topics']:
                topic_id = f"{part['title']}_{chapter['title']}_{topic['title']}".replace(' ', '_')
                print(f"\nGenerating cards for topic: {topic['title']}")
                
                cards = analyzer.generate_cards_for_topic(
                    topic_title=topic['title'],
                    topic_comment=topic.get('comment', ''),
                    textbook_name="Introduction to Python",
                    card_count=3
                )
                all_cards[topic_id] = cards
    
    with open(CONTENT_DIR / 'cards.json', 'w') as f:
        json.dump(all_cards, f, indent=2)
    print("\nAll cards saved to cards.json")
    
    print("\n=== Content Generation and Saving Complete ===")
    print(f"Content saved to: {CONTENT_DIR}")

if __name__ == '__main__':
    save_content_to_files() 