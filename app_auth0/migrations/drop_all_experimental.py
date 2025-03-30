from sqlalchemy import create_engine, text
import urllib.parse

# URL encode the password
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

def drop_tables():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Drop hierarchical notes tables and indexes
        print("Dropping hierarchical notes tables and indexes...")
        
        # Drop indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_notes_user_id;
            DROP INDEX IF EXISTS idx_note_parts_note_id;
            DROP INDEX IF EXISTS idx_note_chapters_part_id;
            DROP INDEX IF EXISTS idx_note_topics_chapter_id;
            DROP INDEX IF EXISTS idx_note_shares_shared_with;
            DROP INDEX IF EXISTS idx_note_part_shares_shared_with;
            DROP INDEX IF EXISTS idx_note_chapter_shares_shared_with;
            DROP INDEX IF EXISTS idx_note_topic_shares_shared_with;
        """))
        
        # Drop note tables
        connection.execute(text("""
            DROP TABLE IF EXISTS note_topic_shares CASCADE;
            DROP TABLE IF EXISTS note_chapter_shares CASCADE;
            DROP TABLE IF EXISTS note_part_shares CASCADE;
            DROP TABLE IF EXISTS note_shares CASCADE;
            DROP TABLE IF EXISTS note_topics CASCADE;
            DROP TABLE IF EXISTS note_chapters CASCADE;
            DROP TABLE IF EXISTS note_parts CASCADE;
            DROP TABLE IF EXISTS study_notes CASCADE;
        """))
        
        print("Dropping social features tables and indexes...")
        
        # Drop social features indexes
        connection.execute(text("""
            DROP INDEX IF EXISTS idx_study_groups_created_by;
            DROP INDEX IF EXISTS idx_study_group_members_user_id;
            DROP INDEX IF EXISTS idx_group_study_sessions_group_id;
            DROP INDEX IF EXISTS idx_study_session_participants_user_id;
            DROP INDEX IF EXISTS idx_practice_exams_user_id;
            DROP INDEX IF EXISTS idx_exam_attempts_user_id;
            DROP INDEX IF EXISTS idx_study_analytics_user_date;
            DROP INDEX IF EXISTS idx_learning_paths_user_id;
            DROP INDEX IF EXISTS idx_learning_path_progress_user_id;
        """))
        
        # Drop social features tables
        connection.execute(text("""
            DROP TABLE IF EXISTS learning_path_progress CASCADE;
            DROP TABLE IF EXISTS learning_paths CASCADE;
            DROP TABLE IF EXISTS study_analytics CASCADE;
            DROP TABLE IF EXISTS exam_attempts CASCADE;
            DROP TABLE IF EXISTS practice_exams CASCADE;
            DROP TABLE IF EXISTS study_session_participants CASCADE;
            DROP TABLE IF EXISTS group_study_sessions CASCADE;
            DROP TABLE IF EXISTS study_group_members CASCADE;
            DROP TABLE IF EXISTS study_groups CASCADE;
        """))
        
        # Commit the transaction
        connection.commit()
        
        print("Successfully dropped all experimental tables")

if __name__ == "__main__":
    print("Starting to drop experimental tables...")
    drop_tables()
    print("Finished dropping tables") 