import os
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="H@ukerkul120700",
            host="db.wxisvjmhokwtjwcqaarb.supabase.co",
            port="5432"
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def is_valid_uuid(uuid_str):
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(uuid_str))
        return True
    except ValueError:
        return False

def cleanup_table(table_name, id_column='id'):
    """Clean up invalid UUIDs in a table."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # First, get all rows with invalid UUIDs
        cur.execute(f"""
            SELECT {id_column} FROM {table_name} 
            WHERE {id_column}::text LIKE '0000%' 
            OR {id_column}::text LIKE 'ffff%'
            OR {id_column}::text LIKE 'eeee%'
            OR {id_column}::text LIKE 'dddd%'
            OR {id_column}::text LIKE 'cccc%'
            OR {id_column}::text LIKE 'bbbb%'
            OR {id_column}::text LIKE 'aaaa%'
        """)
        invalid_rows = cur.fetchall()
        
        if not invalid_rows:
            logger.info(f"No invalid UUIDs found in {table_name}")
            return
            
        logger.info(f"Found {len(invalid_rows)} invalid UUIDs in {table_name}")
        
        # Delete rows with invalid UUIDs
        cur.execute(f"""
            DELETE FROM {table_name} 
            WHERE {id_column}::text LIKE '0000%' 
            OR {id_column}::text LIKE 'ffff%'
            OR {id_column}::text LIKE 'eeee%'
            OR {id_column}::text LIKE 'dddd%'
            OR {id_column}::text LIKE 'cccc%'
            OR {id_column}::text LIKE 'bbbb%'
            OR {id_column}::text LIKE 'aaaa%'
        """)
        
        conn.commit()
        logger.info(f"Successfully cleaned up {table_name}")
        
    except Exception as e:
        logger.error(f"Error cleaning up {table_name}: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def insert_initial_data():
    """Insert initial data with valid UUIDs."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Insert content types
        content_types = [
            (str(uuid.uuid4()), 'deck', 'Flashcard deck for learning', 'deck-icon', True),
            (str(uuid.uuid4()), 'note', 'Study notes', 'note-icon', True),
            (str(uuid.uuid4()), 'course', 'Course material', 'course-icon', True),
            (str(uuid.uuid4()), 'textbook', 'Textbook content', 'book-icon', True),
            (str(uuid.uuid4()), 'video', 'Video content', 'video-icon', True),
            (str(uuid.uuid4()), 'quiz', 'Quiz content', 'quiz-icon', True),
            (str(uuid.uuid4()), 'exercise', 'Practice exercises', 'exercise-icon', True)
        ]
        
        cur.executemany("""
            INSERT INTO content_types (id, name, description, icon, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, content_types)
        
        # Insert content type relationships
        relationships = [
            (str(uuid.uuid4()), content_types[2][0], content_types[0][0], 'contains'),  # course contains deck
            (str(uuid.uuid4()), content_types[2][0], content_types[1][0], 'contains'),  # course contains note
            (str(uuid.uuid4()), content_types[3][0], content_types[0][0], 'generates')   # textbook generates deck
        ]
        
        cur.executemany("""
            INSERT INTO content_type_relationships (id, parent_type_id, child_type_id, relationship_type)
            VALUES (%s, %s, %s, %s)
        """, relationships)
        
        # Insert rating categories
        rating_categories = [
            (str(uuid.uuid4()), 'Clarity', 'How clear and understandable the content is', content_types[0][0], True),
            (str(uuid.uuid4()), 'Accuracy', 'How accurate the information is', content_types[0][0], True),
            (str(uuid.uuid4()), 'Usefulness', 'How helpful the content is for learning', content_types[0][0], True),
            (str(uuid.uuid4()), 'Completeness', 'How comprehensive the content is', content_types[0][0], True),
            (str(uuid.uuid4()), 'Difficulty', 'Appropriate difficulty level', content_types[0][0], True)
        ]
        
        cur.executemany("""
            INSERT INTO rating_categories (id, name, description, content_type_id, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, rating_categories)
        
        # Insert educational institutions
        institutions = [
            (str(uuid.uuid4()), "University of Oslo", "university", "Norway", "Oslo", "https://www.uio.no", "Norway's oldest and largest university"),
            (str(uuid.uuid4()), "Norwegian University of Science and Technology", "university", "Norway", "Trondheim", "https://www.ntnu.no", "Norway's primary institution for engineering education"),
            (str(uuid.uuid4()), "University of Bergen", "university", "Norway", "Bergen", "https://www.uib.no", "Comprehensive research university")
        ]
        
        cur.executemany("""
            INSERT INTO educational_institutions (id, name, type, country, city, website, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, institutions)
        
        # Insert institution departments
        departments = [
            (str(uuid.uuid4()), institutions[0][0], "Department of Business and Management Science", "Business and management science research and education"),
            (str(uuid.uuid4()), institutions[1][0], "Department of Computer Science", "Computer science and information technology research and education"),
            (str(uuid.uuid4()), institutions[2][0], "Department of Mathematics", "Mathematics and natural sciences research and education")
        ]
        
        cur.executemany("""
            INSERT INTO institution_departments (id, institution_id, name, description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (institution_id, name) DO NOTHING
        """, departments)
        
        conn.commit()
        logger.info("Successfully inserted initial data with valid UUIDs")
        
    except Exception as e:
        logger.error(f"Error inserting initial data: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to clean up and fix UUIDs."""
    tables_to_cleanup = [
        'subject_subcategories',
        'subject_categories',
        'rating_categories',
        'institution_departments',
        'educational_institutions',
        'content_types',
        'content_type_relationships',
        'categories'
    ]
    
    try:
        # Clean up each table
        for table in tables_to_cleanup:
            logger.info(f"Cleaning up {table}...")
            cleanup_table(table)
        
        # Insert new data with valid UUIDs
        logger.info("Inserting new data with valid UUIDs...")
        insert_initial_data()
        
        logger.info("Cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise

if __name__ == "__main__":
    main() 