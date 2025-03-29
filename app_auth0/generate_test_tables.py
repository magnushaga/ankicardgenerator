import os
import logging
import json
from datetime import datetime
from supabase_config import supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_users_test_table():
    """Create the users_test table and insert test users."""
    try:
        # Create the users_test table using Supabase's REST API
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users_test (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email VARCHAR NOT NULL,
            username VARCHAR,
            auth0_id VARCHAR UNIQUE,
            test_group VARCHAR,
            test_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE
        );
        """
        
        # Execute the create table query
        response = supabase.rpc(
            'exec_sql',
            {'sql': create_table_query}
        ).execute()
        
        logger.info("Users test table created successfully")
        
        # Test users to insert
        test_users = [
            {
                'email': 'test1@example.com',
                'username': 'test_user1',
                'auth0_id': 'auth0|test1',
                'test_group': 'control',
                'test_data': json.dumps({'preferences': {'theme': 'light'}}),
                'is_active': True,
                'email_verified': True
            },
            {
                'email': 'test2@example.com',
                'username': 'test_user2',
                'auth0_id': 'auth0|test2',
                'test_group': 'experimental',
                'test_data': json.dumps({'preferences': {'theme': 'dark'}}),
                'is_active': True,
                'email_verified': True
            }
        ]
        
        # Insert test users
        for user in test_users:
            # Check if user already exists
            existing = supabase.table('users_test').select('*').eq('auth0_id', user['auth0_id']).execute()
            
            if not existing.data:
                # Insert new user
                supabase.table('users_test').insert(user).execute()
                logger.info(f"Created test user: {user['email']}")
            else:
                # Update existing user
                supabase.table('users_test').update(user).eq('auth0_id', user['auth0_id']).execute()
                logger.info(f"Updated test user: {user['email']}")
                
    except Exception as e:
        logger.error(f"Error creating test users: {e}")
        raise e

def verify_table_creation():
    """Verify that the users_test table was created and contains test users."""
    try:
        response = supabase.table('users_test').select('*').execute()
        logger.info(f"Found {len(response.data)} test users in the database")
        return response.data
    except Exception as e:
        logger.error(f"Error verifying table creation: {e}")
        raise e

def main():
    """Main function to set up test users."""
    try:
        logger.info("Starting test user generation...")
        create_users_test_table()
        verify_table_creation()
        logger.info("Test user generation completed successfully")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise e

if __name__ == "__main__":
    main() 