from flask import Flask, jsonify, request
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
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "http://localhost:5000/api")

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
    audience = AUTH0_AUDIENCE
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

REDIRECT_URI = "http://localhost:5173/profile"
FRONTEND_URL = "http://localhost:5173"

logger.debug(f"Auth0 Domain: {AUTH0_DOMAIN}")
logger.debug(f"Auth0 Client ID: {AUTH0_CLIENT_ID[:6]}...")  # Log only first 6 chars for security
logger.debug(f"Redirect URI: {REDIRECT_URI}")
logger.debug(f"Audience: {AUTH0_AUDIENCE}")

@app.route("/callback", methods=["POST", "OPTIONS"])
def callback():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.json
    code = data.get("code")
    
    if not code:
        logger.error("No authorization code received")
        return jsonify({"error": "Authorization code is missing"}), 400

    logger.debug(f"Received authorization code: {code[:10]}...")
    
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "audience": AUTH0_AUDIENCE
    }

    try:
        logger.debug(f"Attempting token exchange with payload: {payload}")
        response = requests.post(token_url, json=payload)
        
        if not response.ok:
            error_data = response.json()
            logger.error(f"Token exchange failed. Status: {response.status_code}, Response: {error_data}")
            return jsonify({"error": "Token exchange failed", "details": error_data}), response.status_code
            
        tokens = response.json()
        logger.debug("Token exchange successful")
        logger.debug(f"Received tokens with keys: {list(tokens.keys())}")
        return jsonify({
            "access_token": tokens.get("access_token"),
            "token_type": tokens.get("token_type"),
            "expires_in": tokens.get("expires_in")
        })
    except Exception as e:
        logger.error(f"Token exchange failed with exception: {str(e)}")
        return jsonify({"error": "Token exchange failed", "details": str(e)}), 500

@app.route("/userinfo", methods=["GET"])
@requires_auth
def userinfo(decoded):
    token = request.headers.get("Authorization").split(" ")[1]
    userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"

    try:
        logger.debug("Fetching user info...")
        response = requests.get(
            userinfo_url, 
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        user_data = response.json()
        logger.debug("User info fetched successfully")
        return jsonify(user_data)
    except Exception as e:
        logger.error(f"Error fetching user info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    logger.debug("Test endpoint called")
    return jsonify({"message": "Backend is working!", "status": "OK"})

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=5001, debug=True) 