import os
from sqlalchemy import create_engine, text, Table, MetaData, Column, String, DateTime, Boolean, JSON
from urllib.parse import quote_plus, urlparse
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Parse database URL from environment
DATABASE_URL = os.getenv('SUPABASE_URL')
if not DATABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")

# Parse the URL to get components
parsed_url = urlparse(DATABASE_URL)
DB_USER = parsed_url.username
DB_PASSWORD = parsed_url.password
DB_HOST = parsed_url.hostname
DB_PORT = parsed_url.port or "5432"
DB_NAME = parsed_url.path.lstrip('/')

# Create the database URL with password properly encoded
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

def migrate_users():
    try:
        # Create SQLAlchemy engine
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        metadata = MetaData()
        
        # First, check if the old users table exists
        check_table_sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        );
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(check_table_sql)).scalar()
            if not result:
                logger.error("Old users table does not exist. Cannot proceed with migration.")
                return
        
        # Create new users_test table
        users_test = Table(
            'users_test',
            metadata,
            Column('id', String(36), primary_key=True),
            Column('email', String(255), unique=True, nullable=False),
            Column('username', String(255), unique=True, nullable=False),
            Column('auth0_id', String(255), unique=True, nullable=False),
            Column('created_at', DateTime(timezone=True), default=datetime.utcnow),
            Column('last_login', DateTime(timezone=True)),
            Column('is_active', Boolean, default=True),
            Column('email_verified', Boolean, default=False),
            Column('preferred_study_time', String(50)),
            Column('notification_preferences', JSON),
            Column('study_goals', JSON)
        )
        
        # Create the table
        metadata.create_all(engine)
        logger.info("Created users_test table")
        
        # Get existing users data
        get_users_sql = """
        SELECT id, email, username, created_at, last_login, is_active,
               preferred_study_time, notification_preferences, study_goals
        FROM users;
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(get_users_sql))
            existing_users = result.fetchall()
            logger.info(f"Found {len(existing_users)} existing users to migrate")
        
        # Migrate data from old users table to new users_test table
        migration_sql = """
        INSERT INTO users_test (
            id, email, username, auth0_id, created_at, last_login, 
            is_active, email_verified, preferred_study_time, 
            notification_preferences, study_goals
        )
        SELECT 
            id,
            email,
            username,
            id as auth0_id,  -- Using the old id as auth0_id temporarily
            created_at,
            COALESCE(last_login, created_at) as last_login,
            COALESCE(is_active, true) as is_active,
            false as email_verified,  -- Default value for existing users
            preferred_study_time,
            notification_preferences,
            study_goals
        FROM users
        ON CONFLICT (email) DO UPDATE SET
            username = EXCLUDED.username,
            last_login = EXCLUDED.last_login,
            is_active = EXCLUDED.is_active,
            preferred_study_time = EXCLUDED.preferred_study_time,
            notification_preferences = EXCLUDED.notification_preferences,
            study_goals = EXCLUDED.study_goals;
        """
        
        # Execute the migration
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(migration_sql))
                logger.info("Successfully migrated users to users_test table")
        
        # Create indexes for better query performance
        index_sql = """
        CREATE INDEX IF NOT EXISTS idx_users_test_auth0_id ON users_test(auth0_id);
        CREATE INDEX IF NOT EXISTS idx_users_test_email ON users_test(email);
        CREATE INDEX IF NOT EXISTS idx_users_test_username ON users_test(username);
        """
        
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(index_sql))
                logger.info("Created indexes on users_test table")
        
        # Enable RLS and create policies
        rls_sql = """
        ALTER TABLE users_test ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Users can read own data" ON users_test;
        CREATE POLICY "Users can read own data" ON users_test
            FOR SELECT
            USING (auth0_id = current_user);
            
        DROP POLICY IF EXISTS "Users can update own data" ON users_test;
        CREATE POLICY "Users can update own data" ON users_test
            FOR UPDATE
            USING (auth0_id = current_user);
            
        DROP POLICY IF EXISTS "Service role can manage all users" ON users_test;
        CREATE POLICY "Service role can manage all users" ON users_test
            FOR ALL
            USING (auth.role() = 'service_role');
        """
        
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(rls_sql))
                logger.info("Enabled RLS and created policies")
        
        # Verify the migration
        verify_sql = """
        SELECT COUNT(*) FROM users_test;
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(verify_sql)).scalar()
            logger.info(f"Migration completed successfully! Total users in users_test table: {result}")
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_users() 