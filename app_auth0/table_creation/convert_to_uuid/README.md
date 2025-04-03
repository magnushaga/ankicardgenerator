# UUID Migration Script

This script converts all tables using `VARCHAR(36)` for ID fields to use the native PostgreSQL `UUID` type instead.

## Why Migrate to UUID?

- Better performance for indexing and comparisons
- Native type for UUID data in PostgreSQL
- Ensures data integrity (only valid UUIDs can be stored)
- More space-efficient than VARCHAR(36)
- Consistent with most of the existing database schema

## Prerequisites

- PostgreSQL database with the `uuid-ossp` extension enabled
- Python 3.x with psycopg2 installed
- Database connection credentials

## Usage

1. First, make sure you have a backup of your database:
```bash
pg_dump -U postgres -d your_database > backup_before_uuid_migration.sql
```

2. Run the migration script:
```bash
python migrate_to_uuid.py
```

## What the Script Does

1. Finds all tables with `VARCHAR(36)` ID columns
2. For each table:
   - Validates existing values are valid UUIDs
   - Converts the column type from `VARCHAR(36)` to `UUID`
   - Updates all foreign key references to use `UUID`
3. Handles the migration in a transaction-safe manner
4. Provides detailed logging of the migration process

## Safety Features

- Validates all existing values before conversion
- Uses transactions to ensure data integrity
- Rolls back changes if any errors occur
- Logs all operations for debugging

## Tables That Will Be Migrated

The script will migrate all tables that currently use `VARCHAR(36)` for their ID fields, including:
- users
- admin_roles
- admin_permissions
- media_files
- course_materials
- study_resources
- admin_role_permissions
- user_admin_roles
- admin_audit_logs

## Rollback

If you need to rollback the changes:
1. Use the backup created before running the script
2. Restore the database:
```bash
psql -U postgres -d your_database < backup_before_uuid_migration.sql
```

## Notes

- The script assumes all existing values in VARCHAR(36) columns are valid UUIDs
- The migration is done in a single transaction per table
- Foreign key constraints are automatically handled
- The script logs all operations for debugging purposes 