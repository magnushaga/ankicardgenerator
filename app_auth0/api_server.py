from flask import Flask, jsonify, request
from flask_cors import CORS
from api_routes import api
from supabase_config import supabase
import os
from dotenv import load_dotenv
import logging
from functools import wraps
import jwt
from jwt.algorithms import RSAAlgorithm
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }
     }
)

# Register the API blueprint
app.register_blueprint(api)

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE', 'http://localhost:5002/api')

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get("Authorization", None)
    if not auth:
        return None

    parts = auth.split()
    if parts[0].lower() != "bearer":
        return None
    elif len(parts) == 1:
        return None
    elif len(parts) > 2:
        return None

    return parts[1]

def requires_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        if not token:
            return jsonify({"error": "No authorization token provided"}), 401

        try:
            # Get Auth0 public key
            jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # Verify the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=AUTH0_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )

            # Add user info to request
            request.user = payload
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.JWTClaimsError as e:
            logger.error(f"JWT Claims Error: {str(e)}")
            return jsonify({"error": "Invalid claims"}), 401
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401

    return decorated

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint to verify API is working"""
    return jsonify({"message": "API server is working!"})

@app.route('/api/protected', methods=['GET'])
@requires_auth
def protected():
    """Test endpoint to verify authentication is working"""
    return jsonify({
        "message": "Protected endpoint is working!",
        "user": request.user
    })

@app.route('/api/user-decks', methods=['GET'])
@requires_auth
def get_user_decks():
    """Get all decks for the authenticated user"""
    try:
        user_id = request.user['sub']
        result = supabase.table('decks').select('*').eq('user_id', user_id).execute()
        
        return jsonify([{
            'id': deck['id'],
            'title': deck['title'],
            'created_at': deck['created_at']
        } for deck in result.data])
        
    except Exception as e:
        logger.error(f"Error getting user decks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/decks', methods=['POST'])
@requires_auth
def create_deck():
    """Create a new deck for the authenticated user"""
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
            
        deck_data = {
            'id': str(uuid.uuid4()),
            'user_id': request.user['sub'],
            'title': title,
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('decks').insert(deck_data).execute()
        
        return jsonify({
            'id': result.data[0]['id'],
            'title': result.data[0]['title'],
            'created_at': result.data[0]['created_at']
        })
        
    except Exception as e:
        logger.error(f"Error creating deck: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/decks/<deck_id>', methods=['DELETE'])
@requires_auth
def delete_deck(deck_id):
    """Delete a deck (if user owns it)"""
    try:
        # Check if user owns the deck
        deck_result = supabase.table('decks').select('*').eq('id', deck_id).execute()
        if not deck_result.data:
            return jsonify({'error': 'Deck not found'}), 404
            
        deck = deck_result.data[0]
        if deck['user_id'] != request.user['sub']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Delete the deck
        supabase.table('decks').delete().eq('id', deck_id).execute()
        
        return jsonify({'message': 'Deck deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting deck: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting API server...")
    app.run(host="0.0.0.0", port=5002, debug=True) 