#!/usr/bin/env python3
"""
数据库迁移脚本：添加 open_userid 字段到 members 表
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wsgi import application
from flask_sqlalchemy import SQLAlchemy

db = application.extensions['sqlalchemy'].db

def migrate():
    """执行数据库迁移"""
    with application.app_context():
        try:
            # 检查字段是否已存在
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SHOW COLUMNS FROM members LIKE 'open_userid'"))
                row = result.fetchone()
                
                if row:
                    print("⚠️  open_userid 字段已存在，跳过迁移")
                    return True
                
                # 添加字段
                print("📝 正在添加 open_userid 字段...")
                conn.execute(db.text("""
                    ALTER TABLE members 
                    ADD COLUMN open_userid VARCHAR(128) DEFAULT NULL AFTER userid
                """))
                
                # 添加索引
                print("📝 正在添加索引...")
                conn.execute(db.text("""
                    ALTER TABLE members 
                    ADD INDEX idx_open_userid (open_userid)
                """))
                
                conn.commit()
            
            print("✅ 数据库迁移成功")
            return True
            
        except Exception as e:
            print(f"❌ 数据库迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

