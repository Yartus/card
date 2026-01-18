from .main import db
from sqlalchemy import func
from datetime import datetime

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    corp_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    name = db.Column(db.String(256))
    plan = db.Column(db.String(32), default='free')
    permanent_code = db.Column(db.String(512))
    
    # SaaS通用配置字段
    config = db.Column(db.Text)  # JSON配置：用于存储租户级别的应用配置
    
    # 权限相关字段
    installer_userid = db.Column(db.String(128))  # 应用安装者userid
    auth_info = db.Column(db.Text)  # 应用授权信息(JSON)，包含可见范围
    user_limit = db.Column(db.Integer, default=0)  # 用户名额限制
    
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    members = db.relationship('Member', backref='tenant', lazy=True, cascade='all, delete-orphan')

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # 身份标识
    userid = db.Column(db.String(128), nullable=False, index=True)  # 企业内部真实userid
    open_userid = db.Column(db.String(128), index=True)  # 服务商主体下的加密userid（第三方应用可见）
    
    # 基本信息
    name = db.Column(db.String(128))
    mobile = db.Column(db.String(64))
    email = db.Column(db.String(128))
    avatar_url = db.Column(db.String(512))
    department = db.Column(db.String(256))
    position = db.Column(db.String(128))
    
    # 状态与权限
    is_active = db.Column(db.Boolean, default=True)
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

