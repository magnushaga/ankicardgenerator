import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost:5432/anki_test_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # Flask
    DEBUG = True 