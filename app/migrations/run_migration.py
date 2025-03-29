import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Database connection details
DB_PASSWORD = "H@ukerkul120700"
DB_HOST = "db.wxisvjmhokwtjwcqaarb.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"

# Create the database URL with password properly encoded
encoded_password = quote_plus(DB_PASSWORD)
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def run_migration():
    try:
        # Create SQLAlchemy engine
        engine = create_engine(DATABASE_URL)
        
        # Read the migration SQL file
        with open('app/migrations/update_users_table.sql', 'r') as file:
            migration_sql = file.read()
        
        # Execute the migration
        with engine.connect() as connection:
            # Begin transaction
            with connection.begin():
                # Execute each statement separately
                for statement in migration_sql.split(';'):
                    if statement.strip():
                        connection.execute(text(statement))
                        print(f"Executed: {statement[:100]}...")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration() 