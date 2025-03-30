from sqlalchemy import create_engine, text
import urllib.parse

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def upgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Add media_urls column to cards table
        connection.execute(text("""
            ALTER TABLE cards
            ADD COLUMN IF NOT EXISTS media_urls JSONB DEFAULT '[]'::jsonb;
        """))
        
        # Commit the transaction
        connection.commit()
        
        print("Successfully added media_urls column to cards table")

def downgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Remove media_urls column from cards table
        connection.execute(text("""
            ALTER TABLE cards
            DROP COLUMN IF EXISTS media_urls;
        """))
        
        # Commit the transaction
        connection.commit()
        
        print("Successfully removed media_urls column from cards table")

if __name__ == "__main__":
    print("Starting migration...")
    upgrade()
    print("Migration completed successfully!") 