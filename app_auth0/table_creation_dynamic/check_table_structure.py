import os
import sys
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models_proposed_dynamic import Base, UserAdminRoles, AdminRoles, AdminPermissions, AdminRolePermissions

def check_table_structure(connection_string):
    """
    Check the structure of all admin tables
    """
    try:
        # Create engine
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        # List of admin tables to check
        admin_tables = [
            'admin_roles',
            'admin_permissions',
            'admin_role_permissions',
            'user_admin_roles',
            'admin_audit_logs'
        ]
        
        for table_name in admin_tables:
            print(f"\n{'='*50}")
            print(f"Checking table: {table_name}")
            print(f"{'='*50}")
            
            # Check if the table exists
            if table_name in inspector.get_table_names():
                print(f"Table '{table_name}' exists")
                
                # Get column information
                columns = inspector.get_columns(table_name)
                print("\nColumns in table:")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
                    
                # Get primary key information
                pk_constraint = inspector.get_pk_constraint(table_name)
                print(f"\nPrimary key: {pk_constraint['constrained_columns']}")
                
                # Get foreign key information
                fk_constraints = inspector.get_foreign_keys(table_name)
                print("\nForeign keys:")
                for fk in fk_constraints:
                    print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            else:
                print(f"Table '{table_name}' does not exist")
                
            # Print model definition
            model_class = None
            if table_name == 'admin_roles':
                model_class = AdminRoles
            elif table_name == 'admin_permissions':
                model_class = AdminPermissions
            elif table_name == 'admin_role_permissions':
                model_class = AdminRolePermissions
            elif table_name == 'user_admin_roles':
                model_class = UserAdminRoles
            
            if model_class:
                print("\nModel definition from models_proposed_dynamic.py:")
                for column in model_class.__table__.columns:
                    print(f"  - {column.name}: {column.type}")
            
        return True
        
    except Exception as e:
        print(f"Error checking table structure: {str(e)}")
        return False

if __name__ == "__main__":
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        success = check_table_structure(connection_string)
        if success:
            print("\n✅ Table structure check completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Table structure check failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 