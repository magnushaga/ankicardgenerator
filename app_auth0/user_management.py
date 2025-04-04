import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client with service role key
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use service role key

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")

# Initialize Supabase client with service role key to bypass RLS
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def create_or_update_user(auth0_user):
    """
    Create or update a user in Supabase based on Auth0 user data
    Returns the user data if successful, None if failed
    """
    try:
        # Extract user data from Auth0 profile
        user_data = {
            'id': str(uuid.uuid4()),  # Generate a UUID for the user
            'email': auth0_user['email'],
            'username': auth0_user.get('nickname', auth0_user['email'].split('@')[0]),
            'auth0_id': auth0_user['sub'],
            'created_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'is_active': True,
            'email_verified': auth0_user.get('email_verified', False),
            'study_preferences': {
                'preferred_study_time': None,
                'notification_preferences': {},
                'study_goals': {}
            },
            'institution_id': None,
            'department_id': None,
            'role': 'student',  # Default role
            'stripe_customer_id': None,
            'meta_data': {}
        }

        # Check if user exists
        existing_user = supabase.table('users').select('*').eq('auth0_id', auth0_user['sub']).execute()

        if not existing_user.data:
            # Create new user
            logger.info(f"Creating new user: {user_data['email']}")
            # Add picture for new users if available
            if auth0_user.get('picture'):
                user_data['picture'] = auth0_user['picture']
                logger.info(f"Added picture for new user: {user_data['email']}")
            
            result = supabase.table('users').insert(user_data).execute()
            if not result.data:
                logger.error("Failed to create user in Supabase")
                return None
            return result.data[0]
        else:
            # Update existing user
            existing_id = existing_user.data[0]['id']
            logger.info(f"Updating existing user: {user_data['email']}")
            
            # Special handling for admin user
            if existing_id == "845cd193-4692-4e7b-8951-db948424c240":
                if auth0_user.get('picture'):
                    user_data['picture'] = auth0_user['picture']
                    logger.info(f"Updated admin user picture")
            
            update_data = {
                'email': user_data['email'],
                'username': user_data['username'],
                'last_login': user_data['last_login'],
                'email_verified': user_data['email_verified']
            }
            
            # Add picture to update data if it exists in user_data
            if 'picture' in user_data:
                update_data['picture'] = user_data['picture']
            
            result = supabase.table('users').update(update_data).eq('id', existing_id).execute()
            
            if not result.data:
                logger.error("Failed to update user in Supabase")
                return None
            return result.data[0]

    except Exception as e:
        logger.error(f"Error in create_or_update_user: {str(e)}")
        return None

def get_user_by_auth0_id(auth0_id):
    """Get user by Auth0 ID from Supabase"""
    try:
        result = supabase.table('users').select('*').eq('auth0_id', auth0_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return None

def create_or_update_test_user(self, auth0_user, test_group=None, test_data=None):
    """Create or update test user in Supabase from Auth0 user data"""
    try:
        # Extract user data from Auth0 profile
        user_data = {
            'email': auth0_user['email'],
            'username': auth0_user.get('nickname', auth0_user['email'].split('@')[0]),
            'auth0_id': auth0_user['sub'],
            'last_login': datetime.utcnow().isoformat(),
            'is_active': True,
            'email_verified': auth0_user.get('email_verified', False),
            'test_group': test_group,
            'test_data': test_data or {}
        }

        # Check if test user exists
        existing_user = self.supabase.table('users_test').select('*').eq('auth0_id', auth0_user['sub']).execute()

        if not existing_user.data:
            # Create new test user
            user_data.update({
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Creating new test user: {user_data['email']}")
            result = self.supabase.table('users_test').insert(user_data).execute()
            return result.data[0]
        else:
            # Update existing test user
            existing_id = existing_user.data[0]['id']
            logger.info(f"Updating existing test user: {user_data['email']}")
            result = self.supabase.table('users_test').update(user_data).eq('id', existing_id).execute()
            return result.data[0]

    except Exception as e:
        logger.error(f"Error in create_or_update_test_user: {str(e)}")
        raise

def get_test_user(self, auth0_id):
    """Get test user by Auth0 ID"""
    try:
        result = self.supabase.table('users_test').select('*').eq('auth0_id', auth0_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting test user: {str(e)}")
        raise

def update_test_user_data(self, auth0_id, test_data):
    """Update test user's test data"""
    try:
        result = self.supabase.table('users_test').update({
            'test_data': test_data,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('auth0_id', auth0_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error updating test user data: {str(e)}")
        raise

def get_test_users_by_group(self, test_group):
    """Get all test users in a specific test group"""
    try:
        result = self.supabase.table('users_test').select('*').eq('test_group', test_group).execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting test users by group: {str(e)}")
        raise

def _initialize_user_analytics(self, user_id):
    """Initialize learning analytics for new user"""
    try:
        analytics_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'preferred_study_time': None,
            'average_session_duration': 0,
            'cards_per_session': 0,
            'mastery_level': 0.0,
            'weak_areas': [],
            'strong_areas': [],
            'preferred_card_types': [],
            'study_consistency': 0.0
        }
        
        self.supabase.table('learning_analytics').insert(analytics_data).execute()
        logger.info(f"Initialized learning analytics for user: {user_id}")

    except Exception as e:
        logger.error(f"Error initializing user analytics: {str(e)}")
        # Don't raise - this is a non-critical operation 

def sync_auth0_user_to_supabase(auth0_user):
    """Sync Auth0 user data with Supabase"""
    try:
        # Check if user exists by auth0_id
        result = supabase.table('users').select('*').eq('auth0_id', auth0_user['sub']).execute()
        
        user_data = {
            'email': auth0_user['email'],
            'username': auth0_user.get('nickname', auth0_user['email'].split('@')[0]),
            'auth0_id': auth0_user['sub'],
            'picture': auth0_user.get('picture'),
            'email_verified': auth0_user.get('email_verified', False),
            'updated_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'study_preferences': {
                'preferred_study_time': None,
                'notification_preferences': {},
                'study_goals': {}
            },
            'institution_id': None,
            'department_id': None,
            'role': 'student',  # Default role
            'stripe_customer_id': None,
            'meta_data': {}
        }
        
        if result.data and len(result.data) > 0:
            # Update existing user
            user = result.data[0]
            result = supabase.table('users').update(user_data).eq('id', user['id']).execute()
            logger.info(f"Updated user {user['id']} in Supabase")
        else:
            # Create new user
            user_data['id'] = str(uuid.uuid4())  # Generate a UUID for the new user
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['is_active'] = True
            result = supabase.table('users').insert(user_data).execute()
            logger.info(f"Created new user in Supabase")
            
        return result.data[0] if result.data else None
        
    except Exception as e:
        logger.error(f"Error syncing user to Supabase: {str(e)}")
        raise 