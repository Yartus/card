# Ubuntu 服务器从零部署指南

本文档适用于在一个全新的 **Ubuntu 20.04/22.04 LTS** 服务器上，从零开始部署 WeCom SaaS Core 骨架应用。

## 1. 基础环境准备

首先更新系统软件包并安装必要的系统工具。

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python3, pip, venv, git, nginx, redis
sudo apt install -y python3-pip python3-venv git nginx redis-server build-essential libssl-dev libffi-dev python3-dev

# 启动 Redis 并设置开机自启
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 2. 数据库安装与配置

如果你使用的是云数据库（如 RDS），请跳过安装步骤，直接进行数据库创建。这里演示本地安装 MariaDB (兼容 MySQL)。

```bash
# 安装 MariaDB
sudo apt install -y mariadb-server libmysqlclient-dev

# 安全配置 (按提示设置 root 密码，移除匿名用户等)
sudo mysql_secure_installation

# 进入数据库命令行
sudo mysql -u root -p

# --- SQL 命令 ---
# 1. 创建数据库
CREATE DATABASE wecom_saas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 2. 创建用户并授权 (请修改 password 为强密码)
CREATE USER 'wecom_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON wecom_saas.* TO 'wecom_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 3. 项目代码部署

假设我们将代码部署在 `/opt/wecom-saas` 目录。

```bash
# 1. 创建目录并设置权限
sudo mkdir -p /opt/wecom-saas
sudo chown -R $USER:$USER /opt/wecom-saas

# 2. 上传代码
# 将 wecom-saas-scaffold 文件夹中的内容上传到 /opt/wecom-saas
# (可以使用 scp, git clone 或 ftp 工具)
cd /opt/wecom-saas
ls -l  # 确保能看到 requirements.txt, wsgi.py 等文件

# 3. 创建 Python 虚拟环境
python3 -m venv venv

# 4. 激活环境并安装依赖
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# 如果使用 mysql，确保安装了 mysqlclient 或 pymysql
pip install pymysql cryptography
```

## 4. 环境变量配置

复制 `.env.example` (如果不存在则新建) 为 `.env` 并修改配置。

```bash
nano .env
```

**`.env` 文件内容示例：**

```ini
# Flask 配置
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=请生成一个随机的长字符串

# 数据库配置 (注意：如果用 pymysql，驱动写 mysql+pymysql)
DATABASE_URL=mysql+pymysql://wecom_user:your_strong_password@localhost/wecom_saas

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 企业微信服务商配置 (从企微服务商后台获取)
WECOM_CORP_ID=wwxxxxxxxxxxxx
WECOM_SUITE_ID=wwxxxxxxxxxxxx
WECOM_SUITE_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
WECOM_TOKEN=xxxxxxxx
WECOM_ENCODING_AES_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 服务商管理员账号 (用于登录 /api/auth/login)
PROVIDER_ADMIN_USERNAME=admin
# 密码哈希生成方式: echo -n "你的密码" | sha256sum
PROVIDER_ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
PROVIDER_JWT_SECRET=另一个随机的长字符串
```

## 5. 数据库迁移

初始化数据库表结构。

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 初始化迁移仓库 (仅第一次需要)
flask db init

# 生成迁移脚本
flask db migrate -m "Initial migration"

# 应用迁移到数据库
flask db upgrade
```

## 6. 配置 Systemd 服务 (Gunicorn)

创建一个系统服务来管理应用进程。

```bash
sudo nano /etc/systemd/system/wecom-saas.service
```

**文件内容：**

```ini
[Unit]
Description=Gunicorn instance to serve WeCom SaaS
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/opt/wecom-saas
Environment="PATH=/opt/wecom-saas/venv/bin"
# 绑定到本地 5000 端口，4个 worker 进程
ExecStart=/opt/wecom-saas/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 wsgi:application

[Install]
WantedBy=multi-user.target
```
*注意：请根据实际情况修改 User (如 root 或 ubuntu)。*

**启动服务：**

```bash
sudo systemctl daemon-reload
sudo systemctl start wecom-saas
sudo systemctl enable wecom-saas

# 检查状态
sudo systemctl status wecom-saas
```

## 7. 配置 Nginx 反向代理

配置 Nginx 将外部流量转发到 Gunicorn，并配置 HTTPS。

```bash
sudo nano /etc/nginx/sites-available/wecom-saas
```

**文件内容：**

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 企微回调通常需要校验文件，可在此配置
    # location /WW_verify... { root /opt/wecom-saas/static; }
}
```

**启用配置：**

```bash
sudo ln -s /etc/nginx/sites-available/wecom-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**配置 HTTPS (推荐使用 Certbot):**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 8. 验证部署

1.  **检查健康检查接口**: 访问 `https://your-domain.com/healthz`，应返回 `{"status": "ok"}`。
2.  **配置企微后台**:
    *   在企业微信服务商后台，设置 **指令回调URL** 为 `https://your-domain.com/api/v1/wecom/command`。
    *   设置 **数据回调URL** 为 `https://your-domain.com/api/v1/wecom/callback`。
    *   确保 Token 和 EncodingAESKey 与 `.env` 中一致。
3.  **测试安装**: 访问安装链接 (需自行实现或查看 `app/routes/wecom.py` 中的 `/install` 逻辑生成的 URL) 进行扫码测试。

## 9. 常用维护命令

```bash
# 查看应用日志
journalctl -u wecom-saas -f

# 重启应用
sudo systemctl restart wecom-saas

# 数据库变更后迁移
flask db migrate -m "message"
flask db upgrade
```

