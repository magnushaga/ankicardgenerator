from supabase import create_client
import os
from dotenv import load_dotenv
import logging

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

def test_connection():
    try:
        # Create Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Successfully created Supabase client")

        # Test connection by querying the users table
        logger.info("Attempting to query public.users table...")
        response = supabase.table('users').select('*').limit(1).execute()
        
        if response.data:
            logger.info("Successfully queried users table")
            logger.info(f"Sample user data: {response.data[0]}")
            return True
        else:
            logger.warning("No data found in users table")
            return False

    except Exception as e:
        logger.error(f"Error testing database connection: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database connection test...")
    success = test_connection()
    if success:
        logger.info("Database connection test completed successfully")
    else:
        logger.error("Database connection test failed")