/**
 * 企微认证插件
 * 处理企微OAuth认证流程和token管理
 */

export default function ({ $axios, redirect, store }, inject) {
  // Token管理
  const AUTH_TOKEN_KEY = 'wecom_auth_token'
  const USER_INFO_KEY = 'wecom_user_info'

  const auth = {
    // 获取token
    getToken() {
      if (process.client) {
        return localStorage.getItem(AUTH_TOKEN_KEY)
      }
      return null
    },

    // 保存token
    setToken(token) {
      if (process.client) {
        localStorage.setItem(AUTH_TOKEN_KEY, token)
        // 设置axios默认header
        $axios.setToken(token, 'Bearer')
      }
    },

    // 获取用户信息
    getUserInfo() {
      if (process.client) {
        const info = localStorage.getItem(USER_INFO_KEY)
        return info ? JSON.parse(info) : null
      }
      return null
    },

    // 保存用户信息
    setUserInfo(userInfo) {
      if (process.client) {
        localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
      }
    },

    // 清除认证信息
    clearAuth() {
      if (process.client) {
        localStorage.removeItem(AUTH_TOKEN_KEY)
        localStorage.removeItem(USER_INFO_KEY)
        $axios.setToken(false)
      }
    },

    // 检查是否已认证
    isAuthenticated() {
      return !!this.getToken()
    },

    // 验证token有效性
    async verifyToken() {
      const token = this.getToken()
      if (!token) {
        return false
      }

      try {
        const response = await $axios.post('/api/v1/wecom/auth/verify', {}, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        return response.data.valid
      } catch (error) {
        console.error('Token verification failed:', error)
        return false
      }
    },

    // 处理OAuth回调
    async handleOAuthCallback(code, corpId) {
      try {
        const response = await $axios.get('/api/v1/wecom/oauth/callback', {
          params: { code, corp_id: corpId }
        })
        
        if (response.data.success) {
          this.setToken(response.data.token)
          this.setUserInfo(response.data.user)
          return response.data.user
        }
        
        throw new Error('OAuth callback failed')
      } catch (error) {
        console.error('OAuth callback error:', error)
        throw error
      }
    },

    // 获取OAuth授权URL
    async getAuthUrl(redirectUri) {
      try {
        const response = await $axios.get('/api/v1/wecom/oauth/authorize', {
          params: { redirect_uri: redirectUri }
        })
        return response.data.auth_url
      } catch (error) {
        console.error('Get auth URL error:', error)
        throw error
      }
    },

    // 登出
    logout() {
      this.clearAuth()
      redirect('/wecom/install')
    }
  }

  // 注入到Vue实例
  inject('wecomAuth', auth)

  // 初始化：如果有token，设置到axios
  if (process.client) {
    const token = auth.getToken()
    if (token) {
      $axios.setToken(token, 'Bearer')
    }
  }

  // Axios请求拦截器：添加token
  $axios.onRequest((config) => {
    const token = auth.getToken()
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  // Axios响应拦截器：处理401错误（智能token刷新）
  $axios.onError(async (error) => {
    const code = parseInt(error.response && error.response.status)
    
    // 如果请求配置了skipAuthRedirect，跳过自动重定向
    if (error.config?.skipAuthRedirect) {
      console.log('⚠️ 检测到401错误，但请求设置了skipAuthRedirect，不自动跳转')
      return Promise.reject(error)
    }
    
    if (code === 401) {
      console.log('⚠️ 检测到401错误，可能是token过期')
      
      // 检查是否在workspace页面
      if (process.client && window.location.pathname === '/wecom/workspace') {
        console.log('🔄 在workspace页面，尝试静默刷新token...')
        
        try {
          // 尝试重新获取token（静默OAuth）
          const authUrl = await auth.getAuthUrl(window.location.origin + '/wecom/workspace')
          console.log('🔄 静默刷新token，跳转到OAuth...')
          window.location.href = authUrl
          return Promise.reject(error)
        } catch (e) {
          console.error('❌ 静默刷新失败:', e)
        }
      }
      
      // 其他页面或刷新失败，清除认证信息并跳转
      console.log('❌ Token失效，清除认证信息')
      auth.clearAuth()
      
      if (process.client && !window.location.pathname.includes('/wecom/install')) {
        window.location.href = '/wecom/install'
      }
    }
    return Promise.reject(error)
  })
}


