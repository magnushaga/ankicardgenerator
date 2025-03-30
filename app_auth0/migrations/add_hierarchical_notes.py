from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def upgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Create study_notes table first
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS study_notes (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                source_material_id VARCHAR(36) REFERENCES course_materials(id),
                tags JSONB DEFAULT '[]'::jsonb,
                is_public BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create note_parts table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS note_parts (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                note_id VARCHAR(36) NOT NULL REFERENCES study_notes(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                order_index INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(note_id, order_index)
            );
        """))
        
        # Create note_chapters table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS note_chapters (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                part_id VARCHAR(36) NOT NULL REFERENCES note_parts(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                order_index INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(part_id, order_index)
            );
        """))
        
        # Create note_topics table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS note_topics (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                chapter_id VARCHAR(36) NOT NULL REFERENCES note_chapters(id),
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                order_index INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chapter_id, order_index)
            );
        """))
        
        # Create note_shares table (modified to support hierarchical sharing)
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS note_shares (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                note_id VARCHAR(36) REFERENCES study_notes(id),
                shared_with VARCHAR(36) REFERENCES users(id),
                permission VARCHAR(20) DEFAULT 'view', -- view, edit
                shared_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT true,
                UNIQUE(note_id, shared_with)
            );
        """))
        
        # Create note_part_shares table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS note_part_shares (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                part_id VARCHAR(36) REFERENCES note_parts(id),
                shared_with VARCHAR(36) REFERENCES users(id),
                permission VARCHAR(20) DEFAULT 'view',
                shared_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT true,
                UNIQUE(part_id, shared_with)
            );
        """))
        
        # Create note_chapter_shares table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS note_chapter_shares (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                chapter_id VARCHAR(36) REFERENCES note_chapters(id),
                shared_with VARCHAR(36) REFERENCES users(id),
                permission VARCHAR(20) DEFAULT 'view',
                shared_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT true,
                UNIQUE(chapter_id, shared_with)
            );
        """))
        
        # Create note_topic_shares table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS note_topic_shares (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                topic_id VARCHAR(36) REFERENCES note_topics(id),
                shared_with VARCHAR(36) REFERENCES users(id),
                permission VARCHAR(20) DEFAULT 'view',
                shared_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT true,
                UNIQUE(topic_id, shared_with)
            );
        """))
        
        # Add indexes for better performance
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_study_notes_user_id 
            ON study_notes(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_note_parts_note_id 
            ON note_parts(note_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_note_chapters_part_id 
            ON note_chapters(part_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_note_topics_chapter_id 
            ON note_topics(chapter_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_note_shares_shared_with 
            ON note_shares(shared_with);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_note_part_shares_shared_with 
            ON note_part_shares(shared_with);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_note_chapter_shares_shared_with 
            ON note_chapter_shares(shared_with);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_note_topic_shares_shared_with 
            ON note_topic_shares(shared_with);
        """))
        
        # Commit the transaction
        connection.commit()

def downgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_notes_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_note_parts_note_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_note_chapters_part_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_note_topics_chapter_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_note_shares_shared_with;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_note_part_shares_shared_with;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_note_chapter_shares_shared_with;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_note_topic_shares_shared_with;
        """))
        
        # Drop tables
        connection.execute(text("""
            DROP TABLE IF EXISTS note_topic_shares;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS note_chapter_shares;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS note_part_shares;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS note_topics;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS note_chapters;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS note_parts;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS note_shares;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS study_notes;
        """))
        
        # Commit the transaction
        connection.commit()

if __name__ == "__main__":
    print("Starting migration...")
    upgrade()
    print("Migration completed successfully!") 