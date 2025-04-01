import psycopg2
import urllib.parse
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_rating_tables(conn):
    """
    Creates tables related to content ratings and rating categories.
    """
    try:
        with conn.cursor() as cur:
            # Create rating_categories table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rating_categories (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    content_type_id UUID NOT NULL REFERENCES content_types(id) ON DELETE CASCADE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, content_type_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_rating_categories_content_type 
                ON rating_categories(content_type_id);
                
                CREATE INDEX IF NOT EXISTS idx_rating_categories_active 
                ON rating_categories(is_active);
            """)
            logger.info("Created rating_categories table")

            # Create content_ratings table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS content_ratings (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    content_type_id UUID NOT NULL REFERENCES content_types(id) ON DELETE CASCADE,
                    content_id UUID NOT NULL,
                    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    review_text TEXT,
                    helpful_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    institution_id UUID REFERENCES educational_institutions(id) ON DELETE SET NULL,
                    department_id UUID REFERENCES institution_departments(id) ON DELETE SET NULL,
                    UNIQUE(user_id, content_type_id, content_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_content_ratings_content 
                ON content_ratings(content_type_id, content_id);
                
                CREATE INDEX IF NOT EXISTS idx_content_ratings_user 
                ON content_ratings(user_id);
                
                CREATE INDEX IF NOT EXISTS idx_content_ratings_institution 
                ON content_ratings(institution_id);
                
                CREATE INDEX IF NOT EXISTS idx_content_ratings_helpful 
                ON content_ratings(helpful_count);
            """)
            logger.info("Created content_ratings table")

            # Create trigger functions for updating timestamps
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_rating_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)

            # Create triggers for each table
            tables = ['rating_categories', 'content_ratings']
            for table in tables:
                cur.execute(f"""
                    DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
                    CREATE TRIGGER update_{table}_updated_at
                        BEFORE UPDATE ON {table}
                        FOR EACH ROW
                        EXECUTE FUNCTION update_rating_updated_at_column();
                """)
                logger.info(f"Created update trigger for {table}")

            conn.commit()
            logger.info("Successfully created all rating tables")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating rating tables: {str(e)}")
        raise

def insert_initial_data(conn):
    """
    Inserts initial data for rating categories.
    """
    try:
        with conn.cursor() as cur:
            # Insert default rating categories for different content types
            cur.execute("""
                INSERT INTO rating_categories (id, name, description, content_type_id)
                VALUES 
                    -- Deck-specific categories
                    (
                        '00000000-0000-0000-0000-000000000001',
                        'Clarity',
                        'How clear and understandable the content is',
                        '00000000-0000-0000-0000-000000000001'  -- deck
                    ),
                    (
                        '00000000-0000-0000-0000-000000000002',
                        'Accuracy',
                        'How accurate and reliable the information is',
                        '00000000-0000-0000-0000-000000000001'  -- deck
                    ),
                    (
                        '00000000-0000-0000-0000-000000000003',
                        'Usefulness',
                        'How helpful the deck is for learning',
                        '00000000-0000-0000-0000-000000000001'  -- deck
                    ),
                    -- Note-specific categories
                    (
                        '00000000-0000-0000-0000-000000000004',
                        'Organization',
                        'How well the notes are organized',
                        '00000000-0000-0000-0000-000000000002'  -- note
                    ),
                    (
                        '00000000-0000-0000-0000-000000000005',
                        'Completeness',
                        'How comprehensive the notes are',
                        '00000000-0000-0000-0000-000000000002'  -- note
                    ),
                    -- Course-specific categories
                    (
                        '00000000-0000-0000-0000-000000000006',
                        'Structure',
                        'How well the course is structured',
                        '00000000-0000-0000-0000-000000000003'  -- course
                    ),
                    (
                        '00000000-0000-0000-0000-000000000007',
                        'Difficulty',
                        'Appropriate difficulty level',
                        '00000000-0000-0000-0000-000000000003'  -- course
                    )
                ON CONFLICT (id) DO NOTHING;
            """)

            conn.commit()
            logger.info("Successfully inserted initial rating category data")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting initial data: {str(e)}")
        raise

def main():
    """
    Main function to create tables and insert initial data.
    """
    try:
        # Use the same database connection parameters as your main application
        password = urllib.parse.quote_plus("H@ukerkul120700")
        conn_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
        
        with psycopg2.connect(conn_string) as conn:
            # Create the tables
            create_rating_tables(conn)
            
            # Insert initial data
            insert_initial_data(conn)
            
            logger.info("Successfully completed rating table setup")

    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main() 