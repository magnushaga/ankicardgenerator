import os
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from datetime import datetime

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

def create_content_types_table(conn):
    """Create the content_types table if it doesn't exist."""
    cur = conn.cursor()
    try:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'content_types'
            );
        """)
        
        if not cur.fetchone()[0]:
            # Create content_types table
            cur.execute("""
                CREATE TABLE content_types (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    icon VARCHAR(50),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert default content types
            default_types = [
                ('deck', 'Anki deck containing flashcards', 'deck-icon', True),
                ('textbook', 'Educational textbook or book', 'book-icon', True),
                ('course_material', 'Course material or lecture notes', 'document-icon', True),
                ('study_resource', 'Study resource or guide', 'resource-icon', True),
                ('note', 'Detailed note about a topic', 'note-icon', True),
                ('part', 'Part of a note or document', 'section-icon', True),
                ('chapter', 'Chapter within a part', 'chapter-icon', True),
                ('topic', 'Topic within a chapter', 'topic-icon', True)
            ]
            
            for name, description, icon, is_active in default_types:
                cur.execute("""
                    INSERT INTO content_types (name, description, icon, is_active)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING;
                """, (name, description, icon, is_active))
            
            conn.commit()
            logger.info("Created content_types table and inserted default types")
        else:
            logger.info("content_types table already exists")
            
    finally:
        cur.close()

def add_content_type_id_column(conn, table_name):
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
            # Add content_type_id column
            cur.execute(f"""
                ALTER TABLE {table_name}
                ADD COLUMN content_type_id UUID REFERENCES content_types(id);
            """)
            conn.commit()
            logger.info(f"Added content_type_id column to {table_name}")
        else:
            logger.info(f"content_type_id column already exists in {table_name}")
            
    finally:
        cur.close()

def migrate_type_data(conn, table_name, old_type_column):
    """Migrate data from old type column to content_type_id."""
    cur = conn.cursor()
    try:
        # Get unique types from the old column
        cur.execute(f"""
            SELECT DISTINCT {old_type_column}
            FROM {table_name}
            WHERE {old_type_column} IS NOT NULL;
        """)
        
        types = cur.fetchall()
        
        for type_name in types:
            type_name = type_name[0]
            if not type_name:
                continue
                
            # Get or create content type
            cur.execute("""
                INSERT INTO content_types (name, description, icon, is_active)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id;
            """, (type_name, f"Content type for {type_name}", f"{type_name}-icon", True))
            
            content_type_id = cur.fetchone()[0]
            
            # Update rows with the new content_type_id
            cur.execute(f"""
                UPDATE {table_name}
                SET content_type_id = %s
                WHERE {old_type_column} = %s;
            """, (content_type_id, type_name))
            
        conn.commit()
        logger.info(f"Migrated type data for {table_name}")
        
    finally:
        cur.close()

def drop_old_type_column(conn, table_name, old_type_column):
    """Drop the old type column after migration."""
    cur = conn.cursor()
    try:
        # Check if column exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            );
        """, (table_name, old_type_column))
        
        if cur.fetchone()[0]:
            # Drop the column
            cur.execute(f"""
                ALTER TABLE {table_name}
                DROP COLUMN {old_type_column};
            """)
            conn.commit()
            logger.info(f"Dropped {old_type_column} column from {table_name}")
        else:
            logger.info(f"{old_type_column} column already dropped from {table_name}")
            
    finally:
        cur.close()

def main():
    """Main function to run the migration."""
    conn = get_db_connection()
    
    try:
        # Create content_types table
        create_content_types_table(conn)
        
        # Define tables that need migration
        tables_to_migrate = [
            ('decks', None),  # No old column, just add content_type_id
            ('content_subject_relationships', 'content_type'),
            ('course_materials', 'material_type'),
            ('study_resources', 'resource_type'),
            ('content_reports', 'content_type'),
            ('textbooks', None)  # No old column, just add content_type_id
        ]
        
        for table_name, old_type_column in tables_to_migrate:
            logger.info(f"Processing {table_name}...")
            
            # Add content_type_id column
            add_content_type_id_column(conn, table_name)
            
            # Migrate data if there's an old type column
            if old_type_column:
                migrate_type_data(conn, table_name, old_type_column)
                drop_old_type_column(conn, table_name, old_type_column)
            
            # Set default content type for new columns
            cur = conn.cursor()
            try:
                # Get the appropriate content type ID based on table name
                content_type_name = table_name.replace('_', ' ').title()
                cur.execute("""
                    SELECT id FROM content_types WHERE name = %s;
                """, (content_type_name,))
                
                result = cur.fetchone()
                if result:
                    content_type_id = result[0]
                    
                    # Update rows where content_type_id is NULL
                    cur.execute(f"""
                        UPDATE {table_name}
                        SET content_type_id = %s
                        WHERE content_type_id IS NULL;
                    """, (content_type_id,))
                    
                    conn.commit()
                    logger.info(f"Set default content type for {table_name}")
                    
            finally:
                cur.close()
        
        logger.info("Migration completed successfully")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main() 