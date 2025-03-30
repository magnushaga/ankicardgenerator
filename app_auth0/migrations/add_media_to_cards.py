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
        # Create media_files table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS media_files (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                file_name VARCHAR(255) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type VARCHAR(100) NOT NULL,
                storage_path VARCHAR(500) NOT NULL,
                thumbnail_path VARCHAR(500),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create media_associations table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS media_associations (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                media_file_id VARCHAR(36) NOT NULL REFERENCES media_files(id),
                associated_type VARCHAR(50) NOT NULL,
                associated_id VARCHAR(36) NOT NULL,
                position INTEGER,
                context VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Add indexes for better performance
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_media_associations_type_id 
            ON media_associations(associated_type, associated_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_media_files_user_id 
            ON media_files(user_id);
        """))
        
        # Add media_urls column to cards table for backward compatibility
        connection.execute(text("""
            ALTER TABLE cards 
            ADD COLUMN IF NOT EXISTS media_urls JSONB DEFAULT '[]'::jsonb;
        """))
        
        # Commit the transaction
        connection.commit()

def downgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_media_associations_type_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_media_files_user_id;
        """))
        
        # Drop tables
        connection.execute(text("""
            DROP TABLE IF EXISTS media_associations;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS media_files;
        """))
        
        # Remove media_urls column from cards
        connection.execute(text("""
            ALTER TABLE cards 
            DROP COLUMN IF EXISTS media_urls;
        """))
        
        # Commit the transaction
        connection.commit()

if __name__ == "__main__":
    print("Starting migration...")
    upgrade()
    print("Migration completed successfully!") 