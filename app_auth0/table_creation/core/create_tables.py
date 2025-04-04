from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import sys
import os
from urllib.parse import quote_plus

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models_proposed_dynamic import Base

def create_database_tables(connection_string):
    """
    Create all database tables defined in the models
    """
    try:
        # Create engine
        engine = create_engine(connection_string)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("Successfully created all database tables.")
        
        # Create session factory
        Session = sessionmaker(bind=engine)
        return Session()
        
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        session = create_database_tables(connection_string)
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"Failed to set up database: {str(e)}")
        sys.exit(1) 