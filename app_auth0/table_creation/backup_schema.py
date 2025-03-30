import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
import json
from datetime import datetime
import logging
from typing import Dict, List
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Supabase database configuration
DB_USER = "postgres"
DB_PASSWORD = "H@ukerkul120700"
DB_HOST = "db.wxisvjmhokwtjwcqaarb.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

# URL encode the password
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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

def generate_recreation_sql(schema: Dict) -> str:
    """Generate SQL to recreate the database schema"""
    sql_commands = []
    
    # Create tables in order of dependencies
    tables = list(schema.keys())
    created_tables = set()
    
    while tables:
        for table in tables[:]:  # Create a copy to iterate
            # Check if all dependencies are created
            dependencies = set()
            for fk in schema[table]['foreign_keys']:
                dependencies.add(fk['referred_table'])
            
            if dependencies.issubset(created_tables):
                # Generate CREATE TABLE statement
                columns = []
                constraints = []
                
                # Add columns
                for col in schema[table]['columns']:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    default = f"DEFAULT {col['default']}" if col['default'] != 'None' else ""
                    columns.append(f"{col['name']} {col['type']} {nullable} {default}".strip())
                
                # Add primary key
                if schema[table]['primary_key']['constrained_columns']:
                    pk_cols = ', '.join(schema[table]['primary_key']['constrained_columns'])
                    constraints.append(f"PRIMARY KEY ({pk_cols})")
                
                # Add foreign keys
                for fk in schema[table]['foreign_keys']:
                    fk_cols = ', '.join(fk['constrained_columns'])
                    ref_cols = ', '.join(fk['referred_columns'])
                    constraints.append(
                        f"FOREIGN KEY ({fk_cols}) REFERENCES {fk['referred_table']}({ref_cols}) ON DELETE CASCADE"
                    )
                
                # Combine columns and constraints
                all_lines = columns + constraints
                
                sql = f"CREATE TABLE IF NOT EXISTS {table} (\n"
                sql += "    " + ",\n    ".join(all_lines)
                sql += "\n);"
                
                sql_commands.append(sql)
                
                # Add indexes
                for index in schema[table]['indexes']:
                    cols = ', '.join(index['column_names'])
                    idx_name = f"idx_{table}_{('_'.join(index['column_names']))[:30]}"
                    sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({cols});"
                    sql_commands.append(sql)
                
                created_tables.add(table)
                tables.remove(table)
    
    return "\n\n".join(sql_commands)

def generate_models_py(schema: Dict) -> str:
    """Generate Python models from schema"""
    models = []
    
    # Add imports
    models.extend([
        "from datetime import datetime",
        "from sqlalchemy.dialects.postgresql import UUID",
        "import uuid\n"
    ])
    
    # Generate model classes
    for table_name, table_info in schema.items():
        class_name = "".join(word.capitalize() for word in table_name.split("_"))
        
        # Class definition with docstring
        models.extend([
            f"class {class_name}:",
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
        
        models.extend([
            "",
            *init_method,
            "",
            *to_dict_method,
            "",
            *from_dict_method,
            ""
        ])
    
    return "\n".join(models)

def main():
    # Create backup directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(script_dir, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamp for backup files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    logging.info("Extracting current schema from database...")
    schema = get_current_schema()
    
    # Save raw schema JSON
    schema_path = os.path.join(backup_dir, f'schema_{timestamp}.json')
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2)
    logging.info(f"Schema saved to {schema_path}")
    
    # Generate and save recreation SQL
    sql = generate_recreation_sql(schema)
    sql_path = os.path.join(backup_dir, f'recreate_schema_{timestamp}.sql')
    with open(sql_path, 'w') as f:
        f.write(sql)
    logging.info(f"Recreation SQL saved to {sql_path}")
    
    # Generate and save models.py
    models = generate_models_py(schema)
    models_path = os.path.join(backup_dir, f'models_{timestamp}.py')
    with open(models_path, 'w') as f:
        f.write(models)
    logging.info(f"Models saved to {models_path}")
    
    # Update current models.py
    current_models_path = os.path.join(script_dir, '..', 'models.py')
    with open(current_models_path, 'w') as f:
        f.write(models)
    logging.info(f"Current models.py updated")

if __name__ == "__main__":
    main() 