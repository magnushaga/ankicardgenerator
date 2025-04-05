import os
import sys
from sqlalchemy import create_engine, inspect
from urllib.parse import quote_plus
from tabulate import tabulate

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models_proposed_dynamic import Base

def check_missing_tables(connection_string):
    """
    Check which tables from models_proposed_dynamic.py are missing in the database.
    Returns a list of missing tables and their details.
    """
    try:
        # Create engine and inspector
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        # Get existing tables from database
        db_tables = set(inspector.get_table_names())
        print(f"\n📊 Found {len(db_tables)} existing tables in database")
        
        # Get tables defined in models
        model_tables = set(Base.metadata.tables.keys())
        print(f"📝 Found {len(model_tables)} tables defined in models_proposed_dynamic.py")
        
        # Find missing tables
        missing_tables = model_tables - db_tables
        
        if missing_tables:
            print(f"\n🔍 Found {len(missing_tables)} missing tables:")
            
            # Prepare table info for display
            table_info = []
            for table_name in sorted(missing_tables):
                table = Base.metadata.tables[table_name]
                
                # Get column count
                column_count = len(table.columns)
                
                # Get foreign key info
                fk_relations = []
                for fk in table.foreign_keys:
                    fk_relations.append(f"{fk.parent.name} -> {fk.column.table.name}.{fk.column.name}")
                
                # Check if table references content_nodes
                has_content_node_ref = any(
                    fk.column.table.name == 'content_nodes' 
                    for fk in table.foreign_keys
                )
                
                table_info.append([
                    table_name,
                    column_count,
                    len(table.foreign_keys),
                    "Yes" if has_content_node_ref else "No",
                    "\n".join(fk_relations) if fk_relations else "None"
                ])
            
            # Display results in a nice table format
            headers = ["Table Name", "Columns", "Foreign Keys", "Links to ContentNode", "Foreign Key Relations"]
            print("\n" + tabulate(table_info, headers=headers, tablefmt="grid"))
            
            # Show tables that exist
            print(f"\n✅ Existing tables ({len(db_tables)}):")
            for table in sorted(db_tables):
                print(f"  - {table}")
            
        else:
            print("\n✅ All tables from models exist in the database!")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking tables: {str(e)}")
        return False

if __name__ == "__main__":
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        success = check_missing_tables(connection_string)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 