import os
import sys
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus
import networkx as nx

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models_proposed_dynamic import Base

def apply_model_changes(connection_string):
    """
    Create missing tables from models_proposed_dynamic.py in the database.
    This script will:
    1. Check which tables are missing
    2. Create the missing tables in the correct order based on their dependencies
    """
    try:
        # Create engine
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        # Get all tables in the database
        db_tables = inspector.get_table_names()
        print(f"Found {len(db_tables)} existing tables in the database")
        
        # Get all tables defined in models
        model_tables = Base.metadata.tables.keys()
        print(f"Found {len(model_tables)} tables defined in models_proposed_dynamic.py")
        
        # Check for missing tables
        missing_tables = set(model_tables) - set(db_tables)
        if missing_tables:
            print(f"\nFound {len(missing_tables)} tables to create:")
            for table in sorted(missing_tables):
                print(f"  - {table}")
            
            # Create a dependency graph for tables
            print("\nAnalyzing table dependencies...")
            dependency_graph = nx.DiGraph()
            
            # Add all tables to the graph
            for table_name in missing_tables:
                dependency_graph.add_node(table_name)
            
            # Add edges for foreign key dependencies
            for table_name in missing_tables:
                table = Base.metadata.tables[table_name]
                for fk in table.foreign_keys:
                    referenced_table = fk.column.table.name
                    if referenced_table in missing_tables:
                        dependency_graph.add_edge(referenced_table, table_name)
            
            # Get a topological sort of the tables
            try:
                table_order = list(nx.topological_sort(dependency_graph))
                print("\nWill create tables in this order:")
                for i, table in enumerate(table_order):
                    print(f"  {i+1}. {table}")
            except nx.NetworkXUnfeasible:
                print("ERROR: Could not determine a valid order for table creation.")
                return False
            
            # Create missing tables in the correct order
            print("\nCreating tables...")
            for table_name in table_order:
                table = Base.metadata.tables[table_name]
                print(f"Creating table: {table_name}")
                try:
                    table.create(engine)
                    print(f"  ✅ Successfully created table: {table_name}")
                except Exception as e:
                    print(f"  ❌ ERROR creating table {table_name}: {str(e)}")
                    return False
            
            print("\n✅ All missing tables have been created successfully!")
        else:
            print("\n✅ All tables from models already exist in the database")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        success = apply_model_changes(connection_string)
        if success:
            print("\n✅ Tables created successfully!")
            sys.exit(0)
        else:
            print("\n❌ Failed to create tables.")
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 