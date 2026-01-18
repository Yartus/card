<template>
  <div class="asset-library-page">
    <!-- 页面头部 -->
    <AssetLibraryHeader 
      :tenant-info="tenantInfo"
      :library-config="libraryConfig"
      :stats="libraryStats"
      @contact="handleContact"
    />
    
    <!-- 筛选和搜索栏 -->
    <AssetFilters
      v-model:type="selectedType"
      v-model:category="selectedCategory"
      v-model:search="searchQuery"
      :asset-types="assetTypes"
      :categories="categories"
      :loading="loading"
      @filter-change="handleFilterChange"
    />
    
    <!-- 素材网格 -->
    <AssetGrid
      :assets="assets"
      :loading="loading"
      :has-more="pagination.has_next"
      @asset-click="handleAssetClick"
      @load-more="loadMoreAssets"
    />
    
    <!-- 素材详情模态框 -->
    <AssetModal
      v-if="selectedAsset"
      :asset="selectedAsset"
      :tenant-info="tenantInfo"
      @close="selectedAsset = null"
      @share="handleShare"
      @download="handleDownload"
    />
    
    <!-- 联系方式模态框 -->
    <ContactModal
      v-if="showContactModal"
      :contact-info="tenantInfo.contact_info"
      :tenant-info="tenantInfo"
      @close="showContactModal = false"
    />
    
    <!-- 加载状态 -->
    <div v-if="loading && assets.length === 0" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载素材...</p>
    </div>
    
    <!-- 空状态 -->
    <div v-if="!loading && assets.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h3>暂无素材</h3>
      <p>该企业还没有上传任何素材</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button @click="retryLoad" class="retry-btn">重试</button>
    </div>
  </div>
</template>

<script>
import AssetLibraryHeader from '~/components/assets/AssetLibraryHeader.vue'
import AssetFilters from '~/components/assets/AssetFilters.vue'
import AssetGrid from '~/components/assets/AssetGrid.vue'
import AssetModal from '~/components/assets/AssetModal.vue'
import ContactModal from '~/components/assets/ContactModal.vue'

export default {
  name: 'AssetLibraryPage',
  
  components: {
    AssetLibraryHeader,
    AssetFilters,
    AssetGrid,
    AssetModal,
    ContactModal
  },
  
  async asyncData({ params, $axios, error, query }) {
    try {
      const tenantId = params.tenant_id
      
      // 获取素材库数据
      const { data } = await $axios.get(`/api/public/assets/${tenantId}`, {
        params: {
          page: 1,
          limit: 12,
          type: query.type || '',
          category: query.category || '',
          search: query.search || '',
          sort: query.sort || 'created_at'
        }
      })
      
      return {
        tenantId,
        tenantInfo: data.tenant_info,
        assets: data.assets,
        categories: data.categories,
        pagination: data.pagination,
        libraryStats: data.stats,
        libraryConfig: data.tenant_info.library_config || {}
      }
    } catch (err) {
      console.error('Error loading asset library:', err)
      
      if (err.response?.status === 404) {
        error({ statusCode: 404, message: '素材库不存在或已关闭' })
      } else {
        error({ statusCode: 500, message: '服务器错误，请稍后重试' })
      }
    }
  },
  
  data() {
    return {
      selectedType: this.$route.query.type || '',
      selectedCategory: parseInt(this.$route.query.category) || '',
      searchQuery: this.$route.query.search || '',
      selectedAsset: null,
      showContactModal: false,
      loading: false,
      error: null,
      currentPage: 1,
      assetTypes: {
        '': '全部类型',
        'document': '文档资料',
        'image': '图片素材',
        'video': '视频内容',
        'link': '链接资源',
        'presentation': '演示文稿'
      }
    }
  },
  
  head() {
    const seoConfig = this.libraryConfig.seo_config || {}
    const title = seoConfig.title_template?.replace('{company_name}', this.tenantInfo.company_name) || 
                  `${this.tenantInfo.company_name} - 精选素材库`
    const description = seoConfig.description_template?.replace('{company_name}', this.tenantInfo.company_name) ||
                       `${this.tenantInfo.company_name}的官方素材库，包含产品介绍、解决方案、案例展示等精选内容。`
    
    return {
      title,
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: description
        },
        {
          hid: 'keywords',
          name: 'keywords',
          content: seoConfig.keywords || '企业素材,产品介绍,解决方案,案例展示'
        },
        // Open Graph
        {
          hid: 'og:title',
          property: 'og:title',
          content: title
        },
        {
          hid: 'og:description',
          property: 'og:description',
          content: description
        },
        {
          hid: 'og:image',
          property: 'og:image',
          content: seoConfig.og_image || this.tenantInfo.logo
        },
        {
          hid: 'og:url',
          property: 'og:url',
          content: `${process.env.BASE_URL}/assets/${this.tenantId}`
        },
        {
          hid: 'og:type',
          property: 'og:type',
          content: 'website'
        },
        // Twitter Card
        {
          hid: 'twitter:card',
          name: 'twitter:card',
          content: 'summary_large_image'
        },
        {
          hid: 'twitter:title',
          name: 'twitter:title',
          content: title
        },
        {
          hid: 'twitter:description',
          name: 'twitter:description',
          content: description
        },
        {
          hid: 'twitter:image',
          name: 'twitter:image',
          content: seoConfig.og_image || this.tenantInfo.logo
        }
      ],
      link: [
        {
          rel: 'canonical',
          href: `${process.env.BASE_URL}/assets/${this.tenantId}`
        }
      ]
    }
  },
  
  watch: {
    '$route.query': {
      handler(newQuery) {
        this.selectedType = newQuery.type || ''
        this.selectedCategory = parseInt(newQuery.category) || ''
        this.searchQuery = newQuery.search || ''
        this.handleFilterChange()
      },
      deep: true
    }
  },
  
  mounted() {
    // 记录页面访问
    this.trackPageView()
    
    // 设置页面主题色
    this.setPageTheme()
  },
  
  methods: {
    async handleFilterChange() {
      this.loading = true
      this.error = null
      this.currentPage = 1
      
      try {
        // 更新URL查询参数
        const query = {}
        if (this.selectedType) query.type = this.selectedType
        if (this.selectedCategory) query.category = this.selectedCategory
        if (this.searchQuery) query.search = this.searchQuery
        
        await this.$router.replace({ query })
        
        // 获取筛选后的数据
        const { data } = await this.$axios.get(`/api/public/assets/${this.tenantId}`, {
          params: {
            page: 1,
            limit: 12,
            type: this.selectedType,
            category: this.selectedCategory,
            search: this.searchQuery,
            sort: 'created_at'
          }
        })
        
        this.assets = data.assets
        this.pagination = data.pagination
        
      } catch (error) {
        console.error('筛选失败:', error)
        this.error = '筛选失败，请重试'
      } finally {
        this.loading = false
      }
    },
    
    async loadMoreAssets() {
      if (!this.pagination.has_next || this.loading) return
      
      this.loading = true
      
      try {
        const nextPage = this.currentPage + 1
        const { data } = await this.$axios.get(`/api/public/assets/${this.tenantId}`, {
          params: {
            page: nextPage,
            limit: 12,
            type: this.selectedType,
            category: this.selectedCategory,
            search: this.searchQuery,
            sort: 'created_at'
          }
        })
        
        this.assets.push(...data.assets)
        this.pagination = data.pagination
        this.currentPage = nextPage
        
      } catch (error) {
        console.error('加载更多失败:', error)
        this.$toast.error('加载更多失败')
      } finally {
        this.loading = false
      }
    },
    
    handleAssetClick(asset) {
      this.selectedAsset = asset
      
      // 记录点击统计
      this.trackAssetInteraction(asset.id, 'view')
    },
    
    handleContact(type) {
      if (type === 'wechat') {
        this.showWechatContact()
      } else if (type === 'phone') {
        this.makePhoneCall()
      } else {
        this.showContactModal = true
      }
    },
    
    async handleShare(asset) {
      const shareData = {
        title: asset.title,
        text: asset.summary,
        url: typeof window !== 'undefined' ? `${window.location.origin}/assets/${this.tenantId}#asset-${asset.id}` : ''
      }
      
      try {
        if (navigator.share) {
          await navigator.share(shareData)
          // 记录分享统计
          this.trackAssetInteraction(asset.id, 'share')
          this.$toast.success('分享成功')
        } else {
          // 降级到复制链接
          await this.copyToClipboard(shareData.url)
          this.trackAssetInteraction(asset.id, 'share')
          this.$toast.success('链接已复制到剪贴板')
        }
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('分享失败:', error)
          this.$toast.error('分享失败')
        }
      }
    },
    
    handleDownload(asset) {
      if (asset.content_url) {
        if (typeof window !== 'undefined') window.open(asset.content_url, '_blank')
        this.trackAssetInteraction(asset.id, 'download')
      }
    },
    
    showWechatContact() {
      const contactInfo = this.tenantInfo.contact_info
      if (contactInfo.wechat) {
        // 复制微信号
        this.copyToClipboard(contactInfo.wechat)
        this.$toast.success('微信号已复制，请在微信中添加好友')
      } else if (contactInfo.wechat_qr) {
        // 显示微信二维码
        this.showWechatQR(contactInfo.wechat_qr)
      } else {
        this.$toast.info('暂未提供微信联系方式')
      }
    },
    
    makePhoneCall() {
      const contactInfo = this.tenantInfo.contact_info
      const phone = contactInfo.mobile || contactInfo.phone
      
      if (phone) {
        if (typeof window !== 'undefined') window.location.href = `tel:${phone}`
      } else {
        this.$toast.info('暂未提供电话联系方式')
      }
    },
    
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text)
      } catch (error) {
        // 降级方案
        const textArea = document.createElement('textarea')
        textArea.value = text
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
      }
    },
    
    trackPageView() {
      // 记录页面访问统计
      this.$axios.post('/api/analytics/page-view', {
        page_type: 'asset_library',
        tenant_id: this.tenantId,
        referrer: document.referrer,
        user_agent: navigator.userAgent
      }).catch(console.error)
    },
    
    trackAssetInteraction(assetId, actionType) {
      // 记录素材交互统计
      this.$axios.post(`/api/public/assets/${assetId}/track`, {
        action_type: actionType,
        referrer: document.referrer,
        user_agent: navigator.userAgent
      }).catch(console.error)
    },
    
    setPageTheme() {
      // 设置页面主题色
      const themeConfig = this.libraryConfig.theme_config || {}
      const primaryColor = themeConfig.primary_color || '#1890FF'
      
      document.documentElement.style.setProperty('--library-primary-color', primaryColor)
    },
    
    retryLoad() {
      this.error = null
      this.handleFilterChange()
    }
  }
}
</script>

<style lang="scss" scoped>
.asset-library-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--library-primary-color, #1890FF);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }
  
  p {
    color: #8c8c8c;
    font-size: 14px;
  }
}

.empty-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  
  .empty-icon, .error-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  h3 {
    font-size: 18px;
    color: #262626;
    margin: 0 0 8px 0;
  }
  
  p {
    color: #8c8c8c;
    font-size: 14px;
    margin: 0 0 20px 0;
  }
  
  .retry-btn {
    padding: 8px 16px;
    background: var(--library-primary-color, #1890FF);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    
    &:hover {
      opacity: 0.9;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 响应式设计
@media (max-width: 768px) {
  .asset-library-page {
    background: #ffffff;
  }
  
  .loading-container,
  .empty-state,
  .error-state {
    padding: 40px 16px;
  }
}
</style>
