#!/bin/bash

echo "======================================================================"
echo "查看最近的OAuth授权日志"
echo "======================================================================"
echo ""

# 获取Gunicorn进程PID
GUNICORN_PID=$(ps aux | grep "gunicorn.*wsgi:application" | grep -v grep | head -1 | awk '{print $2}')

if [ -z "$GUNICORN_PID" ]; then
    echo "❌ 找不到Gunicorn进程"
    exit 1
fi

echo "📊 查询Gunicorn进程日志: PID=$GUNICORN_PID"
echo ""

# 方法1: 尝试从journalctl读取
echo "方法1: 从systemd日志读取"
echo "----------------------------------------------------------------------"
journalctl _PID=$GUNICORN_PID -n 200 --no-pager | grep -A30 "user_info完整内容" | tail -50

if [ $? -ne 0 ]; then
    echo ""
    echo "方法2: 从stderr读取（如果systemd日志没有）"
    echo "----------------------------------------------------------------------"
    # 尝试从进程的stderr读取
    cat /proc/$GUNICORN_PID/fd/2 2>/dev/null | tail -100 | grep -A30 "user_info完整内容" || echo "无法读取进程stderr"
fi

echo ""
echo "======================================================================"
echo "如果上面没有显示OAuth日志，说明还未触发授权"
echo "请在企微中打开应用，等待授权提示后点击'同意'"
echo "======================================================================"

