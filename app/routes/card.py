from flask import Blueprint, jsonify, request
import os
from ..models import Member, CardTemplate, Tenant
from sqlalchemy.exc import SQLAlchemyError
from ..main import db

bp = Blueprint('card', __name__, url_prefix='/card')

# API 蓝图（新）：/api/card
api_bp = Blueprint('card_api', __name__, url_prefix='/api/card')

@bp.route('/<int:tenant_id>/<int:member_id>', methods=['GET'])
def render_card(tenant_id, member_id):
    # TODO: render template with member data
    return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'status': 'stub'})


# ======== API: /api/card/profile ========
@api_bp.route('/profile', methods=['GET'])
def get_card_profile():
    """返回名片Profile（stub版）：基于 Member 映射 basic_info/contact_info。"""
    tenant_id = request.args.get('tenant_id', type=int)
    member_id = request.args.get('member_id', type=int)
    # 强制演示开关（优先用于暂不可用DB环境）：?stub=1 或 环境变量 CARD_PROFILE_DEMO=1
    force_stub = request.args.get('stub') in ('1', 'true', 'True') or os.getenv('CARD_PROFILE_DEMO') == '1'
    if force_stub:
        demo_profile = {
            'basic_info': {
                'name': '演示用户',
                'title': '产品经理',
                'department': '产品部',
                'company': '演示公司',
                'avatar': '',
                'company_logo': ''
            },
            'contact_info': {
                'mobile': '13800138000',
                'email': 'demo@example.com',
                'wechat': 'demo_wechat',
                'phone': '',
                'address': '',
                'website': ''
            },
            'interactive_features': {
                'quick_call': True,
                'add_wechat': True,
                'save_contact': True,
                'share_card': True
            },
            'business_showcase': {
                'company_intro': '演示公司简介',
                'personal_intro': '演示个人介绍',
                'services': ['服务A', '服务B'],
                'portfolio': []
            },
            'social_media': []
        }
        return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'card_profile': demo_profile, 'stub': True}), 200
    if not tenant_id or not member_id:
        return jsonify({'error': 'tenant_id and member_id are required'}), 400

    try:
        try:
            # 关联查询，避免懒加载关系异常
            result = (
                db.session.query(Member, Tenant.name.label('tenant_name'))
                .outerjoin(Tenant, Member.tenant_id == Tenant.id)
                .filter(Member.id == member_id, Member.tenant_id == tenant_id)
                .first()
            )
        except SQLAlchemyError as e:
            # 数据库不可用或表未创建时，返回演示数据，避免 500 阻塞前端联调
            demo_profile = {
                'basic_info': {
                    'name': '演示用户',
                    'title': '产品经理',
                    'department': '产品部',
                    'company': '演示公司',
                    'avatar': '',
                    'company_logo': ''
                },
                'contact_info': {
                    'mobile': '13800138000',
                    'email': 'demo@example.com',
                    'wechat': 'demo_wechat',
                    'phone': '',
                    'address': '',
                    'website': ''
                },
                'interactive_features': {
                    'quick_call': True,
                    'add_wechat': True,
                    'save_contact': True,
                    'share_card': True
                },
                'business_showcase': {
                    'company_intro': '演示公司简介',
                    'personal_intro': '演示个人介绍',
                    'services': ['服务A', '服务B'],
                    'portfolio': []
                },
                'social_media': []
            }
            return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'card_profile': demo_profile, 'stub': True, 'error': 'db_unavailable'}), 200

        if not result:
            return jsonify({'error': 'member_not_found'}), 404

        member, tenant_name = result

        # 构造 Profile，所有字段做兜底，避免 500
        profile = {
            'basic_info': {
                'name': member.name or '',
                'title': member.position or '',
                'department': member.department or '',
                'company': tenant_name or '',
                'avatar': member.avatar_url or '',
                'company_logo': ''
            },
            'contact_info': {
                'mobile': member.mobile or '',
                'email': member.email or '',
                'wechat': '',
                'phone': '',
                'address': '',
                'website': ''
            },
            'interactive_features': {
                'quick_call': True,
                'add_wechat': True,
                'save_contact': True,
                'share_card': True
            },
            'business_showcase': {
                'company_intro': '',
                'personal_intro': '',
                'services': [],
                'portfolio': []
            },
            'social_media': []
        }

        return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'card_profile': profile})

    except Exception as e:  # 广泛兜底，临时用于定位 500 根因
        return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'error': 'unhandled_exception', 'message': str(e), 'stub': True}), 200


@api_bp.route('/profile', methods=['PUT'])
def update_card_profile():
    """更新名片Profile（stub版）：更新 Member 基础字段，其他字段暂不持久化。"""
    data = request.get_json(silent=True) or {}
    tenant_id = data.get('tenant_id')
    member_id = data.get('member_id')
    card_data = data.get('card_profile') or {}
    # 强制演示开关：不访问数据库，直接回显
    force_stub = request.args.get('stub') in ('1', 'true', 'True') or os.getenv('CARD_PROFILE_DEMO') == '1'
    if force_stub:
        return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'card_profile': card_data, 'stub': True, 'status': 'ok'}), 200
    if not tenant_id or not member_id:
        return jsonify({'error': 'tenant_id and member_id are required'}), 400
    member = Member.query.filter_by(id=member_id, tenant_id=tenant_id).first()
    if not member:
        return jsonify({'error': 'member_not_found'}), 404

    # 映射允许更新的字段
    basic = (card_data or {}).get('basic_info') or {}
    contact = (card_data or {}).get('contact_info') or {}

    if 'name' in basic:
        member.name = basic.get('name') or member.name
    if 'title' in basic:
        member.position = basic.get('title') or member.position
    if 'department' in basic:
        member.department = basic.get('department') or member.department
    if 'avatar' in basic:
        member.avatar_url = basic.get('avatar') or member.avatar_url

    if 'mobile' in contact:
        member.mobile = contact.get('mobile') or member.mobile
    if 'email' in contact:
        member.email = contact.get('email') or member.email

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # 数据库不可用时回显（避免阻塞前端联调）
        return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'card_profile': card_data, 'stub': True, 'error': 'db_commit_failed', 'detail': str(e)}), 200

    return jsonify({'status': 'ok'})


# ======== API: /api/card/preview/thumbnail ========
@api_bp.route('/preview/thumbnail', methods=['POST'])
def generate_or_refresh_thumbnail():
    """生成/刷新分享缩略图（stub版）：返回占位图链接并指示是否覆盖。"""
    data = request.get_json(silent=True) or {}
    member_id = data.get('member_id')
    override = bool(data.get('override', False))
    if not member_id:
        return jsonify({'error': 'member_id is required'}), 400
    # 占位缩略图地址（后续接入真实渲染服务）；优先 BASE_URL 环境变量，其次请求主机
    base_url = os.getenv('BASE_URL') or (request.host_url.rstrip('/') if request.host_url else '')
    if not base_url:
        base_url = 'http://localhost:5001'
    thumbnail_url = f"{base_url}/static/card-thumbs/{member_id}.jpg"
    return jsonify({'member_id': member_id, 'override': override, 'thumbnail_url': thumbnail_url, 'status': 'stub'})


# ======== API: /api/card/settings/contact-visibility ========
@api_bp.route('/settings/contact-visibility', methods=['PUT'])
def update_contact_visibility():
    """更新联系方式显示开关（stub版）：暂不落库，仅回显。"""
    data = request.get_json(silent=True) or {}
    tenant_id = data.get('tenant_id')
    member_id = data.get('member_id')
    visibility = data.get('visibility') or {}
    if not tenant_id or not member_id:
        return jsonify({'error': 'tenant_id and member_id are required'}), 400
    return jsonify({'tenant_id': tenant_id, 'member_id': member_id, 'visibility': visibility, 'status': 'stub'})