from supabase import create_client
import os
from dotenv import load_dotenv
from flask import jsonify, request
import jwt
from functools import wraps
from datetime import datetime, timedelta
import logging

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

if not all([SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET]):
    raise ValueError("Missing Supabase credentials in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logger = logging.getLogger(__name__)

def create_access_token(user_id: str) -> str:
    """Create a JWT access token"""
    payload = {
        'sub': user_id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm='HS256')

def verify_token(token: str) -> dict:
    """Verify a JWT token"""
    try:
        return jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated

def get_social_auth_url(provider: str, code_challenge: str, code_challenge_method: str) -> str:
    """Get the social auth URL for a provider"""
    try:
        frontend_url = os.getenv('FRONTEND_URL')
        logger.info(f"Loaded FRONTEND_URL from environment: {frontend_url}")
        
        if not frontend_url:
            raise ValueError("FRONTEND_URL environment variable is not set")

        redirect_url = f"{frontend_url}/auth/callback"
        logger.info(f"Generating social auth URL for provider {provider} with redirect to {redirect_url}")

        logger.info("Calling Supabase auth.sign_in_with_oauth")
        response = supabase.auth.sign_in_with_oauth({
            'provider': provider,
            'options': {
                'redirect_to': redirect_url,
                'query_params': {
                    'access_type': 'offline',
                    'prompt': 'consent',
                    'code_challenge': code_challenge,
                    'code_challenge_method': code_challenge_method,
                }
            }
        })

        if not response:
            logger.error("No response received from Supabase")
            raise ValueError("No response received from Supabase")

        if not response.url:
            logger.error("No URL in response from Supabase")
            raise ValueError("No URL in response from Supabase")

        logger.info(f"Successfully received auth URL from Supabase")
        return response.url
    except Exception as e:
        logger.error(f"Failed to get social auth URL for provider {provider}: {str(e)}")
        raise Exception(f"Failed to get social auth URL: {str(e)}") 