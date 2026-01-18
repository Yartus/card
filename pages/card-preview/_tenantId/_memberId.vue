<template>
  <div class="card-preview-page">
    <!-- 加载中 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>正在加载名片...</p>
    </div>

    <!-- 卡片预览 -->
    <div v-else-if="cardData" class="preview-wrapper">
      <CardPreview
        :card-data="cardData"
        :card-url="cardUrl"
        @share="handleShare"
        @contact-me="handleContactMe"
      />
      
      <!-- 分享面板（可选） -->
      <SharePanel
        v-if="showSharePanel"
        ref="sharePanel"
        :card-id="cardId"
        :card-data="cardData"
        :is-wecom-env="isWecomEnv"
        @close="showSharePanel = false"
      />
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-card">
        <span class="error-icon">⚠️</span>
        <h3>{{ error }}</h3>
        <p v-if="errorDetail">{{ errorDetail }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import CardPreview from '@/components/card/CardPreview.vue'
import SharePanel from '@/components/card/SharePanel.vue'

export default {
  name: 'CardPreviewPage',
  
  components: {
    CardPreview,
    SharePanel
  },
  
  data() {
    return {
      isLoading: true,
      cardData: null,
      cardId: null,
      error: null,
      errorDetail: null,
      showSharePanel: false,
      isWecomEnv: false
    }
  },
  
  computed: {
    tenantId() {
      return this.$route.params.tenantId
    },
    
    memberId() {
      return this.$route.params.memberId
    },
    
    cardUrl() {
      return `/card/${this.tenantId}/${this.memberId}`
    }
  },
  
  async mounted() {
    console.log('🎴 卡片预览页面加载:', { tenantId: this.tenantId, memberId: this.memberId })
    
    // 检测是否在企微环境
    this.isWecomEnv = /wxwork/i.test(navigator.userAgent)
    
    // 加载卡片数据
    await this.loadCardData()
  },
  
  methods: {
    async loadCardData() {
      this.isLoading = true
      this.error = null
      this.errorDetail = null
      
      try {
        console.log('📋 加载卡片预览数据...')
        
        // 调用后端API获取卡片预览数据
        const { data } = await this.$axios.get(`/api/v1/wecom/card/preview/${this.tenantId}/${this.memberId}`)
        
        if (data.success) {
          this.cardData = data.card_data
          this.cardId = data.card_id
          console.log('✅ 卡片数据加载成功')
        } else {
          throw new Error(data.message || '加载卡片失败')
        }
      } catch (error) {
        console.error('❌ 加载卡片失败:', error)
        
        if (error.response?.status === 404) {
          this.error = '名片不存在'
          this.errorDetail = '该名片不存在或已被删除'
        } else {
          this.error = '加载名片失败'
          this.errorDetail = error.response?.data?.message || error.message
        }
      } finally {
        this.isLoading = false
      }
    },
    
    handleShare(shareData) {
      console.log('📤 分享名片:', shareData)
      this.showSharePanel = true
      
      // 可以在这里添加分享统计
      this.$emit('track-event', {
        event_type: 'share_card',
        event_data: {
          method: 'preview_page',
          card_url: shareData.cardUrl
        },
        card_id: this.cardId,
        timestamp: Date.now()
      })
    },
    
    handleContactMe() {
      // 跳转到完整名片页面
      this.$router.push(this.cardUrl)
    }
  }
}
</script>

<style lang="scss" scoped>
.card-preview-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top: 3px solid #fbb9b6;
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

.preview-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.error-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
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
    margin: 0;
    color: #8c8c8c;
    font-size: 14px;
    line-height: 1.6;
  }
}
</style>

