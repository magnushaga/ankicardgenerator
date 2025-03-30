import re
from typing import Dict, List

def parse_create_table_sql(sql: str) -> Dict:
    """Parse a CREATE TABLE SQL statement and extract schema information"""
    # Extract table name
    table_match = re.search(r'CREATE TABLE IF NOT EXISTS (\w+)', sql)
    if not table_match:
        return None
    
    table_name = table_match.group(1)
    
    # Extract columns
    columns = []
    column_pattern = re.compile(r'(\w+)\s+([\w\(\)]+)(?:\s+(\w+))?(?:\s+DEFAULT\s+([^,\n]+))?')
    
    # Get the content between parentheses
    content_match = re.search(r'\((.*?)\);', sql, re.DOTALL)
    if not content_match:
        return None
    
    content = content_match.group(1)
    
    # Split by commas, but not within parentheses
    lines = []
    current_line = []
    paren_count = 0
    
    for char in content:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif char == ',' and paren_count == 0:
            lines.append(''.join(current_line).strip())
            current_line = []
            continue
        
        current_line.append(char)
    
    if current_line:
        lines.append(''.join(current_line).strip())
    
    # Process each column definition
    for line in lines:
        if 'PRIMARY KEY' in line.upper() or 'FOREIGN KEY' in line.upper() or 'UNIQUE' in line.upper():
            continue
            
        match = column_pattern.search(line)
        if match:
            name, type_, nullable, default = match.groups()
            
            columns.append({
                'name': name,
                'type': type_,
                'nullable': 'NOT NULL' not in line.upper(),
                'default': default if default else None
            })
    
    # Extract primary keys
    pk_match = re.search(r'PRIMARY KEY\s*\((.*?)\)', content)
    primary_key = {'constrained_columns': []} if not pk_match else {
        'constrained_columns': [col.strip() for col in pk_match.group(1).split(',')]
    }
    
    # Extract foreign keys
    foreign_keys = []
    fk_pattern = re.compile(r'FOREIGN KEY\s*\((.*?)\)\s*REFERENCES\s*(\w+)\s*\((.*?)\)')
    for match in fk_pattern.finditer(content):
        foreign_keys.append({
            'constrained_columns': [col.strip() for col in match.group(1).split(',')],
            'referred_table': match.group(2),
            'referred_columns': [col.strip() for col in match.group(3).split(',')]
        })
    
    # Extract indexes (from CREATE INDEX statements)
    indexes = []
    index_pattern = re.compile(r'CREATE INDEX.*?ON\s+' + table_name + r'\s*\((.*?)\)', re.IGNORECASE)
    for match in index_pattern.finditer(sql):
        indexes.append({
            'column_names': [col.strip() for col in match.group(1).split(',')]
        })
    
    return {
        'columns': columns,
        'primary_key': primary_key,
        'foreign_keys': foreign_keys,
        'indexes': indexes
    }

def parse_create_all_tables_file(file_path: str) -> Dict[str, Dict]:
    """Parse the create_all_tables.py file and extract all table schemas"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract all CREATE TABLE statements
    create_statements = re.finditer(r'connection\.execute\(text\("""(.*?)"""\)\)', content, re.DOTALL)
    
    schemas = {}
    for match in create_statements:
        sql = match.group(1).strip()
        if sql.startswith('CREATE TABLE'):
            table_schema = parse_create_table_sql(sql)
            if table_schema:
                table_name = re.search(r'CREATE TABLE IF NOT EXISTS (\w+)', sql).group(1)
                schemas[table_name] = table_schema
    
    return schemas 