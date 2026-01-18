<template>
  <div class="trust-credentials">
    <div class="section-header">
      <h3 class="section-title">{{ title || '信任背书' }}</h3>
    </div>
    
    <!-- 合作客户 -->
    <div v-if="clients && clients.length" class="clients-section">
      <h4 class="subsection-title">合作客户</h4>
      <div class="clients-grid" :class="`grid-cols-${clientColumns}`">
        <div 
          v-for="client in displayClients"
          :key="client.id"
          class="client-item"
          @click="handleClientClick(client)"
        >
          <div class="client-logo">
            <img :src="client.logo" :alt="client.name" />
          </div>
          <div v-if="showClientNames" class="client-name">
            {{ client.name }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 资质认证 -->
    <div v-if="displayCertifications && displayCertifications.length" class="certifications-section">
      <h4 class="subsection-title">资质认证</h4>
      
      <!-- 网格布局 -->
      <div v-if="layout === 'grid'" class="certifications-grid">
        <div 
          v-for="cert in displayCertifications"
          :key="cert.id"
          class="certification-item"
          @click="handleCertClick(cert)"
        >
          <div v-if="cert.image" class="cert-image">
            <img :src="cert.image" :alt="cert.name" />
            <div v-if="enableZoom" class="zoom-indicator">
              <i class="icon-zoom"></i>
            </div>
          </div>
          <div v-else class="cert-badge">
            <i :class="cert.icon || 'icon-certificate'"></i>
          </div>
          <div class="cert-content">
            <h5 class="cert-name">{{ cert.name }}</h5>
            <p v-if="cert.issuer" class="cert-issuer">{{ cert.issuer }}</p>
            <p v-if="showDate && cert.date" class="cert-date">{{ cert.date }}</p>
          </div>
        </div>
      </div>
      
      <!-- 轮播布局（证书墙左右滑动） -->
      <div v-else class="certifications-carousel">
        <!-- 左箭头 -->
        <button 
          v-if="displayCertifications.length > 2"
          class="carousel-nav carousel-nav-left"
          :class="{ disabled: !canScrollLeft }"
          @click="scrollCarousel('left')"
          aria-label="向左滚动"
        >
          <i class="icon-arrow">‹</i>
        </button>
        
        <!-- 证书轨道 -->
        <div class="carousel-track" ref="carouselTrack" @scroll="handleCarouselScroll">
          <div 
            v-for="cert in displayCertifications"
            :key="cert.id"
            class="carousel-item"
            @click="handleCertClick(cert)"
          >
            <div class="carousel-card">
              <div v-if="cert.image" class="carousel-image">
                <img :src="cert.image" :alt="cert.name" />
                <div v-if="enableZoom" class="zoom-indicator">
                  <i class="icon-zoom">🔍</i>
                </div>
              </div>
              <div v-else class="carousel-badge">
                <i :class="cert.icon || 'icon-certificate'">🏆</i>
              </div>
              <div class="carousel-info">
                <h5 class="carousel-title">{{ cert.name }}</h5>
                <p v-if="cert.issuer" class="carousel-issuer">{{ cert.issuer }}</p>
                <p v-if="showDate && cert.date" class="carousel-date">{{ cert.date }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右箭头 -->
        <button 
          v-if="displayCertifications.length > 2"
          class="carousel-nav carousel-nav-right"
          :class="{ disabled: !canScrollRight }"
          @click="scrollCarousel('right')"
          aria-label="向右滚动"
        >
          <i class="icon-arrow">›</i>
        </button>
      </div>
    </div>
    
    <!-- 荣誉奖项 -->
    <div v-if="awards && awards.length" class="awards-section" :class="{ 'has-header': !title }">
      <h4 class="subsection-title">荣誉奖项</h4>
      <div class="awards-grid">
        <div 
          v-for="award in awards"
          :key="award.id"
          class="award-item"
          @click="enableZoom ? showImagePreview(award.image, award.name) : handleAwardClick(award)"
        >
          <div class="award-image">
            <img :src="award.image" :alt="award.name" />
            <div v-if="enableZoom" class="zoom-indicator">
              <i class="icon-zoom"></i>
            </div>
          </div>
          <div class="award-content">
            <h5 class="award-name">{{ award.name }}</h5>
            <p v-if="award.organization" class="award-org">{{ award.organization }}</p>
            <p v-if="award.year" class="award-year">{{ award.year }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图片放大预览Modal -->
    <div v-if="showPreview" class="image-preview-modal" @click="closePreview">
      <div class="preview-content" @click.stop>
        <button class="preview-close" @click="closePreview">×</button>
        <img :src="previewImage" :alt="previewTitle" class="preview-image" />
        <div v-if="previewTitle" class="preview-title">{{ previewTitle }}</div>
      </div>
    </div>
    
    <!-- 数据统计 -->
    <div v-if="statistics && statistics.length" class="statistics-section">
      <h4 class="subsection-title">实力数据</h4>
      <div class="statistics-grid">
        <div 
          v-for="stat in statistics"
          :key="stat.id"
          class="statistic-item"
        >
          <div class="stat-number">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div v-if="stat.unit" class="stat-unit">{{ stat.unit }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrustCredentials',
  
  props: {
    title: {
      type: String,
      default: '信任背书'
    },
    // 合作客户
    clients: {
      type: Array,
      default: () => []
    },
    // 客户展示列数
    clientColumns: {
      type: Number,
      default: 3,
      validator: value => [2, 3, 4, 5, 6].includes(value)
    },
    // 是否显示客户名称
    showClientNames: {
      type: Boolean,
      default: false
    },
    // 最大显示客户数量
    maxClients: {
      type: Number,
      default: 12
    },
    // 资质认证（保持向后兼容）
    certifications: {
      type: Array,
      default: () => []
    },
    // 资质证书（新字段名，与配置组件统一）
    credentials: {
      type: Array,
      default: () => []
    },
    // 荣誉奖项
    awards: {
      type: Array,
      default: () => []
    },
    // 数据统计
    statistics: {
      type: Array,
      default: () => []
    },
    // 是否启用图片放大预览
    enableZoom: {
      type: Boolean,
      default: true
    },
    // 布局样式
    layout: {
      type: String,
      default: 'grid',
      validator: value => ['grid', 'carousel'].includes(value)
    },
    // 是否显示获得时间
    showDate: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      showPreview: false,
      previewImage: '',
      previewTitle: '',
      scrollPosition: 0,
      canScrollLeft: false,
      canScrollRight: true
    }
  },
  
  computed: {
    displayClients() {
      return this.clients.slice(0, this.maxClients)
    },
    
    // 合并 credentials 和 certifications，优先使用 credentials
    // 同时统一字段名映射：title -> name, image -> image, issuer -> issuer, date -> date
    displayCertifications() {
      const items = this.credentials.length > 0 ? this.credentials : this.certifications
      
      // 字段名映射：配置组件使用 title/image/issuer/date，渲染组件使用 name/image/issuer/date
      return items.map(item => ({
        id: item.id,
        name: item.title || item.name, // 支持 title 或 name
        image: item.image,
        issuer: item.issuer,
        date: item.date,
        icon: item.icon
      }))
    }
  },
  
  methods: {
    handleClientClick(client) {
      this.$emit('client-click', client)
    },
    
    handleCertClick(cert) {
      if (this.enableZoom && cert.image) {
        this.showImagePreview(cert.image, cert.name)
      } else {
        this.$emit('certification-click', cert)
      }
    },
    
    handleAwardClick(award) {
      this.$emit('award-click', award)
    },
    
    showImagePreview(image, title) {
      this.previewImage = image
      this.previewTitle = title
      this.showPreview = true
      
      // 锁定背景滚动
      this.scrollPosition = window.pageYOffset
      document.body.style.overflow = 'hidden'
      document.body.style.position = 'fixed'
      document.body.style.top = `-${this.scrollPosition}px`
      document.body.style.width = '100%'
    },
    
    closePreview() {
      this.showPreview = false
      
      // 恢复背景滚动
      document.body.style.removeProperty('overflow')
      document.body.style.removeProperty('position')
      document.body.style.removeProperty('top')
      document.body.style.removeProperty('width')
      window.scrollTo(0, this.scrollPosition || 0)
    },
    
    // 轮播滚动控制
    scrollCarousel(direction) {
      const track = this.$refs.carouselTrack
      if (!track) return
      
      const scrollAmount = 300 // 每次滚动300px
      const currentScroll = track.scrollLeft
      
      if (direction === 'left') {
        track.scrollTo({
          left: currentScroll - scrollAmount,
          behavior: 'smooth'
        })
      } else {
        track.scrollTo({
          left: currentScroll + scrollAmount,
          behavior: 'smooth'
        })
      }
    },
    
    // 处理轮播滚动事件，更新箭头状态
    handleCarouselScroll() {
      const track = this.$refs.carouselTrack
      if (!track) return
      
      const { scrollLeft, scrollWidth, clientWidth } = track
      
      this.canScrollLeft = scrollLeft > 10
      this.canScrollRight = scrollLeft < scrollWidth - clientWidth - 10
    }
  },
  
  mounted() {
    // 初始化轮播箭头状态
    this.$nextTick(() => {
      this.handleCarouselScroll()
    })
  },
  
  beforeDestroy() {
    // 组件销毁时恢复滚动
    if (this.showPreview) {
      this.closePreview()
    }
  }
}
</script>

<style lang="scss" scoped>
.trust-credentials {
  padding: 0; /* ✅ 内容区域padding由内部元素控制 */
  background: #ffffff;
  margin: 12px 16px; /* ✅ 遵循设计规范：外边距12px 16px */
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,.08);
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}

.section-header {
  padding: 20px 20px 16px 20px; /* ✅ 遵循设计规范：统一内边距 */
  border-bottom: 1px solid #f0f2f5;
  margin-bottom: 0; /* padding已包含间距 */
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.subsection-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

/* 合作客户样式 - 参考图片中的Logo展示 */
.clients-section {
  padding: 20px; /* ✅ 遵循设计规范：内容区域统一内边距20px */
  margin-bottom: 0;
  
  &:last-child {
    padding-bottom: 20px; /* 最后一个section保持底部padding */
  }
}

.clients-grid {
  display: grid;
  gap: 12px;
  
  &.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  &.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  &.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
  &.grid-cols-5 { grid-template-columns: repeat(5, 1fr); }
  &.grid-cols-6 { grid-template-columns: repeat(6, 1fr); }
}

.client-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
  
  &:hover {
    border-color: var(--primary-color, #1890FF);
    background: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
}

.client-logo {
  width: 60px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
  
  img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    filter: grayscale(70%);
    transition: filter 0.3s ease;
  }
}

.client-item:hover .client-logo img {
  filter: grayscale(0%);
}

.client-name {
  font-size: 11px;
  color: #8c8c8c;
  text-align: center;
  line-height: 1.2;
}

/* 资质认证样式 */
.certifications-section {
  padding: 0 20px 20px 20px; /* ✅ 遵循设计规范：内容区域统一内边距，顶部由section-header控制 */
  margin-bottom: 0;
  
  &:last-child {
    padding-bottom: 20px; /* 最后一个section保持底部padding */
  }
}

.certifications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.certification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  background: #ffffff;
  
  /* 毛玻璃背景层（渐进增强） */
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 8px;
    z-index: 0;
  }
  
  /* 动态光斑（桌面端） */
  &::after {
    content: '';
    position: absolute;
    width: 120px;
    height: 120px;
    background: radial-gradient(
      circle,
      rgba(102, 126, 234, 0.4) 0%,
      rgba(118, 75, 162, 0.3) 50%,
      transparent 70%
    );
    border-radius: 50%;
    filter: blur(15px);
    animation: blob-float 8s ease-in-out infinite;
    will-change: transform;
    z-index: 1;
    opacity: 0.6;
  }
  
  /* 内容在最上层 */
  > * {
    position: relative;
    z-index: 2;
  }
  
  &:hover {
    border-color: transparent;
    box-shadow: 
      0 4px 16px rgba(102, 126, 234, 0.15),
      0 0 0 1px rgba(102, 126, 234, 0.2);
    transform: translateY(-4px);
    
    .zoom-indicator {
      opacity: 1;
    }
  }
}

/* 动态光斑动画 */
@keyframes blob-float {
  0%, 100% { 
    transform: translate(10px, 10px);
  }
  25% { 
    transform: translate(80px, 15px);
  }
  50% { 
    transform: translate(70px, 50px);
  }
  75% { 
    transform: translate(15px, 45px);
  }
}

/* backdrop-filter 降级方案 */
@supports not (backdrop-filter: blur(20px)) {
  .certification-item::before {
    background: rgba(248, 249, 252, 0.98);
  }
}

.cert-image {
  position: relative;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  overflow: hidden;
  background: #f8f9fa;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.06);
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 12px;
  }
  
  .zoom-indicator {
    position: absolute;
    top: 2px;
    right: 2px;
    width: 16px;
    height: 16px;
    background: rgba(0, 0, 0, 0.6);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    
    i {
      font-size: 10px;
      color: white;
    }
  }
}

.cert-badge {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(82, 196, 26, 0.1);
  border-radius: 8px;
  
  i {
    font-size: 20px;
    color: #52c41a;
  }
}

.cert-content {
  flex: 1;
  min-width: 0;
}

.cert-name {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 2px 0;
  line-height: 1.4;
}

.cert-issuer {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0 0 2px 0;
  line-height: 1.4;
}

.cert-date {
  font-size: 10px;
  color: #bfbfbf;
  margin: 0;
}

/* 轮播布局样式 */
.certifications-carousel {
  position: relative;
  overflow: hidden;
  /* 移除负边距，避免内容溢出容器边界，保持呼吸感 */
  margin: 0;
  padding: 0;
}

/* 轮播导航箭头 */
.carousel-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  
  .icon-arrow {
    font-size: 24px;
    font-weight: bold;
    color: #595959;
    font-style: normal;
    line-height: 1;
  }
  
  &:hover:not(.disabled) {
    background: var(--primary-color, #1890FF);
    border-color: var(--primary-color, #1890FF);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
    
    .icon-arrow {
      color: white;
    }
  }
  
  &:active:not(.disabled) {
    transform: translateY(-50%) scale(0.95);
  }
  
  &.disabled {
    opacity: 0.3;
    cursor: not-allowed;
    background: #f5f5f5;
  }
}

.carousel-nav-left {
  left: 8px;
}

.carousel-nav-right {
  right: 8px;
}

.carousel-track {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  padding: 8px 0;
  
  /* 隐藏滚动条 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE 10+ */
  
  &::-webkit-scrollbar {
    display: none; /* Chrome/Safari/Opera */
  }
}

.carousel-item {
  flex: 0 0 280px;
  max-width: 280px;
}

.carousel-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  
  /* 毛玻璃背景层（渐进增强） */
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 12px;
    z-index: 0;
  }
  
  /* 动态光斑（桌面端） */
  &::after {
    content: '';
    position: absolute;
    width: 160px;
    height: 160px;
    background: radial-gradient(
      circle,
      rgba(102, 126, 234, 0.35) 0%,
      rgba(118, 75, 162, 0.25) 50%,
      transparent 70%
    );
    border-radius: 50%;
    filter: blur(18px);
    animation: blob-float-carousel 10s ease-in-out infinite;
    will-change: transform;
    z-index: 1;
    opacity: 0.5;
  }
  
  /* 内容在最上层 */
  > * {
    position: relative;
    z-index: 2;
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 
      0 8px 24px rgba(102, 126, 234, 0.18),
      0 0 0 1px rgba(102, 126, 234, 0.15);
    
    .zoom-indicator {
      opacity: 1;
    }
  }
  
  &:active {
    transform: translateY(-2px);
  }
}

/* 轮播卡片动态光斑动画（更大范围） */
@keyframes blob-float-carousel {
  0%, 100% { 
    transform: translate(20px, 20px);
  }
  25% { 
    transform: translate(140px, 30px);
  }
  50% { 
    transform: translate(120px, 120px);
  }
  75% { 
    transform: translate(30px, 110px);
  }
}

.carousel-image {
  position: relative;
  width: 100%;
  min-height: 180px;
  max-height: 280px;
  background: #f8f9fa;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  
  img {
    width: 100%;
    height: auto;
    max-height: 280px;
    object-fit: contain;
    border-radius: 12px;
    box-shadow: 
      0 2px 8px rgba(0, 0, 0, 0.08),
      0 0 0 1px rgba(255, 255, 255, 0.8);
    background: #ffffff;
  }
  
  .zoom-indicator {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 32px;
    height: 32px;
    background: rgba(0, 0, 0, 0.6);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    
    i {
      font-size: 16px;
      color: white;
    }
  }
}

.carousel-badge {
  width: 100%;
  aspect-ratio: 4/3;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.1) 0%, rgba(82, 196, 26, 0.05) 100%);
  
  i {
    font-size: 64px;
    color: #52c41a;
  }
}

.carousel-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.carousel-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-align: center;
}

.carousel-issuer {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0 0 4px 0;
  line-height: 1.4;
  text-align: center;
}

.carousel-date {
  font-size: 12px;
  color: #bfbfbf;
  margin: 0;
  text-align: center;
}

/* 荣誉奖项样式 */
.awards-section {
  padding: 0 20px 20px 20px; /* ✅ 遵循设计规范：内容区域统一内边距 */
  margin-bottom: 0;
  
  &.has-header {
    padding-top: 20px; /* 如果没有主标题，则添加顶部padding */
  }
  
  &:last-child {
    padding-bottom: 20px; /* 最后一个section保持底部padding */
  }
}

.awards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.award-item {
  text-align: center;
  padding: 16px 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--primary-color, #1890FF);
    background: #fafbfc;
    transform: translateY(-2px);
  }
}

.award-image {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 12px;
  border-radius: 12px;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    cursor: pointer;
    border-radius: 12px;
  }
}

.award-name {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
  line-height: 1.4;
}

.award-org {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0 0 2px 0;
  line-height: 1.4;
}

.award-year {
  font-size: 10px;
  color: #bfbfbf;
  margin: 0;
}

/* 数据统计样式 */
.statistics-section {
  padding: 0 20px 20px 20px; /* ✅ 遵循设计规范：内容区域统一内边距 */
  margin-bottom: 0;
  
  &:last-child {
    padding-bottom: 20px; /* 最后一个section保持底部padding */
  }
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 16px;
}

.statistic-item {
  text-align: center;
  padding: 16px 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  background: linear-gradient(135deg, #fafbfc 0%, #f0f2f5 100%);
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color, #1890FF);
  margin-bottom: 4px;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #595959;
  font-weight: 500;
  margin-bottom: 2px;
}

.stat-unit {
  font-size: 10px;
  color: #8c8c8c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .clients-grid {
    &.grid-cols-5,
    &.grid-cols-6 {
      grid-template-columns: repeat(3, 1fr);
    }
    &.grid-cols-4 {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  .certifications-grid {
    grid-template-columns: 1fr;
  }
  
  .carousel-item {
    flex: 0 0 240px;
    max-width: 240px;
  }
  
  /* 平板端隐藏箭头，使用触摸滑动 */
  .carousel-nav {
    display: none;
  }
  
  .awards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .carousel-item {
    flex: 0 0 220px;
    max-width: 220px;
  }
  
  .carousel-title {
    font-size: 13px;
  }
  
  .carousel-issuer {
    font-size: 11px;
  }
  
  .carousel-date {
    font-size: 11px;
  }
  
  .subsection-title {
    font-size: 13px;
  }
  
  .carousel-image {
    min-height: 160px;
    max-height: 240px;
    
    img {
      max-height: 240px;
    }
  }
  
  .trust-credentials {
    padding: 16px;
    margin: 12px;
  }
  
  .clients-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .client-logo {
    width: 50px;
    height: 35px;
  }
  
  .awards-grid {
    grid-template-columns: 1fr;
  }
  
  .statistics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-number {
    font-size: 20px;
  }
  
  /* 🎯 移动端性能优化：禁用动态光斑动画 */
  .certification-item::after,
  .carousel-card::after {
    animation: none;  /* 静态光斑，节省性能 */
    opacity: 0.3;     /* 降低透明度 */
  }
}

/* 放大提示图标 */
.zoom-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  
  .icon-zoom {
    color: white;
    font-size: 14px;
  }
}

.award-item:hover .zoom-indicator {
  opacity: 1;
}

/* 图片预览Modal */
.image-preview-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.preview-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: zoomIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes zoomIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.preview-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: rotate(90deg);
  }
}

.preview-image {
  max-width: 100%;
  max-height: calc(90vh - 60px);
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.preview-title {
  margin-top: 16px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  max-width: 80%;
  text-align: center;
}

/* 图标字体 */
.icon-certificate::before { content: "🏆"; }
.icon-zoom::before { content: "🔍"; }
</style>
