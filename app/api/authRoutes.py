from flask import Blueprint, request, jsonify, make_response, current_app
from ..supabase_config import supabase, create_access_token, verify_token, require_auth, get_social_auth_url
from ..models import db, User
from datetime import datetime
import logging
import os
import traceback

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Enable console logging for debugging
console_logging = True

def debug_print(message, data=None):
    if console_logging:
        logger.debug(message)
        if data is not None:
            logger.debug(f"Data: {data}")

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    debug_print("=== Starting Login Process ===")
    debug_print(f"Request method: {request.method}")
    debug_print(f"Request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        debug_print(f"Received login request data: {data}")
        
        if not data or 'email' not in data or 'password' not in data:
            debug_print("Login attempt with missing credentials")
            return jsonify({'error': 'Missing email or password'}), 400

        # Authenticate with Supabase
        debug_print("Attempting to authenticate with Supabase")
        auth_response = supabase.auth.sign_in_with_password({
            'email': data['email'],
            'password': data['password']
        })
        debug_print(f"Supabase auth response: {auth_response}")

        if not auth_response.user:
            debug_print(f"Failed login attempt for email: {data['email']}")
            return jsonify({'error': 'Invalid credentials'}), 401

        # Get or create user profile
        debug_print("Checking if user exists in database")
        user = User.query.filter_by(id=auth_response.user.id).first()
        if not user:
            debug_print(f"Creating new user profile for: {data['email']}")
            user = User(
                id=auth_response.user.id,
                email=data['email'],
                username=data.get('username', data['email'].split('@')[0]),
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            debug_print(f"Created new user: {user.id}")
        else:
            debug_print(f"Found existing user: {user.id}")

        # Create JWT token
        debug_print("Generating JWT token")
        token = create_access_token(user.id)
        debug_print("JWT token generated successfully")

        # Set secure cookie
        debug_print("Creating response with user data and token")
        response = make_response(jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }))
        response.set_cookie(
            'access_token',
            token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=3600  # 1 hour
        )
        debug_print("=== Login Process Completed Successfully ===")
        return response

    except Exception as e:
        debug_print(f"Login error: {str(e)}")
        debug_print(f"Error type: {type(e)}")
        debug_print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Authentication failed'}), 401

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    debug_print("=== Starting Signup Process ===")
    debug_print(f"Request method: {request.method}")
    debug_print(f"Request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        debug_print(f"Received signup request data: {data}")
        
        if not data or 'email' not in data or 'password' not in data:
            debug_print("Signup attempt with missing credentials")
            return jsonify({'error': 'Missing email or password'}), 400

        # Sign up with Supabase
        try:
            debug_print("Attempting to sign up with Supabase")
            auth_response = supabase.auth.sign_up({
                'email': data['email'],
                'password': data['password'],
                'options': {
                    'data': {
                        'username': data.get('username', data['email'].split('@')[0])
                    },
                    'email_redirect_to': f"{os.getenv('FRONTEND_URL')}/auth/callback"
                }
            })
            debug_print(f"Supabase signup response: {auth_response}")
        except Exception as supabase_error:
            debug_print(f"Supabase signup error: {str(supabase_error)}")
            debug_print(f"Error type: {type(supabase_error)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Failed to create user: {str(supabase_error)}'}), 400

        if not auth_response or not auth_response.user:
            debug_print(f"Failed signup attempt for email: {data['email']} - No user returned")
            return jsonify({'error': 'Failed to create user - No user returned'}), 400

        # Create user profile
        try:
            debug_print("Creating user profile in database")
            user = User(
                id=auth_response.user.id,
                email=data['email'],
                username=data.get('username', data['email'].split('@')[0]),
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            debug_print(f"Created user profile: {user.id}")
        except Exception as db_error:
            debug_print(f"Database error during signup: {str(db_error)}")
            debug_print(f"Error type: {type(db_error)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            # Attempt to clean up the Supabase user if database fails
            try:
                debug_print("Attempting to cleanup Supabase user after DB error")
                supabase.auth.admin.delete_user(auth_response.user.id)
            except Exception as cleanup_error:
                debug_print(f"Failed to cleanup Supabase user: {str(cleanup_error)}")
            return jsonify({'error': 'Failed to create user profile'}), 500

        # Create JWT token
        debug_print("Generating JWT token")
        token = create_access_token(user.id)
        debug_print("JWT token generated successfully")

        # Set secure cookie
        debug_print("Creating response with user data and token")
        response = make_response(jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }))
        response.set_cookie(
            'access_token',
            token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=3600  # 1 hour
        )
        debug_print("=== Signup Process Completed Successfully ===")
        return response

    except Exception as e:
        debug_print(f"Signup error: {str(e)}")
        debug_print(f"Error type: {type(e)}")
        debug_print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to create account'}), 400

@auth_bp.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    try:
        # Sign out from Supabase
        supabase.auth.sign_out()
        
        # Clear the access token cookie
        response = make_response(jsonify({'message': 'Logged out successfully'}))
        response.delete_cookie('access_token')
        logger.info(f"User logged out: {request.user_id}")
        return response

    except Exception as e:
        logger.error(f"Logout error for user {request.user_id}: {str(e)}")
        return jsonify({'error': 'Failed to logout'}), 500

@auth_bp.route('/api/auth/me', methods=['GET', 'OPTIONS'])
def get_current_user():
    debug_print("=== Starting get_current_user endpoint ===")
    debug_print(f"Request method: {request.method}")
    debug_print(f"Request headers: {dict(request.headers)}")
    debug_print(f"Request origin: {request.headers.get('Origin')}")
    
    if request.method == 'OPTIONS':
        debug_print("Handling OPTIONS request")
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:5173')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        return response
        
    try:
        debug_print("Attempting to get user from token")
        auth_header = request.headers.get('Authorization')
        debug_print(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            debug_print("No valid token provided")
            return jsonify({'error': 'No valid token provided'}), 401
        
        token = auth_header.split(' ')[1]
        debug_print("Token extracted from header")
        
        # Verify token with Supabase
        try:
            debug_print("Verifying token with Supabase")
            user = supabase.auth.get_user(token)
            debug_print(f"Supabase user data: {user}")
            
            if not user:
                debug_print("Invalid token - no user returned from Supabase")
                return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            debug_print(f"Error verifying token with Supabase: {str(e)}")
            debug_print(f"Error type: {type(e)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({'error': 'Failed to verify token'}), 401
        
        # Get user from our database
        try:
            debug_print(f"Looking up user in database with ID: {user.id}")
            db_user = User.query.get(user.id)
            if not db_user:
                debug_print(f"User not found in database: {user.id}")
                # Create user if not found
                db_user = User(
                    id=user.id,
                    email=user.email,
                    username=user.user_metadata.get('username', user.email.split('@')[0]),
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(db_user)
                db.session.commit()
                debug_print(f"Created new user in database: {db_user.id}")
            else:
                debug_print(f"User found in database: {db_user.id}")
                # Update last login
                db_user.last_login = datetime.utcnow()
                db.session.commit()
            
            debug_print(f"User data: {db_user.to_dict()}")
            
            response = make_response(jsonify(db_user.to_dict()))
            
            # Set CORS headers
            response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:5173')
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            
            debug_print("=== get_current_user endpoint completed successfully ===")
            return response
            
        except Exception as e:
            debug_print(f"Error retrieving user from database: {str(e)}")
            debug_print(f"Error type: {type(e)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({'error': 'Failed to get user data'}), 500
            
    except Exception as e:
        debug_print(f"Error in get_current_user: {str(e)}")
        debug_print(f"Error type: {type(e)}")
        debug_print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/oauth/callback', methods=['POST', 'OPTIONS'])
def oauth_callback():
    debug_print("=== Starting OAuth Callback ===")
    debug_print(f"Request method: {request.method}")
    debug_print(f"Request headers: {dict(request.headers)}")
    
    if request.method == 'OPTIONS':
        debug_print("Handling OPTIONS request")
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response
        
    try:
        data = request.get_json()
        debug_print(f"Received OAuth callback request data: {data}")
        
        if not data or 'code' not in data:
            debug_print("No authorization code provided in callback")
            return jsonify({'error': 'No authorization code provided'}), 400
        
        debug_print(f"Authorization code received: {data['code']}")

        # Exchange the code for a session
        try:
            debug_print("Attempting to exchange code for session with Supabase")
            session = supabase.auth.exchange_code_for_session(data['code'])
            debug_print(f"Successfully exchanged code for session: {session}")
        except Exception as e:
            debug_print(f"Error exchanging code for session: {str(e)}")
            debug_print(f"Error type: {type(e)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({'error': 'Failed to exchange code for session'}), 400
        
        if not session or not session.user:
            debug_print("No user in session after code exchange")
            return jsonify({'error': 'Authentication failed'}), 401
        
        debug_print(f"Session user data: {session.user}")
        
        # Get or create user in our database
        try:
            debug_print("Attempting to get or create user in database")
            user = User.get_or_create_from_supabase(session.user)
            debug_print(f"User created/retrieved successfully: {user.id}")
            debug_print(f"User details: {user.to_dict()}")
        except Exception as e:
            debug_print(f"Error creating/retrieving user: {str(e)}")
            debug_print(f"Error type: {type(e)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate JWT token
        debug_print("Generating JWT token")
        token = create_access_token(user.id)
        debug_print("JWT token generated successfully")
        
        # Create response with user data and token
        response_data = {
            'user': user.to_dict(),
            'access_token': token
        }
        debug_print(f"Response data: {response_data}")
        
        response = make_response(jsonify(response_data))
        
        # Set CORS headers
        debug_print("Setting CORS headers")
        response.headers['Access-Control-Allow-Origin'] = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        
        # Set secure cookie with token
        debug_print("Setting secure cookie")
        response.set_cookie(
            'access_token',
            token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=3600  # 1 hour
        )
        
        debug_print("=== OAuth flow completed successfully ===")
        return response

    except Exception as e:
        debug_print(f"Error in OAuth callback: {str(e)}")
        debug_print(f"Error type: {type(e)}")
        debug_print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

def get_user_from_token():
    """Extract user from token in Authorization header"""
    debug_print("=== Starting get_user_from_token ===")
    try:
        auth_header = request.headers.get('Authorization')
        debug_print(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            debug_print("No valid token provided")
            return None
        
        token = auth_header.split(' ')[1]
        debug_print("Token extracted from header")
        
        # Verify token with Supabase
        try:
            debug_print("Verifying token with Supabase")
            user = supabase.auth.get_user(token)
            debug_print(f"Supabase user data: {user}")
            
            if not user:
                debug_print("Invalid token - no user returned from Supabase")
                return None
        except Exception as e:
            debug_print(f"Error verifying token with Supabase: {str(e)}")
            debug_print(f"Error type: {type(e)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            return None
        
        # Get user from our database
        try:
            debug_print(f"Looking up user in database with ID: {user.id}")
            db_user = User.query.get(user.id)
            if not db_user:
                debug_print(f"User not found in database: {user.id}")
                return None
            debug_print(f"User found in database: {db_user.to_dict()}")
            return db_user
        except Exception as e:
            debug_print(f"Error retrieving user from database: {str(e)}")
            debug_print(f"Error type: {type(e)}")
            debug_print(f"Error traceback: {traceback.format_exc()}")
            return None
            
    except Exception as e:
        debug_print(f"Error in get_user_from_token: {str(e)}")
        debug_print(f"Error type: {type(e)}")
        debug_print(f"Error traceback: {traceback.format_exc()}")
        return None

@auth_bp.route('/api/auth/social/<provider>', methods=['POST'])
def social_auth(provider):
    try:
        logger.info(f"Attempting to get social auth URL for provider: {provider}")
        frontend_url = os.getenv('FRONTEND_URL')
        logger.info(f"Using frontend URL: {frontend_url}")
        
        if not frontend_url:
            logger.error("FRONTEND_URL environment variable is not set")
            return jsonify({'error': 'Frontend URL not configured'}), 500

        # Get PKCE parameters from request body
        data = request.get_json()
        if not data or 'code_challenge' not in data or 'code_challenge_method' not in data:
            logger.error("Missing PKCE parameters in request")
            return jsonify({'error': 'Missing PKCE parameters'}), 400

        redirect_url = f"{frontend_url}/auth/callback"
        logger.info(f"Generated redirect URL: {redirect_url}")

        url = get_social_auth_url(
            provider,
            data['code_challenge'],
            data['code_challenge_method']
        )
        if not url:
            logger.error(f"No URL returned for provider: {provider}")
            return jsonify({'error': 'Failed to generate authentication URL'}), 500

        logger.info(f"Successfully generated social auth URL for provider: {provider}")
        logger.info(f"Auth URL: {url}")
        return jsonify({'url': url})
    except Exception as e:
        logger.error(f"Social auth error for provider {provider}: {str(e)}")
        return jsonify({'error': f'Failed to get social auth URL: {str(e)}'}), 500 