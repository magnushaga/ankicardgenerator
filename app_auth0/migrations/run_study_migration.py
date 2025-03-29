import os
from dotenv import load_dotenv
from supabase_config import supabase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    try:
        # Read the SQL file
        with open('migrations/study_tables.sql', 'r') as file:
            sql = file.read()
        
        # Execute the SQL
        result = supabase.postgrest.rpc('exec_sql', {'sql': sql}).execute()
        
        logger.info("Successfully created study tables and policies")
        return True
        
    except Exception as e:
        logger.error(f"Error running migration: {e}")
        return False

if __name__ == "__main__":
    load_dotenv()
    run_migration() 