import os
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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

def add_content_type_id_column(table_name: str, conn) -> None:
    """Add content_type_id column to a table if it doesn't exist."""
    cur = conn.cursor()
    try:
        # Check if column exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = %s AND column_name = 'content_type_id'
            );
        """, (table_name,))
        
        if not cur.fetchone()[0]:
            # Add the column
            cur.execute(f"""
                ALTER TABLE {table_name}
                ADD COLUMN content_type_id UUID REFERENCES content_types(id);
            """)
            logger.info(f"Added content_type_id column to {table_name}")
        else:
            logger.info(f"content_type_id column already exists in {table_name}")
            
    except Exception as e:
        logger.error(f"Error adding content_type_id to {table_name}: {e}")
        raise
    finally:
        cur.close()

def migrate_old_type_fields(table_name: str, old_field: str, conn) -> None:
    """Migrate data from old type field to content_type_id."""
    cur = conn.cursor()
    try:
        # Check if old field exists
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            );
        """, (table_name, old_field))
        
        if cur.fetchone()[0]:
            # Get the content type ID for this type
            cur.execute("""
                SELECT id FROM content_types WHERE name = %s;
            """, (table_name,))
            
            content_type_id = cur.fetchone()
            if content_type_id:
                content_type_id = content_type_id[0]
                
                # Update content_type_id based on old field
                cur.execute(f"""
                    UPDATE {table_name}
                    SET content_type_id = %s
                    WHERE content_type_id IS NULL;
                """, (content_type_id,))
                
                logger.info(f"Migrated data from {old_field} to content_type_id in {table_name}")
                
                # Drop the old column
                cur.execute(f"""
                    ALTER TABLE {table_name}
                    DROP COLUMN {old_field};
                """)
                logger.info(f"Dropped {old_field} column from {table_name}")
            else:
                logger.warning(f"No content type found for {table_name}")
                
    except Exception as e:
        logger.error(f"Error migrating {old_field} in {table_name}: {e}")
        raise
    finally:
        cur.close()

def main():
    """Main function to run the migration."""
    # Define tables that need content_type_id and their old type fields
    tables_to_update = {
        'decks': None,  # No old field to migrate
        'content_subject_relationships': 'content_type',
        'course_materials': 'material_type',
        'study_resources': 'resource_type',
        'content_reports': 'content_type',
        'textbooks': None  # No old field to migrate
    }
    
    conn = get_db_connection()
    try:
        # First, ensure content_types table exists and has necessary types
        cur = conn.cursor()
        try:
            # Create content_types table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS content_types (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    name VARCHAR NOT NULL UNIQUE,
                    description TEXT,
                    icon VARCHAR,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert default content types if they don't exist
            content_types = [
                ('deck', 'Flashcard deck for learning'),
                ('textbook', 'Educational textbook'),
                ('course_material', 'Course material or lecture notes'),
                ('study_resource', 'Study resource or supplementary material'),
                ('note', 'Detailed notes about a topic'),
                ('content_report', 'Report about content')
            ]
            
            for content_type in content_types:
                cur.execute("""
                    INSERT INTO content_types (name, description)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING;
                """, content_type)
            
            conn.commit()
            logger.info("Content types table and default types created/updated")
            
        finally:
            cur.close()
        
        # Add content_type_id to each table
        for table_name, old_field in tables_to_update.items():
            try:
                # Add content_type_id column
                add_content_type_id_column(table_name, conn)
                
                # Migrate data if there's an old field
                if old_field:
                    migrate_old_type_fields(table_name, old_field, conn)
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"Error processing {table_name}: {e}")
                conn.rollback()
                raise
        
        logger.info("Migration completed successfully")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main() 