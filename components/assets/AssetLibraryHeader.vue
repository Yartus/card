<template>
  <header class="asset-library-header">
    <div class="header-background">
      <div class="header-overlay"></div>
    </div>
    
    <div class="header-content">
      <!-- 企业信息 -->
      <div class="company-info">
        <div class="company-logo-wrapper">
          <img 
            v-if="tenantInfo.logo" 
            :src="tenantInfo.logo" 
            :alt="tenantInfo.company_name"
            class="company-logo"
          />
          <div v-else class="company-logo-placeholder">
            {{ tenantInfo.company_name.charAt(0) }}
          </div>
        </div>
        
        <div class="company-details">
          <h1 class="company-name">{{ tenantInfo.company_name }}</h1>
          <p class="library-title">{{ libraryConfig.title || '精选素材库' }}</p>
          <p v-if="libraryConfig.description" class="library-description">
            {{ libraryConfig.description }}
          </p>
        </div>
      </div>
      
      <!-- 统计信息 -->
      <div v-if="stats && libraryConfig.show_stats" class="stats-section">
        <div class="stat-item">
          <div class="stat-value">{{ stats.total_assets }}</div>
          <div class="stat-label">素材总数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ formatNumber(stats.total_views) }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>
      
      <!-- 快速联系方式 -->
      <div class="quick-contact">
        <button 
          v-if="tenantInfo.contact_info.wechat || tenantInfo.contact_info.wechat_qr"
          @click="$emit('contact', 'wechat')" 
          class="contact-btn wechat-btn"
        >
          <i class="icon-wechat"></i>
          <span>添加企微</span>
        </button>
        
        <button 
          v-if="tenantInfo.contact_info.mobile || tenantInfo.contact_info.phone"
          @click="$emit('contact', 'phone')" 
          class="contact-btn phone-btn"
        >
          <i class="icon-phone"></i>
          <span>联系我们</span>
        </button>
        
        <button 
          @click="$emit('contact', 'more')" 
          class="contact-btn more-btn"
        >
          <i class="icon-contact"></i>
          <span>更多联系方式</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AssetLibraryHeader',
  
  props: {
    tenantInfo: {
      type: Object,
      required: true
    },
    libraryConfig: {
      type: Object,
      default: () => ({})
    },
    stats: {
      type: Object,
      default: () => ({})
    }
  },
  
  emits: ['contact'],
  
  methods: {
    formatNumber(num) {
      if (!num) return '0'
      
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k'
      }
      
      return num.toString()
    }
  }
}
</script>

<style lang="scss" scoped>
.asset-library-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  overflow: hidden;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  
  .header-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.2);
  }
}

.header-content {
  position: relative;
  z-index: 2;
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.company-info {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.company-logo-wrapper {
  flex-shrink: 0;
}

.company-logo {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  object-fit: cover;
  border: 3px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.company-logo-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.2);
}

.company-details {
  flex: 1;
}

.company-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.library-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 4px 0;
  opacity: 0.9;
}

.library-description {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
  line-height: 1.4;
}

.stats-section {
  display: flex;
  gap: 24px;
  flex-shrink: 0;
}

.stat-item {
  text-align: center;
  
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 4px;
  }
  
  .stat-label {
    font-size: 12px;
    opacity: 0.8;
  }
}

.quick-contact {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.contact-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
  }
  
  i {
    font-size: 16px;
  }
  
  &.wechat-btn:hover {
    background: rgba(7, 193, 96, 0.2);
    border-color: rgba(7, 193, 96, 0.5);
  }
  
  &.phone-btn:hover {
    background: rgba(24, 144, 255, 0.2);
    border-color: rgba(24, 144, 255, 0.5);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 24px;
  }
  
  .stats-section {
    align-self: stretch;
    justify-content: center;
  }
  
  .quick-contact {
    align-self: stretch;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 30px 16px;
  }
  
  .company-info {
    gap: 16px;
  }
  
  .company-logo,
  .company-logo-placeholder {
    width: 60px;
    height: 60px;
  }
  
  .company-logo-placeholder {
    font-size: 24px;
  }
  
  .company-name {
    font-size: 24px;
  }
  
  .library-title {
    font-size: 14px;
  }
  
  .library-description {
    font-size: 13px;
  }
  
  .stats-section {
    gap: 20px;
  }
  
  .stat-item .stat-value {
    font-size: 20px;
  }
  
  .quick-contact {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .contact-btn {
    flex: 1;
    min-width: 0;
    justify-content: center;
    padding: 8px 12px;
    font-size: 13px;
    
    span {
      display: none;
    }
    
    i {
      font-size: 18px;
    }
  }
}

@media (max-width: 480px) {
  .company-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 12px;
  }
  
  .stats-section {
    gap: 16px;
  }
  
  .contact-btn span {
    display: inline;
  }
}
</style>
