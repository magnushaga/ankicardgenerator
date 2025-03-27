from dotenv import load_dotenv
import os
from supabase import create_client
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_supabase_connection():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    # Log configuration (without showing the full key)
    logger.debug(f"Supabase URL: {supabase_url}")
    logger.debug(f"Supabase Key present: {'Yes' if supabase_key else 'No'}")
    if supabase_key:
        logger.debug(f"Key starts with: {supabase_key[:10]}...")
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        logger.debug("Supabase client created successfully")
        
        # Test a simple query
        response = supabase.table('users').select("*").limit(1).execute()
        logger.debug("Test query executed successfully")
        logger.debug(f"Response: {response}")
        
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        logger.error(f"Error testing Supabase connection: {str(e)}")
        print("❌ Supabase connection failed!")
        return False

if __name__ == "__main__":
    test_supabase_connection() 