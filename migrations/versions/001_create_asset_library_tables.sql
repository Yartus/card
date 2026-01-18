-- 素材库数据库表创建脚本
-- 版本: 001
-- 日期: 2025-11-05
-- 说明: 创建素材库相关表（已修复类型和枚举问题）

-- 1. 租户素材主表
CREATE TABLE IF NOT EXISTS `tenant_assets` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '素材ID',
  `tenant_id` INT NOT NULL COMMENT '租户ID（Integer类型，对应tenants.id）',
  `title` VARCHAR(200) NOT NULL COMMENT '素材标题',
  `summary` VARCHAR(500) DEFAULT '' COMMENT '素材简介',
  `cover` TEXT COMMENT '封面图片URL',
  `content_type` ENUM('document', 'image', 'video', 'link', 'presentation') DEFAULT 'document' COMMENT '内容类型',
  `content_url` TEXT COMMENT '内容URL',
  `file_size` INT DEFAULT 0 COMMENT '文件大小（字节）',
  `file_format` VARCHAR(20) DEFAULT '' COMMENT '文件格式',
  `view_count` INT DEFAULT 0 COMMENT '浏览次数',
  `share_count` INT DEFAULT 0 COMMENT '分享次数',
  `download_count` INT DEFAULT 0 COMMENT '下载次数',
  `sort_order` INT DEFAULT 0 COMMENT '排序序号',
  `tags` JSON COMMENT '标签列表',
  `metadata` JSON COMMENT '元数据（包含blocks等）',
  `status` ENUM('draft', 'published', 'active', 'inactive') DEFAULT 'draft' COMMENT '状态：draft=草稿, published=已发布, active=激活, inactive=停用',
  `created_by` VARCHAR(50) COMMENT '创建人',
  `updated_by` VARCHAR(50) COMMENT '更新人',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_tenant_id` (`tenant_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_view_count` (`view_count`),
  KEY `idx_sort_order` (`sort_order`),
  CONSTRAINT `tenant_assets_tenant_fk` 
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户素材表';

-- 2. 素材访问统计表
CREATE TABLE IF NOT EXISTS `asset_analytics` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `tenant_id` INT NOT NULL COMMENT '租户ID',
  `asset_id` BIGINT NOT NULL COMMENT '素材ID',
  `visitor_id` VARCHAR(100) COMMENT '访客ID（匿名标识）',
  `visitor_name` VARCHAR(100) COMMENT '访客姓名',
  `visitor_company` VARCHAR(200) COMMENT '访客公司',
  `visitor_title` VARCHAR(100) COMMENT '访客职位',
  `visitor_phone` VARCHAR(50) COMMENT '访客手机',
  `visitor_email` VARCHAR(100) COMMENT '访客邮箱',
  `visitor_ip` VARCHAR(50) COMMENT '访客IP',
  `visitor_location` VARCHAR(200) COMMENT '访客地理位置',
  `device_type` VARCHAR(50) COMMENT '设备类型',
  `browser` VARCHAR(100) COMMENT '浏览器',
  `os` VARCHAR(100) COMMENT '操作系统',
  `referrer` TEXT COMMENT '来源页面',
  `view_duration` INT DEFAULT 0 COMMENT '浏览时长（秒）',
  `action_type` ENUM('view', 'share', 'download', 'click') DEFAULT 'view' COMMENT '操作类型',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
  PRIMARY KEY (`id`),
  KEY `idx_tenant_id` (`tenant_id`),
  KEY `idx_asset_id` (`asset_id`),
  KEY `idx_visitor_id` (`visitor_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `asset_analytics_tenant_fk` 
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
  CONSTRAINT `asset_analytics_asset_fk` 
    FOREIGN KEY (`asset_id`) REFERENCES `tenant_assets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材访问统计表';

-- 3. 素材分类表
CREATE TABLE IF NOT EXISTS `asset_categories` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '分类ID',
  `tenant_id` INT NOT NULL COMMENT '租户ID',
  `name` VARCHAR(100) NOT NULL COMMENT '分类名称',
  `description` VARCHAR(500) COMMENT '分类描述',
  `parent_id` BIGINT COMMENT '父分类ID',
  `sort_order` INT DEFAULT 0 COMMENT '排序序号',
  `icon` VARCHAR(200) COMMENT '分类图标',
  `color` VARCHAR(20) COMMENT '分类颜色',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_tenant_id` (`tenant_id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_sort_order` (`sort_order`),
  CONSTRAINT `asset_categories_tenant_fk` 
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材分类表';

-- 4. 素材与分类关联表
CREATE TABLE IF NOT EXISTS `asset_category_relations` (
  `asset_id` BIGINT NOT NULL COMMENT '素材ID',
  `category_id` BIGINT NOT NULL COMMENT '分类ID',
  PRIMARY KEY (`asset_id`, `category_id`),
  KEY `idx_category_id` (`category_id`),
  CONSTRAINT `asset_category_relations_asset_fk` 
    FOREIGN KEY (`asset_id`) REFERENCES `tenant_assets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `asset_category_relations_category_fk` 
    FOREIGN KEY (`category_id`) REFERENCES `asset_categories` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材分类关联表';

-- 5. 素材库配置表
CREATE TABLE IF NOT EXISTS `asset_library_settings` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `tenant_id` INT NOT NULL COMMENT '租户ID',
  `library_name` VARCHAR(200) COMMENT '素材库名称',
  `library_description` TEXT COMMENT '素材库描述',
  `logo` VARCHAR(500) COMMENT 'Logo URL',
  `theme_color` VARCHAR(20) COMMENT '主题颜色',
  `enable_visitor_tracking` TINYINT(1) DEFAULT 1 COMMENT '是否启用访客追踪',
  `enable_public_access` TINYINT(1) DEFAULT 1 COMMENT '是否允许公开访问',
  `require_login` TINYINT(1) DEFAULT 0 COMMENT '是否需要登录',
  `custom_domain` VARCHAR(200) COMMENT '自定义域名',
  `settings` JSON COMMENT '其他配置（JSON格式）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tenant_id` (`tenant_id`),
  CONSTRAINT `asset_library_settings_tenant_fk` 
    FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材库配置表';

-- 验证表是否创建成功
SELECT 
  TABLE_NAME as '表名',
  TABLE_ROWS as '行数',
  CREATE_TIME as '创建时间'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'qwcard' 
  AND TABLE_NAME IN (
    'tenant_assets', 
    'asset_analytics', 
    'asset_categories', 
    'asset_category_relations', 
    'asset_library_settings'
  )
ORDER BY TABLE_NAME;

SELECT '✅ 素材库表结构创建完成！' AS status;
