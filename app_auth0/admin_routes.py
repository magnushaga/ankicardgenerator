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
                # Get user ID from request
                user_id = request.user.get('sub')
                if not user_id:
                    return jsonify({"error": "User not authenticated"}), 401

                # Check if user has admin role
                result = supabase.table('user_admin_roles').select('role_id').eq('user_id', user_id).execute()
                if not result.data:
                    return jsonify({"error": "User does not have admin role"}), 403

                # Get role IDs
                role_ids = [role['role_id'] for role in result.data]

                # Check if any of the user's roles have the required permission
                result = supabase.table('admin_role_permissions').select('role_id').in_('role_id', role_ids).execute()
                if not result.data:
                    return jsonify({"error": "User does not have required permission"}), 403

                # Log the admin action
                log_admin_action(user_id, f"Accessed {f.__name__}", "admin_route", None)
                
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