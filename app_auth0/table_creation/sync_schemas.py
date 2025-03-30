import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
import json
from typing import Dict, List, Set
import difflib
from schema_parser import parse_create_all_tables_file
import logging

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

def get_current_schema() -> Dict:
    """Extract current schema from Supabase database"""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    schema = {}
    
    for table_name in inspector.get_table_names():
        if table_name in ('spatial_ref_sys',):  # Skip system tables
            continue
            
        columns = []
        for column in inspector.get_columns(table_name):
            col_info = {
                'name': column['name'],
                'type': str(column['type']),
                'nullable': column.get('nullable', True),
                'default': str(column.get('default', 'None')),
            }
            columns.append(col_info)
            
        pks = inspector.get_pk_constraint(table_name)
        fks = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        schema[table_name] = {
            'columns': columns,
            'primary_key': pks,
            'foreign_keys': fks,
            'indexes': indexes
        }
    
    return schema

def get_target_schema() -> Dict:
    """Extract target schema from create_all_tables.py"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    create_tables_path = os.path.join(script_dir, 'create_all_tables.py')
    return parse_create_all_tables_file(create_tables_path)

def normalize_type(type_str: str) -> str:
    """Normalize type strings for comparison"""
    # Common type mappings
    type_map = {
        'VARCHAR': 'character varying',
        'TEXT': 'text',
        'INTEGER': 'integer',
        'FLOAT': 'double precision',
        'BOOLEAN': 'boolean',
        'TIMESTAMP WITH TIME ZONE': 'timestamp with time zone',
        'UUID': 'uuid'
    }
    
    type_str = type_str.upper()
    for k, v in type_map.items():
        if k in type_str:
            return v
    return type_str.lower()

def compare_schemas(current: Dict, target: Dict) -> tuple[List[str], List[str], Dict]:
    """Compare current and target schemas"""
    missing_tables = []
    extra_tables = []
    mismatched_tables = {}
    
    # Find missing and mismatched tables
    target_tables = set(target.keys())
    current_tables = set(current.keys())
    
    missing_tables = list(target_tables - current_tables)
    extra_tables = list(current_tables - target_tables)
    
    # Compare schema of existing tables
    for table in target_tables & current_tables:
        differences = []
        current_cols = {col['name']: col for col in current[table]['columns']}
        target_cols = {col['name']: col for col in target[table]['columns']}
        
        # Check for column differences
        for col_name in set(target_cols) | set(current_cols):
            if col_name not in current_cols:
                differences.append(f"Missing column: {col_name}")
            elif col_name not in target_cols:
                differences.append(f"Extra column: {col_name}")
            else:
                curr_col = current_cols[col_name]
                targ_col = target_cols[col_name]
                
                # Compare normalized types
                curr_type = normalize_type(curr_col['type'])
                targ_type = normalize_type(targ_col['type'])
                
                if curr_type != targ_type:
                    differences.append(f"Type mismatch for {col_name}: {curr_type} vs {targ_type}")
                if curr_col['nullable'] != targ_col['nullable']:
                    differences.append(f"Nullability mismatch for {col_name}")
                
                # Compare defaults if both are specified
                if curr_col['default'] != 'None' and targ_col['default'] != 'None':
                    if curr_col['default'] != targ_col['default']:
                        differences.append(f"Default value mismatch for {col_name}: {curr_col['default']} vs {targ_col['default']}")
        
        # Compare primary keys
        curr_pk = set(current[table]['primary_key'].get('constrained_columns', []))
        targ_pk = set(target[table]['primary_key'].get('constrained_columns', []))
        if curr_pk != targ_pk:
            differences.append(f"Primary key mismatch: {curr_pk} vs {targ_pk}")
        
        # Compare foreign keys
        curr_fks = {(tuple(fk['constrained_columns']), fk['referred_table'], tuple(fk['referred_columns']))
                   for fk in current[table]['foreign_keys']}
        targ_fks = {(tuple(fk['constrained_columns']), fk['referred_table'], tuple(fk['referred_columns']))
                   for fk in target[table]['foreign_keys']}
        if curr_fks != targ_fks:
            differences.append(f"Foreign key mismatch")
        
        if differences:
            mismatched_tables[table] = differences
    
    return missing_tables, extra_tables, mismatched_tables

def generate_migration_sql(current: Dict, target: Dict, missing_tables: List[str], mismatched_tables: Dict) -> str:
    """Generate SQL to migrate from current to target schema"""
    sql_commands = []
    
    # Create missing tables
    for table in missing_tables:
        table_def = target[table]
        columns = []
        constraints = []
        
        for col in table_def['columns']:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f"DEFAULT {col['default']}" if col['default'] != 'None' else ""
            columns.append(f"{col['name']} {col['type']} {nullable} {default}".strip())
        
        # Add primary key constraint
        if table_def['primary_key']['constrained_columns']:
            pk_cols = ', '.join(table_def['primary_key']['constrained_columns'])
            constraints.append(f"PRIMARY KEY ({pk_cols})")
        
        # Add foreign key constraints
        for fk in table_def['foreign_keys']:
            fk_cols = ', '.join(fk['constrained_columns'])
            ref_cols = ', '.join(fk['referred_columns'])
            constraints.append(
                f"FOREIGN KEY ({fk_cols}) REFERENCES {fk['referred_table']}({ref_cols}) ON DELETE CASCADE"
            )
        
        # Combine columns and constraints
        all_lines = columns + constraints
        
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {',\n            '.join(all_lines)}
        );
        """
        sql_commands.append(sql)
    
    # Alter existing tables
    for table, differences in mismatched_tables.items():
        current_cols = {col['name']: col for col in current[table]['columns']}
        target_cols = {col['name']: col for col in target[table]['columns']}
        
        for diff in differences:
            if diff.startswith("Missing column:"):
                col_name = diff.split(":")[1].strip()
                col = target_cols[col_name]
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f"DEFAULT {col['default']}" if col['default'] != 'None' else ""
                sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col['type']} {nullable} {default};"
                sql_commands.append(sql)
            elif diff.startswith("Type mismatch"):
                col_name = diff.split(":")[1].split()[0].strip()
                col = target_cols[col_name]
                sql = f"ALTER TABLE {table} ALTER COLUMN {col_name} TYPE {col['type']} USING {col_name}::{col['type']};"
                sql_commands.append(sql)
            elif diff.startswith("Nullability mismatch"):
                col_name = diff.split("for")[1].strip()
                col = target_cols[col_name]
                constraint = "SET NOT NULL" if not col['nullable'] else "DROP NOT NULL"
                sql = f"ALTER TABLE {table} ALTER COLUMN {col_name} {constraint};"
                sql_commands.append(sql)
    
    # Add indexes
    for table in target:
        if table in current:  # Only for existing tables
            for index in target[table]['indexes']:
                cols = ', '.join(index['column_names'])
                idx_name = f"idx_{table}_{('_'.join(index['column_names']))[:30]}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({cols});"
                sql_commands.append(sql)
    
    return "\n".join(sql_commands)

def update_models_py(current_schema: Dict):
    """Update models.py to match current database schema"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_path = os.path.join(script_dir, '..', 'models.py')
    
    # Generate new models based on current schema
    new_models = []
    for table_name, table_info in current_schema.items():
        class_name = "".join(word.capitalize() for word in table_name.split("_"))
        
        # Generate class definition
        class_def = [f"class {class_name}:"]
        
        # Add class docstring
        class_def.extend([
            '    """',
            f"    Model class for {table_name} table.",
            '    """'
        ])
        
        # Generate __init__ method
        init_params = []
        init_body = []
        
        for col in table_info['columns']:
            col_name = col['name']
            if col_name != 'id':  # Skip id as it's handled specially
                init_params.append(f"{col_name}=None")
            
            if col_name == 'id':
                init_body.append(f"        self.id = id or str(uuid.uuid4())")
            else:
                init_body.append(f"        self.{col_name} = {col_name}")
        
        init_method = [
            f"    def __init__(self, id=None, {', '.join(init_params)}):",
            *init_body
        ]
        
        # Add to_dict method
        to_dict_method = [
            "    def to_dict(self):",
            "        return {",
            *[f"            '{col['name']}': self.{col['name']}," for col in table_info['columns']],
            "        }"
        ]
        
        # Add from_dict method
        from_dict_method = [
            "    @classmethod",
            "    def from_dict(cls, data):",
            "        return cls(**data)"
        ]
        
        new_models.extend(class_def + [""] + init_method + [""] + to_dict_method + [""] + from_dict_method + ["", ""])
    
    # Write updated models
    with open(models_path, "w") as f:
        f.write("from datetime import datetime\n")
        f.write("from sqlalchemy.dialects.postgresql import UUID\n")
        f.write("import uuid\n\n")
        f.write("\n".join(new_models))

def main():
    logging.info("Extracting current schema from database...")
    current_schema = get_current_schema()
    
    logging.info("Loading target schema from create_all_tables.py...")
    target_schema = get_target_schema()
    
    logging.info("Comparing schemas...")
    missing_tables, extra_tables, mismatched_tables = compare_schemas(current_schema, target_schema)
    
    if missing_tables:
        logging.info("\nMissing tables that need to be created:")
        for table in missing_tables:
            logging.info(f"  - {table}")
    
    if extra_tables:
        logging.info("\nExtra tables in database not in target schema:")
        for table in extra_tables:
            logging.info(f"  - {table}")
    
    if mismatched_tables:
        logging.info("\nTables with mismatched schemas:")
        for table, differences in mismatched_tables.items():
            logging.info(f"\n  {table}:")
            for diff in differences:
                logging.info(f"    - {diff}")
    
    logging.info("\nGenerating migration SQL...")
    sql = generate_migration_sql(current_schema, target_schema, missing_tables, mismatched_tables)
    
    # Save SQL to file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, 'migration.sql')
    with open(sql_path, "w") as f:
        f.write(sql)
    logging.info(f"Migration SQL saved to {sql_path}")
    
    logging.info("\nUpdating models.py...")
    update_models_py(current_schema)
    logging.info("models.py has been updated to match current schema")

if __name__ == "__main__":
    main() 