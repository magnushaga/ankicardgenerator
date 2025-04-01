# Table Creation Scripts

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
