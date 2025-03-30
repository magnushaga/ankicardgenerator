from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def test_migration():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Test media_files table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'media_files'
            );
        """))
        media_files_exists = result.scalar()
        print(f"media_files table exists: {media_files_exists}")
        
        # Test media_associations table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'media_associations'
            );
        """))
        media_associations_exists = result.scalar()
        print(f"media_associations table exists: {media_associations_exists}")
        
        # Test media_urls column in cards table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'cards' 
                AND column_name = 'media_urls'
            );
        """))
        media_urls_exists = result.scalar()
        print(f"media_urls column exists in cards table: {media_urls_exists}")
        
        # Test indexes
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_media_associations_type_id'
            );
        """))
        associations_index_exists = result.scalar()
        print(f"media_associations index exists: {associations_index_exists}")
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_media_files_user_id'
            );
        """))
        files_index_exists = result.scalar()
        print(f"media_files index exists: {files_index_exists}")

if __name__ == "__main__":
    print("Testing media migration...")
    test_migration()
    print("Test completed!") 