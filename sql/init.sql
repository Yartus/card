-- 初始化数据库
CREATE DATABASE IF NOT EXISTS wecard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wecard;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'wecard'@'%' IDENTIFIED BY 'wecard123';
GRANT ALL PRIVILEGES ON wecard.* TO 'wecard'@'%';
FLUSH PRIVILEGES;

-- 设置时区
SET time_zone = '+08:00';
