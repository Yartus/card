#!/bin/bash

echo "======================================================================"
echo "系统重启 + 数据库迁移"
echo "======================================================================"

# 执行数据库迁移
echo ""
echo "步骤1: 执行数据库迁移..."
cd /opt/qwcard
source venv/bin/activate
python3 migrations/add_display_name.py

if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败"
    exit 1
fi

# 重启后端
echo ""
echo "步骤2: 重启后端Gunicorn..."
pkill -HUP -f "gunicorn.*wsgi:application"
sleep 2

# 重启前端
echo ""
echo "步骤3: 重启前端Nuxt..."
pkill -9 -f "nuxt --hostname"
pkill -9 -f "npm run dev"
sleep 2
nohup npm run dev:light > /var/log/nuxt-dev.log 2>&1 < /dev/null &

echo ""
echo "步骤4: 等待服务启动..."
sleep 5

echo ""
echo "✅ 系统重启完成"
echo "======================================================================"

