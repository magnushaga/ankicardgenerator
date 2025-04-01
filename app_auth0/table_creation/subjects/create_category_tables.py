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

def create_category_tables():
    """Create category related tables and add columns to existing tables"""
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # 1. Create category tables
            create_queries = [
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_by UUID REFERENCES users(id),
                    is_active BOOLEAN DEFAULT true,
                    UNIQUE(name, parent_id)
                )
                """,
                
                """
                CREATE TABLE IF NOT EXISTS deck_categories (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_by UUID REFERENCES users(id),
                    UNIQUE(deck_id, category_id)
                )
                """
            ]

            # 2. Create indexes for performance
            index_queries = [
                """
                CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
                CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
                CREATE INDEX IF NOT EXISTS idx_deck_categories_deck_id ON deck_categories(deck_id);
                CREATE INDEX IF NOT EXISTS idx_deck_categories_category_id ON deck_categories(category_id);
                """
            ]

            # 3. Create triggers for updated_at
            trigger_queries = [
                """
                CREATE OR REPLACE FUNCTION update_category_updated_at()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                """,
                
                """
                DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;
                CREATE TRIGGER update_categories_updated_at
                BEFORE UPDATE ON categories
                FOR EACH ROW
                EXECUTE FUNCTION update_category_updated_at();
                """
            ]

            # 4. Insert some default categories
            insert_queries = [
                """
                INSERT INTO categories (id, name, description, parent_id, created_at, updated_at, created_by, is_active)
                VALUES 
                    ('00000000-0000-0000-0000-000000000001', 'Mathematics', 'All mathematical subjects', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, true),
                    ('00000000-0000-0000-0000-000000000002', 'Linear Algebra', 'Study of linear equations and their representations', '00000000-0000-0000-0000-000000000001', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, true),
                    ('00000000-0000-0000-0000-000000000003', 'Calculus', 'Study of continuous change', '00000000-0000-0000-0000-000000000001', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, true),
                    ('00000000-0000-0000-0000-000000000004', 'Economics', 'Study of production, distribution, and consumption of goods and services', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, true),
                    ('00000000-0000-0000-0000-000000000005', 'Microeconomics', 'Study of individual markets and decision-making', '00000000-0000-0000-0000-000000000004', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, true),
                    ('00000000-0000-0000-0000-000000000006', 'Macroeconomics', 'Study of the economy as a whole', '00000000-0000-0000-0000-000000000004', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, true)
                ON CONFLICT (id) DO NOTHING;
                """
            ]

            # Execute all queries within a transaction
            try:
                trans = connection.begin()
                
                # Execute queries
                for query in create_queries + index_queries + trigger_queries + insert_queries:
                    logger.info(f"Executing query: {query[:100]}...")
                    connection.execute(text(query))
                    logger.info("Query executed successfully")
                
                # Commit transaction
                trans.commit()
                logger.info("Successfully created category tables and inserted default categories")
                
            except Exception as e:
                logger.error(f"Error executing queries: {str(e)}")
                trans.rollback()
                raise
                
    except Exception as e:
        logger.error(f"Error in create_category_tables: {str(e)}")
        raise

def rollback_category_changes():
    """Rollback category related changes"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            drop_queries = [
                "DROP TABLE IF EXISTS deck_categories",
                "DROP TABLE IF EXISTS categories",
                "DROP FUNCTION IF EXISTS update_category_updated_at() CASCADE"
            ]
            
            try:
                trans = connection.begin()
                
                for query in drop_queries:
                    logger.info(f"Executing rollback query: {query}")
                    connection.execute(text(query))
                    logger.info("Rollback query executed successfully")
                
                trans.commit()
                logger.info("Successfully rolled back category changes")
                
            except Exception as e:
                logger.error(f"Error executing rollback queries: {str(e)}")
                trans.rollback()
                raise
                
    except Exception as e:
        logger.error(f"Error in rollback_category_changes: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        create_category_tables()
    except Exception as e:
        logger.error(f"Failed to create category tables: {str(e)}")
        logger.info("Attempting rollback...")
        rollback_category_changes() 