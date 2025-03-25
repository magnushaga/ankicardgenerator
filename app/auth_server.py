from flask import Flask
from flask_cors import CORS
from .api import auth_bp
from .models import db
import os
import logging
import sys

def create_auth_app():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress noisy third-party logs
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('fsevents').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Auth Server...")

    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    logger.info("Auth Server ready")
    return app

if __name__ == '__main__':
    app = create_auth_app()
    app.run(host='0.0.0.0', port=5001, debug=True) 