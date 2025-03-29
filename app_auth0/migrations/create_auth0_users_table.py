import os
from sqlalchemy import create_engine, text, Table, MetaData, Column, String, DateTime, Boolean, JSON
from urllib.parse import quote_plus, urlparse
from dotenv import load_dotenv
import logging
import time

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv()

# Get Supabase project reference from URL
logger.info("Parsing Supabase URL...")
SUPABASE_URL = os.getenv('SUPABASE_URL')
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")

# Extract project reference from URL
project_ref = SUPABASE_URL.split('//')[1].split('.')[0]
logger.debug(f"Project reference: {project_ref}")

# Construct PostgreSQL connection string
DB_USER = "postgres"
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
DB_HOST = f"db.{project_ref}.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

logger.debug(f"Connection details - Host: {DB_HOST}, Port: {DB_PORT}, DB: {DB_NAME}, User: {DB_USER}")

# Create the database URL with password properly encoded
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

def test_connection():
    """Test database connection with timeout"""
    try:
        logger.info("Testing database connection...")
        start_time = time.time()
        
        # Create SQLAlchemy engine with connection timeout
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={
                'connect_timeout': 10,
                'application_name': 'create_auth0_users'
            }
        )
        
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            end_time = time.time()
            logger.info(f"Connection successful! Response time: {end_time - start_time:.2f} seconds")
            return True
            
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return False

def create_auth0_users_table():
    try:
        # Test connection first
        if not test_connection():
            logger.error("Failed to establish database connection. Aborting.")
            return
            
        logger.info("Creating SQLAlchemy engine...")
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={
                'connect_timeout': 10,
                'application_name': 'create_auth0_users'
            }
        )
        metadata = MetaData()
        
        # Create users table
        logger.info("Creating users table...")
        users = Table(
            'users',
            metadata,
            Column('id', String(36), primary_key=True),  # Auth0 user ID
            Column('email', String(255), unique=True, nullable=False),
            Column('username', String(255), unique=True, nullable=False),
            Column('auth0_id', String(255), unique=True, nullable=False),  # Auth0 sub claim
            Column('created_at', DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP')),
            Column('last_login', DateTime(timezone=True)),
            Column('is_active', Boolean, default=True),
            Column('email_verified', Boolean, default=False),
            Column('preferred_study_time', String(50)),
            Column('notification_preferences', JSON),
            Column('study_goals', JSON)
        )
        
        # Create the table
        metadata.create_all(engine)
        logger.info("Successfully created users table")
        
        # Create indexes for better query performance
        logger.info("Creating indexes...")
        index_sql = """
        CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """
        
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(index_sql))
                logger.info("Created indexes on users table")
        
        # Enable RLS and create policies
        logger.info("Setting up Row Level Security...")
        rls_sql = """
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Users can read own data" ON users;
        CREATE POLICY "Users can read own data" ON users
            FOR SELECT
            USING (auth0_id = current_user);
            
        DROP POLICY IF EXISTS "Users can update own data" ON users;
        CREATE POLICY "Users can update own data" ON users
            FOR UPDATE
            USING (auth0_id = current_user);
            
        DROP POLICY IF EXISTS "Service role can manage all users" ON users;
        CREATE POLICY "Service role can manage all users" ON users
            FOR ALL
            USING (auth.role() = 'service_role');
        """
        
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(rls_sql))
                logger.info("Enabled RLS and created policies")
        
        # Verify the table creation
        verify_sql = """
        SELECT COUNT(*) FROM users;
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(verify_sql)).scalar()
            logger.info(f"Table creation completed successfully! Total users: {result}")
        
    except Exception as e:
        logger.error(f"Error during table creation: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting create_auth0_users_table script...")
    create_auth0_users_table()
    logger.info("Script completed.") 