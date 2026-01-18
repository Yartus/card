"""
素材库API路由
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from sqlalchemy import and_, or_

# ✅ 修复导入路径
from ..main import db
from ..asset_models import TenantAsset, AssetAnalytics
from ..models import Tenant, Member

from .wecom import verify_jwt_token

bp = Blueprint('assets', __name__, url_prefix='/api/tenant/assets')


@bp.route('', methods=['GET'])
def list_assets():
    """
    获取租户的素材列表
    GET /api/tenant/assets
    Headers: Authorization: Bearer <token>
    Query: ?status=published&page=1&per_page=20
    """
    # 验证JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    
    # 查询参数
    status = request.args.get('status')  # published, draft, active, inactive
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # 构建查询
    query = TenantAsset.query.filter_by(tenant_id=tenant_id)
    if status:
        query = query.filter_by(status=status)
    
    # 分页
    pagination = query.order_by(TenantAsset.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    assets = [a.to_admin_dict() for a in pagination.items]
    
    return jsonify({
        'success': True,
        'assets': assets,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    """
    获取单个素材详情
    GET /api/tenant/assets/{asset_id}
    Headers: Authorization: Bearer <token>
    """
    # 验证JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    
    # 查询素材
    asset = TenantAsset.query.filter_by(id=asset_id, tenant_id=tenant_id).first()
    
    if not asset:
        return jsonify({'error': '素材不存在'}), 404
    
    return jsonify({
        'success': True,
        'asset': asset.to_admin_dict()
    })


@bp.route('', methods=['POST'])
def create_asset():
    """
    创建新素材
    POST /api/tenant/assets
    Headers: Authorization: Bearer <token>
    Body: {
        "title": "素材标题",
        "summary": "素材简介",
        "cover": "封面图URL",
        "metadata": {
            "blocks": [...],  // 富文本内容块
            "externalLink": "外部链接",
            "version": "2.0"
        },
        "content": "文本内容（向后兼容）",
        "tags": ["标签1", "标签2"],
        "status": "draft"  // draft, published, active, inactive
    }
    """
    # 验证JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    userid = payload.get('userid')
    
    # 获取请求数据
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少请求数据'}), 400
    
    # 验证必填字段
    if not data.get('title'):
        return jsonify({'error': '标题不能为空'}), 400
    
    if not data.get('summary'):
        return jsonify({'error': '简介不能为空'}), 400
    
    if not data.get('cover'):
        return jsonify({'error': '封面图不能为空'}), 400
    
    # 验证 metadata.blocks
    metadata = data.get('metadata', {})  # API层使用metadata字段名
    if not metadata.get('blocks') or len(metadata['blocks']) == 0:
        return jsonify({'error': '内容不能为空'}), 400
    
    # 创建素材
    asset = TenantAsset(
        tenant_id=tenant_id,
        title=data['title'],
        summary=data['summary'],
        cover=data['cover'],
        content_type='document',  # 默认类型
        meta_data=metadata,  # ✅ 修复：使用meta_data字段
        tags=data.get('tags', []),
        status=data.get('status', 'draft'),
        created_by=userid,
        updated_by=userid
    )
    
    # ✅ 向后兼容：如果提供了旧格式字段，也保存
    if data.get('content'):
        asset.content_url = data['content']  # 可以存储在 content_url 或其他字段
    
    try:
        db.session.add(asset)
        db.session.commit()
        
        current_app.logger.info(f'✅ 素材创建成功: tenant={tenant_id}, user={userid}, asset_id={asset.id}')
        
        return jsonify({
            'success': True,
            'asset': asset.to_admin_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'❌ 素材创建失败: {e}')
        return jsonify({'error': '创建素材失败'}), 500


@bp.route('/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """
    更新素材
    PUT /api/tenant/assets/{asset_id}
    Headers: Authorization: Bearer <token>
    Body: 同创建接口
    """
    # 验证JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    userid = payload.get('userid')
    
    # 查询素材
    asset = TenantAsset.query.filter_by(id=asset_id, tenant_id=tenant_id).first()
    
    if not asset:
        return jsonify({'error': '素材不存在'}), 404
    
    # 获取请求数据
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少请求数据'}), 400
    
    # 更新字段
    if 'title' in data:
        asset.title = data['title']
    
    if 'summary' in data:
        asset.summary = data['summary']
    
    if 'cover' in data:
        asset.cover = data['cover']
    
    if 'metadata' in data:
        asset.meta_data = data['metadata']  # ✅ 修复：使用meta_data字段
    
    if 'tags' in data:
        asset.tags = data['tags']
    
    if 'status' in data:
        asset.status = data['status']
    
    # ✅ 向后兼容：更新旧格式字段
    if 'content' in data:
        asset.content_url = data['content']
    
    asset.updated_by = userid
    asset.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'✅ 素材更新成功: tenant={tenant_id}, user={userid}, asset_id={asset_id}')
        
        return jsonify({
            'success': True,
            'asset': asset.to_admin_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'❌ 素材更新失败: {e}')
        return jsonify({'error': '更新素材失败'}), 500


@bp.route('/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """
    删除素材
    DELETE /api/tenant/assets/{asset_id}
    Headers: Authorization: Bearer <token>
    """
    # 验证JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    
    # 查询素材
    asset = TenantAsset.query.filter_by(id=asset_id, tenant_id=tenant_id).first()
    
    if not asset:
        return jsonify({'error': '素材不存在'}), 404
    
    try:
        db.session.delete(asset)
        db.session.commit()
        
        current_app.logger.info(f'✅ 素材删除成功: tenant={tenant_id}, asset_id={asset_id}')
        
        return jsonify({
            'success': True,
            'message': '素材已删除'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'❌ 素材删除失败: {e}')
        return jsonify({'error': '删除素材失败'}), 500


@bp.route('/<int:asset_id>/status', methods=['PATCH'])
def toggle_asset_status(asset_id):
    """
    切换素材发布状态
    PATCH /api/tenant/assets/{asset_id}/status
    Headers: Authorization: Bearer <token>
    Body: { "status": "published" }  // or "draft", "active", "inactive"
    """
    # 验证JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': '需要认证'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return jsonify({'error': '认证token无效或已过期'}), 401
    
    tenant_id = payload.get('tenant_id')
    userid = payload.get('userid')
    
    # 查询素材
    asset = TenantAsset.query.filter_by(id=asset_id, tenant_id=tenant_id).first()
    
    if not asset:
        return jsonify({'error': '素材不存在'}), 404
    
    # 获取请求数据
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': '缺少status参数'}), 400
    
    if new_status not in ['published', 'draft', 'active', 'inactive']:
        return jsonify({'error': '无效的status值'}), 400
    
    asset.status = new_status
    asset.updated_by = userid
    asset.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'✅ 素材状态更新: tenant={tenant_id}, asset_id={asset_id}, status={new_status}')
        
        return jsonify({
            'success': True,
            'asset': asset.to_admin_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'❌ 素材状态更新失败: {e}')
        return jsonify({'error': '更新状态失败'}), 500

