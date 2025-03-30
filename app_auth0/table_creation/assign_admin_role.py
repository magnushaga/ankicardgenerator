from sqlalchemy import create_engine, text
import urllib.parse

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def assign_admin_role(auth0_id):
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # First, get the user's ID from the users table
        user_result = connection.execute(text("""
            SELECT id FROM users WHERE auth0_id = :auth0_id;
        """), {'auth0_id': auth0_id})
        user_id = user_result.scalar()
        
        if not user_id:
            print(f"Error: User with auth0_id {auth0_id} not found")
            return
        
        print(f"Found user ID: {user_id}")
        
        # Get the super_admin role ID
        role_result = connection.execute(text("""
            SELECT id FROM admin_roles WHERE name = 'super_admin';
        """))
        role_id = role_result.scalar()
        
        if not role_id:
            print("Error: super_admin role not found")
            return
        
        print(f"Found role ID: {role_id}")
        
        # Assign the super_admin role to the user
        connection.execute(text("""
            INSERT INTO user_admin_roles (user_id, role_id, assigned_by)
            VALUES (:user_id, :role_id, :user_id)
            ON CONFLICT (user_id, role_id) DO NOTHING;
        """), {
            'user_id': user_id,
            'role_id': role_id
        })
        
        # Commit the transaction
        connection.commit()
        print(f"Successfully assigned super_admin role to user {user_id}")

if __name__ == "__main__":
    # Your Auth0 ID from the logs
    auth0_id = "google-oauth2|111609262396518867726"
    assign_admin_role(auth0_id) 