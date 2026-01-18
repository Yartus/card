# OAuth授权问题排查指南

## 问题现象
工作台中打开页面时，没有弹出授权界面，也不能打开名片

## 排查步骤

### 1. 确认访问的URL
- **管理员工作台**: `https://your-domain.com/wecom/workspace`  
  → 这个页面是配置界面，不需要OAuth授权
  
- **普通员工名片**: `https://your-domain.com/wecom/card`  
  → 这个页面会触发OAuth授权（如果信息不完整）

**重要**：请确认您访问的是 `/wecom/card` 而不是 `/wecom/workspace`

### 2. 检查浏览器控制台

在企微中打开 `/wecom/card` 页面，查看：

#### 方法A（如果能用Chrome DevTools）：
1. 在页面上长按 → 检查
2. 切换到 Console 标签
3. 查找以下日志：
   - `🎴 企微名片页面加载`
   - `📋 加载用户名片数据...`
   - `🔐 需要OAuth授权获取完整信息` ← **关键**

#### 方法B（使用企微内置调试）：
1. 在企微工作台应用管理中开启"调试模式"
2. 重新打开名片页面
3. 查看日志输出

### 3. 检查网络请求

查看是否成功调用了 `/api/v1/wecom/card/my`：
- **HTTP 200** + `need_oauth: true` → 应该弹出授权弹窗
- **HTTP 401** → Token无效，需要重新认证
- **HTTP 500** → 服务器错误，查看后端日志

### 4. 检查后端日志

```bash
cd /opt/qwcard
# 查看gunicorn进程
ps aux | grep gunicorn

# 实时查看日志（如果有日志文件）
tail -f logs/*.log

# 或者查看nginx日志
tail -f /var/log/nginx/access.log | grep "card/my"
```

### 5. 手动测试API

```bash
# 生成测试token
cd /opt/qwcard && python3 << 'PYEOF'
import jwt
from datetime import datetime, timedelta

JWT_SECRET = 'QULY5j8jMQgURxo5oOCUN8WC4-N6D4sJiDs78APxhh0'
payload = {
    'tenant_id': 3,
    'corp_id': 'wpmKtScgAAXKfGIm-CZyZtotvAzbKebw',
    'userid': 'womKtScgAAEkyZS7yXhQkhLqeCvf7ehQ',
    'is_admin': True,
    'role': 'admin',
    'exp': datetime.utcnow() + timedelta(hours=12),
    'iat': datetime.utcnow()
}
token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
print(token)
PYEOF

# 测试API（替换下面的TOKEN）
curl -X GET "http://127.0.0.1:5001/api/v1/wecom/card/my" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" | python3 -m json.tool
```

期望响应：
```json
{
  "success": false,
  "need_oauth": true,
  "oauth_url": "https://open.weixin.qq.com/connect/oauth2/authorize?...",
  "message": "需要您的授权以获取完整名片信息"
}
```

### 6. 检查数据库状态

```bash
cd /opt/qwcard
mysql -u wecard -pwecard123 wecard << 'SQL'
SELECT 
    id, 
    userid, 
    name, 
    oauth_authorized,
    CASE 
        WHEN name = userid THEN '⚠️ 名字是userid' 
        WHEN name IS NULL THEN '⚠️ 名字为空'
        ELSE '✅ 正常'
    END as name_status,
    CASE 
        WHEN avatar_url IS NULL THEN '⚠️ 无头像'
        ELSE '✅ 有头像'
    END as avatar_status,
    CASE
        WHEN oauth_authorized = 1 THEN '✅ 已授权'
        ELSE '❌ 未授权'
    END as oauth_status
FROM members 
WHERE tenant_id = 3
ORDER BY id DESC 
LIMIT 5;
SQL
```

### 7. 常见问题

#### 问题1：页面一片空白
**可能原因**: 前端路由或认证失败  
**解决**: 
1. 检查是否从企微工作台正确进入
2. 清除浏览器缓存后重试
3. 检查 `/wecom/card` 路由是否正确配置

#### 问题2：看到"认证失败"
**可能原因**: OAuth code失效或处理失败  
**解决**:
1. 重新从企微工作台进入
2. 检查应用是否有 `snsapi_privateinfo` 权限
3. 查看后端日志中的 `auth/verify_user` 调用

#### 问题3：没有弹出授权窗口
**可能原因**: 
1. 前端没有正确处理 `need_oauth` 响应
2. API调用失败（500错误）
3. 成员信息已完整（不需要授权）

**解决**:
1. 打开调试页面测试API
2. 检查前端console日志
3. 确认数据库中成员信息确实不完整

### 8. 下一步

如果以上步骤都无法解决，请提供：
1. 浏览器控制台的完整日志
2. 访问的具体URL
3. API `/api/v1/wecom/card/my` 的响应内容
4. 数据库查询结果

这样我可以更精确地定位问题。
