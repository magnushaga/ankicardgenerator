import sys
import os
import urllib.parse
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL encode the password and create database URL
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def create_live_deck_tables():
    """Create live deck related tables and add columns to existing tables"""
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # 1. Add columns to existing tables
            alter_queries = [
                """
                ALTER TABLE decks 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
                ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS modified_by VARCHAR(36) REFERENCES users(id)
                """,
                
                """
                ALTER TABLE parts 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
                ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS modified_by VARCHAR(36) REFERENCES users(id)
                """,
                
                """
                ALTER TABLE chapters 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
                ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS modified_by VARCHAR(36) REFERENCES users(id)
                """,
                
                """
                ALTER TABLE topics 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
                ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS modified_by VARCHAR(36) REFERENCES users(id)
                """,
                
                """
                ALTER TABLE cards 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
                ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS modified_by VARCHAR(36) REFERENCES users(id)
                """
            ]

            # 2. Create new live deck tables
            create_queries = [
                """
                CREATE TABLE IF NOT EXISTS live_deck_parts (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    live_deck_id UUID REFERENCES live_decks(id) ON DELETE CASCADE,
                    part_id UUID REFERENCES parts(id) ON DELETE CASCADE,
                    is_active BOOLEAN DEFAULT true,
                    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    modified_by VARCHAR(36) REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(live_deck_id, part_id)
                )
                """,
                
                """
                CREATE TABLE IF NOT EXISTS live_deck_chapters (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    live_deck_part_id UUID REFERENCES live_deck_parts(id) ON DELETE CASCADE,
                    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
                    is_active BOOLEAN DEFAULT true,
                    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    modified_by VARCHAR(36) REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(live_deck_part_id, chapter_id)
                )
                """,
                
                """
                CREATE TABLE IF NOT EXISTS live_deck_topics (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    live_deck_chapter_id UUID REFERENCES live_deck_chapters(id) ON DELETE CASCADE,
                    topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
                    is_active BOOLEAN DEFAULT true,
                    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    modified_by VARCHAR(36) REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(live_deck_chapter_id, topic_id)
                )
                """,
                
                """
                CREATE TABLE IF NOT EXISTS live_deck_cards (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    live_deck_topic_id UUID REFERENCES live_deck_topics(id) ON DELETE CASCADE,
                    card_id UUID REFERENCES cards(id) ON DELETE CASCADE,
                    is_active BOOLEAN DEFAULT true,
                    last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    modified_by VARCHAR(36) REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    media_urls JSONB DEFAULT '[]'::jsonb,
                    UNIQUE(live_deck_topic_id, card_id)
                )
                """
            ]

            # 3. Create indexes for performance
            index_queries = [
                """
                CREATE INDEX IF NOT EXISTS idx_live_deck_parts_live_deck_id ON live_deck_parts(live_deck_id);
                CREATE INDEX IF NOT EXISTS idx_live_deck_parts_part_id ON live_deck_parts(part_id);
                CREATE INDEX IF NOT EXISTS idx_live_deck_chapters_live_deck_part_id ON live_deck_chapters(live_deck_part_id);
                CREATE INDEX IF NOT EXISTS idx_live_deck_chapters_chapter_id ON live_deck_chapters(chapter_id);
                CREATE INDEX IF NOT EXISTS idx_live_deck_topics_live_deck_chapter_id ON live_deck_topics(live_deck_chapter_id);
                CREATE INDEX IF NOT EXISTS idx_live_deck_topics_topic_id ON live_deck_topics(topic_id);
                CREATE INDEX IF NOT EXISTS idx_live_deck_cards_live_deck_topic_id ON live_deck_cards(live_deck_topic_id);
                CREATE INDEX IF NOT EXISTS idx_live_deck_cards_card_id ON live_deck_cards(card_id);
                """
            ]

            # 4. Create triggers for last_modified updates
            trigger_queries = [
                """
                CREATE OR REPLACE FUNCTION update_last_modified()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_modified = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                """,
                
                """
                DROP TRIGGER IF EXISTS update_parts_last_modified ON parts;
                CREATE TRIGGER update_parts_last_modified
                BEFORE UPDATE ON parts
                FOR EACH ROW
                EXECUTE FUNCTION update_last_modified();
                """,
                
                """
                DROP TRIGGER IF EXISTS update_chapters_last_modified ON chapters;
                CREATE TRIGGER update_chapters_last_modified
                BEFORE UPDATE ON chapters
                FOR EACH ROW
                EXECUTE FUNCTION update_last_modified();
                """,
                
                """
                DROP TRIGGER IF EXISTS update_topics_last_modified ON topics;
                CREATE TRIGGER update_topics_last_modified
                BEFORE UPDATE ON topics
                FOR EACH ROW
                EXECUTE FUNCTION update_last_modified();
                """,
                
                """
                DROP TRIGGER IF EXISTS update_cards_last_modified ON cards;
                CREATE TRIGGER update_cards_last_modified
                BEFORE UPDATE ON cards
                FOR EACH ROW
                EXECUTE FUNCTION update_last_modified();
                """
            ]

            # Execute all queries within a transaction
            try:
                trans = connection.begin()
                
                # Execute queries
                for query in alter_queries + create_queries + index_queries + trigger_queries:
                    logger.info(f"Executing query: {query[:100]}...")
                    connection.execute(text(query))
                    logger.info("Query executed successfully")
                
                # Commit transaction
                trans.commit()
                logger.info("Successfully created live deck tables and updated existing tables")
                
            except Exception as e:
                logger.error(f"Error executing queries: {str(e)}")
                trans.rollback()
                raise
                
    except Exception as e:
        logger.error(f"Error in create_live_deck_tables: {str(e)}")
        raise

def rollback_live_deck_changes():
    """Rollback live deck related changes"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            drop_queries = [
                "DROP TABLE IF EXISTS live_deck_cards",
                "DROP TABLE IF EXISTS live_deck_topics",
                "DROP TABLE IF EXISTS live_deck_chapters",
                "DROP TABLE IF EXISTS live_deck_parts",
                "DROP FUNCTION IF EXISTS update_last_modified() CASCADE",
                "ALTER TABLE cards DROP COLUMN IF EXISTS is_active, DROP COLUMN IF EXISTS last_modified, DROP COLUMN IF EXISTS modified_by",
                "ALTER TABLE topics DROP COLUMN IF EXISTS is_active, DROP COLUMN IF EXISTS last_modified, DROP COLUMN IF EXISTS modified_by",
                "ALTER TABLE chapters DROP COLUMN IF EXISTS is_active, DROP COLUMN IF EXISTS last_modified, DROP COLUMN IF EXISTS modified_by",
                "ALTER TABLE parts DROP COLUMN IF EXISTS is_active, DROP COLUMN IF EXISTS last_modified, DROP COLUMN IF EXISTS modified_by"
            ]
            
            try:
                trans = connection.begin()
                
                for query in drop_queries:
                    logger.info(f"Executing rollback query: {query}")
                    connection.execute(text(query))
                    logger.info("Rollback query executed successfully")
                
                trans.commit()
                logger.info("Successfully rolled back live deck changes")
                
            except Exception as e:
                logger.error(f"Error executing rollback queries: {str(e)}")
                trans.rollback()
                raise
                
    except Exception as e:
        logger.error(f"Error in rollback_live_deck_changes: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        create_live_deck_tables()
    except Exception as e:
        logger.error(f"Failed to create live deck tables: {str(e)}")
        logger.info("Attempting rollback...")
        rollback_live_deck_changes() 