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

# Call this function when initializing the application
create_users_table() 