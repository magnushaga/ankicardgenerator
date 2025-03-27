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
    with app.app_context():
        db.create_all()
    
    logger.debug("Auth Server ready")
    return app

if __name__ == '__main__':
    app = create_auth_app()
    app.run(host='0.0.0.0', port=5001, debug=True) 