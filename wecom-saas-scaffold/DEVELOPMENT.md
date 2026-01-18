# 开发环境快速启动指南

本文档适用于在本地电脑或开发服务器上，快速启动 WeCom SaaS Core 进行代码开发和调试。

## 1. 环境准备

确保你的开发环境已安装：
*   Python 3.8+
*   Redis (本地启动或远程连接)
*   MySQL (推荐) 或 SQLite (仅用于简单测试)

## 2. 安装与配置

```bash
# 1. 进入项目目录
cd wecom-saas-scaffold

# 2. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

## 3. 配置文件 (.env)

复制 `.env.example` 或新建 `.env` 文件。开发环境配置示例：

```ini
# === 开发模式核心配置 ===
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=1  # 开启调试模式，代码修改自动重启
SECRET_KEY=dev-key-123456

# === 数据库 ===
# 选项1: 使用 SQLite (无需安装MySQL，适合快速体验)
DATABASE_URL=sqlite:///wecard_dev.db

# 选项2: 使用 MySQL (推荐)
# DATABASE_URL=mysql+pymysql://root:password@localhost/wecom_saas_dev

# === Redis (必须) ===
REDIS_URL=redis://localhost:6379/0

# === 企微配置 (需填写真实信息以测试回调) ===
WECOM_CORP_ID=ww...
WECOM_SUITE_ID=ww...
WECOM_SUITE_SECRET=...
WECOM_TOKEN=...
WECOM_ENCODING_AES_KEY=...

# === 服务商后台账号 ===
PROVIDER_ADMIN_USERNAME=admin
# 默认密码 admin123 的 hash
PROVIDER_ADMIN_PASSWORD_HASH=a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

## 4. 初始化数据库

```bash
# 首次运行或模型修改后执行
flask db upgrade
```

## 5. 启动开发服务器

方式一（直接使用 Python）：
```bash
python3 wsgi.py
# 服务器将运行在 http://0.0.0.0:5001
```

方式二（使用 Flask CLI）：
```bash
flask run --host=0.0.0.0 --port=5001
```

## 6. 内网穿透（关键）

由于企业微信需要回调你的接口，开发环境必须配置内网穿透（将本地 5001 端口暴露给公网）。

推荐工具：`ngrok`, `frp`, 或 `cpolar`。

假设穿透后的域名为 `https://dev.your-domain.com`，请在企微服务商后台配置：
*   **指令回调 URL**: `https://dev.your-domain.com/api/v1/wecom/command`
*   **数据回调 URL**: `https://dev.your-domain.com/api/v1/wecom/callback`

## 7. 常用开发命令

*   **创建新迁移**: 修改 `models.py` 后，运行 `flask db migrate -m "备注"`
*   **应用迁移**: `flask db upgrade`
*   **查看路由**: `flask routes`

