<template>
  <div class="standard-grid">
    <div class="section-header">
      <h3 class="section-title">{{ title }}</h3>
      <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
    </div>
    
    <div class="grid-container" :class="gridClass">
      <div 
        v-for="(item, index) in items"
        :key="item.id || index"
        class="grid-item"
        :class="itemClass"
        @click="handleItemClick(item, index)"
      >
        <!-- 图标模式 -->
        <div v-if="displayMode === 'icon'" class="item-icon">
          <!-- Emoji 图标 -->
          <span v-if="!item.iconType || item.iconType === 'emoji'" class="icon-emoji" :style="{ color: item.color }">
            {{ item.icon }}
          </span>
          
          <!-- SVG 图标 -->
          <img
            v-else-if="item.iconType === 'svg'"
            :src="item.icon"
            :alt="item.title"
            class="icon-svg"
            :style="{ filter: item.color ? `drop-shadow(0 0 4px ${item.color})` : '' }"
          />
          
          <!-- CSS 图标 (Font Awesome) -->
          <i
            v-else-if="item.iconType === 'css'"
            :class="item.icon"
            :style="{ color: item.color }"
          ></i>
          
          <!-- Lottie 动画图标（暂不支持，降级为 Emoji） -->
          <span
            v-else-if="item.iconType === 'lottie'"
            class="icon-emoji"
            :style="{ color: item.color }"
          >
            {{ item.icon }}
          </span>
        </div>
        
        <!-- 图片模式 -->
        <div v-else-if="displayMode === 'image'" class="item-image">
          <img :src="item.image" :alt="item.title" />
          <div v-if="showOverlay" class="image-overlay">
            <i class="icon-view"></i>
          </div>
        </div>
        
        <!-- Logo模式 -->
        <div v-else-if="displayMode === 'logo'" class="item-logo">
          <img :src="item.logo" :alt="item.name" />
        </div>
        
        <!-- 内容区域 -->
        <div class="item-content">
          <h4 class="item-title">{{ item.title || item.name }}</h4>
          <p v-if="item.description" class="item-description">{{ item.description }}</p>
          <div v-if="item.tags && item.tags.length" class="item-tags">
            <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情Modal -->
    <div v-if="showDetailModal && currentItem" class="detail-modal" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeDetailModal">×</button>
        
        <!-- 图片轮播区域 -->
        <div v-if="getDetailImages(currentItem).length > 0" class="detail-images">
          <div class="image-slider">
            <img
              :src="getDetailImages(currentItem)[currentImageIndex]"
              :alt="currentItem.title"
              class="detail-image"
            />
            
            <!-- 轮播控制 -->
            <div v-if="getDetailImages(currentItem).length > 1" class="slider-controls">
              <button
                class="slider-btn prev"
                @click.stop="previousImage"
                :disabled="currentImageIndex === 0"
              >
                ‹
              </button>
              <div class="slider-indicators">
                <span
                  v-for="(img, idx) in getDetailImages(currentItem)"
                  :key="idx"
                  class="indicator"
                  :class="{ active: idx === currentImageIndex }"
                  @click.stop="currentImageIndex = idx"
                ></span>
              </div>
              <button
                class="slider-btn next"
                @click.stop="nextImage"
                :disabled="currentImageIndex === getDetailImages(currentItem).length - 1"
              >
                ›
              </button>
            </div>
          </div>
        </div>
        
        <!-- 详情信息 -->
        <div class="detail-info">
          <h2 class="detail-title">{{ currentItem.title || currentItem.name }}</h2>
          
          <!-- 标签 -->
          <div v-if="currentItem.tags && currentItem.tags.length" class="detail-tags">
            <span v-for="tag in currentItem.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          
          <!-- 完整描述 -->
          <div class="detail-description">
            <p v-if="currentItem.fullDescription || currentItem.description">
              {{ currentItem.fullDescription || currentItem.description }}
            </p>
            
            <!-- 额外内容 -->
            <div v-if="currentItem.details" class="detail-sections">
              <div
                v-for="(section, idx) in currentItem.details"
                :key="idx"
                class="detail-section"
              >
                <h4 v-if="section.title">{{ section.title }}</h4>
                <p v-if="section.content">{{ section.content }}</p>
                <ul v-if="section.list">
                  <li v-for="(listItem, li) in section.list" :key="li">{{ listItem }}</li>
                </ul>
              </div>
            </div>
          </div>
          
          <!-- 外部链接 -->
          <a
            v-if="currentItem.link"
            :href="currentItem.link"
            target="_blank"
            class="detail-link"
          >
            了解更多 →
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StandardGrid',
  
  props: {
    // 标题
    title: {
      type: String,
      required: true
    },
    // 副标题
    subtitle: {
      type: String,
      default: ''
    },
    // 数据项
    items: {
      type: Array,
      required: true,
      default: () => []
    },
    // 显示模式：icon, image, logo, text
    displayMode: {
      type: String,
      default: 'image',
      validator: value => ['icon', 'image', 'logo', 'text'].includes(value)
    },
    // 列数：2, 3
    columns: {
      type: Number,
      default: 2,
      validator: value => [2, 3].includes(value)
    },
    // 是否显示图片悬停遮罩
    showOverlay: {
      type: Boolean,
      default: true
    },
    // 是否可点击
    clickable: {
      type: Boolean,
      default: true
    },
    // 是否启用详情页功能
    enableDetail: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      showDetailModal: false,
      currentItem: null,
      currentImageIndex: 0,
      scrollPosition: 0
    }
  },
  
  computed: {
    gridClass() {
      return `grid-cols-${this.columns}`
    },
    
    itemClass() {
      return {
        'clickable': this.clickable,
        [`mode-${this.displayMode}`]: true
      }
    }
  },
  
  beforeDestroy() {
    if (this.showDetailModal) {
      this.closeDetailModal()
    }
  },
  
  methods: {
    handleItemClick(item, index) {
      if (this.clickable) {
        // 如果启用详情页且有详情内容，显示Modal
        if (this.enableDetail && this.hasDetailContent(item)) {
          this.showDetail(item)
        } else {
          // 否则触发外部点击事件
          this.$emit('item-click', { item, index })
        }
      }
    },
    
    hasDetailContent(item) {
      return (
        item.fullDescription ||
        (item.details && item.details.length > 0) ||
        (item.images && item.images.length > 0) ||
        item.link
      )
    },
    
    showDetail(item) {
      this.currentItem = item
      this.currentImageIndex = 0
      this.showDetailModal = true
      
      // 锁定背景滚动
      this.scrollPosition = window.pageYOffset
      document.body.style.overflow = 'hidden'
      document.body.style.position = 'fixed'
      document.body.style.top = `-${this.scrollPosition}px`
      document.body.style.width = '100%'
    },
    
    closeDetailModal() {
      this.showDetailModal = false
      this.currentItem = null
      this.currentImageIndex = 0
      
      // 恢复滚动
      document.body.style.removeProperty('overflow')
      document.body.style.removeProperty('position')
      document.body.style.removeProperty('top')
      document.body.style.removeProperty('width')
      window.scrollTo(0, this.scrollPosition || 0)
    },
    
    getDetailImages(item) {
      const images = []
      
      // 添加主图
      if (item.image) {
        images.push(item.image)
      }
      
      // 添加额外图片
      if (item.images && Array.isArray(item.images)) {
        images.push(...item.images)
      }
      
      return images
    },
    
    previousImage() {
      if (this.currentImageIndex > 0) {
        this.currentImageIndex--
      }
    },
    
    nextImage() {
      const images = this.getDetailImages(this.currentItem)
      if (this.currentImageIndex < images.length - 1) {
        this.currentImageIndex++
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.standard-grid {
  padding: 16px 20px;
  background: #ffffff;
  margin: 12px 16px;
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
  margin: 0 0 6px 0; /* ✅ 遵循设计规范：标题与副标题间距6px */
  line-height: 1.4;
}

.section-subtitle {
  font-size: 14px; /* ✅ 遵循设计规范：副标题14px */
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6; /* ✅ 遵循设计规范：副标题行高1.6 */
}

.grid-container {
  display: grid;
  gap: 16px;
  
  &.grid-cols-1 {
    grid-template-columns: 1fr;
  }
  
  &.grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  &.grid-cols-3 {
    grid-template-columns: repeat(3, 1fr);
  }
}

.grid-item {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &.clickable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      border-color: rgba(24, 144, 255, 0.3);
    }
    
    &:active {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
  
  // 图标模式
  &.mode-icon {
    padding: 20px 16px;
    text-align: center;
    
    .item-icon {
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .icon-emoji {
        font-size: 32px;
      }
      
      .icon-svg {
        width: 48px;
        height: 48px;
        object-fit: contain;
      }
      
      i {
        font-size: 32px;
        color: var(--primary-color, #1890FF);
      }
      
      .icon-lottie {
        width: 48px;
        height: 48px;
      }
    }
  }
  
  // 图片模式
  &.mode-image {
    .item-image {
      position: relative;
      width: 100%;
      height: 140px;
      overflow: hidden;
      background: #f5f5f5;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      .image-overlay {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        
        i {
          color: white;
          font-size: 24px;
        }
      }
      
      &:hover {
        img {
          transform: scale(1.05);
        }
        
        .image-overlay {
          opacity: 1;
        }
      }
    }
    
    .item-content {
      padding: 12px 16px;
    }
  }
  
  // Logo模式
  &.mode-logo {
    padding: 20px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    
    .item-logo {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;
      padding: 8px;
      
      img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        filter: grayscale(80%) opacity(0.8);
        transition: all 0.3s ease;
      }
    }
    
    &:hover .item-logo img {
      filter: grayscale(0%) opacity(1);
      transform: scale(1.05);
    }
  }
  
  // 纯文本模式
  &.mode-text {
    padding: 16px;
  }
}

.item-content {
  .item-title {
    font-size: 14px;
    font-weight: 600;
    color: #262626;
    margin: 0 0 6px 0;
    line-height: 1.3;
  }
  
  .item-description {
    font-size: 12px;
    color: #8c8c8c;
    line-height: 1.4;
    margin: 0 0 8px 0;
  }
  
  .item-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    
    .tag {
      display: inline-block;
      padding: 2px 6px;
      background: #f0f2f5;
      color: #595959;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 500;
    }
  }
}

// 响应式设计
@media (max-width: 480px) {
  .standard-grid {
    padding: 16px;
    margin: 12px;
  }
  
  .grid-container {
    gap: 12px;
  }
  
  .grid-item.mode-image .item-image {
    height: 120px;
  }
  
  .grid-item.mode-icon {
    padding: 16px 12px;
    
    .item-icon {
      .icon-emoji {
        font-size: 28px;
      }
      
      .icon-svg {
        width: 40px;
        height: 40px;
      }
      
      i {
        font-size: 28px;
      }
      
      .icon-lottie {
        width: 40px;
        height: 40px;
      }
    }
  }
}

/* 图标字体 */
.icon-view::before { content: "👁"; }

/* 详情Modal */
.detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease;
  overflow-y: auto;
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 800px;
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  animation: modalSlideUp 0.3s ease;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
  
  &:hover {
    background: rgba(0, 0, 0, 0.7);
    transform: rotate(90deg);
  }
}

.detail-images {
  position: relative;
  background: #000;
}

.image-slider {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9比例 */
}

.detail-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.slider-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%);
}

.slider-btn {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  color: #262626;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    background: white;
    transform: scale(1.1);
  }
  
  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
}

.slider-indicators {
  display: flex;
  gap: 8px;
  
  .indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    transition: all 0.3s ease;
    
    &.active {
      background: white;
      width: 24px;
      border-radius: 4px;
    }
    
    &:hover {
      background: rgba(255, 255, 255, 0.8);
    }
  }
}

.detail-info {
  padding: 24px;
  overflow-y: auto;
}

.detail-title {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 16px 0;
  line-height: 1.3;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
  
  .tag {
    padding: 6px 12px;
    background: linear-gradient(135deg, #f0f2ff 0%, #e6f0ff 100%);
    color: #667eea;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
  }
}

.detail-description {
  font-size: 15px;
  color: #595959;
  line-height: 1.8;
  
  p {
    margin: 0 0 16px 0;
  }
}

.detail-sections {
  margin-top: 24px;
}

.detail-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9ff;
  border-radius: 12px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  h4 {
    font-size: 16px;
    font-weight: 600;
    color: #262626;
    margin: 0 0 12px 0;
  }
  
  p {
    font-size: 14px;
    color: #595959;
    line-height: 1.6;
    margin: 0;
  }
  
  ul {
    margin: 8px 0 0 0;
    padding-left: 20px;
    
    li {
      font-size: 14px;
      color: #595959;
      line-height: 1.8;
      margin-bottom: 6px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.detail-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modalSlideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .detail-modal {
    padding: 0;
    align-items: flex-end;
  }
  
  .modal-content {
    max-width: 100%;
    max-height: 95vh;
    border-radius: 16px 16px 0 0;
  }
  
  .detail-info {
    padding: 20px 16px;
  }
  
  .detail-title {
    font-size: 20px;
  }
  
  .slider-controls {
    padding: 12px;
  }
  
  .slider-btn {
    width: 32px;
    height: 32px;
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .modal-close {
    top: 12px;
    right: 12px;
    width: 32px;
    height: 32px;
    font-size: 20px;
  }
}
</style>
