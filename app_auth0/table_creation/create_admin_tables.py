from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def upgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Create admin_roles table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_roles (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create admin_permissions table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_permissions (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create admin_role_permissions table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_role_permissions (
                role_id VARCHAR(36) REFERENCES admin_roles(id) ON DELETE CASCADE,
                permission_id VARCHAR(36) REFERENCES admin_permissions(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (role_id, permission_id)
            );
        """))
        
        # Create user_admin_roles table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS user_admin_roles (
                user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
                role_id VARCHAR(36) REFERENCES admin_roles(id) ON DELETE CASCADE,
                assigned_by VARCHAR(36) REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, role_id)
            );
        """))
        
        # Create admin_audit_logs table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                admin_id VARCHAR(36) REFERENCES users(id),
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                resource_id VARCHAR(36),
                details JSONB,
                ip_address VARCHAR(45),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create indexes for better performance
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_admin_roles_name 
            ON admin_roles(name);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_admin_permissions_name 
            ON admin_permissions(name);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_admin_roles_user_id 
            ON user_admin_roles(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_admin_id 
            ON admin_audit_logs(admin_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_created_at 
            ON admin_audit_logs(created_at);
        """))
        
        # Insert default admin roles
        connection.execute(text("""
            INSERT INTO admin_roles (name, description)
            VALUES 
                ('super_admin', 'Full system access'),
                ('content_moderator', 'Content moderation access'),
                ('user_manager', 'User management access')
            ON CONFLICT (name) DO NOTHING;
        """))
        
        # Insert default permissions
        connection.execute(text("""
            INSERT INTO admin_permissions (name, description)
            VALUES 
                ('manage_users', 'Can manage user accounts'),
                ('manage_content', 'Can manage content'),
                ('view_analytics', 'Can view system analytics'),
                ('manage_roles', 'Can manage admin roles'),
                ('view_audit_logs', 'Can view audit logs')
            ON CONFLICT (name) DO NOTHING;
        """))
        
        # Assign permissions to super_admin role
        connection.execute(text("""
            INSERT INTO admin_role_permissions (role_id, permission_id)
            SELECT r.id, p.id
            FROM admin_roles r
            CROSS JOIN admin_permissions p
            WHERE r.name = 'super_admin'
            ON CONFLICT DO NOTHING;
        """))
        
        # Commit the transaction
        connection.commit()

def downgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_admin_roles_name;
            DROP INDEX IF EXISTS idx_admin_permissions_name;
            DROP INDEX IF EXISTS idx_user_admin_roles_user_id;
            DROP INDEX IF EXISTS idx_admin_audit_logs_admin_id;
            DROP INDEX IF EXISTS idx_admin_audit_logs_created_at;
        """))
        
        # Drop tables
        connection.execute(text("""
            DROP TABLE IF EXISTS admin_audit_logs;
            DROP TABLE IF EXISTS user_admin_roles;
            DROP TABLE IF EXISTS admin_role_permissions;
            DROP TABLE IF EXISTS admin_permissions;
            DROP TABLE IF EXISTS admin_roles;
        """))
        
        # Commit the transaction
        connection.commit()

if __name__ == "__main__":
    print("Starting admin tables migration...")
    upgrade()
    print("Admin tables migration completed successfully!") 