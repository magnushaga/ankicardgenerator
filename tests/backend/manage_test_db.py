import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_CONFIG = {
    'user': 'postgres',
    'password': 'admin',
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'postgres'  # Connect to default database first
}

TEST_DB_NAME = 'anki_test_db'

def setup_test_db():
    """Create test database if it doesn't exist"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE {TEST_DB_NAME}')
            print(f"Created test database: {TEST_DB_NAME}")
        else:
            print(f"Test database already exists: {TEST_DB_NAME}")
    finally:
        cur.close()
        conn.close()

def teardown_test_db():
    """Drop test database"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # Terminate existing connections
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
            AND pid <> pg_backend_pid()
        """)
        
        # Drop database
        cur.execute(f'DROP DATABASE IF EXISTS {TEST_DB_NAME}')
        print(f"Dropped test database: {TEST_DB_NAME}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'setup':
            setup_test_db()
        elif sys.argv[1] == 'teardown':
            teardown_test_db() 