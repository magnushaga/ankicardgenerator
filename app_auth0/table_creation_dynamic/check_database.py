import os
import sys
from sqlalchemy import create_engine, inspect, text
from urllib.parse import quote_plus

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models_proposed_dynamic import Base

def check_database_structure(connection_string):
    """
    Check the database structure and verify all tables from models_proposed_dynamic.py
    """
    try:
        # Create engine
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        # Get all tables in the database
        db_tables = inspector.get_table_names()
        print(f"Found {len(db_tables)} tables in the database")
        
        # Get all tables defined in models
        model_tables = Base.metadata.tables.keys()
        print(f"Found {len(model_tables)} tables defined in models_proposed_dynamic.py")
        
        # Check for missing tables
        missing_tables = set(model_tables) - set(db_tables)
        if missing_tables:
            print(f"\nWARNING: {len(missing_tables)} tables are missing from the database:")
            for table in sorted(missing_tables):
                print(f"  - {table}")
        else:
            print("\nAll tables from models are present in the database")
        
        # Check for extra tables
        extra_tables = set(db_tables) - set(model_tables)
        if extra_tables:
            print(f"\nNOTE: {len(extra_tables)} tables exist in the database but are not defined in models:")
            for table in sorted(extra_tables):
                print(f"  - {table}")
        
        # Check table columns
        print("\nChecking table columns...")
        column_issues = []
        
        for table_name in model_tables:
            if table_name in db_tables:
                model_columns = {c.name: c for c in Base.metadata.tables[table_name].columns}
                db_columns = {c['name']: c for c in inspector.get_columns(table_name)}
                
                # Check for missing columns
                missing_columns = set(model_columns.keys()) - set(db_columns.keys())
                if missing_columns:
                    column_issues.append(f"Table '{table_name}' is missing columns: {', '.join(missing_columns)}")
                
                # Check for extra columns
                extra_columns = set(db_columns.keys()) - set(model_columns.keys())
                if extra_columns:
                    column_issues.append(f"Table '{table_name}' has extra columns: {', '.join(extra_columns)}")
                
                # Check column types
                for col_name, model_col in model_columns.items():
                    if col_name in db_columns:
                        db_col = db_columns[col_name]
                        model_type = str(model_col.type)
                        db_type = str(db_col['type'])
                        
                        # Simple type comparison (can be enhanced for more complex types)
                        if model_type.lower() != db_type.lower():
                            column_issues.append(f"Table '{table_name}', column '{col_name}': model type '{model_type}' != db type '{db_type}'")
        
        if column_issues:
            print(f"\nWARNING: Found {len(column_issues)} column issues:")
            for issue in column_issues:
                print(f"  - {issue}")
        else:
            print("All table columns match the model definitions")
        
        # Check foreign keys
        print("\nChecking foreign keys...")
        fk_issues = []
        
        for table_name in model_tables:
            if table_name in db_tables:
                model_fks = Base.metadata.tables[table_name].foreign_keys
                db_fks = inspector.get_foreign_keys(table_name)
                
                # Simple check for number of foreign keys
                if len(model_fks) != len(db_fks):
                    fk_issues.append(f"Table '{table_name}': model has {len(model_fks)} foreign keys, database has {len(db_fks)}")
        
        if fk_issues:
            print(f"\nWARNING: Found {len(fk_issues)} foreign key issues:")
            for issue in fk_issues:
                print(f"  - {issue}")
        else:
            print("Foreign key counts match the model definitions")
        
        # Check indexes
        print("\nChecking indexes...")
        index_issues = []
        
        for table_name in model_tables:
            if table_name in db_tables:
                model_indexes = Base.metadata.tables[table_name].indexes
                db_indexes = inspector.get_indexes(table_name)
                
                # Simple check for number of indexes
                if len(model_indexes) != len(db_indexes):
                    index_issues.append(f"Table '{table_name}': model has {len(model_indexes)} indexes, database has {len(db_indexes)}")
        
        if index_issues:
            print(f"\nWARNING: Found {len(index_issues)} index issues:")
            for issue in index_issues:
                print(f"  - {issue}")
        else:
            print("Index counts match the model definitions")
        
        # Check if tables are empty
        print("\nChecking if tables are empty...")
        empty_tables = []
        
        for table_name in db_tables:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                if count == 0:
                    empty_tables.append(table_name)
        
        if empty_tables:
            print(f"Found {len(empty_tables)} empty tables:")
            for table in sorted(empty_tables):
                print(f"  - {table}")
        else:
            print("All tables contain data")
        
        return {
            "missing_tables": missing_tables,
            "extra_tables": extra_tables,
            "column_issues": column_issues,
            "fk_issues": fk_issues,
            "index_issues": index_issues,
            "empty_tables": empty_tables
        }
        
    except Exception as e:
        print(f"Error checking database structure: {str(e)}")
        raise

if __name__ == "__main__":
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        results = check_database_structure(connection_string)
        print("\nDatabase check completed.")
    except Exception as e:
        print(f"Failed to check database: {str(e)}")
        sys.exit(1) 