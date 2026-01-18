"""
WeCard 素材库数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, Enum, JSON, Boolean, TIMESTAMP, ForeignKey, Index
from sqlalchemy.orm import relationship, backref
from .main import db

class TenantAsset(db.Model):
    """租户素材模型"""
    __tablename__ = 'tenant_assets'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)  # ✅ Integer类型
    title = Column(String(200), nullable=False)
    summary = Column(String(500), default='')
    cover = Column(Text)
    content_type = Column(Enum('document', 'image', 'video', 'link', 'presentation'), default='document')
    content_url = Column(Text)
    file_size = Column(Integer, default=0)
    file_format = Column(String(20), default='')
    view_count = Column(Integer, default=0, index=True)
    share_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    sort_order = Column(Integer, default=0, index=True)
    tags = Column(JSON)
    meta_data = Column(JSON)  # ✅ 避免SQLAlchemy保留字
    status = Column(Enum('draft', 'published', 'active', 'inactive'), default='draft', index=True)  # ✅ 添加published
    created_by = Column(String(50))
    updated_by = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    tenant = relationship("Tenant", backref="assets")
    analytics = relationship("AssetAnalytics", backref="asset", cascade="all, delete-orphan")
    categories = relationship("AssetCategory", secondary="asset_category_relations", back_populates="assets")
    
    # 索引
    __table_args__ = (
        Index('idx_tenant_status', 'tenant_id', 'status'),
        Index('idx_tenant_type', 'tenant_id', 'content_type'),
        Index('idx_sort_created', 'sort_order', 'created_at'),
    )
    
    def to_dict(self):
        """转换为字典（完整信息）"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'summary': self.summary,
            'cover': self.cover,
            'content_type': self.content_type,
            'content_url': self.content_url,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'view_count': self.view_count,
            'share_count': self.share_count,
            'download_count': self.download_count,
            'sort_order': self.sort_order,
            'tags': self.tags or [],
            'metadata': self.meta_data or {},  # ✅ API中仍使用metadata字段名
            'status': self.status,
            'categories': [cat.to_dict() for cat in self.categories],
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self):
        """转换为公开字典（隐藏敏感信息）"""
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'cover': self.cover,
            'content_type': self.content_type,
            'content_type_label': self.get_content_type_label(),
            'content_url': self.content_url,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'view_count': self.view_count,
            'share_count': self.share_count,
            'tags': self.tags or [],
            'categories': [cat.to_dict() for cat in self.categories],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'formatted_date': self.get_formatted_date(),
            'file_size_formatted': self.get_formatted_file_size()
        }
    
    def to_admin_dict(self):
        """转换为管理后台字典（包含统计信息）"""
        base_dict = self.to_dict()
        
        # 添加统计信息
        recent_views = AssetAnalytics.query.filter_by(
            asset_id=self.id,
            action_type='view'
        ).filter(
            AssetAnalytics.created_at >= datetime.now() - timedelta(days=30)
        ).count()
        
        base_dict.update({
            'recent_views': recent_views,
            'total_interactions': self.view_count + self.share_count + self.download_count,
            'formatted_date': self.get_formatted_date(),
            'file_size_formatted': self.get_formatted_file_size(),
            'content_type_label': self.get_content_type_label()
        })
        
        return base_dict
    
    def get_content_type_label(self):
        """获取内容类型标签"""
        type_labels = {
            'document': '文档资料',
            'image': '图片素材',
            'video': '视频内容',
            'link': '链接资源',
            'presentation': '演示文稿'
        }
        return type_labels.get(self.content_type, '未知类型')
    
    def get_formatted_date(self):
        """获取格式化日期"""
        if not self.created_at:
            return ''
        
        now = datetime.now()
        diff = now - self.created_at
        
        if diff.days == 0:
            return '今天'
        elif diff.days == 1:
            return '昨天'
        elif diff.days < 7:
            return f'{diff.days}天前'
        elif diff.days < 30:
            weeks = diff.days // 7
            return f'{weeks}周前'
        else:
            return self.created_at.strftime('%Y-%m-%d')
    
    def get_formatted_file_size(self):
        """获取格式化文件大小"""
        if not self.file_size:
            return ''
        
        size = self.file_size
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f'{size:.1f} {units[unit_index]}'

class AssetAnalytics(db.Model):
    """素材访问统计模型"""
    __tablename__ = 'asset_analytics'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_id = Column(BigInteger, ForeignKey('tenant_assets.id'), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)  # ✅ Integer类型
    visitor_ip = Column(String(45))
    visitor_id = Column(String(100))
    user_agent = Column(Text)
    referrer = Column(Text)
    action_type = Column(Enum('view', 'share', 'download', 'click'), default='view', index=True)
    device_type = Column(Enum('mobile', 'tablet', 'desktop', 'unknown'), default='unknown')
    browser = Column(String(50))
    os = Column(String(50))
    country = Column(String(10))
    city = Column(String(50))
    session_id = Column(String(100))
    duration = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    
    # 关系
    tenant = relationship("Tenant", backref="asset_analytics")
    
    # 索引
    __table_args__ = (
        Index('idx_asset_date', 'asset_id', 'created_at'),
        Index('idx_tenant_date', 'tenant_id', 'created_at'),
        Index('idx_action_date', 'action_type', 'created_at'),
        Index('idx_visitor_session', 'visitor_id', 'session_id'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'tenant_id': self.tenant_id,
            'visitor_ip': self.visitor_ip,
            'visitor_id': self.visitor_id,
            'action_type': self.action_type,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'country': self.country,
            'city': self.city,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AssetCategory(db.Model):
    """素材分类模型"""
    __tablename__ = 'asset_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)  # ✅ Integer类型
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(20), default='#1890FF')
    sort_order = Column(Integer, default=0)
    status = Column(Enum('active', 'inactive'), default='active')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    tenant = relationship("Tenant", backref="asset_categories")
    assets = relationship("TenantAsset", secondary="asset_category_relations", back_populates="categories")
    
    # 唯一约束
    __table_args__ = (
        Index('idx_tenant_status', 'tenant_id', 'status'),
        db.UniqueConstraint('tenant_id', 'name', name='uk_tenant_category_name'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'sort_order': self.sort_order,
            'status': self.status,
            'asset_count': len(self.assets) if self.assets else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AssetCategoryRelation(db.Model):
    """素材分类关联模型"""
    __tablename__ = 'asset_category_relations'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    asset_id = Column(BigInteger, ForeignKey('tenant_assets.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('asset_categories.id'), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('asset_id', 'category_id', name='uk_asset_category'),
        Index('idx_category_id', 'category_id'),
    )

class AssetLibrarySettings(db.Model):
    """素材库配置模型"""
    __tablename__ = 'asset_library_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, unique=True)  # ✅ Integer类型
    enabled = Column(Boolean, default=True)
    public_access = Column(Boolean, default=True)
    custom_domain = Column(String(100))
    theme_config = Column(JSON)
    seo_config = Column(JSON)
    contact_config = Column(JSON)
    watermark_config = Column(JSON)
    analytics_enabled = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    tenant = relationship("Tenant", backref=backref("asset_library_settings", uselist=False))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'enabled': self.enabled,
            'public_access': self.public_access,
            'custom_domain': self.custom_domain,
            'theme_config': self.theme_config or {},
            'seo_config': self.seo_config or {},
            'contact_config': self.contact_config or {},
            'watermark_config': self.watermark_config or {},
            'analytics_enabled': self.analytics_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_theme_config(self):
        """获取主题配置（带默认值）"""
        default_config = {
            'title': '精选素材库',
            'description': '企业官方素材库',
            'primary_color': '#1890FF',
            'secondary_color': '#F0F7FF',
            'layout': 'grid',
            'show_categories': True,
            'show_search': True,
            'show_stats': False
        }
        
        if self.theme_config:
            default_config.update(self.theme_config)
        
        return default_config
    
    def get_seo_config(self):
        """获取SEO配置（带默认值）"""
        default_config = {
            'title_template': '{company_name} - 精选素材库',
            'description_template': '{company_name}的官方素材库，包含产品介绍、解决方案、案例展示等精选内容。',
            'keywords': '企业素材,产品介绍,解决方案,案例展示',
            'og_image': None
        }
        
        if self.seo_config:
            default_config.update(self.seo_config)
        
        return default_config
