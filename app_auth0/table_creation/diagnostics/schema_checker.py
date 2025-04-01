import os
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import inspect
from typing import Dict, List, Any
import sys
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add the app_auth0 directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import models directly
from models import (
    Users, Decks, Cards, ContentTypes, ContentTypeRelationships,
    RatingCategories, EducationalInstitutions, InstitutionDepartments,
    SubjectCategories, SubjectSubcategories, ContentSubjectRelationships,
    CourseMaterials, StudyResources, ContentReports, Textbooks
)

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="H@ukerkul120700",
            host="db.wxisvjmhokwtjwcqaarb.supabase.co",
            port="5432"
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get the schema of a specific table."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get column information
        cur.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cur.fetchall()
        
        # Get primary key information
        cur.execute("""
            SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = %s;
        """, (table_name,))
        
        primary_keys = [row[0] for row in cur.fetchall()]
        
        # Get foreign key information
        cur.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
        """, (table_name,))
        
        foreign_keys = cur.fetchall()
        
        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys
        }
        
    finally:
        cur.close()
        conn.close()

def get_model_definition(model_class) -> Dict[str, Any]:
    """Get the model definition from the model class."""
    # Get the __init__ method
    init_method = model_class.__init__
    
    # Get the parameters from the __init__ method
    parameters = inspect.signature(init_method).parameters
    
    # Get the docstring
    docstring = inspect.getdoc(model_class)
    
    return {
        'parameters': parameters,
        'docstring': docstring
    }

def compare_schema_and_model(table_name: str, model_class) -> Dict[str, Any]:
    """Compare database schema with model definition."""
    schema = get_table_schema(table_name)
    model = get_model_definition(model_class)
    
    # Convert schema columns to a set of names
    schema_columns = {col[0] for col in schema['columns']}
    
    # Convert model parameters to a set of names
    model_parameters = {name for name in model['parameters'].keys() if name != 'self'}
    
    # Find discrepancies
    missing_in_schema = model_parameters - schema_columns
    missing_in_model = schema_columns - model_parameters
    
    return {
        'table_name': table_name,
        'model_name': model_class.__name__,
        'missing_in_schema': missing_in_schema,
        'missing_in_model': missing_in_model,
        'schema': schema,
        'model': model
    }

def check_relationships(table_name: str) -> List[Dict[str, Any]]:
    """Check foreign key relationships in a table."""
    schema = get_table_schema(table_name)
    issues = []
    
    for fk in schema['foreign_keys']:
        column_name, foreign_table, foreign_column = fk
        
        # Check if the referenced table exists
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (foreign_table,))
            
            if not cur.fetchone()[0]:
                issues.append({
                    'type': 'missing_table',
                    'table': table_name,
                    'column': column_name,
                    'referenced_table': foreign_table
                })
                
        finally:
            cur.close()
            conn.close()
    
    return issues

def main():
    """Main function to run schema diagnostics."""
    # Define table and model mappings
    table_model_mappings = {
        'users': Users,
        'decks': Decks,
        'cards': Cards,
        'content_types': ContentTypes,
        'content_type_relationships': ContentTypeRelationships,
        'rating_categories': RatingCategories,
        'educational_institutions': EducationalInstitutions,
        'institution_departments': InstitutionDepartments,
        'subject_categories': SubjectCategories,
        'subject_subcategories': SubjectSubcategories,
        'content_subject_relationships': ContentSubjectRelationships,
        'course_materials': CourseMaterials,
        'study_resources': StudyResources,
        'content_reports': ContentReports,
        'textbooks': Textbooks
    }
    
    all_issues = []
    
    for table_name, model_class in table_model_mappings.items():
        logger.info(f"Checking {table_name}...")
        
        try:
            # Compare schema with model
            comparison = compare_schema_and_model(table_name, model_class)
            
            if comparison['missing_in_schema']:
                logger.warning(f"Fields missing in schema for {table_name}: {comparison['missing_in_schema']}")
                all_issues.append({
                    'type': 'missing_in_schema',
                    'table': table_name,
                    'fields': comparison['missing_in_schema']
                })
            
            if comparison['missing_in_model']:
                logger.warning(f"Fields missing in model for {table_name}: {comparison['missing_in_model']}")
                all_issues.append({
                    'type': 'missing_in_model',
                    'table': table_name,
                    'fields': comparison['missing_in_model']
                })
            
            # Check relationships
            relationship_issues = check_relationships(table_name)
            all_issues.extend(relationship_issues)
            
        except Exception as e:
            logger.error(f"Error checking {table_name}: {e}")
            all_issues.append({
                'type': 'error',
                'table': table_name,
                'error': str(e)
            })
    
    # Print summary
    logger.info("\nDiagnostics Summary:")
    logger.info(f"Total issues found: {len(all_issues)}")
    
    if all_issues:
        logger.info("\nDetailed Issues:")
        for issue in all_issues:
            if issue['type'] == 'missing_in_schema':
                logger.warning(f"Table {issue['table']} is missing fields in schema: {issue['fields']}")
            elif issue['type'] == 'missing_in_model':
                logger.warning(f"Table {issue['table']} has fields not in model: {issue['fields']}")
            elif issue['type'] == 'missing_table':
                logger.warning(f"Table {issue['table']} references missing table {issue['referenced_table']}")
            elif issue['type'] == 'error':
                logger.error(f"Error checking table {issue['table']}: {issue['error']}")
    else:
        logger.info("No issues found! Schema and models are in sync.")

if __name__ == "__main__":
    main() 