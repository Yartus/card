from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 加载配置
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    from .config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # 注册核心蓝图
    from .routes.wecom import bp as wecom_bp
    from .routes.provider_auth import bp as provider_auth_bp
    from .routes.admin import bp as admin_bp

    app.register_blueprint(wecom_bp)
    app.register_blueprint(provider_auth_bp)
    app.register_blueprint(admin_bp)

    @app.route('/healthz')
    def healthz():
        return {'status': 'ok', 'service': 'wecom-saas-core'}

    return app

