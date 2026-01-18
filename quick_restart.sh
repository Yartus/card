#!/bin/bash
# 快速重启脚本（按照文档标准流程）

echo "======================================================================"
echo "系统快速重启"
echo "======================================================================"

# 步骤0: 数据库迁移
echo ""
echo "步骤0: 执行数据库迁移..."
cd /opt/qwcard
source venv/bin/activate

python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/qwcard')
from wsgi import application
from app.models import db

with application.app_context():
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SHOW COLUMNS FROM members LIKE 'display_name'"))
            if not result.fetchone():
                conn.execute(db.text("ALTER TABLE members ADD COLUMN display_name VARCHAR(128) DEFAULT NULL AFTER name"))
                conn.commit()
                print("✅ display_name 字段已添加")
            else:
                print("✅ display_name 字段已存在")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败"
    exit 1
fi

# 步骤1: 重启后端 API
echo ""
echo "步骤1: 重启后端 Gunicorn..."
cd /opt/qwcard
pkill -HUP -f "gunicorn.*wsgi:application"

# 步骤2: 重启前端 Nuxt（开发模式）
echo ""
echo "步骤2: 重启前端 Nuxt..."
echo "  - 清理所有Nuxt实例..."
pkill -9 -f "nuxt --hostname"
pkill -9 -f "npm run dev"
sleep 2

echo "  - 启动Nuxt开发服务..."
cd /opt/qwcard
nohup npm run dev:light > /var/log/nuxt-dev.log 2>&1 < /dev/null &

# 步骤3: 重启 Nginx
echo ""
echo "步骤3: 重启 Nginx..."
nginx -t && nginx -s reload

# 步骤4: 等待服务启动
echo ""
echo "步骤4: 等待服务启动..."
sleep 5

# 步骤5: 验证服务状态
echo ""
echo "步骤5: 验证服务状态..."
echo ""
echo "Gunicorn进程:"
ps aux | grep "gunicorn.*wsgi:application" | grep -v grep | head -3

echo ""
echo "Nuxt进程:"
ps aux | grep "npm run dev:light" | grep -v grep | head -2

echo ""
echo "端口监听:"
netstat -tuln | grep -E "3000|5001"

echo ""
echo "======================================================================"
echo "✅ 系统重启完成"
echo "======================================================================"
echo ""
echo "查看日志："
echo "  后端: tail -f /var/log/gunicorn.log"
echo "  前端: tail -f /var/log/nuxt-dev.log"


