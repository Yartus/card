from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..main import db
from ..models import FileAsset, Tenant, Member
from .wecom import verify_jwt_token
import os
import hashlib
from datetime import datetime
import mimetypes

bp = Blueprint('files', __name__, url_prefix='/api/v1/files')

# 允许的文件类型
ALLOWED_EXTENSIONS = {
    'image': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'},
    'video': {'mp4', 'webm', 'mov'},
    'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
}

# 文件大小限制（根据套餐和文件类型）
SIZE_LIMITS = {
    'free': {
        'image': 2 * 1024 * 1024,      # 2MB
        'video': 10 * 1024 * 1024,     # 10MB
        'document': 5 * 1024 * 1024    # 5MB
    },
    'trial': {
        'image': 5 * 1024 * 1024,      # 5MB
        'video': 20 * 1024 * 1024,     # 20MB
        'document': 10 * 1024 * 1024   # 10MB
    },
    'pro': {
        'image': 10 * 1024 * 1024,     # 10MB
        'video': 30 * 1024 * 1024,     # 30MB
        'document': 20 * 1024 * 1024   # 20MB
    },
    'enterprise': {
        'image': 20 * 1024 * 1024,     # 20MB
        'video': 50 * 1024 * 1024,     # 50MB
        'document': 50 * 1024 * 1024   # 50MB
    }
}

def allowed_file(filename, file_type='image'):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    """根据文件扩展名判断类型"""
    if '.' not in filename:
        return 'unknown'
    ext = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return 'unknown'

def calculate_md5(file_content):
    """计算文件MD5"""
    return hashlib.md5(file_content).hexdigest()

@bp.route('/upload', methods=['POST'])
def upload():
    """
    租户文件上传接口（支持JWT认证）
    POST /api/v1/files/upload
    Headers: Authorization: Bearer <token>
    Form-data: 
        - file: 文件
        - file_type: 可选，文件类型（image/video/document）
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
    is_admin = payload.get('is_admin', False)
    
    # 获取租户信息
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    # 获取上传者信息
    member = Member.query.filter_by(tenant_id=tenant_id, userid=userid).first()
    
    # 检查文件
    if 'file' not in request.files:
        return jsonify({'error': '未找到上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 获取文件类型（前端指定或自动判断）
    file_type = request.form.get('file_type') or get_file_type(file.filename)
    
    # 验证文件类型
    if not allowed_file(file.filename, file_type):
        return jsonify({
            'error': '不支持的文件类型',
            'allowed_types': list(ALLOWED_EXTENSIONS.get(file_type, set()))
        }), 400
    
    # 读取文件内容
    file_content = file.read()
    file_size = len(file_content)
    
    # 检查文件大小限制（根据套餐和文件类型）
    plan_limits = SIZE_LIMITS.get(tenant.plan, SIZE_LIMITS['free'])
    size_limit = plan_limits.get(file_type, plan_limits.get('image', 2 * 1024 * 1024))
    
    if file_size > size_limit:
        return jsonify({
            'error': '文件大小超出限制',
            'size': file_size,
            'limit': size_limit,
            'limit_mb': round(size_limit / (1024 * 1024), 1),
            'plan': tenant.plan,
            'file_type': file_type
        }), 400
    
    # 计算MD5（用于去重）
    file_md5 = calculate_md5(file_content)
    
    # 检查是否已存在相同文件
    existing_file = FileAsset.query.filter_by(
        tenant_id=tenant_id,
        md5=file_md5
    ).first()
    
    if existing_file:
        current_app.logger.info(f'文件已存在，返回已有URL: {existing_file.file_url}')
        return jsonify({
            'success': True,
            'file_id': existing_file.id,
            'url': existing_file.file_url,
            'file_name': existing_file.file_name,
            'file_type': existing_file.file_type,
            'size': existing_file.size,
            'duplicate': True
        })
    
    # 生成安全的文件名
    original_filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{tenant_id}_{timestamp}_{file_md5[:8]}_{original_filename}"
    
    # 保存文件到本地（后续可以改为MinIO/OSS）
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', '/opt/qwcard/uploads'), str(tenant_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # 生成文件URL（这里使用本地路径，后续可以改为CDN）
    file_url = f'/uploads/{tenant_id}/{filename}'
    
    # 保存文件记录到数据库
    file_asset = FileAsset(
        tenant_id=tenant_id,
        uploader_id=member.id if member else None,
        file_name=original_filename,
        file_url=file_url,
        file_type=file_type,
        size=file_size,
        md5=file_md5,
        bucket='local',
        object_key=file_path
    )
    
    try:
        db.session.add(file_asset)
        db.session.commit()
        
        current_app.logger.info(f'✅ 文件上传成功: tenant={tenant_id}, user={userid}, file={original_filename}, size={file_size}')
        
        return jsonify({
            'success': True,
            'file_id': file_asset.id,
            'url': file_url,
            'file_name': original_filename,
            'file_type': file_type,
            'size': file_size,
            'duplicate': False
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'❌ 文件上传失败: {e}')
        return jsonify({'error': '保存文件记录失败'}), 500


@bp.route('/list', methods=['GET'])
def list_files():
    """
    获取租户的文件列表
    GET /api/v1/files/list
    Headers: Authorization: Bearer <token>
    Query: ?file_type=image&page=1&per_page=20
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
    file_type = request.args.get('file_type')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # 构建查询
    query = FileAsset.query.filter_by(tenant_id=tenant_id)
    if file_type:
        query = query.filter_by(file_type=file_type)
    
    # 分页
    pagination = query.order_by(FileAsset.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    files = [{
        'id': f.id,
        'file_name': f.file_name,
        'file_url': f.file_url,
        'file_type': f.file_type,
        'size': f.size,
        'created_at': f.created_at.isoformat() if f.created_at else None
    } for f in pagination.items]
    
    return jsonify({
        'success': True,
        'files': files,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })
