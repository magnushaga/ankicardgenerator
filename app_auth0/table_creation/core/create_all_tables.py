from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_tables():
    """Create all tables for the application based on models.py"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        try:
            # Create extension for UUID if not exists
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            
            # Create users table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL,
                    auth0_id VARCHAR(255) UNIQUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create test_users table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS test_users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL,
                    auth0_id VARCHAR(255) UNIQUE,
                    test_group VARCHAR(50),
                    test_data JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    email_verified BOOLEAN DEFAULT false
                );
            """))
            
            # Create textbooks table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS textbooks (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    subject VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create parts table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS parts (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    textbook_id UUID REFERENCES textbooks(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    order_index INTEGER NOT NULL,
                    UNIQUE(textbook_id, order_index)
                );
            """))
            
            # Create chapters table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    part_id UUID REFERENCES parts(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    order_index INTEGER NOT NULL,
                    UNIQUE(part_id, order_index)
                );
            """))
            
            # Create topics table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS topics (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    comment TEXT,
                    order_index INTEGER NOT NULL,
                    UNIQUE(chapter_id, order_index)
                );
            """))
            
            # Create decks table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS decks (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create cards table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS cards (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
                    front TEXT NOT NULL,
                    back TEXT NOT NULL,
                    media_urls JSONB DEFAULT '[]'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    next_review TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    interval INTEGER DEFAULT 1,
                    easiness FLOAT DEFAULT 2.5,
                    repetitions INTEGER DEFAULT 0
                );
            """))
            
            # Create study_sessions table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP WITH TIME ZONE
                );
            """))
            
            # Create card_reviews table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS card_reviews (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    session_id UUID REFERENCES study_sessions(id) ON DELETE CASCADE,
                    card_id UUID REFERENCES cards(id) ON DELETE CASCADE,
                    quality INTEGER NOT NULL,
                    time_taken INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    prev_easiness FLOAT,
                    prev_interval INTEGER,
                    prev_repetitions INTEGER,
                    new_easiness FLOAT,
                    new_interval INTEGER,
                    new_repetitions INTEGER
                );
            """))
            
            # Create media_files table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS media_files (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    file_name VARCHAR(255) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type VARCHAR(255) NOT NULL,
                    storage_path TEXT NOT NULL,
                    thumbnail_path TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create media_associations table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS media_associations (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    media_file_id UUID REFERENCES media_files(id) ON DELETE CASCADE,
                    associated_type VARCHAR(50) NOT NULL,
                    associated_id UUID NOT NULL,
                    position INTEGER,
                    context JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create course_materials table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS course_materials (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    material_type VARCHAR(50) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type VARCHAR(255) NOT NULL,
                    tags JSONB DEFAULT '[]'::jsonb,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create study_resources table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS study_resources (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    resource_type VARCHAR(50) NOT NULL,
                    source_material_id UUID REFERENCES course_materials(id) ON DELETE SET NULL,
                    tags JSONB DEFAULT '[]'::jsonb,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create resource_generations table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS resource_generations (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    resource_id UUID REFERENCES study_resources(id) ON DELETE CASCADE,
                    status VARCHAR(20) NOT NULL,
                    generation_type VARCHAR(50) NOT NULL,
                    prompt TEXT NOT NULL,
                    result JSONB,
                    error TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create achievements table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    type VARCHAR(50) NOT NULL,
                    description TEXT,
                    achieved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create api_logs table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
                    endpoint VARCHAR(255) NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    status_code INTEGER,
                    response_time FLOAT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create deck_collaborations table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS deck_collaborations (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(deck_id, user_id)
                );
            """))
            
            # Create deck_exports table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS deck_exports (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    format VARCHAR(20) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    file_path TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create deck_shares table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS deck_shares (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    shared_by UUID REFERENCES users(id) ON DELETE CASCADE,
                    shared_with UUID REFERENCES users(id) ON DELETE CASCADE,
                    permissions JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create learning_analytics table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS learning_analytics (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    metric_type VARCHAR(50) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create live_decks table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS live_decks (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    status VARCHAR(20) NOT NULL,
                    current_card_index INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create study_reminders table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS study_reminders (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    message TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create textbook_reviews table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS textbook_reviews (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    textbook_id UUID REFERENCES textbooks(id) ON DELETE CASCADE,
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    rating INTEGER NOT NULL,
                    review_text TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create user_card_states table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS user_card_states (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    card_id UUID REFERENCES cards(id) ON DELETE CASCADE,
                    state VARCHAR(20) NOT NULL,
                    last_reviewed TIMESTAMP WITH TIME ZONE,
                    next_review TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, card_id)
                );
            """))
            
            # Create user_decks table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS user_decks (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    deck_id UUID REFERENCES decks(id) ON DELETE CASCADE,
                    last_studied TIMESTAMP WITH TIME ZONE,
                    progress FLOAT DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, deck_id)
                );
            """))
            
            # Create indexes for better performance
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_cards_deck_id ON cards(deck_id);
                CREATE INDEX IF NOT EXISTS idx_cards_topic_id ON cards(topic_id);
                CREATE INDEX IF NOT EXISTS idx_card_reviews_session_id ON card_reviews(session_id);
                CREATE INDEX IF NOT EXISTS idx_card_reviews_card_id ON card_reviews(card_id);
                CREATE INDEX IF NOT EXISTS idx_media_associations_media_file_id ON media_associations(media_file_id);
                CREATE INDEX IF NOT EXISTS idx_study_resources_user_id ON study_resources(user_id);
                CREATE INDEX IF NOT EXISTS idx_resource_generations_resource_id ON resource_generations(resource_id);
                CREATE INDEX IF NOT EXISTS idx_deck_collaborations_deck_id ON deck_collaborations(deck_id);
                CREATE INDEX IF NOT EXISTS idx_deck_shares_deck_id ON deck_shares(deck_id);
                CREATE INDEX IF NOT EXISTS idx_learning_analytics_user_id ON learning_analytics(user_id);
                CREATE INDEX IF NOT EXISTS idx_study_reminders_user_id ON study_reminders(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_card_states_user_id ON user_card_states(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_decks_user_id ON user_decks(user_id);
            """))
            
            # Commit transaction
            trans.commit()
            print("Successfully created all tables and indexes.")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Error creating tables: {str(e)}")
            raise

if __name__ == "__main__":
    print("Starting table creation process...")
    create_tables()
    print("Table creation process completed.") 