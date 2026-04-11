"""
Authentication and session management handlers.
"""
import hashlib
import uuid
import json
import os
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
import logging

# File paths for persistence
USERS_DB_FILE = 'users_db.json'

# User authentication storage
users_db = {}  # {username: {password_hash, email, created_at, sessions: {}, snippets: []}}
sessions_db = {}  # {session_token: {username, created_at, expires_at}}

def load_users_db():
    """Load users from disk."""
    global users_db
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, 'r') as f:
                data = json.load(f)
                # Convert ISO date strings back to datetime objects
                for username, user_data in data.items():
                    if 'created_at' in user_data:
                        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                users_db = data
                print(f"[AUTH] Loaded {len(users_db)} users from disk")
                logging.info(f"[AUTH] Loaded {len(users_db)} users from disk")
        except Exception as e:
            print(f"[AUTH] Error loading users: {e}")
            logging.error(f"[AUTH] Error loading users: {e}")
            users_db = {}
    else:
        print("[AUTH] No existing users database found, starting fresh")
        logging.info("[AUTH] No existing users database found")
        users_db = {}

def save_users_db():
    """Save users to disk."""
    try:
        # Convert datetime objects to ISO strings for JSON serialization
        data_to_save = {}
        for username, user_data in users_db.items():
            user_copy = user_data.copy()
            if 'created_at' in user_copy and isinstance(user_copy['created_at'], datetime):
                user_copy['created_at'] = user_copy['created_at'].isoformat()
            data_to_save[username] = user_copy
        
        with open(USERS_DB_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        logging.info(f"[AUTH] Saved {len(users_db)} users to disk")
    except Exception as e:
        logging.error(f"[AUTH] Error saving users: {e}")

def clear_all_sessions():
    """Clear all sessions - called on server restart"""
    global sessions_db
    sessions_db.clear()
    # Don't clear users - they persist across restarts
    logging.info("[AUTH] All sessions cleared (users preserved)")

# Load users when module is imported
load_users_db()

# Create default admin user if no users exist
def init_default_user():
    """Create default admin user for testing if database is empty"""
    if not users_db:
        default_username = 'admin'
        default_password = 'admin123'
        users_db[default_username] = {
            'password_hash': hash_password(default_password),
            'email': 'admin@example.com',
            'created_at': datetime.now().isoformat(),
            'sessions': {},
            'snippets': [],
            'stats': {
                'total_requests': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
        }
        save_users_db()
        logging.info(f"[AUTH] Created default admin user (username: {default_username}, password: {default_password})")
        print(f"[AUTH] ✓ Default user created - Username: {default_username}, Password: {default_password}")

# Initialize default user
init_default_user()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
    """Generate a unique session token"""
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def get_current_user():
    """Get current logged-in user from session"""
    auth_token = request.headers.get('Authorization') or request.cookies.get('session_token')
    if auth_token and auth_token in sessions_db:
        session_data = sessions_db[auth_token]
        # Check if session is still valid
        if datetime.now() < session_data['expires_at']:
            return session_data['username']
        else:
            # Session expired, remove it
            del sessions_db[auth_token]
    return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = get_current_user()
        if not username:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        
        # Validation
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        if len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if username in users_db:
            return jsonify({'success': False, 'error': 'Username already exists'}), 409
        
        # Create new user
        users_db[username] = {
            'password_hash': hash_password(password),
            'email': email,
            'created_at': datetime.now().isoformat(),
            'sessions': {},  # User's test sessions
            'snippets': [],  # User's code snippets
            'stats': {
                'total_requests': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
        }
        
        # Save to disk
        save_users_db()
        
        logging.info(f"New user registered: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'username': username
        }), 201
        
    except Exception as e:
        logging.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def login():
    """Login user and create session"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        # Check if user exists
        if username not in users_db:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        if users_db[username]['password_hash'] != hash_password(password):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Create session token
        session_token = generate_session_token()
        expires_at = datetime.now() + timedelta(days=7)  # Session valid for 7 days
        
        sessions_db[session_token] = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at
        }
        
        logging.info(f"User logged in: {username}")
        
        response = jsonify({
            'success': True,
            'message': 'Login successful',
            'username': username,
            'email': users_db[username].get('email', ''),
            'session_token': session_token
        })
        
        # Set cookie for browser
        response.set_cookie('session_token', session_token, 
                          max_age=7*24*60*60,  # 7 days
                          httponly=True,
                          samesite='Lax')
        
        return response, 200
        
    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def logout():
    """Logout user and invalidate session"""
    try:
        auth_token = request.headers.get('Authorization') or request.cookies.get('session_token')
        
        if auth_token and auth_token in sessions_db:
            username = sessions_db[auth_token]['username']
            del sessions_db[auth_token]
            logging.info(f"User logged out: {username}")
        
        response = jsonify({
            'success': True,
            'message': 'Logout successful'
        })
        
        response.set_cookie('session_token', '', expires=0)
        
        return response, 200
        
    except Exception as e:
        logging.error(f"Logout error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def check_auth():
    """Check if user is authenticated"""
    username = get_current_user()
    
    # Debug logging
    logging.info(f"[AUTH CHECK] Username: {username}, Sessions count: {len(sessions_db)}, Users count: {len(users_db)}")
    
    if username:
        return jsonify({
            'success': True,
            'authenticated': True,
            'username': username,
            'email': users_db[username].get('email', '')
        }), 200
    else:
        return jsonify({
            'success': True,
            'authenticated': False
        }), 200

def get_profile():
    """Get user profile"""
    username = get_current_user()
    user_data = users_db[username]
    
    return jsonify({
        'success': True,
        'profile': {
            'username': username,
            'email': user_data.get('email', ''),
            'created_at': user_data['created_at'],
            'stats': user_data.get('stats', {})
        }
    }), 200
