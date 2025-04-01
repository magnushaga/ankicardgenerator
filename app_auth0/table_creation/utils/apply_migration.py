import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def apply_migration(dry_run: bool = True):
    """Apply the migration SQL to the database"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, 'migration.sql')
    
    if not os.path.exists(sql_path):
        logging.error(f"Migration file not found: {sql_path}")
        return
    
    with open(sql_path, 'r') as f:
        migration_sql = f.read()
    
    if not migration_sql.strip():
        logging.info("No migration SQL to apply.")
        return
    
    # Split SQL into individual statements
    statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
    
    if dry_run:
        logging.info("DRY RUN - The following SQL statements would be executed:")
        for stmt in statements:
            logging.info("\n" + stmt + ";")
        return
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        try:
            for stmt in statements:
                logging.info(f"Executing:\n{stmt};")
                connection.execute(text(stmt))
            
            # Commit transaction
            trans.commit()
            logging.info("Migration completed successfully.")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            logging.error(f"Error applying migration: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Apply database migration')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the migration (without this flag, it will only show what would be done)')
    args = parser.parse_args()
    
    apply_migration(dry_run=not args.execute)

if __name__ == "__main__":
    main() 