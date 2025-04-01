from flask import Blueprint, jsonify, request
from functools import wraps
from access_control import Role, ResourceType, Permission, get_user_role, assign_role, remove_role
from supabase_config import supabase
import logging
from datetime import datetime, timedelta
from admin_models import AdminRole, AdminPermission, AdminRolePermission, UserAdminRole, AdminAuditLog
import os
import jwt
from jwt.algorithms import RSAAlgorithm
import json
import requests
import time
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create admin blueprint
admin = Blueprint('admin', __name__)

# Token verification cache
token_cache = {}
TOKEN_CACHE_DURATION = timedelta(minutes=5)  # Cache tokens for 5 minutes

# Supabase query cache
supabase_cache = {}
SUPABASE_CACHE_DURATION = timedelta(minutes=1)  # Cache Supabase queries for 1 minute

def get_cached_supabase_query(table, query_params=None, cache_key=None):
    """Get cached Supabase query result or execute new query"""
    try:
        # Generate cache key if not provided
        if not cache_key:
            cache_key = f"{table}_{json.dumps(query_params or {})}"
            
        # Check cache
        if cache_key in supabase_cache:
            cache_entry = supabase_cache[cache_key]
            if datetime.now() - cache_entry['timestamp'] < SUPABASE_CACHE_DURATION:
                logger.info(f"Using cached Supabase query for {table}")
                return cache_entry['data']
            else:
                logger.info(f"Cache expired for {table}, executing new query")
                del supabase_cache[cache_key]
        
        # Execute query with retry logic
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Start with base query
                query = supabase.table(table).select('*')
                
                # Apply query parameters if provided
                if query_params:
                    for key, value in query_params.items():
                        if key == 'order':
                            for field, direction in value.items():
                                query = query.order(field, desc=(direction == 'desc'))
                        elif key == 'limit':
                            query = query.limit(value)
                        else:
                            query = getattr(query, key)(value)
                
                # Execute the query
                result = query.execute()
                
                # Cache the result
                supabase_cache[cache_key] = {
                    'data': result.data,
                    'timestamp': datetime.now()
                }
                
                return result.data
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Supabase query attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise
                    
    except Exception as e:
        logger.error(f"Error in Supabase query: {str(e)}")
        raise

def is_admin(user_id):
    """Check if a user has admin privileges"""
    try:
        logger.info(f"Checking admin status for user: {user_id}")
        
        # Check for super admin
        if user_id == "845cd193-4692-4e7b-8951-db948424c240":
            logger.info("User is super admin")
            return True
            
        # Check user's admin roles
        result = supabase.table('user_admin_roles').select('role_id').eq('user_id', user_id).execute()
        if not result.data:
            logger.info("User has no admin roles")
            return False
            
        # Get the role names
        role_ids = [role['role_id'] for role in result.data]
        roles_result = supabase.table('admin_roles').select('name').in_('id', role_ids).execute()
        
        if not roles_result.data:
            logger.info("No admin roles found")
            return False
            
        role_names = [role['name'] for role in roles_result.data]
        logger.info(f"User has admin roles: {role_names}")
        return True
        
    except Exception as e:
        logger.error(f"Error checking admin status: {str(e)}")
        return False

def verify_token_with_cache(token):
    """Verify token with Auth0 and cache the result"""
    try:
        # Check cache first
        if token in token_cache:
            cache_entry = token_cache[token]
            if datetime.now() - cache_entry['timestamp'] < TOKEN_CACHE_DURATION:
                logger.info("Using cached token verification")
                return cache_entry['user_info']
            else:
                logger.info("Cache expired, verifying token again")
                del token_cache[token]
        
        # Verify with Auth0
        auth0_domain = os.getenv('AUTH0_DOMAIN')
        if not auth0_domain:
            logger.error("Auth0 domain not configured")
            return None
            
        url = f"https://{auth0_domain}/userinfo"
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            logger.warning("Auth0 rate limit hit, using cached result if available")
            if token in token_cache:
                return token_cache[token]['user_info']
            return None
            
        response.raise_for_status()
        user_info = response.json()
        
        # Cache the result
        token_cache[token] = {
            'user_info': user_info,
            'timestamp': datetime.now()
        }
        
        return user_info
        
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None

def requires_admin(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.error("No valid Authorization header")
                return jsonify({"error": "No authorization header"}), 401
                
            token = auth_header.split(' ')[1]
            logger.info(f"Admin check - Auth header present: True")
            logger.info(f"Admin check - Token format: {token[:20]}...")
            
            # Verify token with caching
            user_info = verify_token_with_cache(token)
            if not user_info:
                logger.error("Token verification failed")
                return jsonify({"error": "Invalid token"}), 401
                
            auth0_id = user_info.get('sub')
            if not auth0_id:
                logger.error("No user ID in token")
                return jsonify({"error": "Invalid user info"}), 401
            
            # Get user ID from our database
            user_result = supabase.table('users').select('id').eq('auth0_id', auth0_id).execute()
            if not user_result.data:
                logger.error(f"Admin check - User not found in database for auth0_id: {auth0_id}")
                return jsonify({"error": "User not found"}), 404
                
            user_id = user_result.data[0]['id']
            logger.info(f"Admin check - Database user ID: {user_id}")
            
            if not is_admin(user_id):
                logger.info("Admin check - User is not an admin")
                return jsonify({"error": "Admin access required"}), 403
                
            logger.info("Admin check - User is an admin, access granted")
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in admin check: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
            
    return decorated

@admin.route('/check', methods=['GET'])
@requires_admin
def check_admin():
    """Check if the current user has admin access"""
    logger.info("Admin check endpoint called")
    return jsonify({
        "status": "success",
        "message": "Admin access granted"
    })

@admin.route('/users', methods=['GET'])
@requires_admin
def get_users():
    """Get all users"""
    try:
        result = get_cached_supabase_query('users')
        return jsonify({
            'users': result,
            'total': len(result)
        })
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({"error": "Failed to fetch users. Please try again later."}), 500

@admin.route('/roles', methods=['GET'])
@requires_admin
def get_roles():
    """Get all admin roles"""
    try:
        result = get_cached_supabase_query('admin_roles')
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        return jsonify({"error": "Failed to fetch roles. Please try again later."}), 500

@admin.route('/permissions', methods=['GET'])
@requires_admin
def get_permissions():
    """Get all admin permissions"""
    try:
        result = get_cached_supabase_query('admin_permissions')
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting permissions: {str(e)}")
        return jsonify({"error": "Failed to fetch permissions. Please try again later."}), 500

@admin.route('/audit-logs', methods=['GET'])
@requires_admin
def get_audit_logs():
    """Get admin audit logs"""
    try:
        result = get_cached_supabase_query(
            'admin_audit_logs',
            {'order': {'created_at': 'desc'}, 'limit': 100}
        )
        return jsonify({
            'logs': result,
            'total': len(result)
        })
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        return jsonify({"error": "Failed to fetch audit logs. Please try again later."}), 500

def requires_admin_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # First verify admin status
                if not requires_admin(f)(*args, **kwargs):
                    return jsonify({"error": "Admin access required"}), 403

                # Get user info from request
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return jsonify({"error": "No authorization header"}), 401

                token = auth_header.split(' ')[1]
                user_info = verify_token_with_cache(token)
                
                if not user_info:
                    return jsonify({"error": "Invalid token"}), 401

                # Get user from database
                user_result = supabase.table('users').select('id').eq('auth0_id', user_info['sub']).execute()
                if not user_result.data:
                    return jsonify({"error": "User not found"}), 404

                user_id = user_result.data[0]['id']

                # Check if user has the required permission
                permission_query = supabase.table('admin_role_permissions').select(
                    'admin_roles(name), admin_permissions(name)'
                ).eq('admin_permissions.name', permission).execute()

                if not permission_query.data:
                    return jsonify({"error": "Permission not found"}), 404

                # Get user's roles
                user_roles = supabase.table('user_admin_roles').select(
                    'admin_roles(name)'
                ).eq('user_id', user_id).execute()

                if not user_roles.data:
                    return jsonify({"error": "User has no admin roles"}), 403

                # Check if user has any role with the required permission
                user_role_names = [role['admin_roles']['name'] for role in user_roles.data]
                permission_role_names = [role['admin_roles']['name'] for role in permission_query.data]

                if not any(role in permission_role_names for role in user_role_names):
                    return jsonify({"error": "Insufficient permissions"}), 403

                # Add user info to request for use in the route
                request.user = user_info
                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Error in admin permission check: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        return decorated_function
    return decorator

def log_admin_action(admin_id, action, resource_type, resource_id, details=None):
    """Log an admin action to the audit log"""
    try:
        audit_log = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr
        )
        supabase.table('admin_audit_logs').insert(audit_log.to_dict()).execute()
    except Exception as e:
        logger.error(f"Error logging admin action: {str(e)}")

# User Management Routes
@admin.route('/users', methods=['GET'])
@requires_admin_permission('manage_users')
def get_users_admin():
    """Get all users with pagination and filters"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        # Build query
        query = supabase.table('users').select('*')
        
        if search:
            query = query.ilike('email', f'%{search}%')
            
        # Get total count
        count_result = query.count().execute()
        total = count_result.count
        
        # Get paginated results
        result = query.range((page - 1) * per_page, page * per_page - 1).execute()
        
        return jsonify({
            'users': result.data,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({"error": "Failed to get users"}), 500

@admin.route('/users/<user_id>', methods=['PUT'])
@requires_admin_permission('manage_users')
def update_user_admin(user_id):
    """Update user details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Update user
        result = supabase.table('users').update(data).eq('id', user_id).execute()
        
        if not result.data:
            return jsonify({"error": "User not found"}), 404
            
        # Log the action
        log_admin_action(
            request.user.get('sub'),
            f"Updated user {user_id}",
            "user",
            user_id,
            data
        )
        
        return jsonify(result.data[0])
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({"error": "Failed to update user"}), 500

# Role Management Routes
@admin.route('/roles', methods=['GET'])
@requires_admin_permission('manage_roles')
def get_roles_admin():
    """Get all admin roles"""
    try:
        result = supabase.table('admin_roles').select('*').execute()
        return jsonify(result.data)
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        return jsonify({"error": "Failed to get roles"}), 500

@admin.route('/roles', methods=['POST'])
@requires_admin_permission('manage_roles')
def create_role_admin():
    """Create a new admin role"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Role name is required"}), 400
            
        # Create role
        result = supabase.table('admin_roles').insert(data).execute()
        
        # Log the action
        log_admin_action(
            request.user.get('sub'),
            f"Created role {data['name']}",
            "admin_role",
            result.data[0]['id'],
            data
        )
        
        return jsonify(result.data[0])
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        return jsonify({"error": "Failed to create role"}), 500

# Permission Management Routes
@admin.route('/permissions', methods=['GET'])
@requires_admin_permission('manage_roles')
def get_permissions_admin():
    """Get all admin permissions"""
    try:
        result = supabase.table('admin_permissions').select('*').execute()
        return jsonify(result.data)
    except Exception as e:
        logger.error(f"Error getting permissions: {str(e)}")
        return jsonify({"error": "Failed to get permissions"}), 500

# User-Role Assignment Routes
@admin.route('/users/<user_id>/roles', methods=['POST'])
@requires_admin_permission('manage_roles')
def assign_role_admin(user_id):
    """Assign a role to a user"""
    try:
        data = request.get_json()
        if not data or 'role_id' not in data:
            return jsonify({"error": "Role ID is required"}), 400
            
        # Add assigned_by
        data['assigned_by'] = request.user.get('sub')
        
        # Assign role
        result = supabase.table('user_admin_roles').insert(data).execute()
        
        # Log the action
        log_admin_action(
            request.user.get('sub'),
            f"Assigned role {data['role_id']} to user {user_id}",
            "user_role",
            user_id,
            data
        )
        
        return jsonify(result.data[0])
    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        return jsonify({"error": "Failed to assign role"}), 500

# Audit Log Routes
@admin.route('/audit-logs', methods=['GET'])
@requires_admin_permission('view_audit_logs')
def get_audit_logs_admin():
    """Get admin audit logs with filters"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        admin_id = request.args.get('admin_id')
        
        # Build query
        query = supabase.table('admin_audit_logs').select('*')
        
        if start_date:
            query = query.gte('created_at', start_date)
        if end_date:
            query = query.lte('created_at', end_date)
        if admin_id:
            query = query.eq('admin_id', admin_id)
            
        # Get total count
        count_result = query.count().execute()
        total = count_result.count
        
        # Get paginated results
        result = query.range((page - 1) * per_page, page * per_page - 1).execute()
        
        return jsonify({
            'logs': result.data,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        return jsonify({"error": "Failed to get audit logs"}), 500 

# Enhanced User Management Routes
@admin.route('/users/<user_id>/details', methods=['GET'])
@requires_admin_permission('manage_users')
def get_user_details(user_id):
    """Get detailed user information including study history and preferences"""
    try:
        # Get user basic info
        user_result = supabase.table('users').select('*').eq('id', user_id).execute()
        if not user_result.data:
            return jsonify({"error": "User not found"}), 404
            
        user = user_result.data[0]
        
        # Get user's decks
        decks_result = supabase.table('decks').select('*').eq('user_id', user_id).execute()
        decks = decks_result.data
        
        # Get user's study sessions
        sessions_result = supabase.table('study_sessions').select('*').eq('user_id', user_id).execute()
        sessions = sessions_result.data
        
        # Get user's learning analytics
        analytics_result = supabase.table('learning_analytics').select('*').eq('user_id', user_id).execute()
        analytics = analytics_result.data[0] if analytics_result.data else None
        
        # Get user's admin roles
        roles_result = supabase.table('user_admin_roles').select('role_id').eq('user_id', user_id).execute()
        role_ids = [role['role_id'] for role in roles_result.data]
        admin_roles = []
        if role_ids:
            roles_detail = supabase.table('admin_roles').select('*').in_('id', role_ids).execute()
            admin_roles = roles_detail.data
            
        return jsonify({
            'user': user,
            'decks': decks,
            'study_sessions': sessions,
            'analytics': analytics,
            'admin_roles': admin_roles
        })
    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        return jsonify({"error": "Failed to get user details"}), 500

@admin.route('/users/<user_id>/status', methods=['PUT'])
@requires_admin_permission('manage_users')
def update_user_status(user_id):
    """Update user account status (suspend/activate)"""
    try:
        data = request.get_json()
        if not data or 'is_active' not in data:
            return jsonify({"error": "Status update data required"}), 400
            
        result = supabase.table('users').update({
            'is_active': data['is_active'],
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', user_id).execute()
        
        if not result.data:
            return jsonify({"error": "User not found"}), 404
            
        # Log the action
        log_admin_action(
            request.user.get('sub'),
            f"Updated user status for {user_id}",
            "user",
            user_id,
            data
        )
        
        return jsonify(result.data[0])
    except Exception as e:
        logger.error(f"Error updating user status: {str(e)}")
        return jsonify({"error": "Failed to update user status"}), 500

# Deck Management Routes
@admin.route('/decks', methods=['GET'])
@requires_admin_permission('manage_content')
def get_all_decks():
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # Build query
        query = supabase.table('decks').select('*')

        # Apply search if provided
        if search:
            query = query.ilike('title', f'%{search}%')

        # Apply sorting
        query = query.order(sort_by, desc=(sort_order == 'desc'))

        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        query = query.range(start, end)

        # Execute query
        result = query.execute()

        return jsonify({
            'decks': result.data,
            'total': len(result.data),
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        logger.error(f"Error getting decks: {str(e)}")
        return jsonify({"error": "Failed to get decks"}), 500

@admin.route('/decks/<deck_id>/details', methods=['GET'])
@requires_admin_permission('manage_content')
def get_deck_details(deck_id):
    """Get detailed deck information including content and usage stats"""
    try:
        # Get deck basic info
        deck_result = supabase.table('decks').select('*').eq('id', deck_id).execute()
        if not deck_result.data:
            return jsonify({"error": "Deck not found"}), 404
            
        deck = deck_result.data[0]
        
        # Get deck parts
        parts_result = supabase.table('parts').select('*').eq('deck_id', deck_id).execute()
        parts = parts_result.data
        
        # Get deck shares
        shares_result = supabase.table('deck_shares').select('*').eq('deck_id', deck_id).execute()
        shares = shares_result.data
        
        # Get study sessions for this deck
        sessions_result = supabase.table('study_sessions').select('*').eq('deck_id', deck_id).execute()
        sessions = sessions_result.data
        
        return jsonify({
            'deck': deck,
            'parts': parts,
            'shares': shares,
            'study_sessions': sessions
        })
    except Exception as e:
        logger.error(f"Error getting deck details: {str(e)}")
        return jsonify({"error": "Failed to get deck details"}), 500

@admin.route('/decks/<deck_id>/visibility', methods=['PUT'])
@requires_admin_permission('manage_content')
def update_deck_visibility(deck_id):
    """Update deck visibility (public/private)"""
    try:
        data = request.get_json()
        if not data or 'is_public' not in data:
            return jsonify({"error": "Visibility update data required"}), 400
            
        result = supabase.table('decks').update({
            'is_public': data['is_public'],
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', deck_id).execute()
        
        if not result.data:
            return jsonify({"error": "Deck not found"}), 404
            
        # Log the action
        log_admin_action(
            request.user.get('sub'),
            f"Updated deck visibility for {deck_id}",
            "deck",
            deck_id,
            data
        )
        
        return jsonify(result.data[0])
    except Exception as e:
        logger.error(f"Error updating deck visibility: {str(e)}")
        return jsonify({"error": "Failed to update deck visibility"}), 500

# Analytics Routes
@admin.route('/analytics/system', methods=['GET'])
@requires_admin_permission('view_analytics')
def get_system_analytics():
    try:
        # Get total users
        users_result = supabase.table('users').select('id', count='exact').execute()
        total_users = len(users_result.data)

        # Get total decks
        decks_result = supabase.table('decks').select('id', count='exact').execute()
        total_decks = len(decks_result.data)

        # Get total sessions
        sessions_result = supabase.table('study_sessions').select('id', count='exact').execute()
        total_sessions = len(sessions_result.data)

        # Get recent users (last 24 hours)
        recent_users = supabase.table('users').select('*').gte(
            'created_at', 
            (datetime.utcnow() - timedelta(days=1)).isoformat()
        ).execute()

        return jsonify({
            'total_users': total_users,
            'total_decks': total_decks,
            'total_sessions': total_sessions,
            'recent_users': recent_users.data
        })

    except Exception as e:
        logger.error(f"Error getting system analytics: {str(e)}")
        return jsonify({"error": "Failed to get system analytics"}), 500

@admin.route('/analytics/activity', methods=['GET'])
@requires_admin_permission('view_analytics')
def get_activity_analytics():
    try:
        # Get daily active users (last 24 hours)
        active_users = supabase.table('study_sessions').select(
            'user_id', 
            count='exact'
        ).gte(
            'started_at', 
            (datetime.utcnow() - timedelta(days=1)).isoformat()
        ).execute()

        # Get average session duration
        sessions = supabase.table('study_sessions').select(
            'started_at',
            'ended_at'
        ).not_.is_('ended_at', 'null').execute()

        total_duration = 0
        valid_sessions = 0
        for session in sessions.data:
            if session['ended_at']:
                start = datetime.fromisoformat(session['started_at'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(session['ended_at'].replace('Z', '+00:00'))
                duration = (end - start).total_seconds()
                total_duration += duration
                valid_sessions += 1

        avg_duration = total_duration / valid_sessions if valid_sessions > 0 else 0

        return jsonify({
            'daily_active_users': len(active_users.data),
            'average_session_duration': avg_duration
        })

    except Exception as e:
        logger.error(f"Error getting activity analytics: {str(e)}")
        return jsonify({"error": "Failed to get activity analytics"}), 500

# Content Moderation Routes
@admin.route('/content/reports', methods=['GET'])
@requires_admin_permission('manage_content')
def get_content_reports():
    """Get content reports for moderation"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status = request.args.get('status', 'pending')
        
        # Build query
        query = supabase.table('content_reports').select('*')
        
        if status:
            query = query.eq('status', status)
            
        # Get total count
        count_result = query.count().execute()
        total = count_result.count
        
        # Get paginated results
        result = query.range((page - 1) * per_page, page * per_page - 1).execute()
        
        return jsonify({
            'reports': result.data,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        logger.error(f"Error getting content reports: {str(e)}")
        return jsonify({"error": "Failed to get content reports"}), 500

@admin.route('/content/reports/<report_id>/resolve', methods=['PUT'])
@requires_admin_permission('manage_content')
def resolve_content_report(report_id):
    """Resolve a content report"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({"error": "Resolution status required"}), 400
            
        result = supabase.table('content_reports').update({
            'status': data['status'],
            'resolved_at': datetime.utcnow().isoformat(),
            'resolved_by': request.user.get('sub')
        }).eq('id', report_id).execute()
        
        if not result.data:
            return jsonify({"error": "Report not found"}), 404
            
        # Log the action
        log_admin_action(
            request.user.get('sub'),
            f"Resolved content report {report_id}",
            "content_report",
            report_id,
            data
        )
        
        return jsonify(result.data[0])
    except Exception as e:
        logger.error(f"Error resolving content report: {str(e)}")
        return jsonify({"error": "Failed to resolve content report"}), 500 