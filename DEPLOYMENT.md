# SMARTvCARD 部署指南

## 项目概述

SMARTvCARD 是一个基于 Nuxt.js 的数字名片生成器，可以创建响应式的 HTML 数字名片。项目支持静态生成和服务器端渲染两种部署方式。

## 系统要求

- Node.js 16+ 
- npm 或 yarn
- 现代浏览器支持

## 部署方式

### 方式一：静态网站托管（推荐）

这是最简单的部署方式，适合大多数场景。

#### 1. 构建项目
```bash
# 安装依赖
npm install

# 构建静态文件
npm run build
```

#### 2. 部署到静态托管服务
将 `public` 目录中的所有文件上传到以下任一服务：
- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront
- 阿里云 OSS
- 腾讯云 COS

#### 3. 配置域名（可选）
在静态托管服务中配置自定义域名。

### 方式二：Docker 容器化部署

适合需要服务器端功能的场景。

#### 1. 使用 Docker Compose（推荐）
```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 2. 单独使用 Docker
```bash
# 构建镜像
docker build -t smartvcard .

# 运行容器
docker run -d -p 3000:3000 --name smartvcard smartvcard
```

### 方式三：传统服务器部署

#### 1. 服务器环境准备
```bash
# 安装 Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

#### 2. 部署应用
```bash
# 克隆或上传项目代码
git clone <your-repo-url>
cd smartvcard

# 安装依赖
npm install

# 构建项目
npm run build

# 启动服务
npm start
```

#### 3. 使用 PM2 进程管理（推荐）
```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start npm --name "smartvcard" -- start

# 设置开机自启
pm2 startup
pm2 save
```

## 环境配置

### 环境变量
项目支持以下环境变量：

- `NODE_ENV`: 运行环境 (development/production)
- `HOST`: 服务器地址 (默认: 0.0.0.0)
- `PORT`: 端口号 (默认: 3000)

### 生产环境优化
1. 启用 Gzip 压缩
2. 配置 CDN 加速
3. 设置适当的缓存策略
4. 启用 HTTPS

## 反向代理配置

### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 监控和维护

### 健康检查
- 应用健康检查: `http://your-domain.com/health`
- 静态文件检查: 访问首页确认正常加载

### 日志管理
```bash
# Docker 容器日志
docker-compose logs -f smartvcard

# PM2 日志
pm2 logs smartvcard

# 系统日志
journalctl -u your-service-name
```

### 性能监控
建议配置以下监控：
- 服务器资源使用情况
- 应用响应时间
- 错误率统计
- 访问量统计

## 故障排除

### 常见问题

1. **构建失败**
   - 检查 Node.js 版本是否 >= 16
   - 清除 node_modules 重新安装
   - 检查网络连接

2. **端口冲突**
   - 修改 docker-compose.yml 中的端口映射
   - 或使用 `--port` 参数指定其他端口

3. **静态文件 404**
   - 确认 public 目录存在且包含构建文件
   - 检查 Web 服务器配置

4. **内存不足**
   - 增加服务器内存
   - 优化 Docker 容器资源限制

### 调试模式
```bash
# 开发模式运行
npm run dev

# 查看详细构建信息
npm run build --verbose
```

## 安全建议

1. 定期更新依赖包
2. 使用 HTTPS 加密传输
3. 配置防火墙规则
4. 定期备份数据
5. 监控异常访问

## 备份和恢复

### 备份
```bash
# 备份项目代码
tar -czf smartvcard-backup-$(date +%Y%m%d).tar.gz .

# 备份数据库（如果有）
mysqldump -u username -p database_name > backup.sql
```

### 恢复
```bash
# 解压备份文件
tar -xzf smartvcard-backup-YYYYMMDD.tar.gz

# 重新部署
npm install
npm run build
npm start
```

## 联系支持

如遇到部署问题，请：
1. 查看本文档的故障排除部分
2. 检查项目 GitHub Issues
3. 联系技术支持: ziageekbiz@gmail.com

---

**注意**: 本部署指南基于当前项目配置编写，如有更新请及时同步文档。
