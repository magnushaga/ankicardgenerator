from supabase import create_client
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_supabase_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        
        logger.info(f"Testing connection to Supabase URL: {SUPABASE_URL}")
        
        if not all([SUPABASE_URL, SUPABASE_KEY]):
            raise ValueError("Missing Supabase credentials in .env file")
        
        # Create Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Create test table using PostgreSQL syntax
        create_table_sql = """
        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- Drop existing table if it exists
        DROP TABLE IF EXISTS public.connection_test;

        -- Create the test table
        CREATE TABLE public.connection_test (
            id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
            created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
            test_value text
        );

        -- Set up RLS policies
        ALTER TABLE public.connection_test ENABLE ROW LEVEL SECURITY;

        -- Allow full access to authenticated users
        CREATE POLICY "Enable all access for authenticated users"
        ON public.connection_test
        FOR ALL
        USING (auth.role() = 'authenticated')
        WITH CHECK (auth.role() = 'authenticated');

        -- Grant access to anon and authenticated roles
        GRANT ALL ON public.connection_test TO anon;
        GRANT ALL ON public.connection_test TO authenticated;
        """

        # Execute the table creation SQL
        logger.info("Creating test table...")
        result = supabase.table("connection_test").select("*").execute()
        if "relation" in str(result):
            # Table doesn't exist, create it using raw SQL through Supabase dashboard
            logger.info("Please execute the following SQL in your Supabase dashboard SQL editor:")
            logger.info(create_table_sql)
            logger.info("\nAfter creating the table, run this test again.")
            return False

        # Test insert
        test_data = {
            'test_value': f'Test connection at {datetime.utcnow().isoformat()}'
        }
        
        logger.info("Inserting test data...")
        insert_result = supabase.table('connection_test').insert(test_data).execute()
        logger.info(f"Successfully inserted test data: {insert_result.data}")
        
        # Test select
        logger.info("Retrieving test data...")
        select_result = supabase.table('connection_test').select('*').limit(1).execute()
        logger.info(f"Successfully retrieved test data: {select_result.data}")
        
        logger.info("All connection tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Supabase connection: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Supabase connection...")
    print("\nFirst, execute this SQL in your Supabase dashboard SQL editor:")
    print("""
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Drop existing table if it exists
    DROP TABLE IF EXISTS public.connection_test;

    -- Create the test table
    CREATE TABLE public.connection_test (
        id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
        created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
        test_value text
    );

    -- Set up RLS policies
    ALTER TABLE public.connection_test ENABLE ROW LEVEL SECURITY;

    -- Allow full access to authenticated users
    CREATE POLICY "Enable all access for authenticated users"
    ON public.connection_test
    FOR ALL
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

    -- Grant access to anon and authenticated roles
    GRANT ALL ON public.connection_test TO anon;
    GRANT ALL ON public.connection_test TO authenticated;
    """)
    
    print("\nAfter executing the SQL, press Enter to continue with the connection test...")
    input()
    
    success = test_supabase_connection()
    if success:
        print("✅ Supabase connection test successful!")
    else:
        print("❌ Supabase connection test failed!") 