import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging
import argparse
from datetime import datetime

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

def get_latest_backup_file(backup_dir: str, pattern: str) -> str:
    """Get the most recent backup file matching the pattern"""
    files = [f for f in os.listdir(backup_dir) if f.startswith(pattern)]
    if not files:
        raise FileNotFoundError(f"No backup files found matching pattern: {pattern}")
    
    # Sort by timestamp in filename
    latest_file = max(files, key=lambda x: x.split('_')[1])
    return os.path.join(backup_dir, latest_file)

def recreate_database(backup_file: str = None, dry_run: bool = True):
    """Recreate the database schema from a backup file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(script_dir, 'backups')
    
    if not backup_file:
        # Get the latest recreation SQL file
        backup_file = get_latest_backup_file(backup_dir, 'recreate_schema_')
    
    if not os.path.exists(backup_file):
        logging.error(f"Backup file not found: {backup_file}")
        return
    
    with open(backup_file, 'r') as f:
        recreation_sql = f.read()
    
    if not recreation_sql.strip():
        logging.info("No SQL to execute.")
        return
    
    # Split SQL into individual statements
    statements = [stmt.strip() for stmt in recreation_sql.split(';') if stmt.strip()]
    
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
            # Drop existing tables (in reverse order of creation)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            for table in reversed(tables):
                if table not in ('spatial_ref_sys',):  # Skip system tables
                    logging.info(f"Dropping table: {table}")
                    connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            
            # Create new tables
            for stmt in statements:
                logging.info(f"Executing:\n{stmt};")
                connection.execute(text(stmt))
            
            # Commit transaction
            trans.commit()
            logging.info("Database recreation completed successfully.")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            logging.error(f"Error recreating database: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Recreate database schema from backup')
    parser.add_argument('--backup-file', help='Path to specific backup file to use')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the recreation (without this flag, it will only show what would be done)')
    args = parser.parse_args()
    
    recreate_database(args.backup_file, dry_run=not args.execute)

if __name__ == "__main__":
    main() 