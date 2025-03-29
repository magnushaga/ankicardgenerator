from supabase import create_client
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use service role key

logger.debug(f"Supabase URL: {SUPABASE_URL}")
logger.debug(f"Supabase Service Key present: {'Yes' if SUPABASE_SERVICE_KEY else 'No'}")

if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY]):
    raise ValueError("Missing Supabase credentials")

try:
    # Initialize Supabase client with service role key to bypass RLS
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    logger.debug("Supabase client created successfully")
except Exception as e:
    logger.error(f"Error creating Supabase client: {str(e)}")
    raise

class SupabaseUser:
    def __init__(self):
        self.supabase = supabase

    def sync_auth0_user(self, auth0_user):
        """Sync Auth0 user with Supabase users table"""
        try:
            auth0_id = auth0_user['sub']
            email = auth0_user['email']
            
            logger.debug(f"Syncing user {email} with auth0_id {auth0_id}")
            
            # Check if user exists
            existing_user = self.supabase.table('users').select('*').eq('auth0_id', auth0_id).execute()
            logger.debug(f"Existing user query result: {existing_user.data}")
            
            user_data = {
                'auth0_id': auth0_id,
                'email': email,
                'username': auth0_user.get('nickname', email.split('@')[0]),
                'last_login': datetime.utcnow().isoformat(),
                'picture': auth0_user.get('picture'),
                'metadata': {
                    'name': auth0_user.get('name'),
                    'email_verified': auth0_user.get('email_verified', False),
                    'locale': auth0_user.get('locale'),
                    'updated_at': auth0_user.get('updated_at')
                }
            }

            if not existing_user.data:
                # Create new user
                user_data['created_at'] = datetime.utcnow().isoformat()
                logger.debug(f"Creating new user with data: {user_data}")
                result = self.supabase.table('users').insert(user_data).execute()
                logger.info(f"Created new user in users: {email}")
                return result.data[0]
            else:
                # Update existing user
                logger.debug(f"Updating existing user with data: {user_data}")
                result = self.supabase.table('users').update(user_data).eq('auth0_id', auth0_id).execute()
                logger.info(f"Updated existing user in users: {email}")
                return result.data[0]

        except Exception as e:
            logger.error(f"Error syncing user with Supabase: {str(e)}")
            raise

    def get_user(self, auth0_id):
        """Get user from users table"""
        try:
            result = self.supabase.table('users').select('*').eq('auth0_id', auth0_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise

def create_users_table():
    """Create or update the users table schema"""
    try:
        # Create users table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email TEXT UNIQUE NOT NULL,
            username TEXT,
            auth0_id TEXT UNIQUE,
            picture TEXT,
            email_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
            last_login TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
        );

        -- Add RLS policies
        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

        -- Allow users to read their own data
        CREATE POLICY "Users can read own data" ON public.users
            FOR SELECT USING (auth.uid() = id);

        -- Allow users to update their own data
        CREATE POLICY "Users can update own data" ON public.users
            FOR UPDATE USING (auth.uid() = id);

        -- Allow service role to manage all users
        CREATE POLICY "Service role can manage all users" ON public.users
            FOR ALL USING (auth.role() = 'service_role');
        """
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        logger.info("Users table schema updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating users table: {str(e)}")
        return False

def create_rls_policies():
    """Create RLS policies for the Anki card application"""
    try:
        policies_sql = """
        -- Users table policies
        DROP POLICY IF EXISTS "Users can read own data" ON public.users;
        DROP POLICY IF EXISTS "Users can update own data" ON public.users;
        DROP POLICY IF EXISTS "Service role can manage all users" ON public.users;

        CREATE POLICY "Users can read own data" ON public.users
            FOR SELECT USING (auth.uid() = id);

        CREATE POLICY "Users can update own data" ON public.users
            FOR UPDATE USING (auth.uid() = id);

        CREATE POLICY "Service role can manage all users" ON public.users
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Decks table policies
        DROP POLICY IF EXISTS "Users can read public decks" ON public.decks;
        DROP POLICY IF EXISTS "Users can read own decks" ON public.decks;
        DROP POLICY IF EXISTS "Users can modify own decks" ON public.decks;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.decks;

        CREATE POLICY "Users can read public decks" ON public.decks
            FOR SELECT USING (is_public = true);

        CREATE POLICY "Users can read own decks" ON public.decks
            FOR SELECT USING (user_id = auth.uid());

        CREATE POLICY "Users can modify own decks" ON public.decks
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.decks
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Parts table policies
        DROP POLICY IF EXISTS "Users can read deck parts" ON public.parts;
        DROP POLICY IF EXISTS "Users can modify own deck parts" ON public.parts;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.parts;

        CREATE POLICY "Users can read deck parts" ON public.parts
            FOR SELECT USING (
                EXISTS (
                    SELECT 1 FROM public.decks
                    WHERE decks.id = parts.deck_id
                    AND (decks.is_public = true OR decks.user_id = auth.uid())
                )
            );

        CREATE POLICY "Users can modify own deck parts" ON public.parts
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM public.decks
                    WHERE decks.id = parts.deck_id
                    AND decks.user_id = auth.uid()
                )
            );

        CREATE POLICY "Service role can manage all data" ON public.parts
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Chapters table policies
        DROP POLICY IF EXISTS "Users can read deck chapters" ON public.chapters;
        DROP POLICY IF EXISTS "Users can modify own deck chapters" ON public.chapters;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.chapters;

        CREATE POLICY "Users can read deck chapters" ON public.chapters
            FOR SELECT USING (
                EXISTS (
                    SELECT 1 FROM public.parts
                    JOIN public.decks ON decks.id = parts.deck_id
                    WHERE parts.id = chapters.part_id
                    AND (decks.is_public = true OR decks.user_id = auth.uid())
                )
            );

        CREATE POLICY "Users can modify own deck chapters" ON public.chapters
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM public.parts
                    JOIN public.decks ON decks.id = parts.deck_id
                    WHERE parts.id = chapters.part_id
                    AND decks.user_id = auth.uid()
                )
            );

        CREATE POLICY "Service role can manage all data" ON public.chapters
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Topics table policies
        DROP POLICY IF EXISTS "Users can read deck topics" ON public.topics;
        DROP POLICY IF EXISTS "Users can modify own deck topics" ON public.topics;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.topics;

        CREATE POLICY "Users can read deck topics" ON public.topics
            FOR SELECT USING (
                EXISTS (
                    SELECT 1 FROM public.chapters
                    JOIN public.parts ON parts.id = chapters.part_id
                    JOIN public.decks ON decks.id = parts.deck_id
                    WHERE chapters.id = topics.chapter_id
                    AND (decks.is_public = true OR decks.user_id = auth.uid())
                )
            );

        CREATE POLICY "Users can modify own deck topics" ON public.topics
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM public.chapters
                    JOIN public.parts ON parts.id = chapters.part_id
                    JOIN public.decks ON decks.id = parts.deck_id
                    WHERE chapters.id = topics.chapter_id
                    AND decks.user_id = auth.uid()
                )
            );

        CREATE POLICY "Service role can manage all data" ON public.topics
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Cards table policies
        DROP POLICY IF EXISTS "Users can read deck cards" ON public.cards;
        DROP POLICY IF EXISTS "Users can modify own deck cards" ON public.cards;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.cards;

        CREATE POLICY "Users can read deck cards" ON public.cards
            FOR SELECT USING (
                EXISTS (
                    SELECT 1 FROM public.topics
                    JOIN public.chapters ON chapters.id = topics.chapter_id
                    JOIN public.parts ON parts.id = chapters.part_id
                    JOIN public.decks ON decks.id = parts.deck_id
                    WHERE topics.id = cards.topic_id
                    AND (decks.is_public = true OR decks.user_id = auth.uid())
                )
            );

        CREATE POLICY "Users can modify own deck cards" ON public.cards
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM public.topics
                    JOIN public.chapters ON chapters.id = topics.chapter_id
                    JOIN public.parts ON parts.id = chapters.part_id
                    JOIN public.decks ON decks.id = parts.deck_id
                    WHERE topics.id = cards.topic_id
                    AND decks.user_id = auth.uid()
                )
            );

        CREATE POLICY "Service role can manage all data" ON public.cards
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Live Decks policies
        DROP POLICY IF EXISTS "Users can manage own live decks" ON public.live_decks;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.live_decks;

        CREATE POLICY "Users can manage own live decks" ON public.live_decks
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.live_decks
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- User Card States policies
        DROP POLICY IF EXISTS "Users can manage own card states" ON public.user_card_states;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.user_card_states;

        CREATE POLICY "Users can manage own card states" ON public.user_card_states
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.user_card_states
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Study Sessions policies
        DROP POLICY IF EXISTS "Users can manage own study sessions" ON public.study_sessions;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.study_sessions;

        CREATE POLICY "Users can manage own study sessions" ON public.study_sessions
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.study_sessions
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Card Reviews policies
        DROP POLICY IF EXISTS "Users can manage own card reviews" ON public.card_reviews;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.card_reviews;

        CREATE POLICY "Users can manage own card reviews" ON public.card_reviews
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM public.study_sessions
                    WHERE study_sessions.id = card_reviews.session_id
                    AND study_sessions.user_id = auth.uid()
                )
            );

        CREATE POLICY "Service role can manage all data" ON public.card_reviews
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Learning Analytics policies
        DROP POLICY IF EXISTS "Users can manage own analytics" ON public.learning_analytics;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.learning_analytics;

        CREATE POLICY "Users can manage own analytics" ON public.learning_analytics
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.learning_analytics
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Achievements policies
        DROP POLICY IF EXISTS "Users can manage own achievements" ON public.achievements;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.achievements;

        CREATE POLICY "Users can manage own achievements" ON public.achievements
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.achievements
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Study Reminders policies
        DROP POLICY IF EXISTS "Users can manage own reminders" ON public.study_reminders;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.study_reminders;

        CREATE POLICY "Users can manage own reminders" ON public.study_reminders
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.study_reminders
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Deck Collaborations policies
        DROP POLICY IF EXISTS "Users can view own collaborations" ON public.deck_collaborations;
        DROP POLICY IF EXISTS "Users can modify own collaborations" ON public.deck_collaborations;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.deck_collaborations;

        CREATE POLICY "Users can view own collaborations" ON public.deck_collaborations
            FOR SELECT USING (user_id = auth.uid());

        CREATE POLICY "Users can modify own collaborations" ON public.deck_collaborations
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.deck_collaborations
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Textbook Reviews policies
        DROP POLICY IF EXISTS "Users can manage own textbook reviews" ON public.textbook_reviews;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.textbook_reviews;

        CREATE POLICY "Users can manage own textbook reviews" ON public.textbook_reviews
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.textbook_reviews
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Textbooks policies
        DROP POLICY IF EXISTS "Users can read public textbooks" ON public.textbooks;
        DROP POLICY IF EXISTS "Users can manage own textbooks" ON public.textbooks;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.textbooks;

        CREATE POLICY "Users can read public textbooks" ON public.textbooks
            FOR SELECT USING (is_public = true);

        CREATE POLICY "Users can manage own textbooks" ON public.textbooks
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.textbooks
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Deck Exports policies
        DROP POLICY IF EXISTS "Users can manage own exports" ON public.deck_exports;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.deck_exports;

        CREATE POLICY "Users can manage own exports" ON public.deck_exports
            FOR ALL USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.deck_exports
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- Content Reports policies
        DROP POLICY IF EXISTS "Users can create reports" ON public.content_reports;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.content_reports;

        CREATE POLICY "Users can create reports" ON public.content_reports
            FOR INSERT WITH CHECK (reporter_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.content_reports
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');

        -- API Logs policies
        DROP POLICY IF EXISTS "Users can view own logs" ON public.api_logs;
        DROP POLICY IF EXISTS "Service role can manage all data" ON public.api_logs;

        CREATE POLICY "Users can view own logs" ON public.api_logs
            FOR SELECT USING (user_id = auth.uid());

        CREATE POLICY "Service role can manage all data" ON public.api_logs
            FOR ALL USING (auth.jwt()->>'role' = 'service_role');
        """
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': policies_sql}).execute()
        logger.info("RLS policies created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating RLS policies: {str(e)}")
        return False

# Call this function when initializing the application
create_users_table()
create_rls_policies() 