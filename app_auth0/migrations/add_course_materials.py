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
        # Create course_materials table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS course_materials (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                material_type VARCHAR(50) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type VARCHAR(100) NOT NULL,
                tags JSONB DEFAULT '[]'::jsonb,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create study_resources table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS study_resources (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                content JSONB NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                source_material_id VARCHAR(36) REFERENCES course_materials(id),
                tags JSONB DEFAULT '[]'::jsonb,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create resource_generations table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS resource_generations (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                resource_id VARCHAR(36) NOT NULL REFERENCES study_resources(id),
                status VARCHAR(20) NOT NULL,
                generation_type VARCHAR(50) NOT NULL,
                prompt TEXT NOT NULL,
                result JSONB,
                error TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Add indexes for better performance
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_course_materials_user_id 
            ON course_materials(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_study_resources_user_id 
            ON study_resources(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_study_resources_source_material 
            ON study_resources(source_material_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resource_generations_resource_id 
            ON resource_generations(resource_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resource_generations_status 
            ON resource_generations(status);
        """))
        
        # Commit the transaction
        connection.commit()

def downgrade():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_course_materials_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_resources_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_resources_source_material;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_resource_generations_resource_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_resource_generations_status;
        """))
        
        # Drop tables
        connection.execute(text("""
            DROP TABLE IF EXISTS resource_generations;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS study_resources;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS course_materials;
        """))
        
        # Commit the transaction
        connection.commit()

if __name__ == "__main__":
    print("Starting migration...")
    upgrade()
    print("Migration completed successfully!") 