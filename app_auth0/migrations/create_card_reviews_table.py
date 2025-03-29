from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import urllib.parse
import uuid

# Parse the connection string with URL encoding for special characters
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"

# Create SQLAlchemy engine and base
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class CardReview(Base):
    __tablename__ = 'card_reviews'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('study_sessions.id'), nullable=False)
    card_id = Column(String, ForeignKey('cards.id'), nullable=False)
    quality = Column(Integer, nullable=False)  # 0-5 rating
    time_taken = Column(Integer)  # milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Previous state
    prev_easiness = Column(Float)
    prev_interval = Column(Integer)
    prev_repetitions = Column(Integer)
    
    # New state after review
    new_easiness = Column(Float)
    new_interval = Column(Integer)
    new_repetitions = Column(Integer)

def create_tables():
    try:
        # Create the table
        Base.metadata.create_all(engine)
        print("Successfully created card_reviews table")
        
        # Create session to verify
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verify table exists
        if engine.dialect.has_table(engine, 'card_reviews'):
            print("Verified card_reviews table exists")
        else:
            print("Failed to create card_reviews table")
            
        session.close()
        
    except Exception as e:
        print(f"Error creating table: {str(e)}")

if __name__ == "__main__":
    create_tables() 