import os
import sys
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models_proposed_dynamic import Base

def drop_and_recreate_tables(connection_string):
    """
    Drop all non-admin tables and recreate them based on models_proposed_dynamic.py
    """
    try:
        # Create engine
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        # Get all tables in the database
        db_tables = inspector.get_table_names()
        print(f"Found {len(db_tables)} tables in the database")
        
        # Get all tables defined in models
        model_tables = Base.metadata.tables.keys()
        print(f"Found {len(model_tables)} tables defined in models_proposed_dynamic.py")
        
        # Define admin tables that should not be dropped
        admin_tables = [
            'admin_roles',
            'admin_permissions',
            'admin_role_permissions',
            'user_admin_roles',
            'admin_audit_logs'
        ]
        
        # Get tables to drop (all non-admin tables)
        tables_to_drop = [table for table in db_tables if table not in admin_tables]
        
        print(f"Dropping {len(tables_to_drop)} non-admin tables...")
        
        # Drop tables
        with engine.connect() as conn:
            for table in tables_to_drop:
                print(f"Dropping table: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            conn.commit()
        
        print("All non-admin tables dropped successfully")
        
        # Create tables
        print("Creating tables based on models_proposed_dynamic.py...")
        Base.metadata.create_all(engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        print(f"Database now has {len(created_tables)} tables")
        
        # Check for missing tables
        missing_tables = set(model_tables) - set(created_tables)
        if missing_tables:
            print(f"\nWARNING: {len(missing_tables)} tables are missing from the database:")
            for table in sorted(missing_tables):
                print(f"  - {table}")
        else:
            print("\nAll tables from models are present in the database")
        
        print("All tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"Error during table operations: {str(e)}")
        return False

if __name__ == "__main__":
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        success = drop_and_recreate_tables(connection_string)
        if success:
            print("\n✅ Table operations completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Table operations failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 