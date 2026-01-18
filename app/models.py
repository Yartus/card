from .main import db
from datetime import datetime
from sqlalchemy import func

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    corp_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    name = db.Column(db.String(256))
    plan = db.Column(db.String(32), default='free')
    permanent_code = db.Column(db.String(512))
    config = db.Column(db.Text)  # JSON配置：名片模版、推送配置等
    
    # 权限相关字段
    installer_userid = db.Column(db.String(128))  # 应用安装者userid
    auth_info = db.Column(db.Text)  # 应用授权信息(JSON)，包含可见范围
    user_limit = db.Column(db.Integer, default=0)  # 用户名额限制
    
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    members = db.relationship('Member', backref='tenant', lazy=True, cascade='all, delete-orphan')
    templates = db.relationship('CardTemplate', backref='tenant', lazy=True, cascade='all, delete-orphan')
    files = db.relationship('FileAsset', backref='tenant', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('CardLog', backref='tenant', lazy=True, cascade='all, delete-orphan')

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    userid = db.Column(db.String(128), nullable=False, index=True)  # 企业内部真实userid
    open_userid = db.Column(db.String(128), index=True)  # 服务商主体下的加密userid（第三方应用可见）
    name = db.Column(db.String(128))  # OAuth返回的姓名（通常是加密ID）
    display_name = db.Column(db.String(128))  # 管理员设置的对外显示名称
    mobile = db.Column(db.String(64))
    email = db.Column(db.String(128))
    avatar_url = db.Column(db.String(512))
    custom_avatar_url = db.Column(db.String(512))
    custom_push_photo_url = db.Column(db.String(512))
    department = db.Column(db.String(256))
    position = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    
    # 权限相关字段
    role = db.Column(db.Enum('admin', 'user', name='member_role'), default='user')  # 用户角色
    is_installer = db.Column(db.Boolean, default=False)  # 是否是应用安装者
    in_visible_range = db.Column(db.Boolean, default=True)  # 是否在应用可见范围内
    
    # OAuth授权相关字段
    oauth_authorized = db.Column(db.Boolean, default=False)  # 是否已OAuth授权
    oauth_authorized_at = db.Column(db.DateTime)  # OAuth授权时间
    user_ticket = db.Column(db.String(512))  # 用户票据
    
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 唯一约束：同一租户下userid唯一
    __table_args__ = (db.UniqueConstraint('tenant_id', 'userid', name='uq_tenant_userid'),)

class CardTemplate(db.Model):
    __tablename__ = 'card_templates'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    template_json = db.Column(db.JSON)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

class FileAsset(db.Model):
    __tablename__ = 'file_assets'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    file_name = db.Column(db.String(256), nullable=False)
    file_url = db.Column(db.String(1024), nullable=False)
    file_type = db.Column(db.String(64))
    size = db.Column(db.Integer)
    md5 = db.Column(db.String(64), index=True)
    bucket = db.Column(db.String(128))
    object_key = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=func.now())

class CardLog(db.Model):
    __tablename__ = 'card_logs'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), index=True)
    event = db.Column(db.String(64), nullable=False, index=True)
    meta = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=func.now(), index=True)