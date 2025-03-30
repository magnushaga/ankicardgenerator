import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text
import urllib.parse
from datetime import datetime

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# URL encode the password
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def upgrade():
    # Create engine
    engine = sqlalchemy.create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Create study_groups table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS study_groups (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                created_by VARCHAR(36) NOT NULL REFERENCES users(id),
                is_public BOOLEAN DEFAULT false,
                max_members INTEGER DEFAULT 50,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create study_group_members table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS study_group_members (
                group_id VARCHAR(36) REFERENCES study_groups(id),
                user_id VARCHAR(36) REFERENCES users(id),
                role VARCHAR(20) DEFAULT 'member',
                joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, user_id)
            );
        """))
        
        # Create group_study_sessions table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS group_study_sessions (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                group_id VARCHAR(36) NOT NULL REFERENCES study_groups(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                scheduled_start TIMESTAMP WITH TIME ZONE NOT NULL,
                scheduled_end TIMESTAMP WITH TIME ZONE NOT NULL,
                status VARCHAR(20) DEFAULT 'scheduled',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create study_session_participants table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS study_session_participants (
                session_id VARCHAR(36) REFERENCES group_study_sessions(id),
                user_id VARCHAR(36) REFERENCES users(id),
                status VARCHAR(20) DEFAULT 'pending',
                joined_at TIMESTAMP WITH TIME ZONE,
                left_at TIMESTAMP WITH TIME ZONE,
                PRIMARY KEY (session_id, user_id)
            );
        """))
        
        # Create practice_exams table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS practice_exams (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                source_material_id VARCHAR(36) REFERENCES course_materials(id),
                questions JSONB NOT NULL,
                time_limit INTEGER,
                passing_score INTEGER,
                is_public BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create exam_attempts table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS exam_attempts (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                exam_id VARCHAR(36) NOT NULL REFERENCES practice_exams(id),
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                score INTEGER,
                answers JSONB,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP WITH TIME ZONE,
                status VARCHAR(20) DEFAULT 'in_progress',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create study_analytics table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS study_analytics (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                date DATE NOT NULL,
                study_time INTEGER,
                cards_studied INTEGER,
                notes_created INTEGER,
                exams_taken INTEGER,
                topics_mastered INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            );
        """))
        
        # Create learning_paths table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
                user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                materials JSONB NOT NULL,
                estimated_duration INTEGER,
                difficulty_level VARCHAR(20),
                is_public BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create learning_path_progress table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS learning_path_progress (
                path_id VARCHAR(36) REFERENCES learning_paths(id),
                user_id VARCHAR(36) REFERENCES users(id),
                completed_materials JSONB DEFAULT '[]',
                current_material_index INTEGER DEFAULT 0,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_accessed_at TIMESTAMP WITH TIME ZONE,
                status VARCHAR(20) DEFAULT 'in_progress',
                PRIMARY KEY (path_id, user_id)
            );
        """))
        
        # Add indexes for better performance
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_study_groups_created_by 
            ON study_groups(created_by);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_study_group_members_user_id 
            ON study_group_members(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_group_study_sessions_group_id 
            ON group_study_sessions(group_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_study_session_participants_user_id 
            ON study_session_participants(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_practice_exams_user_id 
            ON practice_exams(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_exam_attempts_user_id 
            ON exam_attempts(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_study_analytics_user_date 
            ON study_analytics(user_id, date);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_learning_paths_user_id 
            ON learning_paths(user_id);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_learning_path_progress_user_id 
            ON learning_path_progress(user_id);
        """))
        
        # Commit the transaction
        connection.commit()

def downgrade():
    # Create engine
    engine = sqlalchemy.create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_groups_created_by;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_group_members_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_group_study_sessions_group_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_session_participants_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_practice_exams_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_exam_attempts_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_analytics_user_date;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_learning_paths_user_id;
        """))
        
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_learning_path_progress_user_id;
        """))
        
        # Drop tables
        connection.execute(text("""
            DROP TABLE IF EXISTS learning_path_progress;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS learning_paths;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS study_analytics;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS exam_attempts;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS practice_exams;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS study_session_participants;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS group_study_sessions;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS study_group_members;
        """))
        
        connection.execute(text("""
            DROP TABLE IF EXISTS study_groups;
        """))
        
        # Commit the transaction
        connection.commit()

if __name__ == "__main__":
    print("Starting migration...")
    upgrade()
    print("Migration completed successfully!") 