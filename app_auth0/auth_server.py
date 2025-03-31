from flask import Flask, jsonify, request, redirect, url_for, session
from flask_session import Session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import requests
from functools import wraps
import jwt
from jwt.algorithms import RSAAlgorithm
import json
import logging
import urllib.parse
from user_management import create_or_update_user, get_user_by_auth0_id
from api_routes import api
from admin_routes import admin
from datetime import datetime, timedelta
from sqlalchemy import text, create_engine
from flask_sqlalchemy import SQLAlchemy
from models import Users
import threading

# Configure logging first, before any other code
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize SQLAlchemy with proper URL parsing
password = urllib.parse.quote_plus("H@ukerkul120700")
DATABASE_URL = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure CORS
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         },
         r"/api/admin/*": {
             "origins": ["http://localhost:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }
     }
)

# Register the API routes blueprint
app.register_blueprint(api, url_prefix='/api')

# Register the admin routes blueprint
app.register_blueprint(admin, url_prefix='/api/admin')
logger.info("Admin routes registered with prefix /api/admin")

# Handle OPTIONS requests
@app.route('/', methods=['OPTIONS'])
def handle_options():
    return jsonify({'status': 'ok'})

# Add a test endpoint for admin routes
@app.route('/api/admin/test', methods=['GET'])
def test_admin():
    logger.info("Admin test endpoint called")
    return jsonify({"message": "Admin routes are working!"})

# Auth0 configuration
oauth = OAuth(app)
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5173')

auth0 = oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=f"https://{AUTH0_DOMAIN}",
    access_token_url=f"https://{AUTH0_DOMAIN}/oauth/token",
    authorize_url=f"https://{AUTH0_DOMAIN}/authorize",
    client_kwargs={"scope": "openid profile email"},
)

FRONTEND_URL = "http://localhost:5173"

logger.info(f"Auth0 Domain: {AUTH0_DOMAIN}")
logger.info(f"Auth0 Client ID: {AUTH0_CLIENT_ID[:6]}...")  # Log only first 6 chars for security
logger.info(f"Redirect URI: {REDIRECT_URI}")

# Add after other global variables
user_info_cache = {}
cache_lock = threading.Lock()
CACHE_DURATION = timedelta(minutes=5)

def get_cached_user_info(token):
    """Get user info from cache if available and not expired"""
    with cache_lock:
        if token in user_info_cache:
            cached_data, timestamp = user_info_cache[token]
            if datetime.now() - timestamp < CACHE_DURATION:
                return cached_data
        return None

def set_cached_user_info(token, user_info):
    """Cache user info with current timestamp"""
    with cache_lock:
        user_info_cache[token] = (user_info, datetime.now())

def exchange_code_for_tokens(code):
    """Exchange authorization code for tokens"""
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error exchanging code for tokens: {str(e)}")
        if hasattr(e, 'response'):
            logger.error(f"Response content: {e.response.text}")
        raise RuntimeError(f"Failed to exchange code for tokens: {str(e)}")

def get_user_info_from_supabase(token):
    """Get user info from Supabase database."""
    try:
        # Extract user ID from token
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get('sub')
        
        if not user_id:
            logger.warning("No user ID found in token")
            return None
            
        # Query Supabase for user info
        user = Users.query.filter_by(auth0_id=user_id).first()
        if user:
            try:
                # Convert user object to dictionary
                user_dict = user.to_dict()
                logger.info(f"Successfully retrieved user info from Supabase for user {user_id}")
                return user_dict
            except Exception as e:
                logger.error(f"Error processing user data: {str(e)}")
                return None
        return None
        
    except Exception as e:
        logger.error(f"Error getting user info from Supabase: {str(e)}")
        return None

def store_user_info_in_supabase(user_info):
    """Store or update user info in Supabase database."""
    try:
        auth0_id = user_info.get('sub')
        if not auth0_id:
            return
            
        # Check if user exists
        existing_user = Users.query.filter_by(auth0_id=auth0_id).first()
        
        if existing_user:
            # Update existing user
            existing_user.email = user_info.get('email')
            existing_user.email_verified = user_info.get('email_verified')
            existing_user.picture = user_info.get('picture')  # Store Auth0 picture
            existing_user.last_login = datetime.utcnow()
            logger.info(f"Updated user {auth0_id} with picture: {user_info.get('picture')}")
        else:
            # Create new user
            new_user = Users(
                auth0_id=auth0_id,
                email=user_info.get('email'),
                email_verified=user_info.get('email_verified'),
                picture=user_info.get('picture'),  # Store Auth0 picture
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                is_active=True
            )
            db.session.add(new_user)
            logger.info(f"Created new user {auth0_id} with picture: {user_info.get('picture')}")
            
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error storing user info in Supabase: {str(e)}")
        db.session.rollback()
        raise

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401
        
        try:
            token = auth_header.split(' ')[1]
            
            # Check cache first
            cached_user_info = get_cached_user_info(token)
            if cached_user_info:
                request.user = cached_user_info
                return f(*args, **kwargs)
            
            # If not in cache, get from Auth0
            userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
            userinfo_response = requests.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if not userinfo_response.ok:
                logger.error(f"Auth0 userinfo request failed: {userinfo_response.text}")
                return jsonify({"error": "Failed to get user info from Auth0"}), 401
                
            user_info = userinfo_response.json()
            
            # Ensure required fields are present
            user_info.setdefault('picture', None)
            user_info.setdefault('name', user_info.get('email', '').split('@')[0])
            user_info.setdefault('email_verified', False)
            user_info.setdefault('updated_at', datetime.utcnow().isoformat())
            
            # Cache the user info
            set_cached_user_info(token, user_info)
            
            # Add user info to request
            request.user = user_info
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
    return decorated

@app.route("/login")
def login():
    """Generate Auth0 login URL"""
    params = {
        'response_type': 'code',
        'client_id': AUTH0_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid profile email',
        'state': 'your-custom-state'
    }
    
    auth_url = f"https://{AUTH0_DOMAIN}/authorize?{urllib.parse.urlencode(params)}"
    logger.info(f"Redirecting to Auth0: {auth_url}")
    return jsonify({"auth_url": auth_url})

@app.route("/callback", methods=["POST"])
def callback():
    """Handle the Auth0 callback"""
    data = request.json
    code = data.get("code")
    
    if not code:
        logger.error("No authorization code received")
        return jsonify({"error": "Authorization code is missing"}), 400

    try:
        # Exchange code for tokens
        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
        
        logger.info("Exchanging code for tokens...")
        token_response = requests.post(token_url, json=payload)
        
        if not token_response.ok:
            logger.error(f"Token exchange failed: {token_response.text}")
            return jsonify({"error": "Failed to exchange code for tokens"}), 500
            
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            logger.error("No access token in response")
            return jsonify({"error": "Failed to get access token"}), 500

        # Get user info from Auth0
        userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
        userinfo_response = requests.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if not userinfo_response.ok:
            logger.error(f"Failed to get user info: {userinfo_response.text}")
            return jsonify({"error": "Failed to get user info"}), 500
            
        user_info = userinfo_response.json()
        logger.info(f"Successfully retrieved user info for: {user_info.get('email')}")

        # Create or update user in Supabase
        try:
            db_user = create_or_update_user(user_info)
            if db_user:
                user_info['db_user'] = db_user
                logger.info(f"Successfully synced user {db_user['email']} with Supabase")
            else:
                logger.error("Failed to sync user with Supabase")
                return jsonify({"error": "Failed to sync user with Supabase"}), 500
        except Exception as e:
            logger.error(f"Error syncing user with Supabase: {str(e)}")
            return jsonify({"error": "Failed to sync user with Supabase"}), 500

        return jsonify({
            "tokens": {
                "access_token": access_token,
                "id_token": token_data.get('id_token')
            },
            "user": user_info
        })

    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/userinfo", methods=["GET"])
@requires_auth
def userinfo():
    """Get user information from Auth0 and our database"""
    try:
        # User info is already available from the requires_auth decorator
        user_info = request.user
        
        # Get user from our database
        try:
            db_user = get_user_by_auth0_id(user_info['sub'])
            if db_user:
                user_info['db_user'] = db_user
                logger.info(f"Successfully retrieved user {db_user['email']} from database")
            else:
                # Create user if not found
                db_user = create_or_update_user(user_info)
                if db_user:
                    user_info['db_user'] = db_user
                    logger.info(f"Created new user {db_user['email']} in database")
                else:
                    logger.error("Failed to create user in database")
        except Exception as e:
            logger.error(f"Error getting user from database: {str(e)}")
            # Continue without database user info

        return jsonify({
            "user": user_info
        })
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    logger.debug("Test endpoint called")
    return jsonify({"message": "Backend is working!", "status": "OK"})

@app.route("/logout", methods=["POST"])
def logout():
    """Handle logout request"""
    try:
        data = request.json
        return_to = data.get('returnTo', 'http://localhost:5173')
        
        # Construct Auth0 logout URL without federated logout
        params = {
            'client_id': AUTH0_CLIENT_ID,
            'returnTo': return_to
        }
        # Remove federated parameter to prevent global logout
        logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?{urllib.parse.urlencode(params)}"
        
        logger.info(f"Logging out user, redirecting to: {return_to}")
        
        return jsonify({
            "logout_url": logout_url,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=5001, debug=True) 