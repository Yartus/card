/**
 * Axios 插件配置
 * 配置全局axios实例
 */

export default function ({ $axios, redirect, error }) {
  // 请求拦截器
  $axios.onRequest(config => {
    // 添加请求头
    config.headers.common['X-Requested-With'] = 'XMLHttpRequest'
    
    // 开发环境添加调试信息
    if (process.env.NODE_ENV === 'development') {
      console.log('API Request:', config.method.toUpperCase(), config.url)
    }
    
    return config
  })

  // 响应拦截器
  $axios.onResponse(response => {
    // 开发环境添加调试信息
    if (process.env.NODE_ENV === 'development') {
      console.log('API Response:', response.status, response.config.url)
    }
    
    return response
  })

  // 错误拦截器
  $axios.onError(err => {
    const code = parseInt(err.response && err.response.status)
    
    // 开发环境显示详细错误
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', code, err.response?.data || err.message)
    }
    
    // 处理特定错误码
    if (code === 401) {
      // 未授权，重定向到登录页
      redirect('/login')
    } else if (code === 403) {
      // 禁止访问
      error({ statusCode: 403, message: '访问被拒绝' })
    } else if (code === 404) {
      // 资源不存在
      error({ statusCode: 404, message: '请求的资源不存在' })
    } else if (code >= 500) {
      // 服务器错误
      error({ statusCode: code, message: '服务器内部错误' })
    }
    
    return Promise.reject(err)
  })
}
