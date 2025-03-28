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
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

logger.debug(f"Supabase URL: {SUPABASE_URL}")
logger.debug(f"Supabase Key present: {'Yes' if SUPABASE_KEY else 'No'}")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing Supabase credentials")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.debug("Supabase client created successfully")
except Exception as e:
    logger.error(f"Error creating Supabase client: {str(e)}")
    raise

class SupabaseUser:
    def __init__(self):
        self.supabase = supabase

    def create_test_table(self):
        """Create test_users table if it doesn't exist"""
        try:
            # First, check if the table exists
            table_exists = False
            try:
                test_query = self.supabase.table('test_users').select('id').limit(1).execute()
                table_exists = True
                logger.info("Test users table already exists")
            except Exception as e:
                if 'relation "test_users" does not exist' not in str(e):
                    raise

            if not table_exists:
                logger.info("Creating test_users table...")
                # Create the table through Supabase dashboard or use their SQL editor
                # For now, we'll just log a message
                logger.warning("Please create the test_users table in Supabase dashboard with the following SQL:")
                logger.warning("""
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                
                CREATE TABLE public.test_users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    auth0_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_login TIMESTAMPTZ,
                    picture TEXT,
                    metadata JSONB DEFAULT '{}'::jsonb
                );

                -- Set up RLS policies
                ALTER TABLE public.test_users ENABLE ROW LEVEL SECURITY;

                -- Allow read access to authenticated users
                CREATE POLICY "Users can read their own data"
                ON public.test_users
                FOR SELECT
                USING (auth.uid() = id);

                -- Allow insert/update for service role
                CREATE POLICY "Service role can manage users"
                ON public.test_users
                USING (auth.role() = 'service_role');
                """)

    def sync_auth0_user(self, auth0_user):
        """Sync Auth0 user with Supabase test_users table"""
        try:
            auth0_id = auth0_user['sub']
            email = auth0_user['email']
            
            logger.debug(f"Syncing user {email} with auth0_id {auth0_id}")
            
            # Check if user exists
            existing_user = self.supabase.table('test_users').select('*').eq('auth0_id', auth0_id).execute()
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
                result = self.supabase.table('test_users').insert(user_data).execute()
                logger.info(f"Created new user in test_users: {email}")
                return result.data[0]
            else:
                # Update existing user
                logger.debug(f"Updating existing user with data: {user_data}")
                result = self.supabase.table('test_users').update(user_data).eq('auth0_id', auth0_id).execute()
                logger.info(f"Updated existing user in test_users: {email}")
                return result.data[0]

        except Exception as e:
            logger.error(f"Error syncing user with Supabase: {str(e)}")
            raise

    def get_user(self, auth0_id):
        """Get user from test_users table"""
        try:
            result = self.supabase.table('test_users').select('*').eq('auth0_id', auth0_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise 