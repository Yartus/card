from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from ..models import Tenant, Member
from ..main import db

bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

@bp.route('/tenants', methods=['GET'])
def list_tenants():
    """获取租户列表（简化版）"""
    page = max(int(request.args.get('page', 1)), 1)
    per_page = min(int(request.args.get('page_size', 20)), 100)
    keyword = request.args.get('keyword', '').strip()

    query = Tenant.query
    if keyword:
        like_term = f"%{keyword}%"
        query = query.filter(or_(
            Tenant.name.ilike(like_term),
            Tenant.corp_id.ilike(like_term)
        ))

    pagination = query.order_by(Tenant.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取成员统计
    tenant_ids = [t.id for t in pagination.items]
    member_counts = {}
    if tenant_ids:
        results = db.session.query(Member.tenant_id, func.count(Member.id))\
            .filter(Member.tenant_id.in_(tenant_ids))\
            .group_by(Member.tenant_id).all()
        member_counts = {r[0]: r[1] for r in results}

    items = []
    for t in pagination.items:
        items.append({
            'id': t.id,
            'corp_id': t.corp_id,
            'name': t.name,
            'plan': t.plan,
            'created_at': t.created_at,
            'member_count': member_counts.get(t.id, 0)
        })

    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    })

@bp.route('/tenants/<int:tenant_id>', methods=['GET'])
def tenant_detail(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    member_count = Member.query.filter_by(tenant_id=tenant_id).count()
    
    return jsonify({
        'tenant': {
            'id': tenant.id,
            'corp_id': tenant.corp_id,
            'name': tenant.name,
            'plan': tenant.plan,
            'created_at': tenant.created_at,
            'config': tenant.config,
            'member_count': member_count
        }
    })

