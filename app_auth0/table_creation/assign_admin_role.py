from sqlalchemy import create_engine, text
import urllib.parse

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def assign_admin_role():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Get the super_admin role ID
        result = connection.execute(text("""
            SELECT id FROM admin_roles WHERE name = 'super_admin';
        """))
        role_id = result.scalar()
        
        if not role_id:
            print("Error: super_admin role not found")
            return
            
        # Get your user ID
        result = connection.execute(text("""
            SELECT id FROM users WHERE auth0_id = 'google-oauth2|111609262396518867726';
        """))
        user_id = result.scalar()
        
        if not user_id:
            print("Error: User not found")
            return
            
        # Assign the role
        connection.execute(text("""
            INSERT INTO user_admin_roles (user_id, role_id)
            VALUES (:user_id, :role_id)
            ON CONFLICT (user_id, role_id) DO NOTHING;
        """), {"user_id": user_id, "role_id": role_id})
        
        # Commit the transaction
        connection.commit()
        print(f"Successfully assigned super_admin role to user {user_id}")

if __name__ == "__main__":
    print("Starting admin role assignment...")
    assign_admin_role()
    print("Admin role assignment completed!") 