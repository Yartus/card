"""
WeCard 素材库 API 接口
提供素材库的公开访问和管理功能
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import joinedload

from ..models import db, TenantAsset, AssetAnalytics, AssetCategory, AssetLibrarySettings, Tenant
from ..utils.auth import require_tenant_auth, get_current_tenant_id, get_client_ip
from ..utils.file_handler import upload_file, validate_file
from ..utils.analytics import track_asset_access, get_asset_analytics
from ..utils.cache import cache_get, cache_set
from ..utils.validators import validate_asset_data

assets_bp = Blueprint('assets', __name__, url_prefix='/api')

# ==================== 公开访问接口 ====================

@assets_bp.route('/public/assets/<tenant_id>', methods=['GET'])
@cross_origin()
def get_public_assets(tenant_id):
    """
    获取租户的公开素材库
    支持分页、类型筛选、搜索、分类筛选
    """
    try:
        # 验证租户存在且启用素材库
        tenant = Tenant.query.filter_by(id=tenant_id, status='active').first()
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # 检查素材库设置
        settings = AssetLibrarySettings.query.filter_by(tenant_id=tenant_id).first()
        if not settings or not settings.enabled or not settings.public_access:
            return jsonify({'error': 'Asset library not available'}), 404
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 12, type=int), 50)  # 最大50个
        asset_type = request.args.get('type', '')
        category_id = request.args.get('category', '', type=int)
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'created_at')  # created_at, view_count, title
        
        # 构建缓存键
        cache_key = f"assets:{tenant_id}:{page}:{limit}:{asset_type}:{category_id}:{search}:{sort_by}"
        cached_result = cache_get(cache_key)
        if cached_result:
            return jsonify(cached_result)
        
        # 构建查询
        query = TenantAsset.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).options(joinedload(TenantAsset.categories))
        
        # 类型筛选
        if asset_type:
            query = query.filter_by(content_type=asset_type)
        
        # 分类筛选
        if category_id:
            query = query.join(TenantAsset.categories).filter(
                AssetCategory.id == category_id
            )
        
        # 搜索筛选
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    TenantAsset.title.like(search_term),
                    TenantAsset.summary.like(search_term),
                    TenantAsset.tags.like(search_term)
                )
            )
        
        # 排序
        if sort_by == 'view_count':
            query = query.order_by(desc(TenantAsset.view_count))
        elif sort_by == 'title':
            query = query.order_by(TenantAsset.title)
        else:  # created_at
            query = query.order_by(
                desc(TenantAsset.sort_order),
                desc(TenantAsset.created_at)
            )
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        # 获取分类列表
        categories = AssetCategory.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).order_by(AssetCategory.sort_order).all()
        
        # 构建响应数据
        result = {
            'assets': [asset.to_public_dict() for asset in pagination.items],
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'per_page': limit
            },
            'categories': [cat.to_dict() for cat in categories],
            'tenant_info': {
                'id': tenant.id,
                'company_name': tenant.company_name,
                'logo': tenant.company_logo,
                'contact_info': tenant.get_public_contact_info(),
                'library_title': settings.theme_config.get('title', '精选素材库') if settings.theme_config else '精选素材库'
            },
            'stats': {
                'total_assets': pagination.total,
                'asset_types': get_asset_type_counts(tenant_id)
            }
        }
        
        # 缓存结果（5分钟）
        cache_set(cache_key, result, timeout=300)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error getting public assets: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assets_bp.route('/public/assets/<int:asset_id>/detail', methods=['GET'])
@cross_origin()
def get_asset_detail(asset_id):
    """获取素材详情"""
    try:
        asset = TenantAsset.query.filter_by(
            id=asset_id,
            status='active'
        ).options(joinedload(TenantAsset.categories)).first()
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # 检查素材库是否公开
        settings = AssetLibrarySettings.query.filter_by(tenant_id=asset.tenant_id).first()
        if not settings or not settings.enabled or not settings.public_access:
            return jsonify({'error': 'Asset not available'}), 404
        
        # 记录访问统计
        track_asset_access(asset_id, asset.tenant_id, 'view', request)
        
        # 获取租户信息
        tenant = Tenant.query.get(asset.tenant_id)
        
        return jsonify({
            'asset': asset.to_public_dict(),
            'tenant_info': {
                'company_name': tenant.company_name,
                'logo': tenant.company_logo,
                'contact_info': tenant.get_public_contact_info()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting asset detail: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assets_bp.route('/public/assets/<int:asset_id>/track', methods=['POST'])
@cross_origin()
def track_asset_interaction(asset_id):
    """记录素材交互统计"""
    try:
        data = request.get_json() or {}
        action_type = data.get('action_type', 'view')
        
        if action_type not in ['view', 'share', 'download', 'click']:
            return jsonify({'error': 'Invalid action type'}), 400
        
        asset = TenantAsset.query.filter_by(
            id=asset_id,
            status='active'
        ).first()
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # 记录统计
        track_asset_access(asset_id, asset.tenant_id, action_type, request, data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error tracking asset interaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ==================== 管理接口 ====================

@assets_bp.route('/tenant/assets', methods=['GET'])
@require_tenant_auth
def get_tenant_assets():
    """获取租户素材列表（管理后台）"""
    try:
        tenant_id = get_current_tenant_id()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        status = request.args.get('status', '')
        asset_type = request.args.get('type', '')
        search = request.args.get('search', '').strip()
        
        # 构建查询
        query = TenantAsset.query.filter_by(tenant_id=tenant_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if asset_type:
            query = query.filter_by(content_type=asset_type)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    TenantAsset.title.like(search_term),
                    TenantAsset.summary.like(search_term)
                )
            )
        
        # 排序和分页
        pagination = query.order_by(
            desc(TenantAsset.sort_order),
            desc(TenantAsset.created_at)
        ).paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        # 获取计划限制
        plan_limits = get_tenant_plan_limits(tenant_id)
        
        # 获取统计数据
        stats = get_tenant_asset_stats(tenant_id)
        
        return jsonify({
            'assets': [asset.to_admin_dict() for asset in pagination.items],
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'plan_limits': plan_limits,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting tenant assets: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assets_bp.route('/tenant/assets', methods=['POST'])
@require_tenant_auth
def create_asset():
    """创建新素材"""
    try:
        tenant_id = get_current_tenant_id()
        data = request.get_json()
        
        # 验证数据
        validation_result = validate_asset_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # 检查计划限制
        current_count = TenantAsset.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).count()
        
        plan_limits = get_tenant_plan_limits(tenant_id)
        if current_count >= plan_limits['asset_library_max']:
            return jsonify({
                'error': 'Asset library limit reached',
                'limit': plan_limits['asset_library_max'],
                'current': current_count
            }), 400
        
        # 创建素材
        asset = TenantAsset(
            tenant_id=tenant_id,
            title=data['title'],
            summary=data.get('summary', ''),
            cover=data.get('cover', ''),
            content_type=data.get('content_type', 'document'),
            content_url=data['content_url'],
            file_size=data.get('file_size', 0),
            file_format=data.get('file_format', ''),
            sort_order=data.get('sort_order', 0),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            status=data.get('status', 'active'),
            created_by=get_current_user_id()
        )
        
        db.session.add(asset)
        db.session.flush()  # 获取ID
        
        # 处理分类关联
        category_ids = data.get('category_ids', [])
        if category_ids:
            for category_id in category_ids:
                category = AssetCategory.query.filter_by(
                    id=category_id,
                    tenant_id=tenant_id
                ).first()
                if category:
                    asset.categories.append(category)
        
        db.session.commit()
        
        return jsonify(asset.to_admin_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating asset: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assets_bp.route('/tenant/assets/<int:asset_id>', methods=['PUT'])
@require_tenant_auth
def update_asset(asset_id):
    """更新素材"""
    try:
        tenant_id = get_current_tenant_id()
        data = request.get_json()
        
        asset = TenantAsset.query.filter_by(
            id=asset_id,
            tenant_id=tenant_id
        ).first()
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # 验证数据
        validation_result = validate_asset_data(data, asset_id)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # 更新字段
        asset.title = data.get('title', asset.title)
        asset.summary = data.get('summary', asset.summary)
        asset.cover = data.get('cover', asset.cover)
        asset.content_type = data.get('content_type', asset.content_type)
        asset.content_url = data.get('content_url', asset.content_url)
        asset.file_size = data.get('file_size', asset.file_size)
        asset.file_format = data.get('file_format', asset.file_format)
        asset.sort_order = data.get('sort_order', asset.sort_order)
        asset.tags = data.get('tags', asset.tags)
        asset.metadata = data.get('metadata', asset.metadata)
        asset.status = data.get('status', asset.status)
        asset.updated_by = get_current_user_id()
        
        # 更新分类关联
        if 'category_ids' in data:
            asset.categories.clear()
            for category_id in data['category_ids']:
                category = AssetCategory.query.filter_by(
                    id=category_id,
                    tenant_id=tenant_id
                ).first()
                if category:
                    asset.categories.append(category)
        
        db.session.commit()
        
        return jsonify(asset.to_admin_dict())
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating asset: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assets_bp.route('/tenant/assets/<int:asset_id>', methods=['DELETE'])
@require_tenant_auth
def delete_asset(asset_id):
    """删除素材"""
    try:
        tenant_id = get_current_tenant_id()
        
        asset = TenantAsset.query.filter_by(
            id=asset_id,
            tenant_id=tenant_id
        ).first()
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # 软删除（设置状态为inactive）
        asset.status = 'inactive'
        asset.updated_by = get_current_user_id()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Asset deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting asset: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@assets_bp.route('/tenant/assets/upload', methods=['POST'])
@require_tenant_auth
def upload_asset_file():
    """上传素材文件"""
    try:
        tenant_id = get_current_tenant_id()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'document')
        
        # 验证文件
        validation_result = validate_file(file, file_type)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # 检查计划限制
        plan_limits = get_tenant_plan_limits(tenant_id)
        if file.content_length > plan_limits['asset_file_size_limit']:
            return jsonify({
                'error': 'File size exceeds limit',
                'limit': plan_limits['asset_file_size_limit']
            }), 400
        
        # 上传文件
        upload_result = upload_file(file, tenant_id, file_type)
        if not upload_result['success']:
            return jsonify({'error': upload_result['message']}), 500
        
        return jsonify({
            'success': True,
            'file_url': upload_result['file_url'],
            'file_size': upload_result['file_size'],
            'file_format': upload_result['file_format']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading asset file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ==================== 辅助函数 ====================

def get_asset_type_counts(tenant_id):
    """获取素材类型统计"""
    result = db.session.query(
        TenantAsset.content_type,
        func.count(TenantAsset.id).label('count')
    ).filter_by(
        tenant_id=tenant_id,
        status='active'
    ).group_by(TenantAsset.content_type).all()
    
    return {item.content_type: item.count for item in result}

def get_tenant_asset_stats(tenant_id):
    """获取租户素材统计"""
    total_assets = TenantAsset.query.filter_by(
        tenant_id=tenant_id,
        status='active'
    ).count()
    
    total_views = db.session.query(
        func.sum(TenantAsset.view_count)
    ).filter_by(
        tenant_id=tenant_id,
        status='active'
    ).scalar() or 0
    
    total_shares = db.session.query(
        func.sum(TenantAsset.share_count)
    ).filter_by(
        tenant_id=tenant_id,
        status='active'
    ).scalar() or 0
    
    # 最近30天访问统计
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_views = AssetAnalytics.query.filter(
        AssetAnalytics.tenant_id == tenant_id,
        AssetAnalytics.created_at >= thirty_days_ago,
        AssetAnalytics.action_type == 'view'
    ).count()
    
    return {
        'total_assets': total_assets,
        'total_views': total_views,
        'total_shares': total_shares,
        'recent_views': recent_views
    }

def get_tenant_plan_limits(tenant_id):
    """获取租户计划限制"""
    # 这里应该根据实际的计划系统来获取限制
    # 暂时返回默认值
    return {
        'asset_library_max': 50,
        'asset_file_size_limit': 100 * 1024 * 1024,  # 100MB
        'video_upload': True,
        'custom_cover_upload': True
    }

def get_current_user_id():
    """获取当前用户ID"""
    # 这里应该从认证系统获取当前用户ID
    return request.headers.get('X-User-ID', 'system')
