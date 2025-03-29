import os
from sqlalchemy import create_engine, text
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
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')  # You'll need to add this to your .env file
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
                'application_name': 'delete_users_table'
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

def delete_users_table():
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
                'application_name': 'delete_users_table'
            }
        )
        
        # First, check if the users table exists
        logger.info("Checking if users table exists...")
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
                logger.warning("Users table does not exist. Nothing to delete.")
                return
            logger.info("Users table exists, proceeding with deletion...")
        
        # Drop the users table and its dependencies
        logger.info("Dropping users table...")
        drop_table_sql = """
        DROP TABLE IF EXISTS users CASCADE;
        """
        
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(drop_table_sql))
                logger.info("Successfully deleted users table and its dependencies")
        
        # Verify the deletion
        logger.info("Verifying deletion...")
        verify_sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        );
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(verify_sql)).scalar()
            if not result:
                logger.info("Verification successful: users table has been deleted")
            else:
                logger.error("Verification failed: users table still exists")
        
    except Exception as e:
        logger.error(f"Error during table deletion: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting delete_users_table script...")
    delete_users_table()
    logger.info("Script completed.") 