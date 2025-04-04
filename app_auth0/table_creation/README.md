# Database Table Creation Scripts

This directory contains scripts for creating the database tables in Supabase PostgreSQL for the application.

## Directory Structure

```
table_creation/
├── core/
│   └── create_tables.py     # Core table creation logic
├── run_migrations.py        # Main script to run all migrations
└── README.md               # This file
```

## Prerequisites

- Python 3.7+
- SQLAlchemy
- psycopg2-binary

## Installation

1. Install required packages:
```bash
pip install sqlalchemy psycopg2-binary
```

## Usage

To create all database tables:

1. Navigate to the table_creation directory:
   ```bash
cd app_auth0/table_creation
   ```

2. Run the migration script:
   ```bash
python run_migrations.py
```

## Tables Created

The script will create all tables defined in `models_proposed_dynamic.py`, including:

- Core Tables:
  - users
  - admin_roles
  - admin_permissions
  - admin_role_permissions
  - user_admin_roles
  - admin_audit_logs

- Content Tables:
  - courses
  - course_content
  - content_chapters
  - content_sections
  - study_materials
  - exam_content

- Study Organization:
  - semester_plans
  - semester_courses
  - weekly_plans
  - weekly_content

- User Content:
  - user_uploads
  - content_mappings
  - ai_generated_content
  - study_material_organization
  - study_material_items

- And many more...

## Error Handling

The scripts include comprehensive error handling and will:
- Report specific database errors
- Handle connection issues
- Provide clear error messages
- Roll back failed operations

## Troubleshooting

If you encounter errors:

1. Check your database connection string
2. Ensure you have the necessary permissions
3. Verify that no tables with conflicting names exist
4. Check the error message for specific issues

## Security Note

The connection string in the scripts includes the database password. In a production environment, you should:
1. Use environment variables for sensitive information
2. Never commit credentials to version control
3. Use appropriate access controls and roles
