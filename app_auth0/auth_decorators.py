from functools import wraps
from flask import request, jsonify
import requests
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

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

            # Verify token with Auth0's userinfo endpoint
            userinfo_url = f"https://{os.getenv('AUTH0_DOMAIN')}/userinfo"
            logger.info(f"Verifying token with Auth0 userinfo endpoint: {userinfo_url}")
            
            try:
                userinfo_response = requests.get(
                    userinfo_url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5  # Add timeout
                )
                userinfo_response.raise_for_status()  # Raise exception for bad status codes
            except requests.exceptions.RequestException as e:
                logger.error(f"Error verifying token with Auth0: {str(e)}")
                return jsonify({"error": "Failed to verify token with Auth0"}), 401

            # Get user info from response
            user_info = userinfo_response.json()
            logger.info(f"Successfully verified token for user: {user_info.get('email')}")
            logger.info(f"Full user info: {user_info}")

            # Add user info and token to request
            request.user = {
                'sub': user_info.get('sub'),  # Auth0 user ID
                'email': user_info.get('email'),
                'email_verified': user_info.get('email_verified'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'token': token,
                'permissions': user_info.get('permissions', ['read:decks']),  # Default permission
                'db_user': user_info.get('db_user', {})  # Include db_user if present
            }
            
            logger.info(f"Added user info to request: {request.user}")

            # Call the decorated function
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error in authentication: {str(e)}")
            logger.error("Exception details:", exc_info=True)
            return jsonify({"error": "Authentication failed"}), 401

    return decorated 