/**
 * 服务商后台认证插件（替代@nuxtjs/auth-next）
 * 仅用于 /admin 和 /login 路由
 */

export default ({ app, $axios }, inject) => {
  const providerAuth = {
    // 登录状态
    loggedIn: false,
    user: null,
    token: null,

    // 初始化
    init() {
      if (process.client) {
        const token = localStorage.getItem('provider_token')
        const user = localStorage.getItem('provider_user')
        
        if (token && user) {
          this.token = token
          this.user = JSON.parse(user)
          this.loggedIn = true
          
          // 设置axios默认header
          $axios.setToken(token, 'Bearer')
        }
      }
    },

    // 登录
    async login(credentials) {
      try {
        const { data } = await $axios.post('/api/auth/login', credentials)
        
        if (data.success) {
          this.token = data.access_token
          this.user = data.user
          this.loggedIn = true
          
          // 保存到localStorage
          if (process.client) {
            localStorage.setItem('provider_token', data.access_token)
            localStorage.setItem('provider_user', JSON.stringify(data.user))
          }
          
          // 设置axios默认header
          $axios.setToken(data.access_token, 'Bearer')
          
          return { success: true }
        }
        
        return { success: false, error: data.message || '登录失败' }
      } catch (error) {
        console.error('登录失败:', error)
        return { 
          success: false, 
          error: error.response?.data?.message || error.message || '登录失败'
        }
      }
    },

    // 登出
    async logout() {
      try {
        await $axios.post('/api/auth/logout')
      } catch (error) {
        console.error('登出API调用失败:', error)
      }
      
      this.token = null
      this.user = null
      this.loggedIn = false
      
      if (process.client) {
        localStorage.removeItem('provider_token')
        localStorage.removeItem('provider_user')
      }
      
      $axios.setToken(false)
      
      // 跳转到登录页
      if (process.client) {
        window.location.href = '/login'
      }
    },

    // 检查是否登录
    isLoggedIn() {
      return this.loggedIn
    },

    // 获取用户信息
    getUser() {
      return this.user
    },

    // 获取token
    getToken() {
      return this.token
    }
  }

  // 初始化
  providerAuth.init()

  // 注入到Vue实例
  inject('providerAuth', providerAuth)
  inject('auth', providerAuth)  // 兼容原有代码中的 $auth

  // 配置axios拦截器（仅针对/api/auth/*路由）
  $axios.onRequest(config => {
    // 如果是服务商API，自动添加token
    if (config.url.startsWith('/api/auth/') && providerAuth.token) {
      config.headers.Authorization = `Bearer ${providerAuth.token}`
    }
    return config
  })

  $axios.onError(error => {
    const code = parseInt(error.response && error.response.status)
    
    // 仅对/api/auth/*路由处理401错误
    if (code === 401 && error.config.url.startsWith('/api/auth/')) {
      console.log('⚠️ 服务商认证失效，跳转登录页')
      providerAuth.logout()
    }
    
    return Promise.reject(error)
  })
}

