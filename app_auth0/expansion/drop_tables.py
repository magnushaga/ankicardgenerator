import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text
import urllib.parse

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# URL encode the password
encoded_password = urllib.parse.quote_plus(str(DB_PASSWORD))

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def drop_tables():
    """Drop the hierarchical notes and social features tables"""
    try:
        # Create engine
        engine = sqlalchemy.create_engine(DATABASE_URL)
        
        # Connect to the database
        with engine.connect() as connection:
            # Drop tables in the correct order (respecting foreign key constraints)
            tables_to_drop = [
                # Note sharing tables
                "note_topic_shares",
                "note_chapter_shares",
                "note_part_shares",
                "note_shares",
                
                # Note hierarchy tables
                "note_topics",
                "note_chapters",
                "note_parts",
                "study_notes",
                
                # Social features tables
                "study_session_participants",
                "group_study_sessions",
                "study_group_members",
                "study_groups",
                
                # Analytics and learning paths
                "learning_path_progress",
                "learning_paths",
                "study_analytics",
                "exam_attempts",
                "practice_exams"
            ]
            
            for table in tables_to_drop:
                try:
                    connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"Successfully dropped table: {table}")
                except Exception as e:
                    print(f"Error dropping table {table}: {str(e)}")
            
            # Commit the transaction
            connection.commit()
            
        print("Successfully dropped all tables")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    print("Starting to drop tables...")
    drop_tables()
    print("Finished dropping tables") 