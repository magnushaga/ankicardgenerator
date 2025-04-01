import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create the new directory structure"""
    directories = [
        'core',
        'subjects',
        'decks',
        'admin',
        'subscriptions',
        'utils'
    ]
    
    base_path = Path('table_creation')
    
    for dir_name in directories:
        dir_path = base_path / dir_name
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

def move_files():
    """Move files to their new locations"""
    moves = {
        # Core files
        'create_all_tables.py': 'core/',
        'sync_schemas.py': 'core/',
        'schema_parser.py': 'core/',
        'recreate_database.py': 'core/',
        
        # Subject files
        'create_subject_dimensions_fact.py': 'subjects/',
        'create_category_tables.py': 'subjects/',
        
        # Deck files
        'create_live_deck_tables.py': 'decks/',
        
        # Admin files
        'create_admin_tables.py': 'admin/',
        'assign_admin_role.py': 'admin/',
        'drop_admin_tables.py': 'admin/',
        
        # Subscription files
        'create_subscription_tables.py': 'subscriptions/',
        
        # Utility files
        'backup_schema.py': 'utils/',
        'apply_migration.py': 'utils/',
        'drop_missing_tables.py': 'utils/'
    }
    
    base_path = Path('table_creation')
    
    for file_name, target_dir in moves.items():
        source_path = base_path / file_name
        target_path = base_path / target_dir / file_name
        
        if source_path.exists():
            shutil.move(str(source_path), str(target_path))
            logger.info(f"Moved {file_name} to {target_dir}")
        else:
            logger.warning(f"File not found: {file_name}")

def create_init_files():
    """Create __init__.py files in each directory"""
    base_path = Path('table_creation')
    directories = ['core', 'subjects', 'decks', 'admin', 'subscriptions', 'utils']
    
    for dir_name in directories:
        init_file = base_path / dir_name / '__init__.py'
        init_file.touch()
        logger.info(f"Created __init__.py in {dir_name}")

def create_readme():
    """Create a README.md file explaining the structure"""
    readme_content = """# Table Creation Scripts

This directory contains scripts for creating and managing database tables.

## Directory Structure

- `core/`: Core database creation and schema management scripts
  - create_all_tables.py
  - sync_schemas.py
  - schema_parser.py
  - recreate_database.py

- `subjects/`: Subject-related table creation scripts
  - create_subject_dimensions_fact.py
  - create_category_tables.py

- `decks/`: Deck-related table creation scripts
  - create_live_deck_tables.py

- `admin/`: Admin-related table creation scripts
  - create_admin_tables.py
  - assign_admin_role.py
  - drop_admin_tables.py

- `subscriptions/`: Subscription-related table creation scripts
  - create_subscription_tables.py

- `utils/`: Utility scripts for database management
  - backup_schema.py
  - apply_migration.py
  - drop_missing_tables.py

- `backups/`: Database backup files

## Usage

1. Core setup:
   ```bash
   python core/create_all_tables.py
   python core/sync_schemas.py
   ```

2. Subject tables:
   ```bash
   python subjects/create_subject_dimensions_fact.py
   python subjects/create_category_tables.py
   ```

3. Deck tables:
   ```bash
   python decks/create_live_deck_tables.py
   ```

4. Admin setup:
   ```bash
   python admin/create_admin_tables.py
   python admin/assign_admin_role.py
   ```

5. Subscription setup:
   ```bash
   python subscriptions/create_subscription_tables.py
   ```

## Utilities

- Backup database: `python utils/backup_schema.py`
- Apply migrations: `python utils/apply_migration.py`
- Drop missing tables: `python utils/drop_missing_tables.py`
"""
    
    readme_path = Path('table_creation') / 'README.md'
    readme_path.write_text(readme_content)
    logger.info("Created README.md")

def main():
    """Main function to reorganize the table_creation folder"""
    try:
        logger.info("Starting table_creation folder reorganization")
        
        # Create directory structure
        create_directory_structure()
        
        # Move files to their new locations
        move_files()
        
        # Create __init__.py files
        create_init_files()
        
        # Create README.md
        create_readme()
        
        logger.info("Successfully completed table_creation folder reorganization")
        
    except Exception as e:
        logger.error(f"Error during reorganization: {str(e)}")
        raise

if __name__ == "__main__":
    main() 