# create_subject_dimensions_fact.py

from sqlalchemy import create_engine, text, Table, Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL parsing for database connection
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Subject Dimension Tables
class SubjectCategories(Base):
    __tablename__ = 'subject_categories'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'))
    level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SubjectSubcategories(Base):
    __tablename__ = 'subject_subcategories'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('subject_categories.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Fact Table for Content-Subject Relationships
class ContentSubjectRelationships(Base):
    __tablename__ = 'content_subject_relationships'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    content_type = Column(String, nullable=False)  # 'textbook', 'deck', or 'live_deck'
    content_id = Column(UUID(as_uuid=True), nullable=False)
    subject_id = Column(UUID(as_uuid=True), nullable=False)
    subject_type = Column(String, nullable=False)  # 'category' or 'subcategory'
    relationship_type = Column(String, nullable=False)  # 'primary', 'secondary', 'related'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_subject_tables():
    """Create subject-related tables"""
    try:
        # Create tables
        Base.metadata.create_all(engine)
        logger.info("Successfully created subject-related tables")
        
        # Add indexes for better query performance
        with engine.connect() as connection:
            # Index for subject categories
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_subject_categories_parent_id 
                ON subject_categories(parent_id);
            """))
            
            # Index for subject subcategories
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_subject_subcategories_category_id 
                ON subject_subcategories(category_id);
            """))
            
            # Indexes for content subject relationships
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_content_subject_relationships_content 
                ON content_subject_relationships(content_type, content_id);
            """))
            
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_content_subject_relationships_subject 
                ON content_subject_relationships(subject_id, subject_type);
            """))
            
            connection.commit()
            logger.info("Successfully created indexes for subject tables")
            
    except Exception as e:
        logger.error(f"Error creating subject tables: {str(e)}")
        raise

def add_subject_columns_to_existing_tables():
    """Add subject-related columns to existing tables"""
    try:
        with engine.connect() as connection:
            # Add columns to textbooks table
            connection.execute(text("""
                ALTER TABLE textbooks 
                ADD COLUMN IF NOT EXISTS main_subject_id UUID REFERENCES subject_categories(id),
                ADD COLUMN IF NOT EXISTS subcategory_ids UUID[] DEFAULT '{}';
            """))
            
            # Add columns to decks table
            connection.execute(text("""
                ALTER TABLE decks 
                ADD COLUMN IF NOT EXISTS main_subject_id UUID REFERENCES subject_categories(id),
                ADD COLUMN IF NOT EXISTS subcategory_ids UUID[] DEFAULT '{}',
                ADD COLUMN IF NOT EXISTS source_textbook_id UUID REFERENCES textbooks(id);
            """))
            
            # Add columns to live_decks table
            connection.execute(text("""
                ALTER TABLE live_decks 
                ADD COLUMN IF NOT EXISTS main_subject_id UUID REFERENCES subject_categories(id),
                ADD COLUMN IF NOT EXISTS subcategory_ids UUID[] DEFAULT '{}';
            """))
            
            connection.commit()
            logger.info("Successfully added subject columns to existing tables")
            
    except Exception as e:
        logger.error(f"Error adding subject columns: {str(e)}")
        raise

def insert_initial_subject_data():
    """Insert initial subject categories and subcategories"""
    try:
        with engine.connect() as connection:
            # Insert main subject categories
            connection.execute(text("""
                INSERT INTO subject_categories (id, name, description, level)
                VALUES 
                    ('11111111-1111-1111-1111-111111111111', 'Economics', 'Study of production, distribution, and consumption of goods and services', 1),
                    ('22222222-2222-2222-2222-222222222222', 'Mathematics', 'Study of numbers, quantity, space, and change', 1),
                    ('33333333-3333-3333-3333-333333333333', 'Physics', 'Study of matter, energy, and their interactions', 1)
                ON CONFLICT (id) DO NOTHING;
            """))
            
            # Insert subcategories
            connection.execute(text("""
                INSERT INTO subject_subcategories (id, category_id, name, description)
                VALUES 
                    ('44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 'Microeconomics', 'Study of individual markets and decision-making'),
                    ('55555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', 'Macroeconomics', 'Study of economy-wide phenomena'),
                    ('66666666-6666-6666-6666-666666666666', '22222222-2222-2222-2222-222222222222', 'Calculus', 'Study of continuous change'),
                    ('77777777-7777-7777-7777-777777777777', '22222222-2222-2222-2222-222222222222', 'Linear Algebra', 'Study of linear equations and their representations')
                ON CONFLICT (id) DO NOTHING;
            """))
            
            connection.commit()
            logger.info("Successfully inserted initial subject data")
            
    except Exception as e:
        logger.error(f"Error inserting initial subject data: {str(e)}")
        raise

def main():
    """Main function to create and populate subject tables"""
    try:
        logger.info("Starting subject table creation process")
        
        # Create subject tables
        create_subject_tables()
        
        # Add subject columns to existing tables
        add_subject_columns_to_existing_tables()
        
        # Insert initial subject data
        insert_initial_subject_data()
        
        logger.info("Successfully completed subject table creation process")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()