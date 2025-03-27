from flask import Flask, jsonify, request, redirect, url_for
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
from stripe_config import (
    create_checkout_session,
    create_customer_portal_session,
    STRIPE_PUBLISHABLE_KEY
)
from supabase import create_client
from jwt_verify import verify_jwt
from supabase_config import sync_auth0_user, supabase
import urllib.parse

# Configure logging first, before any other code
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": "http://localhost:5173",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Session configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "defaultsecret")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
Session(app)

# Auth0 configuration
oauth = OAuth(app)
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5173/profile')
AUDIENCE = os.getenv('AUTH0_AUDIENCE', 'http://localhost:5000/api')

auth0 = oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=f"https://{AUTH0_DOMAIN}",
    access_token_url=f"https://{AUTH0_DOMAIN}/oauth/token",
    authorize_url=f"https://{AUTH0_DOMAIN}/authorize",
    client_kwargs={"scope": "openid profile email"},
)

# JWT validation configuration
def get_jwt_validation_config():
    domain = AUTH0_DOMAIN
    audience = AUDIENCE
    issuer = f"https://{domain}/"
    jwks_url = f"https://{domain}/.well-known/jwks.json"
    return domain, audience, issuer, jwks_url

# JWT validation decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401

        try:
            token = auth_header.split(" ")[1]
            domain, audience, issuer, jwks_url = get_jwt_validation_config()
            
            # Get the JWKS
            jwks_response = requests.get(jwks_url)
            jwks = jwks_response.json()
            
            # Validate the token
            decoded = jwt.decode(
                token,
                key=RSAAlgorithm.from_jwk(json.dumps(jwks["keys"][0])),
                algorithms=["RS256"],
                audience=audience,
                issuer=issuer
            )
            return f(*args, **kwargs, decoded=decoded)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    return decorated

FRONTEND_URL = "http://localhost:5173"

logger.debug(f"Auth0 Domain: {AUTH0_DOMAIN}")
logger.debug(f"Auth0 Client ID: {AUTH0_CLIENT_ID[:6]}...")  # Log only first 6 chars for security
logger.debug(f"Redirect URI: {REDIRECT_URI}")
logger.debug(f"Audience: {AUDIENCE}")

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@app.route("/login")
def login():
    """Generate Auth0 login URL"""
    params = {
        'response_type': 'code',
        'client_id': AUTH0_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'audience': AUDIENCE,
        'scope': 'openid profile email',
        'state': 'your-custom-state'
    }
    
    auth_url = f"https://{AUTH0_DOMAIN}/authorize?{urllib.parse.urlencode(params)}"
    logger.debug(f"Redirecting to Auth0: {auth_url}")
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
        
        logger.debug(f"Exchanging code for tokens with payload: {payload}")
        
        token_response = requests.post(token_url, json=payload)
        token_response.raise_for_status()
        token_data = token_response.json()
        
        access_token = token_data.get('access_token')
        id_token = token_data.get('id_token')
        
        if not access_token:
            logger.error("No access token in response")
            return jsonify({"error": "Failed to get access token"}), 500

        # Get user info from Auth0
        userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
        userinfo_response = requests.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        logger.debug(f"Tokens received: access_token={access_token[:10]}..., id_token={id_token[:10]}...")
        logger.debug(f"User info received: {user_info}")

        return jsonify({
            "access_token": access_token,
            "id_token": id_token,
            "user": user_info,
            "tokens": {
                "access_token": access_token,
                "id_token": id_token,
                "token_type": token_data.get('token_type', 'Bearer'),
                "expires_in": token_data.get('expires_in')
            }
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Error in callback: {str(e)}")
        if hasattr(e, 'response'):
            logger.error(f"Response content: {e.response.text}")
        return jsonify({"error": str(e)}), 500

@app.route("/protected", methods=["GET"])
@requires_auth
def protected_route():
    """Example of a protected route that requires valid JWT"""
    return jsonify({
        "message": "Access granted",
        "user": request.user
    })

@app.route("/userinfo", methods=["GET"])
def userinfo():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid Authorization header"}), 401

    token = auth_header.split(" ")[1]
    try:
        # Verify JWT
        claims = verify_jwt(token)
        
        # Get user from Supabase
        user = supabase.table('users').select('*').eq('auth0_id', claims['sub']).execute()
        
        if not user.data:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(user.data[0])
    except Exception as e:
        logger.error(f"Error fetching user info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    logger.debug("Test endpoint called")
    return jsonify({"message": "Backend is working!", "status": "OK"})

@app.route("/create-checkout-session", methods=["POST"])
def create_stripe_checkout():
    try:
        data = request.json
        price_id = data.get('priceId')
        email = data.get('email')
        
        if not price_id or not email:
            return jsonify({"error": "Missing price ID or email"}), 400
            
        checkout_session = create_checkout_session(price_id, email)
        return jsonify({"sessionId": checkout_session.id})
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/customer-portal", methods=["POST"])
def customer_portal():
    try:
        data = request.json
        customer_id = data.get('customerId')
        
        if not customer_id:
            return jsonify({"error": "Missing customer ID"}), 400
            
        portal_session = create_customer_portal_session(customer_id)
        return jsonify({"url": portal_session.url})
    except Exception as e:
        logger.error(f"Error creating customer portal session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/config", methods=["GET"])
def get_config():
    return jsonify({
        "publishableKey": STRIPE_PUBLISHABLE_KEY
    })

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
        
        logger.debug(f"Constructed logout URL: {logout_url}")
        
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