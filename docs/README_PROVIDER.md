# WeCard 服务商管理系统

> 浙里有邮数字名片 SaaS 平台 - 服务商文档

---

## 🎯 系统概述

WeCard是一个基于企业微信的SaaS数字名片平台，支持多租户架构。

### 三重身份设计

```
┌─────────────────────────────────────────────────┐
│                 WeCard 系统                      │
├─────────────────────────────────────────────────┤
│                                                  │
│  1️⃣ 服务商管理员 (Provider Admin)                │
│     - 访问路径：/login → /admin                  │
│     - 认证方式：账号密码                          │
│     - 功能：查看所有租户、系统统计                │
│                                                  │
│  2️⃣ 租户管理员 (Tenant Admin)                    │
│     - 访问路径：企微工作台 → /wecom/workspace     │
│     - 认证方式：企微OAuth                        │
│     - 功能：配置名片模版、推送设置                │
│                                                  │
│  3️⃣ 租户普通用户 (Tenant User)                   │
│     - 访问路径：企微工作台 → /wecom/card         │
│     - 认证方式：企微OAuth                        │
│     - 功能：查看名片、分享名片                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 访问服务商后台

```
URL: https://zjemail.cn/login
默认账号：admin
默认密码：admin123
```

⚠️ **首次登录后请立即修改密码！**

### 2. 作为租户使用应用

1. 打开企微服务商后台
2. 找到"浙里有邮数字名片"应用
3. 使用自己的企业扫码安装
4. 从企微工作台打开应用
5. 配置名片模版

---

## 📁 文档索引

### 核心文档

1. **[快速开始-服务商后台.md](docs/快速开始-服务商后台.md)**
   - 5分钟快速配置指南
   - 默认密码和登录方式
   - 功能概览

2. **[服务商管理后台配置指南.md](docs/服务商管理后台配置指南.md)**
   - 完整的配置说明
   - API接口文档
   - 安全配置
   - 常见问题

3. **[企微应用配置-管理员与普通用户分离.md](docs/企微应用配置-管理员与普通用户分离.md)**
   - 企微OAuth认证流程
   - 权限系统设计
   - 前后端实现

4. **[企微认证改造与前端优化建议.md](docs/0.企微认证改造与前端优化建议.md)**
   - OAuth认证完整实现
   - 权限检查函数
   - 数据库Schema

---

## 🏗️ 系统架构

### 前端路由

| 路径 | 功能 | 认证方式 | 权限要求 |
|------|------|---------|---------|
| `/login` | 服务商登录 | 账号密码 | 无 |
| `/admin` | 服务商后台 | JWT Token | provider_admin |
| `/wecom/workspace` | 租户编辑工作台 | 企微OAuth | is_admin=true |
| `/wecom/card` | 用户名片查看 | 企微OAuth | 在可见范围内 |
| `/wecom/install` | 应用安装引导 | 无 | 无 |

### 后端API

| 接口 | 功能 | 认证方式 |
|------|------|---------|
| `POST /api/auth/login` | 服务商登录 | 无 |
| `GET /api/auth/user` | 获取用户信息 | Provider JWT |
| `GET /api/admin/tenants` | 租户列表 | Provider JWT |
| `GET /api/v1/wecom/auth/verify_user` | 企微OAuth | code参数 |
| `GET /api/v1/wecom/tenant/info` | 租户工作台信息 | 企微JWT |
| `GET /api/v1/wecom/card/my` | 当前用户名片 | 企微JWT |

### 数据流程

```
┌─────────────────────────────────────────────────┐
│              服务商管理流程                       │
└─────────────────────────────────────────────────┘

访问 /login
    ↓
输入 admin/password
    ↓
POST /api/auth/login
    ↓
生成 Provider JWT Token
    ↓
跳转到 /admin
    ↓
GET /api/admin/tenants (带Token)
    ↓
显示所有租户列表和统计


┌─────────────────────────────────────────────────┐
│           租户管理员使用流程                       │
└─────────────────────────────────────────────────┘

从企微工作台打开应用
    ↓
访问 /wecom/workspace
    ↓
企微OAuth授权（自动跳转）
    ↓
回调带code参数
    ↓
GET /api/v1/wecom/auth/verify_user?code=xxx
    ↓
调用getuserinfo3rd识别企业和用户
    ↓
生成企微JWT Token (is_admin=true)
    ↓
检查权限 → 是管理员 → 留在workspace
    ↓
GET /api/v1/wecom/tenant/info
    ↓
显示编辑工作台（三栏布局）


┌─────────────────────────────────────────────────┐
│           普通用户使用流程                         │
└─────────────────────────────────────────────────┘

从企微工作台打开应用
    ↓
访问 /wecom/workspace
    ↓
OAuth认证
    ↓
生成企微JWT Token (is_admin=false)
    ↓
检查权限 → 不是管理员 → 跳转到 /wecom/card
    ↓
GET /api/v1/wecom/card/my
    ↓
显示个人名片（含分享功能）
```

---

## 🔐 权限体系

### Token类型

#### 1. Provider JWT Token（服务商）

```json
{
  "username": "admin",
  "role": "provider_admin",
  "type": "provider_admin",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**用途：**
- 访问 `/admin` 后台
- 调用 `/api/admin/*` 接口
- 查看所有租户数据

#### 2. 企微JWT Token（租户）

```json
{
  "tenant_id": 1,
  "userid": "zhangsan",
  "corp_id": "ww123456",
  "is_admin": true,
  "role": "installer",
  "in_visible_range": true,
  "exp": 1234567890,
  "iat": 1234567890
}
```

**用途：**
- 访问 `/wecom/*` 页面
- 调用 `/api/v1/wecom/*` 接口
- 根据`is_admin`判断访问权限

---

## 🗂️ 文件结构

```
/opt/qwcard/
├── app/                          # 后端Flask应用
│   ├── routes/
│   │   ├── provider_auth.py     # ✅ 服务商认证API
│   │   ├── admin.py             # ✅ 租户管理API
│   │   ├── wecom.py             # ✅ 企微OAuth和名片API
│   │   ├── card.py              # 名片相关API
│   │   ├── files.py             # 文件上传API
│   │   └── ...
│   ├── models.py                # 数据模型
│   └── main.py                  # Flask应用入口
│
├── pages/                       # 前端Nuxt页面
│   ├── login.vue                # ✅ 服务商登录页面
│   ├── admin/
│   │   ├── index.vue            # ✅ 服务商控制台
│   │   ├── tenant/...           # 租户详情页
│   │   └── ...
│   ├── wecom/
│   │   ├── workspace.vue        # ✅ 租户编辑工作台（管理员）
│   │   ├── card.vue             # ✅ 用户名片页面（普通用户）
│   │   └── install.vue          # 应用安装引导
│   └── ...
│
├── docs/                        # 文档
│   ├── 快速开始-服务商后台.md
│   ├── 服务商管理后台配置指南.md
│   ├── 企微应用配置-管理员与普通用户分离.md
│   └── 0.企微认证改造与前端优化建议.md
│
├── .env                         # 环境变量（需配置）
├── README_PROVIDER.md           # 本文件
└── ...
```

---

## ⚙️ 环境变量配置

### 必需配置

```bash
# 数据库
DATABASE_URL=mysql+pymysql://wecard:wecard123@127.0.0.1:3306/wecard

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

# 企微配置
WECOM_SUITE_ID=ww917724cb573d8629
WECOM_SUITE_SECRET=<your_secret>
WECOM_TOKEN=<your_token>
WECOM_ENCODING_AES_KEY=<your_aes_key>

# 服务商管理员配置（⚠️ 必须修改）
PROVIDER_ADMIN_USERNAME=admin
PROVIDER_ADMIN_PASSWORD_HASH=<sha256_hash>
PROVIDER_JWT_SECRET=<random_secret>
```

### 生成密码hash

```bash
python3 << 'EOF'
import hashlib
password = "your_new_password"
print(hashlib.sha256(password.encode()).hexdigest())
EOF
```

### 生成JWT密钥

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔒 安全建议

### 1. 立即修改默认密码

```bash
# 访问 https://zjemail.cn/login
# 使用 admin/admin123 登录
# 点击"修改密码"或使用API
```

### 2. 保护环境变量

```bash
chmod 600 /opt/qwcard/.env
chown root:root /opt/qwcard/.env
```

### 3. 启用HTTPS

确保Nginx配置了SSL证书：

```nginx
server {
    listen 443 ssl http2;
    server_name zjemail.cn;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ...
}
```

### 4. 定期备份

```bash
# 备份数据库
mysqldump -u wecard -p wecard > backup.sql

# 备份.env
cp .env .env.backup
```

---

## 🐛 故障排查

### 服务检查

```bash
# 后端服务
systemctl status wecard-api.service
journalctl -u wecard-api.service -f

# 前端服务（如果使用pm2）
pm2 list
pm2 logs nuxt

# 数据库
systemctl status mysql
mysql -u wecard -p -e "SELECT COUNT(*) FROM tenants;"

# Redis
redis-cli ping
```

### 常见问题

1. **无法登录服务商后台**
   - 检查密码hash是否正确
   - 查看API日志
   - 测试`curl`命令

2. **企微OAuth循环**
   - 检查suite_ticket是否正常推送
   - 查看Redis缓存
   - 检查permanent_code

3. **普通用户无法查看名片**
   - 检查用户是否在可见范围
   - 查看member表记录
   - 检查权限判断逻辑

---

## 📞 支持

- 文档位置：`/opt/qwcard/docs/`
- 日志位置：`journalctl -u wecard-api.service`
- 配置文件：`/opt/qwcard/.env`

---

**系统状态**: ✅ 可用  
**最后更新**: 2025-10-13  
**版本**: v1.0

