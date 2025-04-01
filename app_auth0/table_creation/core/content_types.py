import psycopg2
import urllib.parse
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_content_type_tables(conn):
    """
    Creates tables related to content types and their relationships.
    """
    try:
        with conn.cursor() as cur:
            # Create content_types dimension table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS content_types (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    icon VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    version INTEGER DEFAULT 1,
                    template_schema JSONB,
                    validation_rules JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_content_types_active 
                ON content_types(is_active);
                
                CREATE INDEX IF NOT EXISTS idx_content_types_version 
                ON content_types(version);
            """)
            logger.info("Created content_types table")

            # Create content_type_relationships fact table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS content_type_relationships (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    parent_type_id UUID REFERENCES content_types(id) ON DELETE CASCADE,
                    child_type_id UUID REFERENCES content_types(id) ON DELETE CASCADE,
                    relationship_type VARCHAR(50) NOT NULL,  -- e.g., 'contains', 'derived_from', 'prerequisite', 'complementary'
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(parent_type_id, child_type_id, relationship_type)
                );
                
                CREATE INDEX IF NOT EXISTS idx_content_type_relationships_parent 
                ON content_type_relationships(parent_type_id);
                
                CREATE INDEX IF NOT EXISTS idx_content_type_relationships_child 
                ON content_type_relationships(child_type_id);
                
                CREATE INDEX IF NOT EXISTS idx_content_type_relationships_type 
                ON content_type_relationships(relationship_type);
            """)
            logger.info("Created content_type_relationships table")

            # Create trigger functions for updating timestamps
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_content_type_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)

            # Create triggers for each table
            tables = ['content_types', 'content_type_relationships']
            for table in tables:
                cur.execute(f"""
                    DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
                    CREATE TRIGGER update_{table}_updated_at
                        BEFORE UPDATE ON {table}
                        FOR EACH ROW
                        EXECUTE FUNCTION update_content_type_updated_at_column();
                """)
                logger.info(f"Created update trigger for {table}")

            conn.commit()
            logger.info("Successfully created all content type tables")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating content type tables: {str(e)}")
        raise

def insert_initial_data(conn):
    """
    Inserts initial data for content types and their relationships.
    """
    try:
        with conn.cursor() as cur:
            # Insert default content types
            cur.execute("""
                INSERT INTO content_types (id, name, description, icon, is_active, version, template_schema, validation_rules)
                VALUES 
                    -- Core content types
                    (
                        '00000000-0000-0000-0000-000000000001',
                        'deck',
                        'A collection of flashcards for learning',
                        'deck-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "description"], "optional_fields": ["tags", "difficulty"]}',
                        '{"min_cards": 1, "max_cards": 1000}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000002',
                        'note',
                        'Study notes and summaries',
                        'note-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "content"], "optional_fields": ["tags", "format"]}',
                        '{"min_length": 10, "max_length": 10000}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000003',
                        'course',
                        'Complete course materials',
                        'course-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "description", "instructor"], "optional_fields": ["syllabus", "schedule"]}',
                        '{"min_duration": "1 week", "max_duration": "1 year"}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000004',
                        'textbook',
                        'Educational textbooks and books',
                        'book-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "author"], "optional_fields": ["isbn", "edition"]}',
                        '{"min_pages": 1, "max_pages": 1000}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000005',
                        'video',
                        'Educational videos and lectures',
                        'video-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "url"], "optional_fields": ["duration", "transcript"]}',
                        '{"min_duration": "1 minute", "max_duration": "4 hours"}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000006',
                        'quiz',
                        'Practice quizzes and assessments',
                        'quiz-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "questions"], "optional_fields": ["time_limit", "passing_score"]}',
                        '{"min_questions": 1, "max_questions": 100}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000007',
                        'exercise',
                        'Practice exercises and problems',
                        'exercise-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "problem"], "optional_fields": ["solution", "hints"]}',
                        '{"min_difficulty": 1, "max_difficulty": 5}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000008',
                        'flashcard',
                        'Individual flashcard',
                        'card-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["front", "back"], "optional_fields": ["tags", "media"]}',
                        '{"min_length": 1, "max_length": 500}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000009',
                        'study_plan',
                        'Structured study plan',
                        'plan-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "schedule"], "optional_fields": ["goals", "milestones"]}',
                        '{"min_duration": "1 day", "max_duration": "1 year"}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000010',
                        'practice_test',
                        'Full-length practice test',
                        'test-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "questions"], "optional_fields": ["time_limit", "scoring"]}',
                        '{"min_duration": "30 minutes", "max_duration": "4 hours"}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000011',
                        'lecture_slides',
                        'Lecture presentation slides',
                        'slides-icon',
                        TRUE,
                        1,
                        '{"required_fields": ["title", "slides"], "optional_fields": ["notes", "handouts"]}',
                        '{"min_slides": 1, "max_slides": 100}'
                    )
                ON CONFLICT (id) DO NOTHING;
            """)

            # Insert content type relationships
            cur.execute("""
                INSERT INTO content_type_relationships (id, parent_type_id, child_type_id, relationship_type, metadata)
                VALUES 
                    -- Course contains various content types
                    (
                        '00000000-0000-0000-0000-000000000001',
                        '00000000-0000-0000-0000-000000000003',  -- course
                        '00000000-0000-0000-0000-000000000001',  -- deck
                        'contains',
                        '{"min_items": 1, "max_items": 100}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000002',
                        '00000000-0000-0000-0000-000000000003',  -- course
                        '00000000-0000-0000-0000-000000000002',  -- note
                        'contains',
                        '{"min_items": 1, "max_items": 50}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000003',
                        '00000000-0000-0000-0000-000000000003',  -- course
                        '00000000-0000-0000-0000-000000000005',  -- video
                        'contains',
                        '{"min_items": 1, "max_items": 20}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000004',
                        '00000000-0000-0000-0000-000000000003',  -- course
                        '00000000-0000-0000-0000-000000000006',  -- quiz
                        'contains',
                        '{"min_items": 1, "max_items": 10}'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000005',
                        '00000000-0000-0000-0000-000000000003',  -- course
                        '00000000-0000-0000-0000-000000000007',  -- exercise
                        'contains',
                        '{"min_items": 1, "max_items": 50}'
                    ),
                    -- Deck contains flashcards
                    (
                        '00000000-0000-0000-0000-000000000006',
                        '00000000-0000-0000-0000-000000000001',  -- deck
                        '00000000-0000-0000-0000-000000000008',  -- flashcard
                        'contains',
                        '{"min_items": 1, "max_items": 1000}'
                    ),
                    -- Study plan relationships
                    (
                        '00000000-0000-0000-0000-000000000007',
                        '00000000-0000-0000-0000-000000000009',  -- study_plan
                        '00000000-0000-0000-0000-000000000001',  -- deck
                        'recommends',
                        '{"frequency": "daily", "duration": "30 minutes"}'
                    ),
                    -- Prerequisites
                    (
                        '00000000-0000-0000-0000-000000000008',
                        '00000000-0000-0000-0000-000000000010',  -- practice_test
                        '00000000-0000-0000-0000-000000000006',  -- quiz
                        'prerequisite',
                        '{"min_score": 70}'
                    ),
                    -- Complementary content
                    (
                        '00000000-0000-0000-0000-000000000009',
                        '00000000-0000-0000-0000-000000000011',  -- lecture_slides
                        '00000000-0000-0000-0000-000000000002',  -- note
                        'complementary',
                        '{"recommended_order": "after"}'
                    )
                ON CONFLICT (id) DO NOTHING;
            """)

            conn.commit()
            logger.info("Successfully inserted initial content type data")

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
            create_content_type_tables(conn)
            
            # Insert initial data
            insert_initial_data(conn)
            
            logger.info("Successfully completed content type table setup")

    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main() 