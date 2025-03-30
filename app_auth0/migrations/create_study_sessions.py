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
        # Create study_sessions table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id),
                deck_id UUID NOT NULL REFERENCES decks(id),
                started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP WITH TIME ZONE,
                cards_studied INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );

            -- Add RLS policies
            ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;

            -- Allow users to read their own study sessions
            CREATE POLICY "Users can read own study sessions" ON study_sessions
                FOR SELECT USING (user_id = auth.uid());

            -- Allow users to create their own study sessions
            CREATE POLICY "Users can create own study sessions" ON study_sessions
                FOR INSERT WITH CHECK (user_id = auth.uid());

            -- Allow users to update their own study sessions
            CREATE POLICY "Users can update own study sessions" ON study_sessions
                FOR UPDATE USING (user_id = auth.uid());

            -- Allow service role to manage all study sessions
            CREATE POLICY "Service role can manage all study sessions" ON study_sessions
                FOR ALL USING (auth.role() = 'service_role');

            -- Add indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON study_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_study_sessions_deck_id ON study_sessions(deck_id);
        """))
        
        # Commit the transaction
        connection.commit()

def downgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_sessions_user_id;
            DROP INDEX IF EXISTS idx_study_sessions_deck_id;
        """))
        
        # Drop policies
        connection.execute(text("""
            DROP POLICY IF EXISTS "Users can read own study sessions" ON study_sessions;
            DROP POLICY IF EXISTS "Users can create own study sessions" ON study_sessions;
            DROP POLICY IF EXISTS "Users can update own study sessions" ON study_sessions;
            DROP POLICY IF EXISTS "Service role can manage all study sessions" ON study_sessions;
        """))
        
        # Drop table
        connection.execute(text("""
            DROP TABLE IF EXISTS study_sessions;
        """))
        
        # Commit the transaction
        connection.commit()

if __name__ == "__main__":
    print("Starting migration...")
    upgrade()
    print("Migration completed successfully!") 