import jwt
import requests
from functools import wraps
from flask import request, jsonify
import logging
from cachetools import TTLCache
import json

logger = logging.getLogger(__name__)

# Cache the JWKS data for 1 hour to avoid frequent HTTP requests
jwks_cache = TTLCache(maxsize=1, ttl=3600)

def get_jwks():
    """Fetch and cache the JWKS from Auth0"""
    if 'jwks' not in jwks_cache:
        jwks_url = "https://dev-pv6ho0i8drbnbp6l.eu.auth0.com/.well-known/jwks.json"
        try:
            jwks = requests.get(jwks_url).json()
            jwks_cache['jwks'] = jwks
            logger.debug("JWKS fetched and cached successfully")
        except Exception as e:
            logger.error(f"Error fetching JWKS: {str(e)}")
            raise
    return jwks_cache['jwks']

def verify_jwt(token):
    """Verify the JWT token using Auth0's JWKS"""
    try:
        # First try to decode without verification to get the header
        try:
            unverified_header = jwt.get_unverified_header(token)
        except Exception as e:
            logger.error(f"Error getting unverified header: {str(e)}")
            raise jwt.InvalidTokenError("Invalid token format")

        jwks = get_jwks()
        
        # Find the key that matches the token's key ID
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if not rsa_key:
            raise jwt.InvalidTokenError("No matching key found")

        # Verify the token
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience="http://localhost:5002/api",  # Your API identifier
                issuer=f"https://dev-pv6ho0i8drbnbp6l.eu.auth0.com/"
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise
        except jwt.JWTClaimsError as e:
            logger.error(f"Invalid claims: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Error in verify_jwt: {str(e)}")
        raise

def requires_auth(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401

        try:
            # Extract token from Authorization header
            parts = auth_header.split(" ")
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({"error": "Invalid authorization header format"}), 401
            
            token = parts[1]
            if not token:
                return jsonify({"error": "Empty token"}), 401

            # Verify the token
            payload = verify_jwt(token)
            
            # Add user info to request context
            request.user = payload
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except (jwt.JWTClaimsError, jwt.InvalidTokenError) as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            logger.error(f"Unexpected error in requires_auth: {str(e)}")
            return jsonify({"error": "Authentication failed"}), 401

    return decorated 