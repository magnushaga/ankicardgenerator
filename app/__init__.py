from flask import Flask
from flask_cors import CORS
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI', 'postgresql://postgres:admin@localhost:5432/anki_test_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize CORS
    CORS(app)
    
    # Initialize extensions
    db.init_app(app)
    
    # Import and register blueprints
    from .api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Create tables within app context
    with app.app_context():
        db.create_all()
    
    return app

# Create the app instance
app = create_app()

# Ensure we're in application context
ctx = app.app_context()
ctx.push()

if __name__ == '__main__':
    app.run(debug=True) 