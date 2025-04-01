import psycopg2
import urllib.parse
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    """Create a database connection"""
    password = urllib.parse.quote_plus("H@ukerkul120700")
    DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    return psycopg2.connect(DATABASE_URL)

def get_varchar_id_columns(conn):
    """Get all columns that are VARCHAR(36) and are named 'id' or contain '_id' or 'id_'"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE data_type = 'character varying'
            AND character_maximum_length = 36
            AND (
                column_name = 'id' 
                OR column_name LIKE '%%_id'  -- Use double % to escape for Python string formatting
                OR column_name LIKE 'id_%%'  -- Use double % to escape for Python string formatting
            )
            ORDER BY table_name, column_name;
        """)
        return cur.fetchall()

def get_foreign_key_references(conn, table_name):
    """Get all foreign key references to a table"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = %s;
        """, (table_name,))
        return cur.fetchall()

def get_column_default(conn, table_name, column_name):
    """Get the default value for a column"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_default
            FROM information_schema.columns
            WHERE table_name = %s
            AND column_name = %s;
        """, (table_name, column_name))
        result = cur.fetchone()
        return result[0] if result else None

def get_foreign_key_constraints(conn, table_name):
    """Get all foreign key constraints for a table."""
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND (tc.table_name = %s OR ccu.table_name = %s)
        """, (table_name, table_name))
        return cur.fetchall()
    finally:
        cur.close()

def drop_constraint_if_exists(cur, schema, table, constraint_name):
    """Drop a constraint if it exists."""
    try:
        cur.execute(f"""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.table_constraints 
                    WHERE table_schema = %s
                    AND table_name = %s 
                    AND constraint_name = %s
                ) THEN
                    ALTER TABLE {schema}.{table} DROP CONSTRAINT {constraint_name};
                END IF;
            END $$;
        """, (schema, table, constraint_name))
    except Exception as e:
        logging.error(f"Error dropping constraint {constraint_name} on {schema}.{table}: {str(e)}")
        raise

def migrate_related_columns(conn, table_name, column_name):
    """Migrate a column and all its related foreign key columns to UUID."""
    cur = conn.cursor()
    try:
        # Get all related foreign key constraints
        cur.execute("""
            SELECT 
                tc.table_schema, 
                tc.table_name, 
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_catalog = kcu.constraint_catalog
                AND tc.constraint_schema = kcu.constraint_schema
                AND tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_catalog = tc.constraint_catalog
                AND ccu.constraint_schema = tc.constraint_schema
                AND ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND (
                (kcu.table_schema = %s AND kcu.table_name = %s AND kcu.column_name = %s)
                OR (ccu.table_schema = %s AND ccu.table_name = %s AND ccu.column_name = %s)
            )
        """, (table_name.split('.')[0] if '.' in table_name else 'public', 
              table_name.split('.')[1] if '.' in table_name else table_name,
              column_name,
              table_name.split('.')[0] if '.' in table_name else 'public',
              table_name.split('.')[1] if '.' in table_name else table_name,
              column_name))
        
        related_columns = cur.fetchall()
        
        # First, drop all related constraints
        for rel in related_columns:
            drop_constraint_if_exists(cur, rel[0], rel[1], rel[6])
        
        # Convert all related columns to UUID
        for rel in related_columns:
            # Drop default value if exists
            cur.execute(f"""
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_schema = %s 
                        AND table_name = %s 
                        AND column_name = %s 
                        AND column_default IS NOT NULL
                    ) THEN
                        ALTER TABLE {rel[0]}.{rel[1]} ALTER COLUMN {rel[2]} DROP DEFAULT;
                    END IF;
                END $$;
            """, (rel[0], rel[1], rel[2]))
            
            # Convert to UUID
            cur.execute(f"""
                ALTER TABLE {rel[0]}.{rel[1]} 
                ALTER COLUMN {rel[2]} TYPE uuid 
                USING {rel[2]}::uuid;
            """)
        
        # Convert the main column to UUID
        cur.execute(f"""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_schema = %s 
                    AND table_name = %s 
                    AND column_name = %s 
                    AND column_default IS NOT NULL
                ) THEN
                    ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP DEFAULT;
                END IF;
            END $$;
        """, (table_name.split('.')[0] if '.' in table_name else 'public',
              table_name.split('.')[1] if '.' in table_name else table_name,
              column_name))
        
        cur.execute(f"""
            ALTER TABLE {table_name} 
            ALTER COLUMN {column_name} TYPE uuid 
            USING {column_name}::uuid;
        """)
        
        # Recreate all constraints
        for rel in related_columns:
            cur.execute(f"""
                ALTER TABLE {rel[0]}.{rel[1]} 
                ADD CONSTRAINT {rel[6]} 
                FOREIGN KEY ({rel[2]}) 
                REFERENCES {rel[3]}.{rel[4]}({rel[5]});
            """)
        
        # Set default value for primary key columns
        if column_name == 'id':
            cur.execute(f"""
                ALTER TABLE {table_name} 
                ALTER COLUMN {column_name} 
                SET DEFAULT uuid_generate_v4();
            """)
        
        conn.commit()
        logging.info(f"Successfully migrated {table_name}.{column_name} and related columns")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error migrating {table_name}.{column_name} and related columns: {str(e)}")
        raise

def migrate_table_columns_to_uuid(conn, table_name):
    """Migrate all ID columns in a table to UUID."""
    cur = conn.cursor()
    try:
        # Get all VARCHAR(36) columns that are named 'id' or contain '_id' or 'id_'
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = %s 
            AND data_type = 'character varying' 
            AND character_maximum_length = 36
            AND (
                column_name = 'id'
                OR column_name LIKE '%%_id'
                OR column_name LIKE 'id_%%'
            )
        """, (table_name.split('.')[0] if '.' in table_name else 'public',
              table_name.split('.')[1] if '.' in table_name else table_name))
        
        columns = [row[0] for row in cur.fetchall()]
        
        for column_name in columns:
            migrate_related_columns(conn, table_name, column_name)
            
    except Exception as e:
        conn.rollback()
        logging.error(f"Error migrating columns in {table_name}: {str(e)}")
        raise

def ensure_uuid_extension(conn):
    """Ensure the uuid-ossp extension is enabled"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            """)
            conn.commit()
            logger.info("UUID extension enabled")
    except Exception as e:
        logger.error(f"Error enabling UUID extension: {str(e)}")
        conn.rollback()
        raise

def get_table_dependencies(conn):
    """Get table dependencies to determine migration order"""
    with conn.cursor() as cur:
        cur.execute("""
            WITH RECURSIVE deps AS (
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column,
                    1 as level
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                
                UNION ALL
                
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column,
                    d.level + 1
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                JOIN deps d ON d.table_name = ccu.table_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND d.level < 10  -- Prevent infinite recursion
            )
            SELECT DISTINCT table_name, MAX(level) as dependency_level
            FROM deps
            GROUP BY table_name
            ORDER BY dependency_level DESC, table_name;
        """)
        return cur.fetchall()

def get_migration_order(conn, tables):
    """Determine the correct order for migration based on foreign key dependencies."""
    cur = conn.cursor()
    try:
        # Get all foreign key relationships
        cur.execute("""
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name IN %s
        """, (tuple(tables),))
        
        dependencies = cur.fetchall()
        
        # Build dependency graph
        graph = {table: set() for table in tables}
        for schema, table, _, ref_schema, ref_table, _ in dependencies:
            if ref_table in graph:
                graph[table].add(ref_table)
        
        # Topological sort
        visited = set()
        temp = set()
        order = []
        
        def visit(table):
            if table in temp:
                raise ValueError(f"Circular dependency detected involving {table}")
            if table not in visited:
                temp.add(table)
                for dep in graph[table]:
                    visit(dep)
                temp.remove(table)
                visited.add(table)
                order.append(table)
        
        for table in tables:
            if table not in visited:
                visit(table)
        
        return order
    finally:
        cur.close()

def migrate_to_uuid():
    """Main function to migrate all ID columns to UUID."""
    conn = get_connection()
    try:
        ensure_uuid_extension(conn)
        
        # Get all tables with VARCHAR(36) ID columns
        tables = get_varchar_id_columns(conn)
        
        # Sort tables by dependencies
        migration_order = get_migration_order(conn, [table for table, _ in tables])
        logger.info(f"Migration order: {migration_order}")
        
        # Migrate each table
        for table_name in migration_order:
            logger.info(f"Starting migration for {table_name}")
            migrate_table_columns_to_uuid(conn, table_name)
            
        conn.commit()
        logger.info("Migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Starting UUID migration")
    migrate_to_uuid() 