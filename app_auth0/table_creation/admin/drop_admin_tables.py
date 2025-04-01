from sqlalchemy import create_engine, text
import urllib.parse

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def drop_admin_tables():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop indexes first
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_admin_roles_name;
            DROP INDEX IF EXISTS idx_admin_permissions_name;
            DROP INDEX IF EXISTS idx_user_admin_roles_user_id;
            DROP INDEX IF EXISTS idx_admin_audit_logs_admin_id;
            DROP INDEX IF EXISTS idx_admin_audit_logs_created_at;
        """))
        
        # Drop tables in correct order (respecting foreign key constraints)
        connection.execute(text("""
            DROP TABLE IF EXISTS admin_audit_logs;
            DROP TABLE IF EXISTS user_admin_roles;
            DROP TABLE IF EXISTS admin_role_permissions;
            DROP TABLE IF EXISTS admin_permissions;
            DROP TABLE IF EXISTS admin_roles;
        """))
        
        # Commit the transaction
        connection.commit()
        print("Successfully dropped all admin tables and indexes")

if __name__ == "__main__":
    print("Starting to drop admin tables...")
    drop_admin_tables()
    print("Finished dropping admin tables") 