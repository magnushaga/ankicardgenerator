import os
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse

# Get the absolute path to the .env file
env_path = Path(__file__).parent / '.env'

# Load environment variables from .env file
load_dotenv(env_path)

class Config:
    # Database
    password = urllib.parse.quote_plus('H@ukerkul120700')
    SQLALCHEMY_DATABASE_URI = f'postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    # Flask
    DEBUG = True 