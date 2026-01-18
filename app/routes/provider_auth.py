"""
服务商管理后台认证模块
用于服务商（SaaS提供商）登录和权限管理
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
JWT_EXPIRATION = 3600 * 24 * 7  # 7天

# 服务商管理员配置（从环境变量读取）
PROVIDER_ADMIN_USERNAME = os.getenv('PROVIDER_ADMIN_USERNAME', 'admin')
PROVIDER_ADMIN_PASSWORD_HASH = os.getenv('PROVIDER_ADMIN_PASSWORD_HASH')

# 如果没有配置密码hash，使用默认密码（仅开发环境）
if not PROVIDER_ADMIN_PASSWORD_HASH:
    # 默认密码：admin123（仅用于开发，生产环境必须修改）
    PROVIDER_ADMIN_PASSWORD_HASH = hashlib.sha256('admin123'.encode()).hexdigest()
    print('⚠️  警告：使用默认服务商密码，请在生产环境中修改！')


def hash_password(password):
    """SHA256加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """验证密码"""
    return hash_password(password) == password_hash


def generate_provider_token(payload, expires_in=JWT_EXPIRATION):
    """生成服务商JWT token"""
    exp = datetime.utcnow() + timedelta(seconds=expires_in)
    token_payload = {
        **payload,
        'exp': exp,
        'iat': datetime.utcnow(),
        'type': 'provider_admin'  # 标识这是服务商token
    }
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_provider_token(token):
    """验证服务商JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get('type') != 'provider_admin':
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@bp.route('/login', methods=['POST'])
def login():
    """
    服务商管理员登录
    POST /api/auth/login
    Body: { "username": "admin", "password": "xxx" }
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'error': '请输入用户名和密码'}), 400
    
    # 验证用户名和密码
    if username != PROVIDER_ADMIN_USERNAME:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    if not verify_password(password, PROVIDER_ADMIN_PASSWORD_HASH):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 生成token
    token = generate_provider_token({
        'username': username,
        'role': 'provider_admin'
    })
    
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': JWT_EXPIRATION,
        'user': {
            'username': username,
            'role': 'provider_admin',
            'name': '服务商管理员'
        }
    })


@bp.route('/user', methods=['GET'])
def get_user():
    """
    获取当前登录用户信息
    GET /api/auth/user
    Headers: Authorization: Bearer <token>
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '未授权'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_provider_token(token)
    
    if not payload:
        return jsonify({'error': 'Token无效或已过期'}), 401
    
    return jsonify({
        'username': payload.get('username'),
        'role': payload.get('role'),
        'name': '服务商管理员'
    })


@bp.route('/logout', methods=['POST'])
def logout():
    """
    退出登录（客户端删除token即可）
    POST /api/auth/logout
    """
    return jsonify({'success': True, 'message': '已退出登录'})


@bp.route('/change-password', methods=['POST'])
def change_password():
    """
    修改密码
    POST /api/auth/change-password
    Headers: Authorization: Bearer <token>
    Body: { "old_password": "xxx", "new_password": "yyy" }
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '未授权'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_provider_token(token)
    
    if not payload:
        return jsonify({'error': 'Token无效或已过期'}), 401
    
    data = request.get_json() or {}
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    
    if not old_password or not new_password:
        return jsonify({'error': '请输入旧密码和新密码'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': '新密码长度至少6位'}), 400
    
    # 验证旧密码
    if not verify_password(old_password, PROVIDER_ADMIN_PASSWORD_HASH):
        return jsonify({'error': '旧密码错误'}), 401
    
    # 生成新密码hash
    new_password_hash = hash_password(new_password)
    
    return jsonify({
        'success': True,
        'message': '密码修改成功，请更新.env文件中的PROVIDER_ADMIN_PASSWORD_HASH',
        'new_password_hash': new_password_hash,
        'instruction': f'请在.env文件中添加：\nPROVIDER_ADMIN_PASSWORD_HASH={new_password_hash}'
    })

