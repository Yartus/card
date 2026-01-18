from flask import Blueprint, request, jsonify, current_app, session, redirect
import json
import hashlib
import time
import requests
from urllib.parse import urlencode, quote
import logging
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import jwt
import secrets
import redis
import sys
import random
import string

from ..models import db, Tenant, Member

bp = Blueprint('wecom', __name__, url_prefix='/api/v1/wecom')

# JWT配置
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600 * 12

WECOM_CONFIG = {
    'suite_id': os.getenv('WECOM_SUITE_ID', ''),
    'suite_secret': os.getenv('WECOM_SUITE_SECRET', ''),
    'token': os.getenv('WECOM_TOKEN', ''),
    'encoding_aes_key': os.getenv('WECOM_ENCODING_AES_KEY', ''),
}

# Redis缓存配置
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    max_connections=10
)
redis_client = redis.Redis(connection_pool=redis_pool)


def set_cache(key, value, ttl=600):
    """使用Redis设置缓存"""
    try:
        redis_client.setex(f'wecom:{key}', ttl, value)
        return True
    except Exception as e:
        current_app.logger.error(f'Redis set_cache error: {e}')
        return False


def get_cache(key):
    """使用Redis获取缓存"""
    try:
        value = redis_client.get(f'wecom:{key}')
        return value
    except Exception as e:
        current_app.logger.error(f'Redis get_cache error: {e}')
        return None

# =============================================================================
# 核心认证与票据管理 (Core Auth & Ticket Management)
# =============================================================================

def get_suite_access_token():
    cached = get_cache('suite_access_token')
    if cached:
        return cached

    payload = {
        'suite_id': WECOM_CONFIG['suite_id'],
        'suite_secret': WECOM_CONFIG['suite_secret'],
        'suite_ticket': get_cache('suite_ticket') or ''
    }
    try:
        resp = requests.post('https://qyapi.weixin.qq.com/cgi-bin/service/get_suite_token', json=payload, timeout=5)
        data = resp.json()
        if 'suite_access_token' in data and data.get('errcode', 0) == 0:
            token = data['suite_access_token']
            expires_in = int(data.get('expires_in', 7200)) - 60
            set_cache('suite_access_token', token, ttl=max(expires_in, 60))
            return token
        current_app.logger.error(f'get_suite_access_token error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_suite_access_token exception: {exc}')
    return None


def get_pre_auth_code():
    token = get_suite_access_token()
    if not token:
        return None
    cached = get_cache('pre_auth_code')
    if cached:
        return cached
    try:
        resp = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/get_pre_auth_code?suite_id={WECOM_CONFIG["suite_id"]}&suite_access_token={token}',
            timeout=5
        )
        data = resp.json()
        if data.get('errcode') == 0:
            code = data['pre_auth_code']
            set_cache('pre_auth_code', code, ttl=600)
            return code
        current_app.logger.error(f'get_pre_auth_code error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_pre_auth_code exception: {exc}')
    return None


def exchange_permanent_code(auth_code):
    token = get_suite_access_token()
    if not token:
        return None
    try:
        resp = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code?access_token={token}',
            json={'auth_code': auth_code},
            timeout=5
        )
        data = resp.json()
        if 'permanent_code' in data and data.get('errcode', 0) == 0:
            return data
        current_app.logger.error(f'get_permanent_code error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_permanent_code exception: {exc}')
    return None


def get_corp_info(corp_id, permanent_code):
    token = get_suite_access_token()
    if not token:
        return None
    try:
        resp = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/get_auth_info?access_token={token}',
            json={'auth_corpid': corp_id, 'permanent_code': permanent_code},
            timeout=5
        )
        data = resp.json()
        if data.get('errcode') == 0:
            return data.get('auth_corp_info')
        current_app.logger.error(f'get_corp_info error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_corp_info exception: {exc}')
    return None


def cache_suite_ticket(ticket):
    set_cache('suite_ticket', ticket, ttl=600)
    current_app.logger.info('suite_ticket cached')


def ensure_config():
    missing = [k for k, v in WECOM_CONFIG.items() if not v]
    if missing:
        current_app.logger.error(f'Missing WeCom config: {missing}')
        return False
    return True

# =============================================================================
# 安装与回调处理 (Install & Callback)
# =============================================================================

@bp.route('/install', methods=['GET'])
def install():
    """生成应用安装/授权链接"""
    if not ensure_config():
        return jsonify({'error': '缺少服务商配置'}), 500

    pre_auth_code = get_pre_auth_code()
    if not pre_auth_code:
        return jsonify({'error': '未能获取pre_auth_code'}), 502

    redirect = request.args.get('redirect_uri') or 'https://zjemail.cn/wecom/settings' # 替换为你的默认回调
    qr_url = (
        'https://open.work.weixin.qq.com/wwopen/sso/3rd_qrConnect?'
        + urlencode({
            'appid': WECOM_CONFIG['suite_id'],
            'redirect_uri': redirect,
            'state': request.args.get('state', 'wechat_auth'),
            'usertype': 'admin',
            'pre_auth_code': pre_auth_code
        })
    )
    return jsonify({'pre_auth_code': pre_auth_code, 'qr_url': qr_url})


@bp.route('/auth', methods=['POST'])
def auth_callback():
    """前端扫码授权后的回调（如果前端直接处理回调）"""
    # 注：通常由企微服务器直接推送到 /callback 接口，但有些场景前端会获取 auth_code 传给后端
    payload = request.get_json() or {}
    auth_code = payload.get('auth_code')
    if not auth_code:
        return jsonify({'error': 'missing auth_code'}), 400

    api_result = exchange_permanent_code(auth_code)
    if not api_result:
        return jsonify({'error': 'get permanent_code failed'}), 502

    # 这里复用了 create_auth 的逻辑，可以根据需要完善
    # 建议主要依赖 /command 的 create_auth 事件
    return jsonify({'success': True})


@bp.route('/callback', methods=['GET', 'POST'])
def callback_handler():
    """
    通用回调接口 (接收 suite_ticket 等)
    对应企微配置的 "指令回调URL"
    """
    if request.method == 'GET':
        signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        if not verify_signature(WECOM_CONFIG['token'], timestamp, nonce, echostr, signature):
            return 'Invalid signature', 400
        return decrypt_message(echostr)

    # POST: 处理推送事件
    signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    raw_body = request.get_data() or b''
    
    try:
        root = ET.fromstring(raw_body)
        encrypt_text = root.find('Encrypt').text
    except Exception as exc:
        return 'Invalid XML', 400

    if not verify_signature(WECOM_CONFIG['token'], timestamp, nonce, encrypt_text, signature):
        return 'Invalid signature', 400

    plaintext = decrypt_message(encrypt_text)
    process_event(plaintext)
    return 'success'


@bp.route('/command', methods=['GET', 'POST'])
def command_handler():
    """
    指令回调接口 (功能同 callback，部分配置可能分开)
    """
    return callback_handler()


def process_event(xml_plaintext):
    """处理解密后的XML事件"""
    import sys
    try:
        root = ET.fromstring(xml_plaintext)
        info_type = root.findtext('InfoType')
        print(f'⭐ wecom event: {info_type}', file=sys.stderr, flush=True)
        
        if info_type == 'suite_ticket':
            ticket = root.findtext('SuiteTicket')
            cache_suite_ticket(ticket)
            
        elif info_type in ('create_auth', 'change_auth'):
            # 处理企业授权/安装应用
            auth_code = root.findtext('AuthCode')
            handle_auth_event(auth_code)
            
        elif info_type == 'cancel_auth':
            # 处理取消授权
            corp_id = root.findtext('AuthCorpId')
            tenant = Tenant.query.filter_by(corp_id=corp_id).first()
            if tenant:
                tenant.plan = 'cancelled'
                db.session.commit()
                
        # 其他业务相关事件（如通讯录变更、外部联系人变更）可在此扩展
        
    except Exception as exc:
        current_app.logger.error(f'process_event error: {exc}')


def handle_auth_event(auth_code):
    """处理授权/安装逻辑"""
    import sys
    try:
        api_result = exchange_permanent_code(auth_code)
        if not api_result:
            return
        
        auth_corp_info = api_result.get('auth_corp_info', {})
        corp_id = auth_corp_info.get('corpid')
        corp_name = auth_corp_info.get('corp_name', 'Unknown')
        permanent_code = api_result.get('permanent_code')
        
        auth_info = api_result.get('auth_info', {})
        auth_user_info = api_result.get('auth_user_info', {})
        installer_userid = auth_user_info.get('userid')
        
        # 计算可见范围用户数
        user_limit = 0
        if auth_info and 'agent' in auth_info:
            for agent in auth_info['agent']:
                privilege = agent.get('privilege', {})
                allow_users = privilege.get('allow_user', [])
                user_limit = len(allow_users)
        
        if not corp_id or not permanent_code:
            return
        
        tenant = Tenant.query.filter_by(corp_id=corp_id).first()
        if not tenant:
            tenant = Tenant(corp_id=corp_id, name=corp_name)
            print(f'➕ 创建新租户：{corp_name}', file=sys.stderr, flush=True)
        else:
            tenant.name = corp_name
            print(f'🔄 更新租户：{corp_name}', file=sys.stderr, flush=True)
        
        tenant.permanent_code = permanent_code
        tenant.installer_userid = installer_userid
        tenant.auth_info = json.dumps(auth_info, ensure_ascii=False)
        tenant.user_limit = user_limit
        
        if tenant.config is None:
            tenant.config = '{}'
        
        db.session.add(tenant)
        db.session.commit()
        
    except Exception as e:
        print(f'❌ 处理授权失败: {e}', file=sys.stderr, flush=True)

# =============================================================================
# 加密与签名 (Crypto & Signature)
# =============================================================================

def verify_signature(token, timestamp, nonce, data, signature):
    try:
        params = [token, timestamp, nonce, data]
        params.sort()
        calculated = hashlib.sha1(''.join(params).encode('utf-8')).hexdigest()
        return calculated == signature
    except Exception:
        return False

def decrypt_message(encrypted):
    try:
        from Crypto.Cipher import AES
        import struct
        import base64
        data = base64.b64decode(encrypted)
        aes_key = base64.b64decode(WECOM_CONFIG['encoding_aes_key'] + '=')
        cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
        decrypted = cipher.decrypt(data)
        pad = decrypted[-1]
        if isinstance(pad, str):
            pad = ord(pad)
        decrypted = decrypted[:-pad]
        msg_len = struct.unpack('!I', decrypted[16:20])[0]
        msg = decrypted[20:20 + msg_len].decode('utf-8')
        return msg
    except Exception as exc:
        current_app.logger.error(f'decrypt error: {exc}')
        return encrypted

# =============================================================================
# 用户鉴权与OAuth (User Auth & OAuth)
# =============================================================================

def generate_jwt_token(payload, expires_in=JWT_EXPIRATION):
    exp = datetime.utcnow() + timedelta(seconds=expires_in)
    token_payload = {**payload, 'exp': exp, 'iat': datetime.utcnow()}
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_corp_access_token(corp_id, permanent_code):
    suite_access_token = get_suite_access_token()
    if not suite_access_token:
        return None
    try:
        resp = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/get_corp_token?suite_access_token={suite_access_token}',
            json={'auth_corpid': corp_id, 'permanent_code': permanent_code},
            timeout=5
        )
        data = resp.json()
        if 'access_token' in data and data.get('errcode', 0) == 0:
            return data['access_token']
    except Exception:
        pass
    return None

def check_user_permission(tenant_id, userid):
    """检查用户权限：installer/super_admin/user"""
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {'has_access': False, 'is_admin': False, 'role': 'none'}
    
    # 1. 安装者
    if tenant.installer_userid and tenant.installer_userid == userid:
        return {'has_access': True, 'is_admin': True, 'role': 'installer'}
    
    # 2. 企业超管 (简化逻辑，实际应调用企微API检查)
    # if check_user_admin_permission(...): return ...
    
    # 3. 可见范围
    in_visible_range = False
    if tenant.auth_info:
        try:
            auth_info = json.loads(tenant.auth_info)
            if auth_info and 'agent' in auth_info:
                for agent in auth_info['agent']:
                    privilege = agent.get('privilege', {})
                    allow_users = privilege.get('allow_user', [])
                    if userid in allow_users:
                        in_visible_range = True
                        break
        except:
            pass
    
    if in_visible_range:
        return {'has_access': True, 'is_admin': False, 'role': 'user'}
        
    return {'has_access': False, 'is_admin': False, 'role': 'none'}

@bp.route('/auth/verify_user', methods=['GET'])
def verify_user():
    """
    核心接口：前端OAuth code换取用户信息和JWT
    """
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'missing code'}), 400
        
    suite_access_token = get_suite_access_token()
    if not suite_access_token:
        return jsonify({'error': 'suite token error'}), 500
        
    try:
        # 调用 getuserinfo3rd 获取用户身份和所属企业
        resp = requests.get(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/auth/getuserinfo3rd',
            params={'suite_access_token': suite_access_token, 'code': code},
            timeout=5
        )
        user_data = resp.json()
        if user_data.get('errcode') != 0:
            return jsonify({'error': 'getuserinfo3rd failed', 'detail': user_data}), 400
            
        corp_id = user_data.get('corpid')
        userid = user_data.get('userid')
        open_userid = user_data.get('open_userid')
        
        if not corp_id or not userid:
            return jsonify({'error': 'incomplete user info'}), 400
            
        # 查找对应的租户
        tenant = Tenant.query.filter_by(corp_id=corp_id).first()
        if not tenant:
            return jsonify({'error': 'Tenant not found. Please install the app first.'}), 404
            
        # 检查权限
        permission = check_user_permission(tenant.id, userid)
        
        # 生成JWT
        token = generate_jwt_token({
            'tenant_id': tenant.id,
            'userid': userid,
            'corp_id': corp_id,
            'open_userid': open_userid,
            'is_admin': permission['is_admin'],
            'role': permission['role']
        })
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'userid': userid,
                'tenant_id': tenant.id,
                'is_admin': permission['is_admin'],
                'role': permission['role']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# 通讯录同步 (Contact Sync)
# =============================================================================

@bp.route('/sync-members', methods=['POST'])
def sync_members():
    """同步企业通讯录成员"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    if not payload or not payload.get('is_admin'):
        return jsonify({'error': 'Admin required'}), 403
        
    tenant_id = payload.get('tenant_id')
    tenant = Tenant.query.get(tenant_id)
    
    # 这里保留核心同步逻辑框架
    # 实际同步代码需要调用 get_department_list, get_user_list 等接口
    # ... (同步逻辑参考原wecom.py)
    
    return jsonify({'success': True, 'message': 'Sync functionality skeleton'})

# 如有需要，保留 get_jssdk_signature 等通用接口

