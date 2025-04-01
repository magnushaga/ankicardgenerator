import psycopg2
import urllib.parse
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_educational_tables(conn):
    """
    Creates tables related to educational institutions and their relationships.
    """
    try:
        with conn.cursor() as cur:
            # Create educational_institutions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS educational_institutions (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    country VARCHAR(100),
                    city VARCHAR(100),
                    website VARCHAR(255),
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_educational_institutions_name 
                ON educational_institutions(name);
                
                CREATE INDEX IF NOT EXISTS idx_educational_institutions_type 
                ON educational_institutions(type);
            """)
            logger.info("Created educational_institutions table")

            # Create institution_departments table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS institution_departments (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    institution_id UUID NOT NULL REFERENCES educational_institutions(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(institution_id, name)
                );
                
                CREATE INDEX IF NOT EXISTS idx_institution_departments_institution 
                ON institution_departments(institution_id);
            """)
            logger.info("Created institution_departments table")

            # Create user_institution_affiliations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_institution_affiliations (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    institution_id UUID NOT NULL REFERENCES educational_institutions(id) ON DELETE CASCADE,
                    department_id UUID REFERENCES institution_departments(id) ON DELETE SET NULL,
                    role VARCHAR(50) NOT NULL,
                    start_date DATE,
                    end_date DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT valid_date_range CHECK (end_date IS NULL OR end_date >= start_date)
                );
                
                CREATE INDEX IF NOT EXISTS idx_user_institution_affiliations_user 
                ON user_institution_affiliations(user_id);
                
                CREATE INDEX IF NOT EXISTS idx_user_institution_affiliations_institution 
                ON user_institution_affiliations(institution_id);
                
                CREATE INDEX IF NOT EXISTS idx_user_institution_affiliations_active 
                ON user_institution_affiliations(is_active);
            """)
            logger.info("Created user_institution_affiliations table")

            # Create deck_institution_associations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS deck_institution_associations (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    deck_id UUID NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
                    institution_id UUID NOT NULL REFERENCES educational_institutions(id) ON DELETE CASCADE,
                    department_id UUID REFERENCES institution_departments(id) ON DELETE SET NULL,
                    association_type VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(deck_id, institution_id, department_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_deck_institution_associations_deck 
                ON deck_institution_associations(deck_id);
                
                CREATE INDEX IF NOT EXISTS idx_deck_institution_associations_institution 
                ON deck_institution_associations(institution_id);
                
                CREATE INDEX IF NOT EXISTS idx_deck_institution_associations_type 
                ON deck_institution_associations(association_type);
            """)
            logger.info("Created deck_institution_associations table")

            # Create trigger functions for updating timestamps
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)

            # Create triggers for each table
            tables = [
                'educational_institutions',
                'institution_departments',
                'user_institution_affiliations',
                'deck_institution_associations'
            ]
            
            for table in tables:
                cur.execute(f"""
                    DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};
                    CREATE TRIGGER update_{table}_updated_at
                        BEFORE UPDATE ON {table}
                        FOR EACH ROW
                        EXECUTE FUNCTION update_updated_at_column();
                """)
                logger.info(f"Created update trigger for {table}")

            conn.commit()
            logger.info("Successfully created all educational institution tables")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating educational institution tables: {str(e)}")
        raise

def insert_initial_data(conn):
    """
    Inserts initial data for educational institutions.
    """
    try:
        with conn.cursor() as cur:
            # Insert some example institutions
            cur.execute("""
                INSERT INTO educational_institutions (id, name, type, country, city, website, description)
                VALUES 
                    (
                        '00000000-0000-0000-0000-000000000001',
                        'Norwegian School of Economics',
                        'university',
                        'Norway',
                        'Bergen',
                        'https://www.nhh.no',
                        'A leading business school in Norway'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000002',
                        'University of Oslo',
                        'university',
                        'Norway',
                        'Oslo',
                        'https://www.uio.no',
                        'The oldest and largest university in Norway'
                    )
                ON CONFLICT (id) DO NOTHING;
            """)
            
            # Insert some example departments
            cur.execute("""
                INSERT INTO institution_departments (id, institution_id, name, description)
                VALUES 
                    (
                        '00000000-0000-0000-0000-000000000003',
                        '00000000-0000-0000-0000-000000000001',
                        'Department of Economics',
                        'Research and education in economics'
                    ),
                    (
                        '00000000-0000-0000-0000-000000000004',
                        '00000000-0000-0000-0000-000000000001',
                        'Department of Business and Management Science',
                        'Research and education in business and management'
                    )
                ON CONFLICT (institution_id, name) DO NOTHING;
            """)

            conn.commit()
            logger.info("Successfully inserted initial educational institution data")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting initial data: {str(e)}")
        raise

def main():
    """
    Main function to create tables and insert initial data.
    """
    try:
        # Use the same database connection parameters as your main application
        password = urllib.parse.quote_plus("H@ukerkul120700")
        conn_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
        
        with psycopg2.connect(conn_string) as conn:
            # Create the tables
            create_educational_tables(conn)
            
            # Insert initial data
            insert_initial_data(conn)
            
            logger.info("Successfully completed educational institution table setup")

    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main() 