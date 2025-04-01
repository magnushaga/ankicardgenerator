import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path to import from sibling directories
sys.path.append(str(Path(__file__).parent.parent.parent))

load_dotenv()

def create_notes_tables():
    """Create the enhanced notes system tables with UUID primary keys."""
    
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        # Enable UUID extension if not already enabled
        cur.execute("""
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """)

        # Create notes table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID NOT NULL REFERENCES users(id),
            title VARCHAR(255) NOT NULL,
            content TEXT,
            format VARCHAR(50) DEFAULT 'markdown',
            tags TEXT[],
            is_public BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            parent_id UUID REFERENCES notes(id),
            version INTEGER DEFAULT 1,
            is_deleted BOOLEAN DEFAULT false,
            metadata JSONB
        );
        """)

        # Create note_versions table for version control
        cur.execute("""
        CREATE TABLE IF NOT EXISTS note_versions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            content TEXT,
            version INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_by UUID REFERENCES users(id),
            change_summary VARCHAR(500),
            metadata JSONB
        );
        """)

        # Create note_collaborators table for shared editing
        cur.execute("""
        CREATE TABLE IF NOT EXISTS note_collaborators (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id),
            permission_level VARCHAR(50),
            invited_by UUID REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create note_tags table for better tag management
        cur.execute("""
        CREATE TABLE IF NOT EXISTS note_tags (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            tag VARCHAR(100) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_by UUID REFERENCES users(id)
        );
        """)

        # Create note_references table for linking between notes
        cur.execute("""
        CREATE TABLE IF NOT EXISTS note_references (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            source_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            target_note_id UUID NOT NULL REFERENCES notes(id),
            reference_type VARCHAR(50),
            context TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_by UUID REFERENCES users(id)
        );
        """)

        # Create indexes for better query performance
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
        CREATE INDEX IF NOT EXISTS idx_notes_parent_id ON notes(parent_id);
        CREATE INDEX IF NOT EXISTS idx_note_versions_note_id ON note_versions(note_id);
        CREATE INDEX IF NOT EXISTS idx_note_collaborators_note_id ON note_collaborators(note_id);
        CREATE INDEX IF NOT EXISTS idx_note_collaborators_user_id ON note_collaborators(user_id);
        CREATE INDEX IF NOT EXISTS idx_note_tags_note_id ON note_tags(note_id);
        CREATE INDEX IF NOT EXISTS idx_note_tags_tag ON note_tags(tag);
        CREATE INDEX IF NOT EXISTS idx_note_references_source_id ON note_references(source_note_id);
        CREATE INDEX IF NOT EXISTS idx_note_references_target_id ON note_references(target_note_id);
        """)

        print("Successfully created notes tables and indexes.")

    except Exception as e:
        print(f"Error creating notes tables: {e}")
        raise

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_notes_tables() 