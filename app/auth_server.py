from flask import Flask
from flask_cors import CORS
from .api import auth_bp
from .models import db
import os
import logging
import sys
from urllib.parse import quote_plus
import psycopg2

def create_auth_app():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers to DEBUG level
    loggers = [
        'app',
        'app.api',
        'app.api.authRoutes',
        'werkzeug',
        'urllib3',
        'fsevents',
        'flask',
        'flask_cors'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        # Ensure the logger has a handler
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
    logger = logging.getLogger(__name__)
    logger.debug("Starting Auth Server...")

    app = Flask(__name__)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # Create database tables
    try:
        db_url = os.getenv('DATABASE_URL')
        logger.debug(f"Attempting to connect to database at: {db_url.split('@')[1].split('/')[0]}")
        with app.app_context():
            db.create_all()
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        # Continue without database for testing
        pass
    
    logger.debug("Database URL format check:")
    db_url = os.getenv('DATABASE_URL')
    logger.debug(f"- Contains postgres:// prefix: {'postgres://' in db_url}")
    logger.debug(f"- Contains correct host: {'db.wxisvjmhokwtjwcqaarb.supabase.co' in db_url}")
    logger.debug(f"- Contains encoded @ in password: {'%40' in db_url}")
    
    logger.debug("Auth Server ready")
    return app

if __name__ == '__main__':
    app = create_auth_app()
    app.run(host='0.0.0.0', port=5001, debug=True)

password = "H@ukerkul120700"
encoded_password = quote_plus(password)
print(f"postgresql://postgres:{encoded_password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres")

try:
    conn = psycopg2.connect(
        "dbname=postgres user=postgres password=H@ukerkul120700 host=aws-0-eu-central-1.pooler.supabase.com"
    )
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}") 