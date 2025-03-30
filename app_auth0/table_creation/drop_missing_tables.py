from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def drop_tables():
    """Drop tables that are missing from models.py but present in the database"""
    engine = create_engine(DATABASE_URL)
    
    tables_to_drop = [
        'achievements',
        'api_logs',
        'content_reports',
        'deck_collaborations',
        'deck_exports',
        'deck_shares',
        'learning_analytics',
        'live_decks',
        'study_reminders',
        'textbook_reviews',
        'user_card_states',
        'user_decks'
    ]
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        try:
            # Drop each table if it exists
            for table in tables_to_drop:
                print(f"Dropping table {table} if exists...")
                connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            
            # Commit transaction
            trans.commit()
            print("Successfully dropped all specified tables.")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Error dropping tables: {str(e)}")
            raise

if __name__ == "__main__":
    print("Starting table drop process...")
    drop_tables()
    print("Table drop process completed.") 