/**
 * API 中间件
 * 处理 API 路由转发到 Flask 后端
 */

const express = require('express')
const { createProxyMiddleware } = require('http-proxy-middleware')

const app = express()

// 代理到 Flask 后端
app.use('/', createProxyMiddleware({
  target: process.env.API_BASE_URL || 'http://127.0.0.1:5001',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '' // 移除 /api 前缀
  },
  onError: (err, req, res) => {
    console.error('API Proxy Error:', err.message)
    res.status(500).json({ error: 'API服务不可用' })
  }
}))

module.exports = app
