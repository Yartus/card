import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:wecard123@localhost:3306/wecard')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # MinIO/S3配置
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'wecard-files')
    MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
    
    # 企业微信配置
    WECOM_CORP_ID = os.getenv('WECOM_CORP_ID', '')
    WECOM_CORP_SECRET = os.getenv('WECOM_CORP_SECRET', '')
    WECOM_AGENT_ID = os.getenv('WECOM_AGENT_ID', '')
    WECOM_CALLBACK_TOKEN = os.getenv('WECOM_CALLBACK_TOKEN', '')
    WECOM_CALLBACK_AES_KEY = os.getenv('WECOM_CALLBACK_AES_KEY', '')
    
    # 应用配置
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # 文件上传限制
    MAX_FILE_SIZE_FREE = int(os.getenv('MAX_FILE_SIZE_FREE', '5242880'))  # 5MB
    MAX_FILE_SIZE_PAID = int(os.getenv('MAX_FILE_SIZE_PAID', '20971520'))  # 20MB
    MAX_FILES_FREE = int(os.getenv('MAX_FILES_FREE', '5'))
    MAX_FILES_PAID = int(os.getenv('MAX_FILES_PAID', '50'))

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
