<template>
  <div class="wecom-card-view">
    <!-- 加载中 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>正在加载名片...</p>
    </div>

    <!-- 名片内容 -->
    <div v-else-if="cardData" class="card-wrapper">
      <WecardOptimized
        :card-data="cardData"
        :card-id="cardId"
        :theme="cardTheme"
        :show-options="{
          showContactDetails: true,
          showBusinessSection: true,
          showSocialLinks: true,
          showSaveButton: true
        }"
        :is-wecom-env="isWecomEnv"
        :contact-visibility="cardData.contact_visibility || {}"
        :logo-config="cardData.logo_config || {}"
        :header-background="cardData.header_background || {}"
        :show-share-panel="false"
        @track-event="handleTrackEvent"
        @analytics-event="handleAnalyticsEvent"
      />
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-card">
        <span class="error-icon">⚠️</span>
        <h3>{{ error }}</h3>
        <p v-if="errorDetail">{{ errorDetail }}</p>
        <button class="retry-btn" @click="loadCard">重试</button>
      </div>
    </div>
  </div>
</template>

<script>
import WecardOptimized from '@/components/WecardOptimized.vue'

export default {
  name: 'WecomCardView',
  
  components: {
    WecardOptimized
  },
  
  head() {
    const meta = this.shareMeta || {}
    return {
      title: meta.title || 'WeCard 数字名片',
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: meta.description || 'WeCard 数字名片'
        },
        {
          hid: 'og:title',
          property: 'og:title',
          content: meta.title || 'WeCard 数字名片'
        },
        {
          hid: 'og:description',
          property: 'og:description',
          content: meta.description || 'WeCard 数字名片'
        },
        {
          hid: 'og:image',
          property: 'og:image',
          content: meta.image || ''
        },
        {
          hid: 'og:url',
          property: 'og:url',
          content: meta.url || ''
        },
        {
          hid: 'twitter:card',
          name: 'twitter:card',
          content: 'summary_large_image'
        },
        {
          hid: 'twitter:title',
          name: 'twitter:title',
          content: meta.title || 'WeCard 数字名片'
        },
        {
          hid: 'twitter:description',
          name: 'twitter:description',
          content: meta.description || 'WeCard 数字名片'
        },
        {
          hid: 'twitter:image',
          name: 'twitter:image',
          content: meta.image || ''
        }
      ]
    }
  },
  
  data() {
    return {
      isLoading: true,
      cardData: null,
      cardId: null,
      cardTheme: 'light',
      error: null,
      errorDetail: null,
      isWecomEnv: false
    }
  },
  
  async mounted() {
    console.log('🎴 企微名片页面加载')
    
    // 检测是否在企微环境
    this.isWecomEnv = /wxwork/i.test(navigator.userAgent)
    
    // ✅ 检测OAuth授权成功回调
    const oauthSuccess = this.$route.query.oauth_success
    const tokenFromUrl = this.$route.query.token
    
    if (oauthSuccess === '1' && tokenFromUrl) {
      console.log('✅ OAuth授权成功，更新token')
      this.$wecomAuth.setToken(tokenFromUrl)
      
      // 清除URL参数
      this.$router.replace({ query: {} })
      
      // 加载名片数据
      await this.loadCard()
      return
    }
    
    // 处理OAuth认证
    const code = this.$route.query.code
    
    if (code) {
      console.log('📱 检测到OAuth code，开始验证用户身份...')
      try {
        const { data } = await this.$axios.get('/api/v1/wecom/auth/verify_user', {
          params: {
            code,
            target: 'card',
            allow_non_admin: true
          }
        })
        
        if (data.success) {
          this.$wecomAuth.setToken(data.token)
          this.$wecomAuth.setUserInfo(data.user)
          console.log('✅ 认证成功:', data.user)
          
          // 清除URL中的code参数
          this.$router.replace({ query: {} })
        } else {
          throw new Error(data.message || '认证失败')
        }
      } catch (error) {
        console.error('❌ 认证失败:', error)
        this.error = '认证失败'
        this.errorDetail = error.response?.data?.message || error.message
        this.isLoading = false
        return
      }
    }
    
    // 检查token
    if (!this.$wecomAuth.isAuthenticated()) {
      console.log('⚠️ 未检测到token，发起OAuth授权')
      if (!code) {
        await this.redirectToAuth()
        return
      }
    }
    
    // 验证token有效性
    const isValid = await this.$wecomAuth.verifyToken()
    if (!isValid) {
      console.log('⚠️ Token已失效，重新认证')
      this.$wecomAuth.clearAuth()
      await this.redirectToAuth()
      return
    }
    
    // 加载名片数据
    await this.loadCard()
  },
  
  computed: {
    shareMeta() {
      const card = this.cardData || {}
      const basic = card.basic_info || {}
      const metaTitle =
        basic.share_title ||
        (basic.name ? `${basic.name}的数字名片` : 'WeCard 数字名片')
      const metaDesc =
        basic.share_description ||
        [basic.title, basic.company].filter(Boolean).join(' · ') ||
        '一张可以互动的数字名片'
      const metaImage =
        card.share_cover ||
        basic.share_cover ||
        basic.avatar ||
        (card.header_background && card.header_background.backgroundImage) ||
        ''
      const routePath = (this.$route && this.$route.fullPath) || ''
      const baseUrl =
        process.env.APP_URL ||
        (process.client ? window.location.origin : 'https://zjemail.cn')
      return {
        title: metaTitle,
        description: metaDesc,
        image: metaImage,
        url: `${baseUrl}${routePath}`
      }
    }
  },
  
  methods: {
    async loadCard() {
      this.isLoading = true
      this.error = null
      this.errorDetail = null
      
      try {
        console.log('📋 加载用户名片数据...')
        
        // 调用后端API获取当前用户的名片数据
        const { data } = await this.$axios.get('/api/v1/wecom/card/my')
        
        // ✅ 检测是否需要OAuth授权
        if (data.need_oauth) {
          console.log('🔐 需要OAuth授权获取完整信息')
          this.showOAuthDialog(data.oauth_url, data.message)
          this.isLoading = false
          return
        }
        
        if (data.success) {
          this.cardData = data.card_data
          this.cardId = data.card_id
          this.cardTheme = data.theme || 'light'
          console.log('✅ 名片数据加载成功')
        } else {
          throw new Error(data.message || '加载名片失败')
        }
      } catch (error) {
        console.error('❌ 加载名片失败:', error)
        
        if (error.response?.status === 401) {
          // Token失效，重新认证
          this.$wecomAuth.clearAuth()
          await this.redirectToAuth()
        } else if (error.response?.status === 404) {
          this.error = '名片不存在'
          this.errorDetail = '管理员还没有为您配置名片，请联系管理员'
        } else {
          this.error = '加载名片失败'
          this.errorDetail = error.response?.data?.message || error.message
        }
      } finally {
        this.isLoading = false
      }
    },
    
    showOAuthDialog(oauthUrl, message) {
      // 使用企微JSAPI弹窗（如果可用）
      if (window.wx && window.wx.invoke) {
        wx.invoke('sendAppMessage', {
          title: '授权提醒',
          desc: message || '需要您的授权以获取完整名片信息',
          link: oauthUrl
        })
      } else {
        // 降级方案：原生confirm弹窗
        const confirmed = confirm(
          `${message || '需要您的授权以获取完整名片信息'}\n\n` +
          '为了给您提供完整的名片服务，我们需要获取以下信息：\n' +
          '• 对外显示名称\n' +
          '• 头像\n' +
          '• 手机号码\n' +
          '• 职位信息\n\n' +
          '点击"确定"进行授权（仅需授权一次）'
        )
        
        if (confirmed) {
          console.log('🔗 跳转到OAuth授权页面:', oauthUrl)
          window.location.href = oauthUrl
        } else {
          this.error = '需要授权'
          this.errorDetail = '您暂时无法查看名片，如需继续请刷新页面并同意授权'
        }
      }
    },
    
    async redirectToAuth() {
      const redirectUri = window.location.origin + this.$route.path
      const authUrl = await this.$wecomAuth.getAuthUrl(redirectUri)
      window.location.href = authUrl
    },
    
    handleTrackEvent(eventData) {
      console.log('📊 追踪事件:', eventData)
      // 可以在这里添加统计逻辑
    },
    
    handleAnalyticsEvent(eventData) {
      console.log('📈 分析事件:', eventData)
      // 可以在这里添加分析逻辑
    }
  }
}
</script>

<style lang="scss" scoped>
.wecom-card-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #ffffff;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #1890ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  p {
    margin-top: 16px;
    color: #666;
    font-size: 14px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.card-wrapper {
  max-width: 100%;
  margin: 0 auto;
  background: #ffffff;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background: #f5f5f5;
}

.error-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  
  .error-icon {
    font-size: 48px;
    display: block;
    margin-bottom: 16px;
  }
  
  h3 {
    margin: 0 0 12px 0;
    color: #262626;
    font-size: 20px;
    font-weight: 600;
  }
  
  p {
    margin: 0 0 24px 0;
    color: #8c8c8c;
    font-size: 14px;
    line-height: 1.6;
  }
  
  .retry-btn {
    padding: 10px 24px;
    background: #1890ff;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      background: #40a9ff;
    }
    
    &:active {
      background: #096dd9;
    }
  }
}
</style>

