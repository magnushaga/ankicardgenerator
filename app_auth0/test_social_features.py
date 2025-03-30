from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def test_migration():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Test study_groups table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'study_groups'
            );
        """))
        print("study_groups table exists:", result.scalar())
        
        # Test study_group_members table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'study_group_members'
            );
        """))
        print("study_group_members table exists:", result.scalar())
        
        # Test group_study_sessions table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'group_study_sessions'
            );
        """))
        print("group_study_sessions table exists:", result.scalar())
        
        # Test study_session_participants table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'study_session_participants'
            );
        """))
        print("study_session_participants table exists:", result.scalar())
        
        # Test practice_exams table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'practice_exams'
            );
        """))
        print("practice_exams table exists:", result.scalar())
        
        # Test exam_attempts table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'exam_attempts'
            );
        """))
        print("exam_attempts table exists:", result.scalar())
        
        # Test study_analytics table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'study_analytics'
            );
        """))
        print("study_analytics table exists:", result.scalar())
        
        # Test learning_paths table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'learning_paths'
            );
        """))
        print("learning_paths table exists:", result.scalar())
        
        # Test learning_path_progress table
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'learning_path_progress'
            );
        """))
        print("learning_path_progress table exists:", result.scalar())
        
        # Test indexes
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_study_groups_created_by'
            );
        """))
        print("idx_study_groups_created_by index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_study_group_members_user_id'
            );
        """))
        print("idx_study_group_members_user_id index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_group_study_sessions_group_id'
            );
        """))
        print("idx_group_study_sessions_group_id index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_study_session_participants_user_id'
            );
        """))
        print("idx_study_session_participants_user_id index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_practice_exams_user_id'
            );
        """))
        print("idx_practice_exams_user_id index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_exam_attempts_user_id'
            );
        """))
        print("idx_exam_attempts_user_id index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_study_analytics_user_date'
            );
        """))
        print("idx_study_analytics_user_date index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_learning_paths_user_id'
            );
        """))
        print("idx_learning_paths_user_id index exists:", result.scalar())
        
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = 'idx_learning_path_progress_user_id'
            );
        """))
        print("idx_learning_path_progress_user_id index exists:", result.scalar())

if __name__ == "__main__":
    print("Starting test...")
    test_migration()
    print("Test completed!") 