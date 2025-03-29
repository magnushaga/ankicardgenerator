from functools import wraps
from flask import request, jsonify
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "http://localhost:5002/api")

# Get Auth0 public key
def get_auth0_public_key():
    """Get Auth0's public key for JWT verification"""
    try:
        jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
        response = requests.get(jwks_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching Auth0 public key: {str(e)}")
        raise

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

def requires_scope(required_scope):
    """Decorator to require specific scopes for routes"""
    def decorator(f):
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

                # Check for required scope
                token_scopes = payload.get("scope", "").split()
                if required_scope not in token_scopes:
                    return jsonify({"error": f"Required scope '{required_scope}' not found"}), 403

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
    return decorator 