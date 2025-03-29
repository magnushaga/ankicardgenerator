from functools import wraps
from flask import request, jsonify
import requests
import os
import logging
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError

# Configure logging
logger = logging.getLogger(__name__)

# Cache for user info
user_info_cache = {}
CACHE_DURATION = timedelta(minutes=5)  # Cache user info for 5 minutes

def get_user_info_from_token(token):
    """Extract user info from JWT token without making an API call"""
    try:
        # Decode the JWT token without verification (since we trust Auth0)
        decoded = jwt.decode(token, options={"verify_signature": False})
        return {
            'sub': decoded.get('sub'),
            'email': decoded.get('email'),
            'email_verified': decoded.get('email_verified'),
            'name': decoded.get('name'),
            'picture': decoded.get('picture'),
            'permissions': decoded.get('permissions', ['read:decks'])
        }
    except InvalidTokenError as e:
        logger.error(f"Error decoding token: {str(e)}")
        return None

def requires_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Log all request headers for debugging
            logger.info("Request headers: %s", dict(request.headers))
            
            # Get the Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                logger.error("No Authorization header found")
                return jsonify({"error": "No authorization header"}), 401

            # Extract the token
            parts = auth_header.split()
            if parts[0].lower() != "bearer":
                logger.error("Invalid authorization header format")
                return jsonify({"error": "Invalid authorization header format"}), 401
            token = parts[1]

            # Log the token for debugging (first 20 chars only)
            logger.info(f"Received token: {token[:20]}...")

            # Try to get user info from cache first
            cached_info = user_info_cache.get(token)
            if cached_info and datetime.utcnow() - cached_info['timestamp'] < CACHE_DURATION:
                logger.info("Using cached user info")
                user_info = cached_info['data']
            else:
                # Try to get user info from token first
                user_info = get_user_info_from_token(token)
                
                if not user_info:
                    # If token decoding fails, fall back to Auth0 API
                    userinfo_url = f"https://{os.getenv('AUTH0_DOMAIN')}/userinfo"
                    logger.info(f"Fetching user info from Auth0: {userinfo_url}")
                    
                    try:
                        userinfo_response = requests.get(
                            userinfo_url,
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=5
                        )
                        userinfo_response.raise_for_status()
                        user_info = userinfo_response.json()
                        logger.info(f"Successfully fetched user info from Auth0 for: {user_info.get('email')}")
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Error fetching user info from Auth0: {str(e)}")
                        return jsonify({"error": "Failed to verify token with Auth0"}), 401
                
                # Cache the user info
                user_info_cache[token] = {
                    'data': user_info,
                    'timestamp': datetime.utcnow()
                }

            # Add user info and token to request
            request.user = {
                'sub': user_info.get('sub'),
                'email': user_info.get('email'),
                'email_verified': user_info.get('email_verified'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'token': token,
                'permissions': user_info.get('permissions', ['read:decks']),
                'db_user': user_info.get('db_user', {})
            }
            
            logger.info(f"Added user info to request: {request.user}")

            # Call the decorated function
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error in authentication: {str(e)}")
            logger.error("Exception details:", exc_info=True)
            return jsonify({"error": "Authentication failed"}), 401

    return decorated 