from flask import Flask
from flask_cors import CORS
from .extensions import db
import os
import logging
import sys
from .config import Config

def create_app():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting Flask application...")

    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    logger.info("Configuration loaded successfully")
    
    # Initialize CORS
    CORS(app)
    logger.info("CORS initialized")
    
    # Initialize extensions
    db.init_app(app)
    logger.info("Database extension initialized")
    
    # Import and register blueprints
    try:
        from .api.routes import api_bp
        app.register_blueprint(api_bp)
        logger.info("API blueprint registered successfully")
    except Exception as e:
        logger.error(f"Error registering blueprint: {str(e)}")
        raise
    
    # Create tables within app context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    logger.info("Flask application created successfully")
    return app

# Create the app instance
app = create_app()

# Ensure we're in application context
ctx = app.app_context()
ctx.push()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 