import os
from dotenv import load_dotenv
import psycopg2
from pathlib import Path
import socket

def test_dns_resolution(host):
    print(f"\nTesting DNS resolution for {host}...")
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ DNS Resolution successful: {host} -> {ip}")
        return True
    except socket.gaierror:
        print(f"❌ DNS Resolution failed for {host}")
        return False

def test_database_connection():
    # Load environment variables from the current directory
    load_dotenv()

    # Preferred regions in order
    urls = [
        (f"postgresql://postgres:H%40ukerkul120700@aws-0-eu-north-1.pooler.supabase.com:5432/postgres", "EU North (Stockholm)"),
        (os.getenv('DATABASE_URL'), "Environment URL"),
        (f"postgresql://postgres:H%40ukerkul120700@aws-0-eu-central-1.pooler.supabase.com:5432/postgres", "EU Central"),
        (f"postgresql://postgres:H%40ukerkul120700@aws-0-eu-west-1.pooler.supabase.com:5432/postgres", "EU West")
    ]

    success = False
    for url, region in urls:
        if not url:
            print(f"\nSkipping {region} - URL not configured")
            continue
            
        print(f"\nTesting connection to {region}...")
        try:
            host = url.split('@')[1].split('/')[0].split(':')[0]
            if not test_dns_resolution(host):
                continue

            print(f"Attempting connection...")
            conn = psycopg2.connect(url)
            
            cur = conn.cursor()
            cur.execute('SELECT version();')
            version = cur.fetchone()
            
            print(f"\n✅ Connection successful to {region}!")
            print(f"Server version: {version[0]}")
            
            # Test creating a table
            print("\nTesting table creation...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS auth_test (
                    id SERIAL PRIMARY KEY,
                    test_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ Table creation successful!")
            
            cur.close()
            conn.close()
            print("Connection closed properly")
            
            success = True
            print(f"\n💡 Recommendation: Use this working endpoint in your .env file:")
            print(f"DATABASE_URL={url}")
            break
            
        except psycopg2.OperationalError as e:
            print(f"\n❌ Connection failed to {region}")
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"\n❌ Unexpected error with {region}")
            print(f"Error: {str(e)}")

    if not success:
        print("\n❌ All connection attempts failed")
        print("Suggestions:")
        print("1. Verify your Supabase project settings in the dashboard")
        print("2. Check if IP allowlisting is enabled")
        print("3. Verify your database password")
        print("4. Ensure DATABASE_URL is set in your .env file")

if __name__ == "__main__":
    test_database_connection()