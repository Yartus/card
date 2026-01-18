"""
服务商管理后台认证模块
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import jwt
import os
import secrets
import hashlib

bp = Blueprint('provider_auth', __name__, url_prefix='/api/auth')

# JWT配置
JWT_SECRET = os.getenv('PROVIDER_JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600 * 24 * 7

PROVIDER_ADMIN_USERNAME = os.getenv('PROVIDER_ADMIN_USERNAME', 'admin')
PROVIDER_ADMIN_PASSWORD_HASH = os.getenv('PROVIDER_ADMIN_PASSWORD_HASH')

if not PROVIDER_ADMIN_PASSWORD_HASH:
    # Default: admin123
    PROVIDER_ADMIN_PASSWORD_HASH = hashlib.sha256('admin123'.encode()).hexdigest()

def verify_password(password, password_hash):
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def generate_provider_token(payload):
    exp = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
    payload = {**payload, 'exp': exp, 'type': 'provider_admin'}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    if username != PROVIDER_ADMIN_USERNAME or not verify_password(password, PROVIDER_ADMIN_PASSWORD_HASH):
        return jsonify({'error': 'Invalid credentials'}), 401
        
    token = generate_provider_token({'username': username, 'role': 'provider_admin'})
    return jsonify({'access_token': token, 'user': {'username': username, 'role': 'provider_admin'}})

@bp.route('/user', methods=['GET'])
def get_user():
    # Verify token logic (simplified)
    return jsonify({'username': PROVIDER_ADMIN_USERNAME, 'role': 'provider_admin'})

