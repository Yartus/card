#!/bin/bash
# WeCard 健康检查脚本
# 每5分钟运行一次，确保服务正常

LOG_FILE="/var/log/wecard-health.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Health check started" >> $LOG_FILE

# 检查后端API
if ! systemctl is-active --quiet wecard-api.service; then
    echo "[$DATE] ❌ Backend API is down, restarting..." >> $LOG_FILE
    systemctl restart wecard-api.service
    echo "[$DATE] ✅ Backend API restarted" >> $LOG_FILE
fi

# 检查前端Nuxt
if ! systemctl is-active --quiet wecard-nuxt.service; then
    echo "[$DATE] ❌ Frontend Nuxt is down, restarting..." >> $LOG_FILE
    systemctl restart wecard-nuxt.service
    echo "[$DATE] ✅ Frontend Nuxt restarted" >> $LOG_FILE
fi

# 检查Nginx
if ! systemctl is-active --quiet nginx; then
    echo "[$DATE] ❌ Nginx is down, restarting..." >> $LOG_FILE
    systemctl restart nginx
    echo "[$DATE] ✅ Nginx restarted" >> $LOG_FILE
fi

# 检查内存使用
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "[$DATE] ⚠️ High memory usage: ${MEM_USAGE}%" >> $LOG_FILE
fi

# 检查磁盘使用
DISK_USAGE=$(df / | tail -1 | awk '{print int($5)}')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] ⚠️ High disk usage: ${DISK_USAGE}%" >> $LOG_FILE
fi

echo "[$DATE] Health check completed" >> $LOG_FILE

