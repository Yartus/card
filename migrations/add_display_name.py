#!/usr/bin/env python3
"""
添加 display_name 字段到 members 表
用于存储管理员设置的对外显示名称
"""

import sys
sys.path.insert(0, '/opt/qwcard')

from wsgi import application
from app.models import db

def migrate():
    with application.app_context():
        try:
            with db.engine.connect() as conn:
                # 检查 display_name 字段是否存在
                result = conn.execute(db.text("SHOW COLUMNS FROM members LIKE 'display_name'"))
                if not result.fetchone():
                    print("📝 添加 display_name 字段...")
                    conn.execute(db.text(
                        "ALTER TABLE members ADD COLUMN display_name VARCHAR(128) DEFAULT NULL AFTER name"
                    ))
                    conn.commit()
                    print("✅ display_name 字段添加成功")
                else:
                    print("⚠️  display_name 字段已存在，跳过")
                
                return True
        except Exception as e:
            print(f"❌ 数据库迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("="*70)
    print("数据库迁移：添加 display_name 字段")
    print("="*70)
    
    success = migrate()
    
    if success:
        print("\n✅ 迁移完成")
        sys.exit(0)
    else:
        print("\n❌ 迁移失败")
        sys.exit(1)

