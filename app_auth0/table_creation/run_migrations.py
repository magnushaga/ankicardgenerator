import os
import sys
from urllib.parse import quote_plus
from core.create_tables import create_database_tables

def main():
    """
    Main function to run all database migrations in the correct order
    """
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        print("Starting database setup...")
        
        # Create all tables
        session = create_database_tables(connection_string)
        
        print("\nDatabase setup completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\nError during database setup: {str(e)}")
        return 1
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    sys.exit(main()) 