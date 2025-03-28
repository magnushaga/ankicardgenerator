from datetime import datetime
import uuid
import logging
from supabase_config import supabase

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.supabase = supabase

    def create_or_update_user(self, auth0_user):
        """Create or update user in Supabase from Auth0 user data"""
        try:
            # Extract user data from Auth0 profile
            user_data = {
                'email': auth0_user['email'],
                'username': auth0_user.get('nickname', auth0_user['email'].split('@')[0]),
                'auth0_id': auth0_user['sub'],
                'last_login': datetime.utcnow().isoformat(),
                'is_active': True,
                'picture': auth0_user.get('picture'),
                'name': auth0_user.get('name'),
            }

            # Check if user exists
            existing_user = self.supabase.table('users').select('*').eq('auth0_id', auth0_user['sub']).execute()

            if not existing_user.data:
                # Create new user
                user_data.update({
                    'id': str(uuid.uuid4()),
                    'created_at': datetime.utcnow().isoformat(),
                    'preferred_study_time': None,
                    'notification_preferences': {},
                    'study_goals': {}
                })
                
                logger.info(f"Creating new user: {user_data['email']}")
                result = self.supabase.table('users').insert(user_data).execute()
                
                # Initialize related tables
                self._initialize_user_analytics(user_data['id'])
                return result.data[0]
            else:
                # Update existing user
                existing_id = existing_user.data[0]['id']
                logger.info(f"Updating existing user: {user_data['email']}")
                result = self.supabase.table('users').update(user_data).eq('id', existing_id).execute()
                return result.data[0]

        except Exception as e:
            logger.error(f"Error in create_or_update_user: {str(e)}")
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