import os
import sys
import uuid
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models_proposed_dynamic import Base, AdminRoles, AdminPermissions, AdminRolePermissions, UserAdminRoles

def add_super_admin(connection_string, user_id):
    """
    Add a super_admin role and assign it to the specified user
    """
    try:
        # Create engine
        engine = create_engine(connection_string)
        
        # Convert user_id string to UUID
        user_uuid = uuid.UUID(user_id)
        
        with engine.connect() as conn:
            # Check if super_admin role exists
            result = conn.execute(text("SELECT id FROM admin_roles WHERE name = 'super_admin'"))
            role_row = result.fetchone()
            
            if role_row:
                role_id = role_row[0]
                print(f"Super admin role already exists with ID: {role_id}")
            else:
                # Create super_admin role
                role_id = uuid.uuid4()
                conn.execute(
                    text("INSERT INTO admin_roles (id, name, description) VALUES (:id, :name, :description)"),
                    {"id": role_id, "name": "super_admin", "description": "Super administrator with full system access"}
                )
                print(f"Created super admin role with ID: {role_id}")
            
            # Check if user already has the super_admin role
            result = conn.execute(
                text("SELECT user_id FROM user_admin_roles WHERE user_id = :user_id AND role_id = :role_id"),
                {"user_id": user_uuid, "role_id": role_id}
            )
            user_role_row = result.fetchone()
            
            if user_role_row:
                print(f"User {user_id} already has the super_admin role")
            else:
                # Assign super_admin role to user
                conn.execute(
                    text("INSERT INTO user_admin_roles (user_id, role_id, assigned_by) VALUES (:user_id, :role_id, :assigned_by)"),
                    {"user_id": user_uuid, "role_id": role_id, "assigned_by": user_uuid}
                )
                print(f"Assigned super_admin role to user {user_id}")
            
            # Check if all necessary permissions exist
            permissions = [
                ("manage_users", "Full access to manage users"),
                ("manage_content", "Full access to manage all content"),
                ("manage_courses", "Full access to manage courses"),
                ("manage_decks", "Full access to manage decks"),
                ("manage_admin", "Full access to manage admin settings"),
                ("view_analytics", "Access to view analytics and reports"),
                ("manage_subscriptions", "Full access to manage subscriptions"),
                ("manage_files", "Full access to manage files and storage")
            ]
            
            for perm_name, perm_desc in permissions:
                # Check if permission exists
                result = conn.execute(
                    text("SELECT id FROM admin_permissions WHERE name = :name"),
                    {"name": perm_name}
                )
                perm_row = result.fetchone()
                
                if perm_row:
                    perm_id = perm_row[0]
                    print(f"Permission '{perm_name}' already exists with ID: {perm_id}")
                else:
                    # Create permission
                    perm_id = uuid.uuid4()
                    conn.execute(
                        text("INSERT INTO admin_permissions (id, name, description) VALUES (:id, :name, :description)"),
                        {"id": perm_id, "name": perm_name, "description": perm_desc}
                    )
                    print(f"Created permission '{perm_name}' with ID: {perm_id}")
                
                # Check if role-permission relationship exists
                result = conn.execute(
                    text("SELECT role_id FROM admin_role_permissions WHERE role_id = :role_id AND permission_id = :perm_id"),
                    {"role_id": role_id, "perm_id": perm_id}
                )
                role_perm_row = result.fetchone()
                
                if role_perm_row:
                    print(f"Role-permission relationship for '{perm_name}' already exists")
                else:
                    # Create role-permission relationship
                    conn.execute(
                        text("INSERT INTO admin_role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)"),
                        {"role_id": role_id, "permission_id": perm_id}
                    )
                    print(f"Created role-permission relationship for '{perm_name}'")
            
            conn.commit()
            print("\n✅ Super admin role and permissions setup completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error during super admin setup: {str(e)}")
        return False

if __name__ == "__main__":
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    # User ID to make super admin
    user_id = "093cd56b-1611-41bf-b874-ddde1d387daa"
    
    try:
        success = add_super_admin(connection_string, user_id)
        if success:
            print("\n✅ Super admin setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Super admin setup failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 