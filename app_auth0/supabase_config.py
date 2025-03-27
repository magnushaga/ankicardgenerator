from supabase import create_client
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')

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

# Auth0 configuration for Supabase
AUTH0_CLIENT_ID = "3eX3XsOE7QwXEKxRUfHqZjpyXtnDjBvx"
AUTH0_CLIENT_SECRET = "e4ZCVdLhAMrmK2DlkQ8j0aF6Uje9XM7vj2IWUqB1eChIUerG6pg7_LCGaW9IR7YJ"

def sync_auth0_user(auth0_user):
    """Sync Auth0 user with Supabase (synchronous version)"""
    try:
        # Check if user exists
        user_query = supabase.table('users').select('*').eq('auth0_id', auth0_user['sub']).execute()
        
        user_data = {
            'email': auth0_user['email'],
            'username': auth0_user.get('nickname', auth0_user['email'].split('@')[0]),
            'auth0_id': auth0_user['sub'],
            'last_login': datetime.utcnow().isoformat()
        }

        if not user_query.data:
            # Create new user
            user_data['created_at'] = datetime.utcnow().isoformat()
            result = supabase.table('users').insert(user_data).execute()
            logger.info(f"Created new user in Supabase: {auth0_user['email']}")
            return result.data[0]
        else:
            # Update existing user
            result = supabase.table('users').update(user_data).eq('auth0_id', auth0_user['sub']).execute()
            logger.info(f"Updated existing user in Supabase: {auth0_user['email']}")
            return result.data[0]
    except Exception as e:
        logger.error(f"Error syncing user with Supabase: {str(e)}")
        raise 