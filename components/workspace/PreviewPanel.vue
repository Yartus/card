<template>
  <div 
    :class="['preview-panel', { fullscreen }]"
    style="display: flex; flex-direction: column; height: 100%;"
  >
    <!-- 头部 -->
    <div class="preview-header">
      <h3 class="preview-title">
        <span class="icon">👁</span>
        实时预览
      </h3>
      
      <div v-if="!fullscreen" class="device-switcher">
        <button
          v-for="device in devices"
          :key="device.key"
          :class="['device-btn', { active: currentDevice === device.key }]"
          @click="currentDevice = device.key"
          :title="device.label"
        >
          <span class="icon">{{ device.icon }}</span>
        </button>
      </div>
    </div>

    <!-- 预览容器 -->
    <div 
      class="preview-body" 
      style="flex: 1; min-height: 0; overflow-y: auto !important; overflow-x: hidden;"
    >
      <div class="preview-scroll-container">
        <div 
          :class="['preview-viewport', `device-${currentDevice}`]"
          :style="viewportStyle"
        >
          <!-- 名片预览 -->
          <div class="card-preview-wrapper">
            <WecardOptimized
              v-if="previewData"
              :card-data="enhancedPreviewData"
              :card-id="'preview'"
              :theme="theme"
              :show-share-panel="false"
              :contact-visibility="contactVisibility"
              :header-background="headerBackground"
              :avatar-config="avatarConfig"
              :logo-config="logoConfig"
            />
            
            <!-- 空状态 -->
            <div v-else class="preview-empty">
              <span class="empty-icon">📱</span>
              <p>添加模块后即可预览</p>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import WecardOptimized from '@/components/WecardOptimized.vue'

export default {
  name: 'PreviewPanel',
  
  components: {
    WecardOptimized
  },
  
  props: {
    fullscreen: {
      type: Boolean,
      default: false
    },
    previewCardData: {
      type: Object,
      default: () => null
    },
    contactVisibility: {
      type: Object,
      default: () => ({
        mobile: true,
        email: true,
        wechat: true,
        phone: true,
        address: true,
        website: true
      })
    },
    headerBackground: {
      type: Object,
      default: () => ({})
    },
    logoConfig: {
      type: Object,
      default: () => ({})
    },
    avatarConfig: {
      type: Object,
      default: () => ({
        useWecomAvatar: true,
        customAvatar: '',
        wecomAvatar: ''
      })
    },
    companyInfo: {
      type: Object,
      default: () => ({
        phone: '',
        address: '',
        website: ''
      })
    }
  },
  
  data() {
    return {
      currentDevice: 'mobile',
      devices: [
        { key: 'mobile', label: '手机', icon: '📱', width: 375 },
        { key: 'tablet', label: '平板', icon: '📱', width: 768 },
        { key: 'desktop', label: '桌面', icon: '💻', width: 1024 }
      ],
      refreshKey: 0
    }
  },
  
  computed: {
    ...mapState('workspace', ['modules']),
    ...mapGetters('workspace', ['previewData', 'enabledModuleCount']),
    
    // ✅ 增强预览数据，优先展示真实名片数据，再叠加工作台配置
    enhancedPreviewData() {
      if (!this.previewData) return null

      const storePreview = this.previewData || {}
      const actualCard = this.previewCardData || {}

      const mergedBasicInfo = {
        ...(storePreview.basic_info || {}),
        ...(actualCard.basic_info || {})
      }
      if (!mergedBasicInfo.name) mergedBasicInfo.name = '张三'
      if (!mergedBasicInfo.title) mergedBasicInfo.title = '产品经理'
      if (!mergedBasicInfo.company) {
        mergedBasicInfo.company = storePreview.basic_info?.company || '示例公司'
      }
      if (!mergedBasicInfo.slogan) {
        mergedBasicInfo.slogan = storePreview.basic_info?.slogan || '以白为底，科技为线'
      }
      if (!mergedBasicInfo.avatar) {
        mergedBasicInfo.avatar = this.getDefaultAvatar()
      }
      if (!mergedBasicInfo.department) {
        mergedBasicInfo.department = storePreview.basic_info?.department || '产品部'
      }

      const mergedContactInfo = {
        ...(storePreview.contact_info || {}),
        ...(actualCard.contact_info || {})
      }

      const companyOverrides = this.companyInfo || {}
      ;['phone', 'address', 'website'].forEach((field) => {
        if (Object.prototype.hasOwnProperty.call(companyOverrides, field)) {
          mergedContactInfo[field] = companyOverrides[field]
        }
      })

      const actualCustomItems = (actualCard.contact_info && actualCard.contact_info.custom_items) 
        ? actualCard.contact_info.custom_items 
        : []

      const finalContactInfo = {
        mobile: mergedContactInfo.mobile || '',
        email: mergedContactInfo.email || '',
        wechat: mergedContactInfo.wechat || '',
        phone: mergedContactInfo.phone || '',
        address: mergedContactInfo.address || '',
        website: mergedContactInfo.website || '',
        custom_items: mergedContactInfo.custom_items || actualCustomItems
      }

      const defaultHeaderBackground = {
        backgroundType: 'svg',
        svgPattern: 'geometric',
        svgGradientStart: '#ffffff',
        svgGradientEnd: '#FC726E',
        svgDensity: 300,
        svgOpacity: 0.5
      }

      const headerBackgroundConfig = Object.keys(this.headerBackground || {}).length > 0
        ? this.headerBackground
        : (storePreview.header_background || actualCard.header_background || defaultHeaderBackground)

      const avatarConfig = Object.keys(this.avatarConfig || {}).length > 0
        ? this.avatarConfig
        : (storePreview.avatar_config || actualCard.avatar_config || {
            useWecomAvatar: true,
            customAvatar: '',
            wecomAvatar: this.getDefaultAvatar()
          })

      return {
        ...actualCard,
        ...storePreview,
        basic_info: {
          ...mergedBasicInfo
        },
        contact_info: finalContactInfo,
        modules_list: storePreview.modules_list || actualCard.modules_list || [],
        modules: storePreview.modules || actualCard.modules || {},
        header_background: headerBackgroundConfig,
        avatar_config: avatarConfig
      }
    },
    
    theme: {
      get() {
        return this.$store.state.workspace.theme
      },
      set(value) {
        this.$store.dispatch('workspace/setTheme', value)
      }
    },
    
    viewportStyle() {
      if (this.fullscreen) {
        return {}
      }
      
      const device = this.devices.find(d => d.key === this.currentDevice)
      return {
        width: `${device.width}px`,
        maxWidth: `${device.width}px`,
        minWidth: `${device.width}px`
      }
    }
  },
  
  watch: {
    // 监听模块变化，自动刷新预览
    modules: {
      handler() {
        this.debouncedRefresh()
      },
      deep: true
    },
    
    // 监听配置变化
    contactVisibility: {
      handler() {
        this.debouncedRefresh()
      },
      deep: true
    },
    
    headerBackground: {
      handler() {
        this.debouncedRefresh()
      },
      deep: true
    },
    
    logoConfig: {
      handler() {
        this.debouncedRefresh()
      },
      deep: true
    }
  },
  
  methods: {
    // ✅ 生成默认头像（使用姓名首字母）
    getDefaultAvatar() {
      const name = this.previewData?.basic_info?.name || '张三'
      const names = name.split(' ')
      if (names.length >= 2) {
        return `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect fill="#667eea" width="200" height="200"/><text x="50%" y="50%" font-size="80" fill="white" text-anchor="middle" dominant-baseline="central" font-family="Arial">${names[0].charAt(0)}${names[1].charAt(0)}</text></svg>`)}`
      }
      return `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect fill="#667eea" width="200" height="200"/><text x="50%" y="50%" font-size="80" fill="white" text-anchor="middle" dominant-baseline="central" font-family="Arial">${name.charAt(0)}</text></svg>`)}`
    },
    
    refreshPreview() {
      this.refreshKey++
      this.$toast?.success('预览已刷新')
    },
    
    debouncedRefresh: (() => {
      let timer
      return function() {
        clearTimeout(timer)
        timer = setTimeout(() => {
          this.refreshKey++
        }, 500) // 增加到500ms，减少频繁更新
      }
    })()
  }
}
</script>

<style scoped>
.preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.preview-panel.fullscreen {
  height: 100%;
}

/* 头部 */
.preview-header {
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.device-switcher {
  display: flex;
  gap: 4px;
  background: #f5f5f5;
  padding: 4px;
  border-radius: 6px;
}

.device-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #8c8c8c;
  transition: all 0.2s ease;
}

.device-btn:hover {
  background: rgba(0, 0, 0, 0.04);
}

.device-btn.active {
  background: white;
  color: #1890ff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

/* 预览主体 */
.preview-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  background: #f5f5f5;
  /* 确保滚动条可见 */
  -webkit-overflow-scrolling: touch;
}

/* 滚动容器 */
.preview-scroll-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch; /* 拉伸子元素 */
  padding: 0; /* 完全去掉padding */
}

.preview-viewport {
  width: 100%;
  background: white;
  border-radius: 20px;
  box-shadow: 
    0 0 0 6px rgba(102, 126, 234, 0.08), /* 淡紫色边框 */
    0 4px 16px rgba(0, 0, 0, 0.1); /* 阴影 */
  overflow: hidden;
  transition: all 0.3s ease;
  flex: 1; /* 占满父容器 */
  position: relative;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.preview-viewport.device-mobile {
  width: 100% !important; /* 占满容器 */
  max-width: 100% !important;
  min-width: 100% !important;
  height: 100%; /* 占满容器高度 */
  max-height: 100%;
  margin: 0; /* 去掉margin */
}

.preview-viewport.device-tablet {
  max-width: 768px;
  height: 1024px;
}

.preview-viewport.device-desktop {
  max-width: 1024px;
  height: 768px;
}

.card-preview-wrapper {
  width: 100%;
  height: 100%;
  overflow-y: auto; /* 允许内部滚动 */
  overflow-x: hidden;
  /* 美化滚动条 */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

.card-preview-wrapper::-webkit-scrollbar {
  width: 4px; /* 更细的滚动条 */
}

.card-preview-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.card-preview-wrapper::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 2px;
}

.card-preview-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* 空状态 */
.preview-empty {
  min-height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c8c8c;
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
  opacity: 0.3;
}

.preview-empty p {
  font-size: 14px;
  margin: 0;
}

/* 自定义滚动条样式 */
.preview-body::-webkit-scrollbar {
  width: 8px;
}

.preview-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.preview-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.preview-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 底部工具栏 */
.preview-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  align-items: center;
  background: #fafafa;
  flex-shrink: 0;
}

.theme-selector {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  color: #262626;
  background: white;
  cursor: pointer;
  outline: none;
  transition: all 0.2s ease;
}

.theme-selector:hover {
  border-color: #1890ff;
}

.theme-selector:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.tool-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.tool-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

/* 滚动条 */
.preview-body::-webkit-scrollbar {
  width: 6px;
}

.preview-body::-webkit-scrollbar-track {
  background: transparent;
}

.preview-body::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.preview-body::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

/* 全屏模式 */
.preview-panel.fullscreen .preview-viewport {
  max-width: 100%;
  border-radius: 0;
  box-shadow: none;
}

.preview-panel.fullscreen .preview-body {
  padding: 0;
  background: white;
}
</style>

