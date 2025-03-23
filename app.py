from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from api import api
from deck_routes import deck_routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app, 
         resources={r"/api/*": {
             "origins": app.config['CORS_ORIGINS'],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"]
         }})
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(api)
    app.register_blueprint(deck_routes)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=53550, debug=True)