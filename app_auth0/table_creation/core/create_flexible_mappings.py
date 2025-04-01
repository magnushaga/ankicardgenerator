import os
import sys
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_flexible_mapping_tables():
    """Create tables for flexible content mapping."""
    
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    
    cur = conn.cursor()
    
    try:
        # Enable UUID extension if not already enabled
        cur.execute("""
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """)

        # Create content_locations table for flexible content mapping
        cur.execute("""
        CREATE TABLE IF NOT EXISTS content_locations (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            parent_id UUID REFERENCES content_locations(id),
            level_type VARCHAR(50) NOT NULL, -- 'part', 'chapter', 'topic', 'section', 'custom'
            order_index INTEGER,
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create flexible_content_mappings table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS flexible_content_mappings (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            content_id UUID NOT NULL,
            content_type VARCHAR(50) NOT NULL, -- 'upload', 'note', 'deck', 'ai_generated', etc.
            location_id UUID REFERENCES content_locations(id),
            confidence_score FLOAT,
            mapping_type VARCHAR(50) NOT NULL, -- 'auto', 'manual', 'suggested'
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create content_relationships table for linking related content
        cur.execute("""
        CREATE TABLE IF NOT EXISTS content_relationships (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            source_content_id UUID NOT NULL,
            target_content_id UUID NOT NULL,
            relationship_type VARCHAR(50) NOT NULL, -- 'related', 'prerequisite', 'continuation', etc.
            strength FLOAT, -- AI-determined relationship strength
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create content_tags table for flexible content organization
        cur.execute("""
        CREATE TABLE IF NOT EXISTS content_tags (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            content_id UUID NOT NULL,
            content_type VARCHAR(50) NOT NULL,
            tag VARCHAR(100) NOT NULL,
            tag_type VARCHAR(50), -- 'topic', 'skill', 'concept', etc.
            created_by UUID REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create indexes for better query performance
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_locations_parent_id ON content_locations(parent_id);
        CREATE INDEX IF NOT EXISTS idx_content_locations_level_type ON content_locations(level_type);
        CREATE INDEX IF NOT EXISTS idx_flexible_mappings_content ON flexible_content_mappings(content_id, content_type);
        CREATE INDEX IF NOT EXISTS idx_flexible_mappings_location ON flexible_content_mappings(location_id);
        CREATE INDEX IF NOT EXISTS idx_content_relationships_source ON content_relationships(source_content_id);
        CREATE INDEX IF NOT EXISTS idx_content_relationships_target ON content_relationships(target_content_id);
        CREATE INDEX IF NOT EXISTS idx_content_tags_content ON content_tags(content_id, content_type);
        CREATE INDEX IF NOT EXISTS idx_content_tags_tag ON content_tags(tag);
        """)

        # Create trigger to update timestamps
        cur.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """)

        # Add triggers to tables
        for table in ['content_locations', 'flexible_content_mappings', 'content_relationships']:
            cur.execute(f"""
            DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
            CREATE TRIGGER update_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """)

        conn.commit()
        print("Successfully created flexible mapping tables and indexes.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_flexible_mapping_tables() 