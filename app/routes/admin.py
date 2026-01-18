from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from sqlalchemy.sql import text
from ..models import Tenant, Member, CardLog, FileAsset
from ..main import db

bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')


@bp.route('/tenants', methods=['GET'])
def list_tenants():
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

    tenant_ids = [tenant.id for tenant in pagination.items]

    member_counts = dict(
        db.session.query(Member.tenant_id, func.count(Member.id))
        .filter(Member.tenant_id.in_(tenant_ids))
        .group_by(Member.tenant_id)
    ) if tenant_ids else {}

    asset_counts = dict(
        db.session.query(FileAsset.tenant_id, func.count(FileAsset.id))
        .filter(FileAsset.tenant_id.in_(tenant_ids))
        .group_by(FileAsset.tenant_id)
    ) if tenant_ids else {}

    storage_used_map = dict(
        db.session.query(FileAsset.tenant_id, func.coalesce(func.sum(FileAsset.size), 0))
        .filter(FileAsset.tenant_id.in_(tenant_ids))
        .group_by(FileAsset.tenant_id)
    ) if tenant_ids else {}

    views_last_30d = dict(
        db.session.query(CardLog.tenant_id, func.count(CardLog.id))
        .filter(
            CardLog.tenant_id.in_(tenant_ids),
            CardLog.event == 'page_view',
            CardLog.created_at >= func.DATE_SUB(func.now(), text('INTERVAL 30 DAY'))
        )
        .group_by(CardLog.tenant_id)
    ) if tenant_ids else {}

    response_items = []
    for tenant in pagination.items:
        response_items.append({
            'id': tenant.id,
            'corp_id': tenant.corp_id,
            'company_name': tenant.name,
            'plan': tenant.plan,
            'created_at': tenant.created_at,
            'member_count': member_counts.get(tenant.id, 0),
            'asset_count': asset_counts.get(tenant.id, 0),
            'views_last_30d': views_last_30d.get(tenant.id, 0),
            'storage_used_bytes': storage_used_map.get(tenant.id, 0),
            'last_synced_at': tenant.updated_at,
        })

    total_tenants = Tenant.query.count()
    active_last_30d = db.session.query(Tenant.id).join(CardLog, CardLog.tenant_id == Tenant.id).filter(
        CardLog.event == 'page_view',
        CardLog.created_at >= func.DATE_SUB(func.now(), text('INTERVAL 30 DAY'))
    ).distinct().count()
    total_views = db.session.query(func.count(CardLog.id)).scalar()
    total_assets = db.session.query(func.count(FileAsset.id)).scalar()
    storage_used_total = db.session.query(func.coalesce(func.sum(FileAsset.size), 0)).scalar()

    summary = {
        'total_tenants': total_tenants,
        'active_last_30d': active_last_30d,
        'total_views': total_views,
        'total_assets': total_assets,
        'storage_used_bytes': storage_used_total,
    }

    return jsonify({
        'items': response_items,
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
        },
        'summary': summary,
    })


@bp.route('/tenants/<int:tenant_id>', methods=['GET'])
def tenant_detail(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)

    member_stats = db.session.query(func.count(Member.id)).filter(Member.tenant_id == tenant_id).scalar()
    asset_stats = db.session.query(func.count(FileAsset.id), func.coalesce(func.sum(FileAsset.size), 0)).filter(FileAsset.tenant_id == tenant_id).first()
    recent_logs = db.session.query(CardLog).filter(CardLog.tenant_id == tenant_id).order_by(CardLog.created_at.desc()).limit(20).all()
    member_list = Member.query.filter(Member.tenant_id == tenant_id).order_by(Member.updated_at.desc()).limit(200).all()

    tenant_data = {
        'id': tenant.id,
        'corp_id': tenant.corp_id,
        'company_name': tenant.name,
        'plan': tenant.plan,
        'created_at': tenant.created_at,
        'updated_at': tenant.updated_at,
        'member_count': member_stats,
        'asset_count': asset_stats[0] if asset_stats else 0,
        'storage_used_bytes': asset_stats[1] if asset_stats else 0,
    }

    member_data = [{
        'id': m.id,
        'name': m.name,
        'userid': m.userid,
        'department': m.department,
        'position': m.position,
        'mobile': m.mobile,
        'email': m.email,
        'updated_at': m.updated_at,
    } for m in member_list]

    log_data = [{
        'id': log.id,
        'event': log.event,
        'meta': log.meta,
        'member_id': log.member_id,
        'created_at': log.created_at,
    } for log in recent_logs]

    return jsonify({
        'tenant': tenant_data,
        'members': member_data,
        'logs': log_data,
    })
