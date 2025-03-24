import os
from dotenv import load_dotenv
import pathlib

# Get the project root directory
ROOT_DIR = pathlib.Path(__file__).parent

# Load environment variables
print(f"Looking for .env file in: {ROOT_DIR}")
load_dotenv(ROOT_DIR / '.env')

# Get and print API key
api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print("\nAPI Key found:")
    print(f"First 10 chars: {api_key[:10]}...")
    print(f"Last 10 chars: {api_key[-10:]}")
    print(f"Length: {len(api_key)}")
else:
    print("\nERROR: No API key found in environment variables!")
    print("Please check that:")
    print("1. The .env file exists in the correct location")
    print("2. The file contains: ANTHROPIC_API_KEY=your-key-here")
    print("3. There are no extra spaces or quotes around the key") 