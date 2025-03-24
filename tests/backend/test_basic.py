import sys
import os
import pytest
from flask import Flask
from app.models import db
import psycopg2

# Test database configuration
DB_CONFIG = {
    'user': 'postgres',
    'password': 'admin',
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'anki_test_db'
}

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}",
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    return app

@pytest.fixture(scope='function')
def test_client(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_database_connection():
    """Test basic database connection"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        cur = conn.cursor()
        cur.execute('SELECT 1')
        result = cur.fetchone()
        cur.close()
        conn.close()
        assert result[0] == 1
        print("Database connection successful!")
    except Exception as e:
        assert False, f"Database connection failed: {str(e)}"

def test_flask_app(test_client):
    """Test Flask application setup"""
    assert test_client is not None
    print("Flask application setup successful!") 