import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase project reference from URL
SUPABASE_URL = os.getenv('SUPABASE_URL')
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")

# Extract project reference from URL
project_ref = SUPABASE_URL.split('//')[1].split('.')[0]

# Construct PostgreSQL connection string
DB_USER = "postgres"
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
DB_HOST = f"db.{project_ref}.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

# Create the database URL with password properly encoded
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

def get_db_engine():
    """Create and return a SQLAlchemy engine"""
    return create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            'connect_timeout': 10,
            'application_name': 'user_management'
        }
    )

def create_or_update_user(auth0_user):
    """
    Create or update a user in the database based on Auth0 user data
    Returns the user data if successful, None if failed
    """
    try:
        engine = get_db_engine()
        
        # Check if user exists
        check_sql = """
        SELECT id, email, username, auth0_id, created_at, last_login, 
               is_active, email_verified, preferred_study_time, 
               notification_preferences, study_goals
        FROM users 
        WHERE auth0_id = :auth0_id;
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(check_sql), {'auth0_id': auth0_user['sub']}).first()
            
            if result:
                # Update existing user
                update_sql = """
                UPDATE users 
                SET email = :email,
                    username = :username,
                    last_login = CURRENT_TIMESTAMP,
                    email_verified = :email_verified
                WHERE auth0_id = :auth0_id
                RETURNING *;
                """
                
                user_data = {
                    'email': auth0_user['email'],
                    'username': auth0_user.get('nickname', auth0_user['email'].split('@')[0]),
                    'auth0_id': auth0_user['sub'],
                    'email_verified': auth0_user.get('email_verified', False)
                }
                
                result = connection.execute(text(update_sql), user_data).first()
                logger.info(f"Updated existing user: {result['email']}")
                
            else:
                # Create new user
                insert_sql = """
                INSERT INTO users (
                    id, email, username, auth0_id, created_at, 
                    last_login, is_active, email_verified,
                    preferred_study_time, notification_preferences, study_goals
                ) VALUES (
                    :id, :email, :username, :auth0_id, CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP, true, :email_verified,
                    null, '{}', '{}'
                ) RETURNING *;
                """
                
                user_data = {
                    'id': str(uuid.uuid4()),
                    'email': auth0_user['email'],
                    'username': auth0_user.get('nickname', auth0_user['email'].split('@')[0]),
                    'auth0_id': auth0_user['sub'],
                    'email_verified': auth0_user.get('email_verified', False)
                }
                
                result = connection.execute(text(insert_sql), user_data).first()
                logger.info(f"Created new user: {result['email']}")
            
            return {
                'id': result['id'],
                'email': result['email'],
                'username': result['username'],
                'auth0_id': result['auth0_id'],
                'created_at': result['created_at'].isoformat(),
                'last_login': result['last_login'].isoformat() if result['last_login'] else None,
                'is_active': result['is_active'],
                'email_verified': result['email_verified'],
                'preferred_study_time': result['preferred_study_time'],
                'notification_preferences': result['notification_preferences'],
                'study_goals': result['study_goals']
            }
            
    except Exception as e:
        logger.error(f"Error creating/updating user: {str(e)}")
        return None

def get_user_by_auth0_id(auth0_id):
    """Get user by Auth0 ID"""
    try:
        engine = get_db_engine()
        
        sql = """
        SELECT id, email, username, auth0_id, created_at, last_login, 
               is_active, email_verified, preferred_study_time, 
               notification_preferences, study_goals
        FROM users 
        WHERE auth0_id = :auth0_id;
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(sql), {'auth0_id': auth0_id}).first()
            
            if result:
                return {
                    'id': result['id'],
                    'email': result['email'],
                    'username': result['username'],
                    'auth0_id': result['auth0_id'],
                    'created_at': result['created_at'].isoformat(),
                    'last_login': result['last_login'].isoformat() if result['last_login'] else None,
                    'is_active': result['is_active'],
                    'email_verified': result['email_verified'],
                    'preferred_study_time': result['preferred_study_time'],
                    'notification_preferences': result['notification_preferences'],
                    'study_goals': result['study_goals']
                }
            return None
            
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
            'last_login': datetime.utcnow().isoformat()
        }
        
        if result.data and len(result.data) > 0:
            # Update existing user
            user = result.data[0]
            result = supabase.table('users').update(user_data).eq('id', user['id']).execute()
            logger.info(f"Updated user {user['id']} in Supabase")
        else:
            # Create new user
            result = supabase.table('users').insert(user_data).execute()
            logger.info(f"Created new user in Supabase")
            
        return result.data[0] if result.data else None
        
    except Exception as e:
        logger.error(f"Error syncing user to Supabase: {str(e)}")
        raise 