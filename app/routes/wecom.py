from flask import Blueprint, request, jsonify, current_app, session, redirect
import json
import hashlib
import hmac
import base64
import time
import requests
from urllib.parse import urlencode, quote
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
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
JWT_EXPIRATION = 3600 * 12  # 12小时（合理的工作时长，不会有安全隐患）

WECOM_CONFIG = {
    'suite_id': os.getenv('WECOM_SUITE_ID', ''),
    'suite_secret': os.getenv('WECOM_SUITE_SECRET', ''),
    'token': os.getenv('WECOM_TOKEN', ''),
    'encoding_aes_key': os.getenv('WECOM_ENCODING_AES_KEY', ''),
}

# Redis缓存配置（替代内存缓存，解决Gunicorn多Worker问题）
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
    """使用Redis设置缓存，支持跨Worker共享"""
    try:
        redis_client.setex(f'wecom:{key}', ttl, value)
        return True
    except Exception as e:
        current_app.logger.error(f'Redis set_cache error: {e}')
        return False


def get_cache(key):
    """使用Redis获取缓存，支持跨Worker共享"""
    try:
        value = redis_client.get(f'wecom:{key}')
        return value
    except Exception as e:
        current_app.logger.error(f'Redis get_cache error: {e}')
        return None


def sanitize_media_url(value):
    """标准化头像/图片URL，空字符串返回None"""
    if not value:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    return value or None


def build_member_avatar_config(member, header_avatar_config=None):
    """
    根据优先级生成头像配置：
    1. 管理员单人成员设置 custom_avatar_url
    2. AvatarEditor 中的统一配置（useWecomAvatar=false 且有 customAvatar）
    3. 企微同步 avatar_url
    """
    header_avatar_config = header_avatar_config or {}
    base_config = {
        'useWecomAvatar': header_avatar_config.get('useWecomAvatar', True),
        'customAvatar': header_avatar_config.get('customAvatar', ''),
        'wecomAvatar': header_avatar_config.get('wecomAvatar') or member.avatar_url or ''
    }

    resolved_avatar = member.avatar_url or ''

    if member.custom_avatar_url:
        base_config['useWecomAvatar'] = True
        base_config['wecomAvatar'] = member.custom_avatar_url
        resolved_avatar = member.custom_avatar_url
    elif base_config.get('useWecomAvatar', True):
        base_config['wecomAvatar'] = base_config.get('wecomAvatar') or member.avatar_url or ''
        resolved_avatar = base_config['wecomAvatar'] or member.avatar_url or ''
    else:
        resolved_avatar = base_config.get('customAvatar') or member.avatar_url or ''

    return base_config, resolved_avatar


def build_card_preview_config(raw_config, header_background, member_custom_push_photo):
    """
    构建推送卡片配置，优先级：
    1. 管理员在成员管理中设置 custom_push_photo_url
    2. 推送配置中的 companyAvatar / avatarMode
    3. 企微默认头像（交给前端在 avatarMode=member 时处理）
    """
    header_background = header_background or {}
    resolved = {
        'avatarMode': raw_config.get('avatarMode', 'company'),
        'companyAvatar': raw_config.get('companyAvatar', ''),
        'backgroundType': raw_config.get('backgroundType', header_background.get('backgroundType', 'solid')),
        'backgroundImage': raw_config.get('backgroundImage', header_background.get('backgroundImage', '')),
        'backgroundColor': raw_config.get('backgroundColor', header_background.get('backgroundColor', '#f5f5f5')),
        'svgPattern': raw_config.get('svgPattern', header_background.get('svgPattern', 'geometric')),
        'svgGradientStart': raw_config.get('svgGradientStart', header_background.get('svgGradientStart', '#ffffff')),
        'svgGradientEnd': raw_config.get('svgGradientEnd', header_background.get('svgGradientEnd', '#FC726E')),
        'themeColor': raw_config.get('themeColor', '#fbb9b6'),
        'personalIntro': raw_config.get('personalIntro', '')
    }

    if member_custom_push_photo:
        resolved['avatarMode'] = 'company'
        resolved['companyAvatar'] = member_custom_push_photo

    return resolved


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
        # 企微成功响应：有suite_access_token字段且无errcode，或errcode=0
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
        # 企微成功响应：有permanent_code字段且无errcode，或errcode=0
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


@bp.route('/install', methods=['GET'])
def install():
    if not ensure_config():
        return jsonify({'error': '缺少服务商配置：请填写 WECOM_SUITE_ID/SECRET/TOKEN/ENCODING_AES_KEY'}), 500

    pre_auth_code = get_pre_auth_code()
    if not pre_auth_code:
        current_app.logger.error('Failed to obtain pre_auth_code from WeCom API')
        return jsonify({'error': '未能从企业微信获取授权二维码，请检查suite_ticket或API权限'}), 502

    redirect = request.args.get('redirect_uri') or 'https://zjemail.cn/wecom/settings'
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
    current_app.logger.info(f'Generated pre_auth_code={pre_auth_code[:8]}..., redirect={redirect}')
    return jsonify({'pre_auth_code': pre_auth_code, 'qr_url': qr_url})


@bp.route('/auth', methods=['POST'])
def auth_callback():
    if not ensure_config():
        return jsonify({'error': 'wecom config missing'}), 500

    payload = request.get_json() or {}
    auth_code = payload.get('auth_code')
    if not auth_code:
        return jsonify({'error': 'missing auth_code'}), 400

    api_result = exchange_permanent_code(auth_code)
    if not api_result:
        return jsonify({'error': 'get permanent_code failed'}), 502

    corp_info = api_result.get('auth_corp_info') or {}
    corp_id = corp_info.get('corpid')
    corp_name = corp_info.get('corp_name') or ''
    permanent_code = api_result.get('permanent_code')

    if not corp_id or not permanent_code:
        current_app.logger.error(f'auth incomplete data: {api_result}')
        return jsonify({'error': 'incomplete auth data'}), 502

    tenant = Tenant.query.filter_by(corp_id=corp_id).first()
    if tenant:
        tenant.permanent_code = permanent_code
        tenant.name = corp_name or tenant.name
        tenant.updated_at = db.func.now()
        action = 'update'
    else:
        tenant = Tenant(
            corp_id=corp_id,
            name=corp_name or corp_id,
            plan='free',
            permanent_code=permanent_code
        )
        db.session.add(tenant)
        action = 'create'

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'DB error on tenant {corp_id}: {exc}')
        return jsonify({'error': 'db commit failed'}), 500

    detail = get_corp_info(corp_id, permanent_code)

    current_app.logger.info(
        f'tenant {action}: corp_id={corp_id}, tenant_id={tenant.id}, corp_name={corp_name}, scopes={detail.get("auth_user_info", {}) if detail else {}}'
    )

    return jsonify({
        'success': True,
        'tenant_id': tenant.id,
        'corp_id': corp_id,
        'corp_name': tenant.name,
        'permanent_code': permanent_code,
        'auth_info': detail or {}
    })


@bp.route('/callback', methods=['GET', 'POST'])
def callback_handler():
    if request.method == 'GET':
        signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        if not verify_signature(WECOM_CONFIG['token'], timestamp, nonce, echostr, signature):
            return 'Invalid signature', 400
        return decrypt_message(echostr)

    import sys
    print('=== callback POST received ===', file=sys.stderr, flush=True)
    signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    raw_body = request.get_data() or b''
    print(f'callback body length: {len(raw_body)}', file=sys.stderr, flush=True)
    try:
        root = ET.fromstring(raw_body)
        encrypt_text = root.find('Encrypt').text
        print(f'encrypt_text extracted, length: {len(encrypt_text)}', file=sys.stderr, flush=True)
    except Exception as exc:
        current_app.logger.error(f'parse callback xml error: {exc}; body={raw_body[:200]}')
        return 'Invalid XML', 400

    if not verify_signature(WECOM_CONFIG['token'], timestamp, nonce, encrypt_text, signature):
        current_app.logger.error('callback signature verify failed')
        return 'Invalid signature', 400
    print('callback signature verified', file=sys.stderr, flush=True)

    plaintext = decrypt_message(encrypt_text)
    print(f'decrypt result length: {len(plaintext) if plaintext else 0}', file=sys.stderr, flush=True)
    if plaintext:
        print(f'📄 FULL DECRYPTED XML:', file=sys.stderr, flush=True)
        print(plaintext, file=sys.stderr, flush=True)
        print(f'📄 END OF XML', file=sys.stderr, flush=True)
    process_event(plaintext)
    print('=== callback processing done ===', file=sys.stderr, flush=True)
    return 'success'


@bp.route('/command', methods=['GET', 'POST'])
def command_handler():
    if request.method == 'GET':
        signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        if not verify_signature(WECOM_CONFIG['token'], timestamp, nonce, echostr, signature):
            return 'Invalid signature', 400
        return decrypt_message(echostr)

    import sys
    print('=== COMMAND POST received ===', file=sys.stderr, flush=True)
    signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    body = request.get_data() or b''
    print(f'command body length: {len(body)}', file=sys.stderr, flush=True)
    try:
        root = ET.fromstring(body)
        encrypt_text = root.find('Encrypt').text
        print(f'command encrypt_text extracted, length: {len(encrypt_text)}', file=sys.stderr, flush=True)
    except Exception as exc:
        current_app.logger.error(f'parse command xml error: {exc}; body={body[:200]}')
        return 'Invalid XML', 400

    if not verify_signature(WECOM_CONFIG['token'], timestamp, nonce, encrypt_text, signature):
        current_app.logger.error('command signature verify failed')
        return 'Invalid signature', 400
    print('command signature verified', file=sys.stderr, flush=True)

    plaintext = decrypt_message(encrypt_text)
    print(f'command decrypt result length: {len(plaintext) if plaintext else 0}', file=sys.stderr, flush=True)
    if plaintext:
        print(f'📄 COMMAND FULL DECRYPTED XML:', file=sys.stderr, flush=True)
        print(plaintext, file=sys.stderr, flush=True)
        print(f'📄 END OF COMMAND XML', file=sys.stderr, flush=True)
    process_event(plaintext)
    print('=== COMMAND processing done ===', file=sys.stderr, flush=True)
    return 'success'


def process_event(xml_plaintext):
    import sys
    try:
        root = ET.fromstring(xml_plaintext)
        info_type = root.findtext('InfoType')
        print(f'⭐ wecom event: {info_type}', file=sys.stderr, flush=True)
        if info_type == 'suite_ticket':
            ticket = root.findtext('SuiteTicket')
            print(f'⭐ suite_ticket extracted: {ticket[:20]}...', file=sys.stderr, flush=True)
            cache_suite_ticket(ticket)
            print(f'⭐ suite_ticket cached successfully!', file=sys.stderr, flush=True)
        elif info_type in ('create_auth', 'change_auth'):
            auth_code = root.findtext('AuthCode')
            print(f'⭐ {info_type} auth_code={auth_code[:20]}...', file=sys.stderr, flush=True)
            # 处理租户授权
            print(f'🔄 开始处理租户授权...', file=sys.stderr, flush=True)
            try:
                api_result = exchange_permanent_code(auth_code)
                if not api_result:
                    print(f'❌ 换取permanent_code失败', file=sys.stderr, flush=True)
                    return
                
                # 从API返回中提取企业信息
                auth_corp_info = api_result.get('auth_corp_info', {})
                corp_id = auth_corp_info.get('corpid')
                corp_name = auth_corp_info.get('corp_name', 'Unknown')
                permanent_code = api_result.get('permanent_code')
                
                # 提取授权信息（包含可见范围）
                auth_info = api_result.get('auth_info', {})
                auth_user_info = api_result.get('auth_user_info', {})
                installer_userid = auth_user_info.get('userid')  # 安装者userid
                
                # 提取可见范围用户列表
                visible_users = []
                user_limit = 0
                if auth_info and 'agent' in auth_info:
                    for agent in auth_info['agent']:
                        privilege = agent.get('privilege', {})
                        allow_users = privilege.get('allow_user', [])
                        visible_users.extend(allow_users)
                        user_limit = len(allow_users)
                
                # 打印完整信息以便调试
                print(f'📋 企业信息：{auth_corp_info}', file=sys.stderr, flush=True)
                print(f'👤 安装者：{installer_userid}', file=sys.stderr, flush=True)
                print(f'👥 可见范围用户数：{user_limit}', file=sys.stderr, flush=True)
                
                if not corp_id or not permanent_code:
                    print(f'❌ API返回数据不完整', file=sys.stderr, flush=True)
                    return
                
                print(f'✅ 获得permanent_code', file=sys.stderr, flush=True)
                print(f'   corp_id: {corp_id}', file=sys.stderr, flush=True)
                print(f'   corp_name: {corp_name}', file=sys.stderr, flush=True)
                
                # 保存或更新租户
                tenant = Tenant.query.filter_by(corp_id=corp_id).first()
                if not tenant:
                    tenant = Tenant(corp_id=corp_id, name=corp_name)
                    print(f'➕ 创建新租户：{corp_name}', file=sys.stderr, flush=True)
                else:
                    tenant.name = corp_name
                    print(f'🔄 更新租户：{corp_name}', file=sys.stderr, flush=True)
                
                tenant.permanent_code = permanent_code
                tenant.plan = 'trial'
                tenant.installer_userid = installer_userid
                tenant.auth_info = json.dumps(auth_info, ensure_ascii=False)
                tenant.user_limit = user_limit
                
                # config字段是Text类型，需要存JSON字符串
                if tenant.config is None or tenant.config == '':
                    tenant.config = '{}'
                
                db.session.add(tenant)
                db.session.commit()
                
                print(f'🎉 租户保存成功！ID={tenant.id}, Name={tenant.name}, 安装者={installer_userid}, 名额={user_limit}', file=sys.stderr, flush=True)
            except Exception as e:
                print(f'❌ 处理授权时发生错误: {e}', file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
        elif info_type == 'cancel_auth':
            corp_id = root.findtext('AuthCorpId')
            tenant = Tenant.query.filter_by(corp_id=corp_id).first()
            if tenant:
                tenant.plan = 'cancelled'
                db.session.commit()
            print(f'⭐ cancel auth corp_id={corp_id}', file=sys.stderr, flush=True)
        elif info_type == 'change_external_contact':
            # 处理外部联系人事件
            change_type = root.findtext('ChangeType')
            userid = root.findtext('UserID')
            external_userid = root.findtext('ExternalUserID')
            auth_corp_id = root.findtext('AuthCorpId')
            welcome_code = root.findtext('WelcomeCode')
            state = root.findtext('State')
            
            print(f'📇 外部联系人事件: change_type={change_type}, userid={userid}, external_userid={external_userid}', 
                  file=sys.stderr, flush=True)
            print(f'   auth_corp_id={auth_corp_id}, welcome_code={welcome_code[:20] if welcome_code else "None"}', 
                  file=sys.stderr, flush=True)
            
            # 查找租户
            tenant = Tenant.query.filter_by(corp_id=auth_corp_id).first()
            if not tenant:
                print(f'❌ 租户不存在: auth_corp_id={auth_corp_id}', file=sys.stderr, flush=True)
            else:
                print(f'✅ 找到租户: id={tenant.id}, name={tenant.name}', file=sys.stderr, flush=True)
                
                # 查找员工
                member = Member.query.filter_by(tenant_id=tenant.id, userid=userid).first()
                if not member:
                    print(f'⚠️ 员工不存在，尝试同步: userid={userid}', file=sys.stderr, flush=True)
                else:
                    print(f'✅ 找到员工: id={member.id}, name={member.name}', file=sys.stderr, flush=True)
                
                if change_type in ('add_external_contact', 'add_half_external_contact'):
                    event_name = '添加外部联系人' if change_type == 'add_external_contact' else '外部联系人免验证添加成员'
                    print(f'➕ 处理{event_name}事件', file=sys.stderr, flush=True)
                    
                    # ✅ 检查成员OAuth授权状态
                    if member and not member.oauth_authorized:
                        if not member.name or member.name == userid or not member.avatar_url:
                            print(f'⚠️ 成员尚未完成OAuth授权，推送名片可能显示不完整: userid={userid}, name={member.name}, has_avatar={bool(member.avatar_url)}', file=sys.stderr, flush=True)
                    
                    # 只有在有welcome_code且员工存在的情况下才推送名片
                    if welcome_code and member:
                        # 1. 构建卡片预览链接（用于推送消息）
                        card_preview_url = f'https://zjemail.cn/card-preview/{tenant.id}/{member.id}'
                        # 2. 构建完整名片链接（点击后跳转）
                        card_url = f'https://zjemail.cn/card/{tenant.id}/{member.id}'
                        print(f'🎨 构建卡片预览链接: {card_preview_url}', file=sys.stderr, flush=True)
                        print(f'🎨 构建完整名片链接: {card_url}', file=sys.stderr, flush=True)
                        
                        # 2. 获取推送配置（从租户配置中读取，如果没有使用默认值）
                        try:
                            config = json.loads(tenant.config or '{}')
                            push_config = config.get('push_config', {})
                            card_title = push_config.get('cardTitle', f'{member.name}的电子名片')
                            
                            print(f'📋 推送配置: title={card_title}', file=sys.stderr, flush=True)
                        except Exception as e:
                            print(f'⚠️ 读取推送配置失败，使用默认值: {e}', file=sys.stderr, flush=True)
                            card_title = f'{member.name}的电子名片'
                        
                        # 3. 发送欢迎语（推送两条消息：文字标题 + 卡片链接）
                        success = send_welcome_message(
                            corp_id=auth_corp_id,
                            permanent_code=tenant.permanent_code,
                            welcome_code=welcome_code,
                            card_preview_url=card_preview_url,  # 卡片预览链接
                            card_title=card_title  # 第一条文字消息的标题
                        )
                        
                        if success:
                            print(f'🎉 名片自动推送成功！客户将收到 {member.name} 的数字名片', file=sys.stderr, flush=True)
                        else:
                            print(f'⚠️ 名片推送失败，但不影响业务流程', file=sys.stderr, flush=True)
                    else:
                        if not welcome_code:
                            print(f'⚠️ 缺少welcome_code，无法发送欢迎语', file=sys.stderr, flush=True)
                        if not member:
                            print(f'⚠️ 员工不存在，无法推送名片', file=sys.stderr, flush=True)
                    
                elif change_type == 'del_external_contact':
                    print(f'➖ 处理删除外部联系人事件', file=sys.stderr, flush=True)
                elif change_type == 'del_follow_user':
                    print(f'🗑️ 处理成员被客户删除事件', file=sys.stderr, flush=True)
    except Exception as exc:
        print(f'❌ process_event error: {exc}; data={xml_plaintext[:200]}', file=sys.stderr, flush=True)
        current_app.logger.error(f'process_event error: {exc}; data={xml_plaintext[:200]}')


def verify_signature(token, timestamp, nonce, data, signature):
    try:
        params = [token, timestamp, nonce, data]
        params.sort()
        calculated = hashlib.sha1(''.join(params).encode('utf-8')).hexdigest()
        return calculated == signature
    except Exception as exc:
        current_app.logger.error(f'Verify signature error: {exc}')
        return False


def decrypt_message(encrypted):
    try:
        from Crypto.Cipher import AES
        import struct
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


def generate_jwt_token(payload, expires_in=JWT_EXPIRATION):
    """生成JWT token"""
    exp = datetime.utcnow() + timedelta(seconds=expires_in)
    token_payload = {
        **payload,
        'exp': exp,
        'iat': datetime.utcnow()
    }
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_oauth_url(redirect_uri, state='oauth_login'):
    """生成OAuth授权URL（使用snsapi_privateinfo获取敏感信息）"""
    suite_id = WECOM_CONFIG['suite_id']
    params = {
        'appid': suite_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'snsapi_privateinfo',  # ✅ 关键：获取敏感信息
        'state': state
    }
    oauth_url = f"https://open.weixin.qq.com/connect/oauth2/authorize?{urlencode(params)}#wechat_redirect"
    print(f'🔗 生成OAuth URL: {oauth_url}', file=sys.stderr, flush=True)
    return oauth_url


def fetch_oauth_user_info(auth_code, tenant):
    """通过OAuth code获取用户完整信息
    
    流程：
    1. getuserinfo3rd - 获取user_ticket
    2. getuserdetail3rd - 获取完整用户信息（包括对外显示名称、头像等）
    
    返回：
    {
        'userid': 'xxx',
        'name': '对外显示名称',
        'avatar': 'http://...',
        'mobile': '13800138000',
        'position': '产品经理',
        'external_position': '高级产品经理',
        'email': 'xxx@company.com',
        'qr_code': 'http://...'
    }
    """
    try:
        # Step 1: 获取suite_access_token
        suite_token = get_suite_access_token()
        if not suite_token:
            print(f'❌ 获取suite_access_token失败', file=sys.stderr, flush=True)
            return None
        
        # Step 2: 获取corp_access_token
        corp_token = get_corp_access_token(tenant.corp_id, tenant.permanent_code)
        if not corp_token:
            print(f'❌ 获取corp_access_token失败', file=sys.stderr, flush=True)
            return None
        
        # Step 3: 调用getuserinfo3rd获取user_ticket
        print(f'🔑 调用getuserinfo3rd获取user_ticket, code={auth_code}', file=sys.stderr, flush=True)
        resp1 = requests.get(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/getuserinfo3rd',
            params={
                'suite_access_token': suite_token,
                'code': auth_code
            },
            timeout=10
        )
        data1 = resp1.json()
        print(f'📥 getuserinfo3rd响应: {data1}', file=sys.stderr, flush=True)
        
        if data1.get('errcode') != 0:
            print(f'❌ getuserinfo3rd失败: {data1}', file=sys.stderr, flush=True)
            return None
        
        userid = data1.get('userid') or data1.get('UserId')
        open_userid = data1.get('open_userid')  # 服务商主体下的加密userid
        user_ticket = data1.get('user_ticket')
        
        # ⚠️ 注意：第三方应用调用getuserinfo3rd时，返回的userid实际上就是open_userid
        # 如果明确返回了open_userid字段，则使用它；否则当前userid就是open_userid
        if not open_userid:
            open_userid = userid
        
        if not user_ticket:
            print(f'⚠️ 未获取到user_ticket，可能是管理员或scope不足', file=sys.stderr, flush=True)
            # 返回基础信息
            return {'userid': userid, 'open_userid': open_userid}
        
        # Step 4: 使用user_ticket调用getuserdetail3rd获取完整信息
        print(f'🎫 使用user_ticket获取完整信息', file=sys.stderr, flush=True)
        resp2 = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/getuserdetail3rd',
            params={'suite_access_token': suite_token},
            json={'user_ticket': user_ticket},
            timeout=10
        )
        data2 = resp2.json()
        print(f'📥 getuserdetail3rd完整响应: {json.dumps(data2, ensure_ascii=False, indent=2)}', file=sys.stderr, flush=True)
        
        if data2.get('errcode') != 0:
            print(f'❌ getuserdetail3rd失败: {data2}', file=sys.stderr, flush=True)
            return {'userid': userid}
        
        # ✅ 提取完整信息（注意：这里的name就是对外显示名称）
        user_info = {
            'userid': userid,
            'open_userid': open_userid,  # 服务商主体下的加密userid
            'user_ticket': user_ticket,
            'name': data2.get('name'),  # 对外显示名称
            'avatar': data2.get('avatar'),
            'mobile': data2.get('mobile'),
            'position': data2.get('position'),
            'external_position': data2.get('external_position'),
            'email': data2.get('email'),
            'qr_code': data2.get('qr_code'),
            'gender': data2.get('gender'),
            'telephone': data2.get('telephone'),
            'address': data2.get('address')
        }
        
        print(f'✅ OAuth提取的信息:', file=sys.stderr, flush=True)
        print(f'  - userid: {userid}', file=sys.stderr, flush=True)
        print(f'  - name: {user_info.get("name")} (类型: {type(user_info.get("name"))})', file=sys.stderr, flush=True)
        print(f'  - avatar: {user_info.get("avatar")}', file=sys.stderr, flush=True)
        print(f'  - mobile: {user_info.get("mobile")} (类型: {type(user_info.get("mobile"))})', file=sys.stderr, flush=True)
        print(f'  - position: {user_info.get("position")} (类型: {type(user_info.get("position"))})', file=sys.stderr, flush=True)
        print(f'  - external_position: {user_info.get("external_position")}', file=sys.stderr, flush=True)
        print(f'  - email: {user_info.get("email")}', file=sys.stderr, flush=True)
        return user_info
        
    except requests.Timeout:
        print(f'❌ OAuth请求超时', file=sys.stderr, flush=True)
        return None
    except Exception as e:
        print(f'❌ OAuth获取用户信息异常: {e}', file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return None


def get_corp_access_token(corp_id, permanent_code):
    """获取企业的access_token"""
    suite_access_token = get_suite_access_token()
    if not suite_access_token:
        return None
    
    try:
        resp = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/get_corp_token?suite_access_token={suite_access_token}',
            json={
                'auth_corpid': corp_id,
                'permanent_code': permanent_code
            },
            timeout=5
        )
        data = resp.json()
        # 企微成功响应：有access_token字段且无errcode，或errcode=0
        if 'access_token' in data and data.get('errcode', 0) == 0:
            return data['access_token']
        current_app.logger.error(f'get_corp_access_token error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_corp_access_token exception: {exc}')
    return None


def send_welcome_message(corp_id, permanent_code, welcome_code, card_preview_url, card_title):
    """
    发送欢迎语（推送名片）
    发送两条消息：
    1. 第一条：纯文字消息（标题）
    2. 第二条：卡片消息（链接到卡片预览页面）
    
    参数:
        corp_id: 企业ID
        permanent_code: 永久授权码
        welcome_code: 欢迎语code（从回调事件中获取）
        card_preview_url: 卡片预览链接
        card_title: 消息标题（纯文字）
    
    返回:
        成功返回True，失败返回False
    """
    import sys
    
    # 1. 获取企业access_token
    access_token = get_corp_access_token(corp_id, permanent_code)
    if not access_token:
        print(f'❌ 获取access_token失败: corp_id={corp_id}', file=sys.stderr, flush=True)
        return False
    
    print(f'✅ 获取access_token成功', file=sys.stderr, flush=True)
    
    # 2. 构建欢迎语消息（发送两条消息）
    # 第一条：纯文字消息
    # 第二条：卡片消息（链接）
    message_data = {
        'welcome_code': welcome_code,
        'attachments': [
            {
                'msgtype': 'text',
                'text': {
                    'content': card_title
                }
            },
            {
                'msgtype': 'link',
                'link': {
                    'title': '我的数字名片',
                    'url': card_preview_url,
                    'desc': '点击查看我的联系方式和服务介绍'
                }
            }
        ]
    }
    
    print(f'📤 准备发送欢迎语: 第一条文字={card_title}, 第二条卡片链接={card_preview_url}', file=sys.stderr, flush=True)
    
    # 3. 调用企微API发送欢迎语
    try:
        api_url = f'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/send_welcome_msg?access_token={access_token}'
        resp = requests.post(api_url, json=message_data, timeout=10)
        result = resp.json()
        
        if result.get('errcode') == 0:
            print(f'✅ 名片推送成功！', file=sys.stderr, flush=True)
            return True
        else:
            print(f'❌ 名片推送失败: errcode={result.get("errcode")}, errmsg={result.get("errmsg")}', 
                  file=sys.stderr, flush=True)
            current_app.logger.error(f'send_welcome_message error: {result}')
            return False
    except Exception as exc:
        print(f'❌ 发送欢迎语异常: {exc}', file=sys.stderr, flush=True)
        current_app.logger.error(f'send_welcome_message exception: {exc}')
        return False


def get_user_info_by_code(corp_id, permanent_code, code):
    """通过code获取用户信息"""
    access_token = get_corp_access_token(corp_id, permanent_code)
    if not access_token:
        return None
    
    try:
        resp = requests.get(
            f'https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo?access_token={access_token}&code={code}',
            timeout=5
        )
        data = resp.json()
        if data.get('errcode') == 0:
            return data
        current_app.logger.error(f'get_user_info_by_code error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_user_info_by_code exception: {exc}')
    return None


def get_user_info(access_token, userid):
    """
    通过企业access_token获取单个成员的详细信息
    """
    try:
        resp = requests.get(
            'https://qyapi.weixin.qq.com/cgi-bin/user/get',
            params={
                'access_token': access_token,
                'userid': userid
            },
            timeout=5
        )
        data = resp.json()
        if data.get('errcode') == 0:
            return data
        current_app.logger.error(f'get_user_info error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_user_info exception: {exc}')
    return None


def sync_member_profile(tenant, userid, role, member=None):
    """
    使用企微API同步成员资料，确保名片展示信息完整
    """
    try:
        print(f'🔄 开始同步成员资料: tenant_id={tenant.id}, userid={userid}', file=sys.stderr, flush=True)
        
        corp_access_token = get_corp_access_token(tenant.corp_id, tenant.permanent_code)
        if not corp_access_token:
            current_app.logger.warning(f'sync_member_profile: failed to get corp access token for tenant {tenant.id}')
            print(f'❌ 获取corp_access_token失败', file=sys.stderr, flush=True)
            return member
        
        print(f'✅ 获取到corp_access_token: {corp_access_token[:20]}...', file=sys.stderr, flush=True)
        
        user_info = get_user_info(corp_access_token, userid)
        if not user_info:
            current_app.logger.warning(f'sync_member_profile: empty user_info for userid={userid}')
            print(f'❌ 从企微API获取用户信息失败', file=sys.stderr, flush=True)
            return member
        
        print(f'✅ 从企微API获取到用户信息: {user_info}', file=sys.stderr, flush=True)
        
        created = False
        if member is None:
            member = Member(
                tenant_id=tenant.id,
                userid=userid
            )
            db.session.add(member)
            created = True
        
        # ✅ 优先使用对外属性中的名称（第三方应用无法获取name，返回userid）
        external_profile = user_info.get('external_profile', {})
        external_attr = external_profile.get('external_attr', []) if isinstance(external_profile, dict) else []
        
        # 尝试从对外属性中获取对外名称
        external_name = None
        for attr in external_attr:
            if attr.get('type') == 0:  # 文本类型
                attr_name = attr.get('name', '')
                if attr_name in ['姓名', '对外名称', 'name']:
                    external_name = attr.get('value', {}).get('text', '')
                    break
        
        # 名称优先级：对外属性名称 > API返回的name > 现有name > userid
        name_value = external_name or user_info.get('name')
        if name_value and name_value != userid:
            member.name = name_value
        elif not member.name or member.name == userid:
            # 如果无法获取真实姓名，使用userid但添加提示
            member.name = userid
            print(f'⚠️ 无法获取真实姓名，使用userid: {userid}（第三方应用限制）', file=sys.stderr, flush=True)
        
        mobile_value = user_info.get('mobile')
        if mobile_value:
            member.mobile = mobile_value
        
        email_value = user_info.get('email')
        if email_value:
            member.email = email_value
        
        # ✅ 头像获取（第三方应用可能无法获取）
        avatar_value = user_info.get('avatar') or user_info.get('avatar_url') or user_info.get('thumb_avatar')
        if avatar_value:
            member.avatar_url = avatar_value
        else:
            print(f'⚠️ 无法获取头像URL（第三方应用限制）', file=sys.stderr, flush=True)
        
        # ✅ 职位优先使用对外职位
        position_value = user_info.get('external_position') or user_info.get('position')
        if position_value:
            member.position = position_value
        
        department_name = (
            user_info.get('main_department_name')
            or user_info.get('main_department')
            or user_info.get('department_name')
        )
        if department_name:
            member.department = str(department_name)
        elif isinstance(user_info.get('department'), list) and user_info.get('department'):
            member.department = ' / '.join(str(dep) for dep in user_info.get('department'))
        
        status = user_info.get('status')
        if status is not None:
            member.is_active = (status == 1)
        
        member.role = 'admin' if role in ('installer', 'super_admin') else 'user'
        member.is_installer = (role == 'installer')
        member.in_visible_range = True
        
        db.session.commit()
        
        if created:
            current_app.logger.info(f'sync_member_profile: created member record for userid={userid}')
        else:
            current_app.logger.info(f'sync_member_profile: updated member record for userid={userid}')
        
    except Exception as exc:
        current_app.logger.error(f'sync_member_profile error: {exc}', exc_info=True)
        db.session.rollback()
    return member


def get_admin_list(corp_id, permanent_code):
    """
    获取应用管理员列表
    返回格式: [{"userid": "xxx", "auth_type": 0/1}, ...]
    auth_type: 0=发消息权限, 1=管理权限
    """
    access_token = get_corp_access_token(corp_id, permanent_code)
    if not access_token:
        return None
    
    try:
        resp = requests.post(
            f'https://qyapi.weixin.qq.com/cgi-bin/agent/get_admin_list?access_token={access_token}',
            timeout=5
        )
        data = resp.json()
        if data.get('errcode') == 0:
            return data.get('admin', [])
        current_app.logger.error(f'get_admin_list error: {data}')
    except Exception as exc:
        current_app.logger.error(f'get_admin_list exception: {exc}')
    return None


def check_user_admin_permission(corp_id, permanent_code, userid):
    """
    检查用户是否有管理员权限
    优先使用get_admin_list，降级到user/get的is_leader字段
    """
    # 方案1：使用管理员列表（推荐，官方接口）
    admin_list = get_admin_list(corp_id, permanent_code)
    if admin_list:
        # auth_type=1 表示管理权限
        for admin in admin_list:
            if admin.get('userid') == userid and admin.get('auth_type') == 1:
                return True
    
    # 方案2：降级方案，使用is_leader字段
    access_token = get_corp_access_token(corp_id, permanent_code)
    if not access_token:
        return False
    
    try:
        # 获取用户详情
        resp = requests.get(
            f'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={userid}',
            timeout=5
        )
        data = resp.json()
        if data.get('errcode') == 0:
            # 检查是否是管理员（isleader=1 或在特定管理部门）
            is_leader = data.get('isleader') == 1
            # 可以根据需要添加更多权限检查逻辑
            return is_leader
        current_app.logger.error(f'check_user_admin_permission error: {data}')
    except Exception as exc:
        current_app.logger.error(f'check_user_admin_permission exception: {exc}')
    return False


def check_user_permission(tenant_id, userid):
    """
    完整的用户权限检查（新版本）
    
    检查逻辑：
    1. 应用安装者 → 管理权限
    2. 企业超管（isleader=1） → 管理权限
    3. 应用可见范围内 → 使用权限
    4. 不在可见范围 → 无权限
    
    返回格式：
    {
        'has_access': bool,      # 是否有访问权限
        'is_admin': bool,        # 是否有管理权限
        'role': str,             # 角色：installer/super_admin/user/none
        'in_visible_range': bool # 是否在可见范围内
    }
    """
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {'has_access': False, 'is_admin': False, 'role': 'none', 'in_visible_range': False}
    
    # 1. 检查是否是安装者（最高优先级）
    if tenant.installer_userid and tenant.installer_userid == userid:
        return {
            'has_access': True,
            'is_admin': True,
            'role': 'installer',
            'in_visible_range': True
        }
    
    # 2. 检查是否是企业超管
    if check_user_admin_permission(tenant.corp_id, tenant.permanent_code, userid):
        return {
            'has_access': True,
            'is_admin': True,
            'role': 'super_admin',
            'in_visible_range': True
        }
    
    # 3. 检查是否在可见范围内
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
        return {
            'has_access': True,
            'is_admin': False,
            'role': 'user',
            'in_visible_range': True
        }
    
    # 4. 无权限
    return {
        'has_access': False,
        'is_admin': False,
        'role': 'none',
        'in_visible_range': False
    }


@bp.route('/oauth/authorize', methods=['GET'])
def oauth_authorize():
    """
    企微OAuth授权入口
    用户访问workspace时，如果未认证，跳转到此接口
    此接口会重定向到企微授权页面
    """
    redirect_uri = request.args.get('redirect_uri', 'https://zjemail.cn/wecom/workspace')
    state = secrets.token_urlsafe(16)
    
    # 将state和redirect_uri存储到session或缓存中
    set_cache(f'oauth_state_{state}', redirect_uri, ttl=600)
    
    # 构造企微授权URL
    suite_id = WECOM_CONFIG['suite_id']
    auth_url = (
        f'https://open.weixin.qq.com/connect/oauth2/authorize'
        f'?appid={suite_id}'
        f'&redirect_uri={quote(redirect_uri, safe="")}'
        f'&response_type=code'
        f'&scope=snsapi_base'
        f'&state={state}'
        f'#wechat_redirect'
    )
    
    return jsonify({'auth_url': auth_url})


@bp.route('/auth/verify_user', methods=['GET'])
def verify_user():
    """
    ✅ 官方推荐的第三方应用认证接口
    使用suite_access_token调用getuserinfo3rd，自动识别企业
    GET /api/v1/wecom/auth/verify_user?code=xxx
    
    返回: {
        "success": true,
        "token": "JWT_TOKEN",
        "user": {
            "userid": "zhangsan",
            "tenant_id": 1,
            "corp_id": "wxabc123",
            "is_admin": true,
            "open_userid": "woxxx..."
        }
    }
    """
    code = request.args.get('code')
    
    if not code:
        return jsonify({'error': '缺少授权code参数'}), 400
    
    # 1. 获取suite_access_token
    suite_access_token = get_suite_access_token()
    if not suite_access_token:
        return jsonify({
            'error': '获取服务商凭证失败',
            'message': '请稍后重试'
        }), 500
    
    # 2. 使用第三方接口获取用户身份（官方推荐）
    try:
        resp = requests.get(
            f'https://qyapi.weixin.qq.com/cgi-bin/service/auth/getuserinfo3rd',
            params={
                'suite_access_token': suite_access_token,
                'code': code
            },
            timeout=5
        )
        user_data = resp.json()
        
        if user_data.get('errcode') != 0:
            current_app.logger.error(f'getuserinfo3rd error: {user_data}')
            return jsonify({
                'error': '获取用户信息失败',
                'message': user_data.get('errmsg', 'code可能已过期，请刷新页面重试')
            }), 400
        
        # 从返回结果中获取corpid（自动识别企业）
        corp_id = user_data.get('corpid')
        userid = user_data.get('userid')
        open_userid = user_data.get('open_userid')
        
        if not corp_id:
            # 用户不属于任何企业
            return jsonify({
                'error': '用户未加入企业',
                'message': '请使用企业微信账号访问',
                'openid': user_data.get('openid')
            }), 403
        
        if not userid:
            return jsonify({
                'error': '用户信息不完整',
                'message': '无法获取userid'
            }), 400
            
    except Exception as exc:
        current_app.logger.error(f'getuserinfo3rd exception: {exc}')
        return jsonify({
            'error': '网络请求失败',
            'message': '请稍后重试'
        }), 500
    
    # 3. 查询租户
    tenant = Tenant.query.filter_by(corp_id=corp_id).first()
    if not tenant:
        return jsonify({
            'error': '未找到对应的企业信息',
            'message': f'企业（{corp_id}）尚未安装应用，请先完成安装'
        }), 404
    
    if not tenant.permanent_code:
        return jsonify({
            'error': '企业授权信息不完整',
            'message': '请重新安装应用'
        }), 400
    
    # 4. 使用新的权限检查（完整版本）
    permission = check_user_permission(tenant.id, userid)
    
    # 只有管理员可以访问配置工作台
    allow_non_admin = request.args.get('allow_non_admin') in ('1', 'true', 'True') or request.args.get('target') == 'card'
    if not permission['is_admin']:
        if not permission['has_access']:
            return jsonify({
                'error': '无访问权限',
                'message': '您不在应用可见范围内，无法访问此功能',
                'userid': userid,
                'corp_id': corp_id,
                'role': permission['role']
            }), 403
        if not allow_non_admin:
            return jsonify({
                'error': '权限不足',
                'message': '您是普通用户，只有管理员才能配置名片工作台',
                'role': permission['role'],
                'userid': userid,
                'corp_id': corp_id
            }), 403
    
    # 5. 生成JWT token（包含完整权限信息）
    token_payload = {
        'tenant_id': tenant.id,
        'userid': userid,
        'corp_id': corp_id,
        'open_userid': open_userid,
        'is_admin': permission['is_admin'],
        'role': permission['role'],
        'in_visible_range': permission['in_visible_range'],
        'has_access': permission['has_access']
    }
    
    token = generate_jwt_token(token_payload)
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'userid': userid,
            'open_userid': open_userid,
            'tenant_id': tenant.id,
            'tenant_name': tenant.name,
            'corp_id': corp_id,
            'is_admin': permission['is_admin'],
            'role': permission['role'],
            'in_visible_range': permission['in_visible_range'],
            'has_access': permission['has_access']
        }
    })


@bp.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    """
    企微OAuth回调处理
    企微会携带code和state回调到这里
    
    支持两种场景：
    1. state=oauth_login - 普通登录（原有逻辑）
    2. state=oauth_member_info - 获取完整成员信息（新增）
    """
    code = request.args.get('code')
    state = request.args.get('state', 'oauth_login')
    
    if not code:
        return jsonify({'error': '缺少授权code'}), 400
    
    # 这里需要知道用户来自哪个企业
    corp_id = request.args.get('corp_id')
    if not corp_id:
        return jsonify({'error': '缺少企业标识，请从企业微信工作台访问'}), 400
    
    # 查找租户
    tenant = Tenant.query.filter_by(corp_id=corp_id).first()
    if not tenant:
        return jsonify({'error': '未找到对应的企业信息，请先完成应用安装'}), 404
    
    # ✅ 场景2：获取完整成员信息（使用snsapi_privateinfo）
    if state == 'oauth_member_info':
        print(f'🎫 OAuth获取成员完整信息: corp_id={corp_id}, code={code}', file=sys.stderr, flush=True)
        
        # 调用fetch_oauth_user_info获取完整信息
        user_info = fetch_oauth_user_info(code, tenant)
        if not user_info:
            return jsonify({'error': '获取用户完整信息失败'}), 502
        
        userid = user_info.get('userid')
        open_userid = user_info.get('open_userid')
        if not userid:
            return jsonify({'error': '无法获取用户ID'}), 502
        
        # ⚠️ 注意：OAuth授权时，userid实际是open_userid（加密ID）
        # 先用open_userid查询成员，如果找不到则创建
        member = Member.query.filter_by(tenant_id=tenant.id, open_userid=open_userid).first()
        
        # 如果通过open_userid没找到，尝试通过userid查找（兼容旧数据）
        if not member and userid:
            member = Member.query.filter_by(tenant_id=tenant.id, userid=userid).first()
        
        # 如果还是没找到，创建新成员（userid暂时等于open_userid，后续同步时会更新）
        if not member:
            member = Member(
                tenant_id=tenant.id,
                userid=userid,  # 暂时使用返回的userid（实际是open_userid）
                open_userid=open_userid
            )
            db.session.add(member)
            print(f'📝 创建新成员记录: userid={userid}, open_userid={open_userid}', file=sys.stderr, flush=True)
        else:
            # 更新open_userid字段（如果之前没有）
            if not member.open_userid:
                member.open_userid = open_userid
                print(f'📝 更新成员open_userid: userid={member.userid}, open_userid={open_userid}', file=sys.stderr, flush=True)
        
        # 🔍 详细调试：检查user_info的每个字段
        print(f'🔍 user_info完整内容:', file=sys.stderr, flush=True)
        print(f'  - userid: {user_info.get("userid")}', file=sys.stderr, flush=True)
        print(f'  - open_userid: {user_info.get("open_userid")}', file=sys.stderr, flush=True)
        print(f'  - name: {user_info.get("name")} (类型: {type(user_info.get("name"))}, 长度: {len(user_info.get("name") or "")})', file=sys.stderr, flush=True)
        print(f'  - mobile: {user_info.get("mobile")} (类型: {type(user_info.get("mobile"))})', file=sys.stderr, flush=True)
        print(f'  - avatar: {user_info.get("avatar")}', file=sys.stderr, flush=True)
        print(f'  - position: {user_info.get("position")}', file=sys.stderr, flush=True)
        print(f'  - external_position: {user_info.get("external_position")}', file=sys.stderr, flush=True)
        print(f'  - email: {user_info.get("email")}', file=sys.stderr, flush=True)
        print(f'  - user_ticket: {user_info.get("user_ticket") is not None}', file=sys.stderr, flush=True)
        
        # ✅ 更新成员信息（优先使用external_position）
        if user_info.get('name'):
            member.name = user_info['name']  # 对外显示名称
            print(f'  ✅ 更新name: {member.name}', file=sys.stderr, flush=True)
        else:
            print(f'  ⚠️  name为空，不更新', file=sys.stderr, flush=True)
            
        if user_info.get('avatar'):
            member.avatar_url = user_info['avatar']
            print(f'  ✅ 更新avatar_url', file=sys.stderr, flush=True)
        else:
            print(f'  ⚠️  avatar为空，不更新', file=sys.stderr, flush=True)
            
        if user_info.get('mobile'):
            member.mobile = user_info['mobile']
            print(f'  ✅ 更新mobile: {member.mobile}', file=sys.stderr, flush=True)
        else:
            print(f'  ⚠️  mobile为空，不更新', file=sys.stderr, flush=True)
            
        if user_info.get('external_position'):
            member.position = user_info['external_position']
            print(f'  ✅ 更新position(external): {member.position}', file=sys.stderr, flush=True)
        elif user_info.get('position'):
            member.position = user_info['position']
            print(f'  ✅ 更新position: {member.position}', file=sys.stderr, flush=True)
        else:
            print(f'  ⚠️  position为空，不更新', file=sys.stderr, flush=True)
            
        if user_info.get('email'):
            member.email = user_info['email']
            print(f'  ✅ 更新email: {member.email}', file=sys.stderr, flush=True)
        else:
            print(f'  ⚠️  email为空，不更新', file=sys.stderr, flush=True)
        
        # 标记已授权
        member.oauth_authorized = True
        member.oauth_authorized_at = datetime.now()
        if user_info.get('user_ticket'):
            member.user_ticket = user_info['user_ticket']
        
        try:
            db.session.commit()
            print(f'✅ 成员信息已更新并标记授权: userid={userid}, name={member.name}, has_avatar={bool(member.avatar_url)}, has_mobile={bool(member.mobile)}', file=sys.stderr, flush=True)
        except Exception as e:
            db.session.rollback()
            print(f'❌ 保存成员信息失败: {e}', file=sys.stderr, flush=True)
            return jsonify({'error': '保存用户信息失败'}), 500
        
        # 检查用户权限
        is_admin = check_user_admin_permission(corp_id, tenant.permanent_code, userid)
        
        # 生成新token
        token = generate_jwt_token({
            'tenant_id': tenant.id,
            'corp_id': corp_id,
            'userid': userid,
            'is_admin': is_admin,
            'role': 'admin' if is_admin else 'user'
        })
        
        # 重定向到名片页面（带token）
        frontend_url = request.url_root.rstrip('/')
        redirect_url = f'{frontend_url}/wecom/card?token={token}&oauth_success=1'
        return redirect(redirect_url)
    
    # ✅ 场景1：普通登录（原有逻辑）
    # 通过code获取用户信息
    user_info = get_user_info_by_code(corp_id, tenant.permanent_code, code)
    if not user_info:
        return jsonify({'error': '获取用户信息失败'}), 502
    
    userid = user_info.get('userid') or user_info.get('UserId')
    if not userid:
        return jsonify({'error': '无法获取用户ID'}), 502
    
    # 检查用户是否有管理员权限
    is_admin = check_user_admin_permission(corp_id, tenant.permanent_code, userid)
    
    # 生成JWT token
    token = generate_jwt_token({
        'tenant_id': tenant.id,
        'corp_id': corp_id,
        'userid': userid,
        'is_admin': is_admin
    })
    
    # 记录登录日志
    current_app.logger.info(
        f'User login: tenant_id={tenant.id}, corp_id={corp_id}, userid={userid}, is_admin={is_admin}'
    )
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'userid': userid,
            'tenant_id': tenant.id,
            'corp_id': corp_id,
            'is_admin': is_admin
        }
    })


@bp.route('/auth/verify', methods=['POST'])
def verify_auth():
    """验证认证token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '缺少认证token'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    return jsonify({
        'valid': True,
        'user': {
            'tenant_id': payload.get('tenant_id'),
            'corp_id': payload.get('corp_id'),
            'userid': payload.get('userid'),
            'is_admin': payload.get('is_admin', False)
        }
    })


@bp.route('/tenant/info', methods=['GET'])
def get_tenant_info():
    """获取租户工作台信息（需要企业微信身份认证）"""
    # 从Authorization header获取token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '未识别到租户身份，请从企业微信中访问'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期，请重新登录'}), 401
    
    tenant_id = payload.get('tenant_id')
    is_admin = payload.get('is_admin', False)
    
    # 只有管理员可以访问workspace配置
    if not is_admin:
        return jsonify({'error': '您没有权限访问此功能，请联系管理员'}), 403
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    # 获取名片模版配置（从 JSON 字段或单独的配置表）
    template_config = json.loads(tenant.config or '{}').get('card_template', {
        'title': '员工数字名片',
        'theme': 'tech',
        'fields': {
            'name': True,
            'phone': True,
            'email': True,
            'position': True,
            'department': True
        }
    })
    
    # 获取推送配置
    push_config = json.loads(tenant.config or '{}').get('push_config', {
        'cardUrl': 'https://zjemail.cn/card/{userid}',
        'cardTitle': '这是我的电子名片',
        'cardDesc': '点击查看我的联系方式和详细信息',
        'cardImage': ''
    })
    
    # 获取统计数据（临时返回模拟数据，后续从 card_logs 表统计）
    stats = {
        'totalPush': 0,
        'totalView': 0,
        'openRate': '0%',
        'totalInteraction': 0
    }
    
    return jsonify({
        'tenant': {
            'id': tenant.id,
            'name': tenant.name,
            'corp_id': tenant.corp_id,
            'plan': tenant.plan
        },
        'user': {
            'userid': payload.get('userid'),
            'is_admin': is_admin
        },
        'template': template_config,
        'pushConfig': push_config,
        'stats': stats
    })


@bp.route('/tenant/template', methods=['POST'])
def save_tenant_template():
    """保存租户名片模版配置"""
    tenant_id = request.args.get('tenant_id') or request.headers.get('X-Tenant-ID')
    
    if not tenant_id:
        return jsonify({'error': '未识别到租户身份'}), 401
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    payload = request.get_json() or {}
    
    # 更新配置
    config = json.loads(tenant.config or '{}')
    config['card_template'] = payload
    tenant.config = json.dumps(config, ensure_ascii=False)
    
    try:
        db.session.commit()
        current_app.logger.info(f'Tenant {tenant_id} updated card template')
        return jsonify({'success': True, 'message': '名片模版保存成功'})
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Failed to save template for tenant {tenant_id}: {exc}')
        return jsonify({'error': '保存失败，请稍后重试'}), 500


@bp.route('/tenant/push-config', methods=['POST'])
def save_push_config():
    """保存租户推送配置"""
    tenant_id = request.args.get('tenant_id') or request.headers.get('X-Tenant-ID')
    
    if not tenant_id:
        return jsonify({'error': '未识别到租户身份'}), 401
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    payload = request.get_json() or {}
    
    # 更新配置
    config = json.loads(tenant.config or '{}')
    config['push_config'] = payload
    tenant.config = json.dumps(config, ensure_ascii=False)
    
    try:
        db.session.commit()
        current_app.logger.info(f'Tenant {tenant_id} updated push config')
        return jsonify({'success': True, 'message': '推送配置保存成功'})
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f'Failed to save push config for tenant {tenant_id}: {exc}')
        return jsonify({'error': '保存失败，请稍后重试'}), 500


# ============================================================
# 工作台配置接口（新增）
# ============================================================

@bp.route('/tenant/workspace', methods=['GET'])
def get_workspace_config():
    """
    获取租户工作台配置（需要JWT认证）
    GET /api/v1/wecom/tenant/workspace
    Headers: Authorization: Bearer <token>
    """
    # 验证认证token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    is_admin = payload.get('is_admin', False)
    
    # 只有管理员可以访问workspace配置
    if not is_admin:
        return jsonify({'error': '您没有管理员权限'}), 403
    
    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # 解析配置
    try:
        config = json.loads(tenant.config or '{}')
    except json.JSONDecodeError:
        config = {}
    
    # 如果没有workspace配置，返回默认配置
    workspace_config = config.get('workspace', {
        'version': '1.0',
        'modules': [],
        'header': {
            'background_style': 'solid',
            'slogan': '',
            'show_company_logo': True,
            'contact_visibility': {
                'mobile': True,
                'wechat': True,
                'email': True,
                'phone': False,
                'address': False,
                'website': True
            }
        },
        'theme': 'tech'
    })
    
    return jsonify({
        'success': True,
        'tenant_info': {
            'id': tenant.id,
            'name': tenant.name,
            'corp_id': tenant.corp_id,
            'plan': tenant.plan,
            'logo': ''  # TODO: 从配置中获取Logo
        },
        'config': workspace_config
    })


@bp.route('/tenant/workspace', methods=['PUT'])
def save_workspace_config():
    """
    保存租户工作台配置（需要JWT认证）
    PUT /api/v1/wecom/tenant/workspace
    Headers: Authorization: Bearer <token>
    Body: {
        "config": {
            "version": "1.0",
            "modules": [...],
            "header": {...},
            "theme": "tech"
        }
    }
    """
    # 验证认证token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    auth_payload = verify_jwt_token(token)
    
    if not auth_payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = auth_payload.get('tenant_id')
    is_admin = auth_payload.get('is_admin', False)
    
    # 只有管理员可以保存配置
    if not is_admin:
        return jsonify({'error': '您没有管理员权限'}), 403
    
    payload = request.get_json() or {}
    new_workspace_config = payload.get('config')
    push_config = payload.get('push_config')
    
    # 调试日志 - 记录完整的请求内容
    current_app.logger.info(f'收到保存请求: tenant_id={tenant_id}')
    current_app.logger.info(f'请求体内容: push_config={push_config is not None}, config={new_workspace_config is not None}')
    if new_workspace_config:
        current_app.logger.info(f'config字段内容: {list(new_workspace_config.keys()) if isinstance(new_workspace_config, dict) else type(new_workspace_config)}')
    
    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # 读取现有配置
    try:
        config = json.loads(tenant.config or '{}')
    except json.JSONDecodeError as e:
        current_app.logger.warning(f'解析现有配置失败，使用空配置: {e}')
        config = {}
    
    # 如果提供了push_config，直接保存推送配置（优先处理）
    if push_config is not None:
        # 验证push_config格式
        if not isinstance(push_config, dict):
            current_app.logger.error(f'推送配置格式错误: {type(push_config)}')
            return jsonify({'error': '推送配置格式错误，必须是对象'}), 400
        
        config['push_config'] = push_config
        current_app.logger.info(f'Tenant {tenant_id} updated push config: cardTitle={push_config.get("cardTitle", "")}, cardDesc={push_config.get("cardDesc", "")}')
    
    # 如果提供了workspace config，验证并保存（只有当config真正存在且不为空时才处理）
    # 注意：只保存push_config时，不应该提供config字段，或者提供空对象时会被忽略
    # 只有当config是字典类型且包含必填字段时才处理
    if new_workspace_config is not None:
        if not isinstance(new_workspace_config, dict):
            current_app.logger.error(f'workspace config格式错误: {type(new_workspace_config)}')
            return jsonify({'error': 'Invalid config format'}), 400
        
        # 只有当config有内容时才验证和保存（空字典直接忽略）
        config_keys = list(new_workspace_config.keys()) if isinstance(new_workspace_config, dict) else []
        current_app.logger.info(f'workspace config键值: {config_keys}, 长度: {len(new_workspace_config) if isinstance(new_workspace_config, dict) else 0}')
        
        if len(new_workspace_config) > 0:
            # 验证必填字段
            required_fields = ['version', 'modules', 'header', 'theme']
            missing_fields = [field for field in required_fields if field not in new_workspace_config]
            if missing_fields:
                current_app.logger.error(f'缺少必填字段: {missing_fields}, 配置内容: {config_keys}')
                # 如果只保存push_config，不应该验证config字段
                if push_config is not None:
                    current_app.logger.warning(f'同时收到push_config和config，但config缺少必填字段。忽略config，只保存push_config')
                else:
                    return jsonify({'error': f'Missing required field: {missing_fields[0]}'}), 400
            else:
                # 所有必填字段都存在，更新workspace配置
                config['workspace'] = new_workspace_config
                config['workspace']['updated_at'] = datetime.now().isoformat()
                current_app.logger.info(f'Tenant {tenant_id} saved workspace config with {len(new_workspace_config.get("modules", []))} modules')
        else:
            # 空字典，忽略
            current_app.logger.info(f'收到空的workspace config，已忽略')
    
    # 检查是否有任何配置需要保存
    if push_config is None and (new_workspace_config is None or (isinstance(new_workspace_config, dict) and len(new_workspace_config) == 0)):
        current_app.logger.warning(f'没有提供需要保存的配置: push_config={push_config is not None}, workspace_config={new_workspace_config is not None}')
        return jsonify({'error': '没有提供需要保存的配置'}), 400
    
    # 保存到数据库
    try:
        tenant.config = json.dumps(config, ensure_ascii=False)
        db.session.commit()
        
        response_data = {
            'success': True,
            'message': '配置保存成功'
        }
        
        if config.get('workspace', {}).get('updated_at'):
            response_data['saved_at'] = config['workspace']['updated_at']
        elif push_config is not None:
            response_data['saved_at'] = datetime.now().isoformat()
        
        return jsonify(response_data)
    except Exception as exc:
        db.session.rollback()
        error_msg = str(exc)
        current_app.logger.error(f'Failed to save workspace config for tenant {tenant_id}: {exc}', exc_info=True)
        return jsonify({
            'error': '保存失败',
            'message': error_msg
        }), 500


@bp.route('/sync-members', methods=['POST'])
def sync_members():
    """
    从企业微信同步成员信息
    POST /api/v1/wecom/sync-members
    Headers: Authorization: Bearer <token>
    """
    import sys
    
    print('🔄 收到同步成员请求', file=sys.stderr, flush=True)
    
    # 验证认证token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print('❌ 缺少Authorization header', file=sys.stderr, flush=True)
        return jsonify({
            'error': '需要认证',
            'message': '请先登录后再进行同步操作',
            'code': 'AUTH_REQUIRED'
        }), 401
    
    token = auth_header.split(' ')[1]
    print(f'🔑 Token前8位: {token[:8]}...', file=sys.stderr, flush=True)
    
    payload = verify_jwt_token(token)
    
    if not payload:
        print('❌ Token验证失败', file=sys.stderr, flush=True)
        return jsonify({
            'error': '认证token无效或已过期',
            'message': '您的登录已过期，请刷新页面重新登录',
            'code': 'TOKEN_EXPIRED'
        }), 401
    
    tenant_id = payload.get('tenant_id')
    corp_id = payload.get('corp_id')
    is_admin = payload.get('is_admin', False)
    
    print(f'✅ Token验证成功: tenant_id={tenant_id}, corp_id={corp_id}, is_admin={is_admin}', file=sys.stderr, flush=True)
    
    # 只有管理员可以同步
    if not is_admin:
        print(f'❌ 用户无管理员权限', file=sys.stderr, flush=True)
        return jsonify({
            'error': '您没有管理员权限',
            'message': '只有管理员才能同步企业通讯录',
            'code': 'PERMISSION_DENIED'
        }), 403
    
    # 查询租户
    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        print(f'❌ 租户不存在: tenant_id={tenant_id}', file=sys.stderr, flush=True)
        return jsonify({
            'error': '企业不存在',
            'message': '未找到对应的企业信息',
            'code': 'TENANT_NOT_FOUND'
        }), 404
    
    if not tenant.permanent_code:
        print(f'❌ 租户permanent_code为空', file=sys.stderr, flush=True)
        return jsonify({
            'error': '企业授权信息不完整',
            'message': '请重新安装应用或联系管理员',
            'code': 'PERMANENT_CODE_MISSING'
        }), 400
    
    print(f'🔄 开始同步成员: tenant_id={tenant_id}, corp_id={corp_id}, tenant_name={tenant.name}', file=sys.stderr, flush=True)
    
    try:
        # 获取企业access_token
        corp_access_token = get_corp_access_token(corp_id, tenant.permanent_code)
        if not corp_access_token:
            return jsonify({'error': '获取企业access_token失败'}), 502
        
        # 获取部门列表
        dept_url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list'
        dept_resp = requests.get(dept_url, params={'access_token': corp_access_token}, timeout=10)
        dept_data = dept_resp.json()
        
        if dept_data.get('errcode') != 0:
            print(f'❌ 获取部门列表失败: {dept_data}', file=sys.stderr, flush=True)
            return jsonify({'error': f'获取部门列表失败: {dept_data.get("errmsg")}'}), 502
        
        departments = dept_data.get('department', [])
        print(f'📂 获取到 {len(departments)} 个部门', file=sys.stderr, flush=True)
        
        # 遍历部门获取成员
        synced_count = 0
        updated_count = 0
        created_count = 0
        synced_userids = set()  # 记录本次同步到的userid，用于标记离职/不可见用户
        
        for dept in departments:
            dept_id = dept.get('id')
            dept_name = dept.get('name')
            print(f'  📁 同步部门: {dept_name} (id={dept_id})', file=sys.stderr, flush=True)
            
            # 获取部门成员详细信息
            user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list'
            user_resp = requests.get(user_url, params={
                'access_token': corp_access_token,
                'department_id': dept_id,
                'fetch_child': 0
            }, timeout=10)
            user_data = user_resp.json()
            
            if user_data.get('errcode') != 0:
                print(f'  ⚠️ 获取部门成员失败: {user_data.get("errmsg")}', file=sys.stderr, flush=True)
                continue
            
            userlist = user_data.get('userlist', [])
            print(f'    👥 部门成员数: {len(userlist)}', file=sys.stderr, flush=True)
            
            for user_info in userlist:
                userid = user_info.get('userid')  # ✅ 这是企业内部真实userid
                if not userid:
                    continue
                
                synced_userids.add(userid)  # 记录本次同步到的用户
                
                # 查找成员：优先通过真实userid，如果找不到尝试通过name+mobile匹配
                member = Member.query.filter_by(tenant_id=tenant_id, userid=userid).first()
                
                # 如果通过userid没找到，尝试通过name或mobile匹配（可能是OAuth创建的成员）
                if not member:
                    name = user_info.get('name')
                    mobile = user_info.get('mobile')
                    
                    if name and mobile:
                        # 通过name+mobile精确匹配
                        member = Member.query.filter_by(
                            tenant_id=tenant_id,
                            name=name,
                            mobile=mobile
                        ).first()
                        if member:
                            print(f'    🔗 通过name+mobile匹配到成员，更新真实userid: {name} ({member.userid} → {userid})', file=sys.stderr, flush=True)
                            member.userid = userid  # 更新为真实userid
                    elif mobile:
                        # 仅通过mobile匹配
                        member = Member.query.filter_by(
                            tenant_id=tenant_id,
                            mobile=mobile
                        ).first()
                        if member:
                            print(f'    🔗 通过mobile匹配到成员，更新真实userid: {mobile} ({member.userid} → {userid})', file=sys.stderr, flush=True)
                            member.userid = userid  # 更新为真实userid
                
                # 从企微API获取成员状态
                status = user_info.get('status', 1)  # 1=激活，2=禁用，4=未激活，5=退出企业
                is_active = (status == 1)
                
                if member:
                    # 更新现有成员
                    member.name = user_info.get('name') or member.name
                    member.mobile = user_info.get('mobile') or member.mobile
                    member.email = user_info.get('email') or member.email
                    member.avatar_url = user_info.get('avatar') or member.avatar_url
                    member.position = user_info.get('position') or member.position
                    member.department = dept_name
                    member.is_active = is_active  # 更新在职状态
                    member.in_visible_range = True  # 能获取到说明在可见范围内
                    member.updated_at = db.func.now()
                    updated_count += 1
                    status_emoji = "✅" if is_active else "⚠️"
                    print(f'    {status_emoji} 更新成员: {member.name} ({userid})', file=sys.stderr, flush=True)
                else:
                    # 创建新成员
                    member = Member(
                        tenant_id=tenant_id,
                        userid=userid,  # ✅ 存储真实的企业内部userid
                        open_userid=None,  # open_userid将在OAuth授权时填充
                        name=user_info.get('name', userid),
                        mobile=user_info.get('mobile'),
                        email=user_info.get('email'),
                        avatar_url=user_info.get('avatar'),
                        position=user_info.get('position'),
                        department=dept_name,
                        role='user',
                        is_installer=False,
                        in_visible_range=True,
                        is_active=is_active
                    )
                    db.session.add(member)
                    created_count += 1
                    status_emoji = "✅" if is_active else "⚠️"
                    print(f'    {status_emoji} 创建成员: {member.name} ({userid})', file=sys.stderr, flush=True)
                
                synced_count += 1
        
        # 标记本次未同步到的成员为"不可见"或"离职"
        # 这些成员可能已离职或不在应用可见范围内
        deactivated_count = 0
        all_members = Member.query.filter_by(tenant_id=tenant_id).all()
        for member in all_members:
            if member.userid not in synced_userids:
                # 本次同步未获取到此成员，标记为不可见
                if member.in_visible_range or member.is_active:
                    member.in_visible_range = False
                    member.is_active = False  # 保守起见，同时标记为离职
                    member.updated_at = db.func.now()
                    deactivated_count += 1
                    print(f'  🚫 标记为不可见: {member.name} ({member.userid})', file=sys.stderr, flush=True)
        
        # 提交到数据库
        db.session.commit()
        
        # 更新租户配置中的同步时间
        try:
            config = json.loads(tenant.config or '{}')
            if 'workspace' not in config:
                config['workspace'] = {}
            config['workspace']['last_member_sync'] = datetime.now().isoformat()
            tenant.config = json.dumps(config, ensure_ascii=False)
            db.session.commit()
        except Exception as e:
            print(f'⚠️ 更新同步时间失败: {e}', file=sys.stderr, flush=True)
        
        print(f'✅ 同步完成: 总计={synced_count}, 新增={created_count}, 更新={updated_count}, 停用={deactivated_count}', file=sys.stderr, flush=True)
        
        return jsonify({
            'success': True,
            'count': synced_count,
            'created': created_count,
            'updated': updated_count,
            'deactivated': deactivated_count,
            'synced_at': datetime.now().isoformat(),
            'message': f'成功同步 {synced_count} 位成员（新增{created_count}，更新{updated_count}，停用{deactivated_count}）'
        })
        
    except requests.Timeout:
        return jsonify({'error': '企业微信API请求超时'}), 504
    except Exception as e:
        db.session.rollback()
        print(f'❌ 同步失败: {e}', file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'同步失败: {str(e)}'}), 500


@bp.route('/members', methods=['GET'])
def get_members():
    """
    获取租户下的所有成员列表
    GET /api/v1/wecom/members
    Headers: Authorization: Bearer <token>
    """
    import sys
    print('📋 收到获取成员列表请求', file=sys.stderr, flush=True)
    
    # 验证认证token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    is_admin = payload.get('is_admin', False)
    
    # 只有管理员可以查看成员列表
    if not is_admin:
        return jsonify({'error': '权限不足，仅管理员可访问'}), 403
    
    try:
        # 查询该租户下的所有成员
        members = Member.query.filter_by(tenant_id=tenant_id).all()
        
        members_data = []
        for m in members:
            members_data.append({
                'id': m.id,
                'userid': m.userid,  # 企业内部真实userid
                'open_userid': m.open_userid,  # 服务商主体下的加密userid
                'name': m.name,  # OAuth返回的姓名（通常是加密ID）
                'display_name': m.display_name,  # 管理员设置的对外显示名称
                'mobile': m.mobile,
                'position': m.position,
                'avatar_url': m.avatar_url,
                'custom_avatar_url': m.custom_avatar_url,
                'custom_push_photo_url': m.custom_push_photo_url,
                'is_admin': (m.role == 'admin'),
                'oauth_authorized': m.oauth_authorized,
                'oauth_authorized_at': m.oauth_authorized_at.strftime('%Y-%m-%d %H:%M:%S') if m.oauth_authorized_at else None,
                'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S') if m.created_at else None
            })
        
        print(f'✅ 返回 {len(members_data)} 个成员', file=sys.stderr, flush=True)
        return jsonify({
            'members': members_data,
            'total': len(members_data)
        })
        
    except Exception as e:
        print(f'❌ 获取成员列表失败: {str(e)}', file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取成员列表失败: {str(e)}'}), 500


@bp.route('/jssdk/signature', methods=['GET'])
def get_jssdk_signature():
    """
    获取企微JSSDK签名（用于管理后台 open-data 组件）
    GET /api/v1/wecom/jssdk/signature?url=<当前页面URL>
    Headers: Authorization: Bearer <token>
    
    返回:
    {
        "corpid": "ww...",
        "agentid": "1000002",
        "timestamp": "1234567890",
        "nonceStr": "abc123",
        "signature": "sha1..."
    }
    """
    print(f'🔐 收到JSSDK签名请求', file=sys.stderr, flush=True)
    
    # 验证认证token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    
    # 获取URL参数
    url = request.args.get('url')
    if not url:
        return jsonify({'error': '缺少url参数'}), 400
    
    print(f'📝 请求签名的URL: {url}', file=sys.stderr, flush=True)
    
    try:
        # 查询租户
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        if not tenant:
            return jsonify({'error': '租户不存在'}), 404
        
        # 获取 corp_access_token
        corp_token = get_corp_access_token(tenant.corp_id, tenant.permanent_code)
        if not corp_token:
            print(f'❌ 获取corp_access_token失败', file=sys.stderr, flush=True)
            return jsonify({'error': '获取企业凭证失败'}), 500
        
        # 获取 jsapi_ticket
        print(f'🎫 获取jsapi_ticket...', file=sys.stderr, flush=True)
        resp = requests.get(
            'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket',
            params={'access_token': corp_token},
            timeout=5
        )
        ticket_data = resp.json()
        print(f'📥 jsapi_ticket响应: {ticket_data}', file=sys.stderr, flush=True)
        
        if ticket_data.get('errcode') != 0:
            return jsonify({'error': f'获取jsapi_ticket失败: {ticket_data.get("errmsg")}'}), 500
        
        ticket = ticket_data['ticket']
        
        # 生成签名参数
        timestamp = str(int(time.time()))
        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # 按照企微规范生成签名字符串
        sign_str = f"jsapi_ticket={ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={url}"
        signature = hashlib.sha1(sign_str.encode()).hexdigest()
        
        print(f'✅ 签名生成成功', file=sys.stderr, flush=True)
        print(f'  - timestamp: {timestamp}', file=sys.stderr, flush=True)
        print(f'  - nonceStr: {nonce_str}', file=sys.stderr, flush=True)
        print(f'  - signature: {signature}', file=sys.stderr, flush=True)
        
        return jsonify({
            'corpid': tenant.corp_id,
            'agentid': current_app.config.get('WECOM_AGENT_ID', '1000002'),
            'timestamp': timestamp,
            'nonceStr': nonce_str,
            'signature': signature
        })
        
    except Exception as e:
        print(f'❌ 生成签名失败: {e}', file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成签名失败: {str(e)}'}), 500


@bp.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """
    更新成员信息（管理员手动编辑）
    PUT /api/v1/wecom/members/<member_id>
    Headers: Authorization: Bearer <token>
    Body: {
        "name": "张三",
        "mobile": "13800138000",
        "position": "产品经理"
    }
    """
    import sys
    print(f'✏️ 收到更新成员请求: member_id={member_id}', file=sys.stderr, flush=True)
    
    # 验证认证token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    is_admin = payload.get('is_admin', False)
    
    # 只有管理员可以编辑成员
    if not is_admin:
        return jsonify({'error': '权限不足，仅管理员可编辑成员信息'}), 403
    
    try:
        # 查询成员
        member = Member.query.filter_by(id=member_id, tenant_id=tenant_id).first()
        if not member:
            return jsonify({'error': '成员不存在'}), 404
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        # 更新字段（只允许更新特定字段）
        updated_fields = []
        
        if 'display_name' in data:
            member.display_name = data['display_name'].strip() if data['display_name'] else None
            updated_fields.append('display_name')
        
        if 'mobile' in data:
            member.mobile = data['mobile'].strip() if data['mobile'] else None
            updated_fields.append('mobile')
        
        if 'position' in data:
            member.position = data['position'].strip() if data['position'] else None
            updated_fields.append('position')

        if 'custom_avatar_url' in data:
            member.custom_avatar_url = sanitize_media_url(data.get('custom_avatar_url'))
            updated_fields.append('custom_avatar_url')

        if 'custom_push_photo_url' in data:
            member.custom_push_photo_url = sanitize_media_url(data.get('custom_push_photo_url'))
            updated_fields.append('custom_push_photo_url')
        
        # 保存到数据库
        db.session.commit()
        
        print(f'✅ 成员更新成功: {updated_fields}', file=sys.stderr, flush=True)
        
        return jsonify({
            'success': True,
            'message': '成员信息更新成功',
            'updated_fields': updated_fields,
            'member': {
                'id': member.id,
                'userid': member.userid,
                'display_name': member.display_name,
                'mobile': member.mobile,
                'position': member.position,
                'avatar_url': member.avatar_url,
                'custom_avatar_url': member.custom_avatar_url,
                'custom_push_photo_url': member.custom_push_photo_url
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f'❌ 更新成员失败: {str(e)}', file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'更新成员失败: {str(e)}'}), 500


@bp.route('/card/my', methods=['GET'])
def get_my_card():
    """获取当前用户的名片数据（普通用户和管理员都可以访问）"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '未识别到用户身份'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        
        if not payload:
            return jsonify({'error': '认证token无效或已过期'}), 401
        
        tenant_id = payload.get('tenant_id')
        userid = payload.get('userid')
        corp_id = payload.get('corp_id')
        role = payload.get('role', 'user')
        
        print(f'📇 获取用户名片: tenant_id={tenant_id}, userid={userid}, role={role}', file=sys.stderr, flush=True)
        
        # 查询租户
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': '企业不存在'}), 404
        
        # 查询成员信息
        member = Member.query.filter_by(tenant_id=tenant_id, userid=userid).first()
        
        # ✅ OAuth授权检测：检查是否需要用户手动授权获取完整信息
        needs_oauth = False
        if not member:
            needs_oauth = True
        elif not member.oauth_authorized:
            # 检查关键字段是否完整（第三方应用限制导致的）
            if (not member.name or member.name == userid or 
                not member.avatar_url or 
                not member.mobile):
                needs_oauth = True
                print(f'⚠️ 成员信息不完整，需要OAuth授权: userid={userid}, name={member.name}, has_avatar={bool(member.avatar_url)}, has_mobile={bool(member.mobile)}', file=sys.stderr, flush=True)
        
        # ✅ 如果需要OAuth授权，返回授权引导
        if needs_oauth:
            try:
                from urllib.parse import quote, urlencode
                # 构建回调URL（需要携带corp_id）
                callback_params = urlencode({'corp_id': corp_id})
                redirect_uri = f'{request.url_root.rstrip("/")}/api/v1/wecom/oauth/callback?{callback_params}'
                print(f'🔗 构建redirect_uri: {redirect_uri}', file=sys.stderr, flush=True)
                
                oauth_url = generate_oauth_url(redirect_uri, state='oauth_member_info')
                print(f'✅ OAuth URL生成成功', file=sys.stderr, flush=True)
                
                return jsonify({
                    'success': False,
                    'need_oauth': True,
                    'oauth_url': oauth_url,
                    'message': '需要您的授权以获取完整名片信息'
                })
            except Exception as e:
                print(f'❌ 生成OAuth URL失败: {e}', file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'生成授权URL失败: {str(e)}'}), 500
        
        # 如果已授权但超过30天，尝试静默同步（可选）
        if member and member.oauth_authorized:
            # 检查是否需要同步更新
            needs_sync = False
            if member.oauth_authorized_at:
                days_since_auth = (datetime.now() - member.oauth_authorized_at).days
                if days_since_auth > 30:
                    needs_sync = True
                    print(f'📅 成员信息已超过30天，尝试更新: userid={userid}', file=sys.stderr, flush=True)
            
            if needs_sync:
                # 这里可以添加静默刷新逻辑（使用user_ticket）
                pass
        
        if not member:
            return jsonify({
                'error': '名片不存在',
                'message': '管理员还没有为您配置名片，请联系管理员'
            }), 404
        
        # 获取租户的名片模版配置
        config = json.loads(tenant.config or '{}')
        workspace_config = config.get('workspace', {})
        card_template = config.get('card_template', {})
        
        # 构建名片数据
        # 获取header配置（优先从workspace，其次从card_template）
        header_config = workspace_config.get('header', card_template.get('header', {})) or {}
        contact_visibility = header_config.get('contact_visibility') or card_template.get('contact_visibility') or {
            'mobile': True,
            'email': True,
            'wechat': True,
            'phone': True,
            'address': True,
            'website': True
        }
        
        workspace_modules = workspace_config.get('modules', []) or []
        modules_list = []
        for module in workspace_modules:
            if not module:
                continue
            if module.get('enabled') is False:
                continue
            modules_list.append({
                'id': module.get('id'),
                'type': module.get('framework_type') or module.get('type'),
                'title': module.get('custom_title') or module.get('title'),
                'sort_order': module.get('sort_order', 0),
                'data': module.get('data', {}),
                'framework_version': module.get('framework_version'),
                'enabled': module.get('enabled', True)
            })
        
        header_avatar_config = header_config.get('avatar', {})
        avatar_config, resolved_avatar = build_member_avatar_config(member, header_avatar_config)

        card_data = {
            'basic_info': {
                'name': member.display_name or member.name or '未设置',  # 优先使用display_name
                'title': member.position or '员工',
                'department': member.department or '',
                'company': tenant.name,
                'avatar': resolved_avatar,
                'company_logo': header_config.get('logo', {}).get('logoUrl') or card_template.get('company_logo', ''),
                'slogan': header_config.get('slogan', '') or card_template.get('slogan', '以白为底，科技为线')
            },
            'header_options': card_template.get('header_options', {
                'backgroundImage': '',
                'headerGlow': True,
                'scanLine': False,
                'slogan': header_config.get('slogan', card_template.get('slogan', '以白为底，科技为线'))
            }),
            # ✅ 新增：头部背景配置
            'header_background': header_config.get('background', {
                'backgroundType': 'solid',  # 默认纯色背景
                'backgroundImage': '',
                'backgroundColor': '#f5f5f5'
            }),
            # ✅ 新增：头像配置（包含管理员单人设置）
            'avatar_config': avatar_config,
            'contact_info': {
                'mobile': member.mobile if contact_visibility.get('mobile', True) else '',
                'email': member.email if contact_visibility.get('email', True) else '',
                'wechat': '',  # ✅ 修复：Member模型无wechat字段，暂时留空
                'phone': header_config.get('company_info', {}).get('phone', '') if contact_visibility.get('phone', False) else '',
                'address': header_config.get('company_info', {}).get('address', '') if contact_visibility.get('address', True) else '',
                'website': header_config.get('company_info', {}).get('website', '') if contact_visibility.get('website', True) else ''
            },
            'interactive_features': {
                'quick_call': True,
                'add_wechat': True,
                'save_contact': True,
                'share_card': True
            },
            'business_showcase': card_template.get('business_showcase') or None,
            'social_media': card_template.get('social_media', []),
            'modules': card_template.get('modules', {}),
            'modules_list': modules_list,
            'contact_visibility': contact_visibility,
            'logo_config': header_config.get('logo', {}) or {}
            }
        
        print(f'✅ 名片数据构建成功', file=sys.stderr, flush=True)
        
        return jsonify({
            'success': True,
            'card_data': card_data,
            'card_id': f'{tenant_id}_{member.id}',
            'theme': workspace_config.get('theme') or card_template.get('theme', 'light') or 'light',
            'role': role,
            'is_admin': payload.get('is_admin', False)
        })
        
    except Exception as e:
        print(f'❌ 获取名片失败: {e}', file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取名片失败: {str(e)}'}), 500


@bp.route('/card/preview/<int:tenant_id>/<int:member_id>', methods=['GET'])
def get_card_preview(tenant_id, member_id):
    """
    获取卡片预览数据（公开接口，无需认证）
    用于推送消息中的卡片预览页面
    """
    import sys
    
    print(f'📇 获取卡片预览: tenant_id={tenant_id}, member_id={member_id}', file=sys.stderr, flush=True)
    
    # 查询租户
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': '企业不存在'}), 404
    
    # 查询成员信息
    member = Member.query.filter_by(tenant_id=tenant_id, id=member_id).first()
    if not member:
        return jsonify({
            'error': '名片不存在',
            'message': '该名片不存在或已被删除'
        }), 404
    
    # 获取租户的名片模版配置
    config = json.loads(tenant.config or '{}')
    workspace_config = config.get('workspace', {})
    card_template = config.get('card_template', {})
    push_config = config.get('push_config', {})
    card_preview_config = push_config.get('cardPreviewConfig', {})
    
    # 构建名片数据
    # 获取header配置（优先从workspace，其次从card_template）
    header_config = workspace_config.get('header', card_template.get('header', {})) or {}
    header_background = header_config.get('background', {}) or {}

    # 头像优先级：成员自定义 > AvatarEditor 统一设置 > 企微默认
    avatar_config, resolved_avatar = build_member_avatar_config(member, header_config.get('avatar', {}))

    # 推送卡片配置优先级：成员自定义推送照片 > 推送模块统一配置 > 企微头像
    resolved_card_preview_config = build_card_preview_config(
        card_preview_config or {},
        header_background,
        member.custom_push_photo_url
    )

    # 获取背景配置（兼容旧字段）
    background_config = {
        'backgroundType': resolved_card_preview_config.get('backgroundType', 'solid'),
        'backgroundImage': resolved_card_preview_config.get('backgroundImage', ''),
        'backgroundColor': resolved_card_preview_config.get('backgroundColor', '#f5f5f5'),
        'svgPattern': resolved_card_preview_config.get('svgPattern', 'geometric'),
        'svgGradientStart': resolved_card_preview_config.get('svgGradientStart', '#ffffff'),
        'svgGradientEnd': resolved_card_preview_config.get('svgGradientEnd', '#FC726E'),
        'themeColor': resolved_card_preview_config.get('themeColor', '#fbb9b6')
    }
    
    card_data = {
        'basic_info': {
            'name': member.name or '未设置',
            'title': member.position or '员工',
            'department': member.department or '',
            'company': tenant.name,
            'avatar': resolved_avatar,
            'company_logo': card_template.get('company_logo', ''),
            'slogan': card_template.get('slogan', '以白为底，科技为线')
        },
        'header_options': card_template.get('header_options', {
            'backgroundImage': '',
            'headerGlow': True,
            'scanLine': False,
            'slogan': header_config.get('slogan', card_template.get('slogan', '以白为底，科技为线'))
        }),
        # 头部背景配置（使用卡片预览配置）
        'header_background': background_config,
        # 头像配置（包含管理员单人成员设置）
        'avatar_config': {
            'avatarMode': resolved_card_preview_config.get('avatarMode', 'company'),
            'companyAvatar': resolved_card_preview_config.get('companyAvatar', ''),
            'wecomAvatar': resolved_avatar
        },
        # 个人介绍（优先从卡片预览配置，其次从推送配置，最后从其他配置）
        'personal_intro': (
            card_preview_config.get('personalIntro', '') or
            push_config.get('personalIntro', '') or
            header_config.get('personal_intro', '') or
            card_template.get('personal_intro', '') or
            card_template.get('slogan', '')
        ),
        # 卡片预览样式配置（用于前端渲染）
        'card_preview_config': resolved_card_preview_config,
        # 公司简称和介绍（默认使用公司配置）
        'company_short': card_template.get('company_short', tenant.name[:10] if tenant.name else ''),
        'company_intro': card_template.get('company_intro', card_template.get('slogan', '')),
        'contact_info': {
            'mobile': member.mobile or '',
            'email': member.email or '',
            'wechat': '',
            'phone': '',
            'address': card_template.get('company_address', ''),
            'website': card_template.get('company_website', '')
        },
        'interactive_features': {
            'quick_call': True,
            'add_wechat': True,
            'save_contact': True,
            'share_card': True
        },
        'business_showcase': card_template.get('business_showcase', {}),
        'social_media': card_template.get('social_media', []),
        'modules': card_template.get('modules', {})
    }
    
    print(f'✅ 卡片预览数据构建成功', file=sys.stderr, flush=True)
    
    return jsonify({
        'success': True,
        'card_data': card_data,
        'card_id': f'{tenant_id}_{member.id}',
        'theme': card_template.get('theme', 'light')
    })
