#!/bin/bash

echo "======================================================================"
echo "实时监控OAuth授权日志"
echo "======================================================================"
echo ""
echo "请在企微中打开应用，触发OAuth授权"
echo "按 Ctrl+C 停止监控"
echo ""
echo "======================================================================"
echo ""

# 获取Gunicorn主进程PID
GUNICORN_PID=$(ps aux | grep "gunicorn.*wsgi:application" | grep -v grep | head -1 | awk '{print $2}')

if [ -z "$GUNICORN_PID" ]; then
    echo "❌ 找不到Gunicorn进程"
    exit 1
fi

echo "✅ 监控Gunicorn进程: PID=$GUNICORN_PID"
echo ""

# 实时查看Gunicorn的stderr输出
journalctl -f _PID=$GUNICORN_PID --no-pager | grep --line-buffered -E "OAuth|oauth|授权|user_info|getuserdetail"

