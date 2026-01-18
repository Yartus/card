<template>
  <div class="business-showcase">
    <div class="section-header">
      <h3 class="section-title">业务展示</h3>
    </div>
    
    <!-- 公司介绍 -->
    <div v-if="businessData.company_intro" class="company-intro">
      <h4>公司简介</h4>
      <p>{{ businessData.company_intro }}</p>
    </div>
    
    <!-- 个人介绍 -->
    <div v-if="businessData.personal_intro" class="personal-intro">
      <h4>个人介绍</h4>
      <p>{{ businessData.personal_intro }}</p>
    </div>
    
    <!-- 主营业务 -->
    <div v-if="businessData.services && businessData.services.length > 0" class="services">
      <h4>主营业务</h4>
      <div class="services-grid">
        <span 
          v-for="service in businessData.services"
          :key="service"
          class="service-tag"
        >
          {{ service }}
        </span>
      </div>
    </div>
    
    <!-- 成就荣誉 -->
    <div v-if="businessData.achievements && businessData.achievements.length > 0" class="achievements">
      <h4>成就荣誉</h4>
      <ul class="achievements-list">
        <li v-for="achievement in businessData.achievements" :key="achievement">
          {{ achievement }}
        </li>
      </ul>
    </div>
    
    <!-- 作品集 -->
    <div v-if="businessData.portfolio && businessData.portfolio.length > 0" class="portfolio">
      <h4>作品展示</h4>
      <div class="portfolio-grid">
        <div 
          v-for="item in businessData.portfolio"
          :key="item.id"
          class="portfolio-item"
          @click="openImageModal(item)"
        >
          <div class="portfolio-image">
            <img :src="item.image" :alt="item.title" />
            <div class="image-overlay">
              <i class="icon-zoom-in"></i>
            </div>
          </div>
          <div class="portfolio-content">
            <h5 class="portfolio-title">{{ item.title }}</h5>
            <p class="portfolio-description">{{ item.description }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图片模态框 -->
    <div v-if="showImageModal" class="image-modal" @click="closeImageModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeImageModal">&times;</button>
        <img :src="selectedImage.image" :alt="selectedImage.title" class="modal-image" />
        <div class="modal-info">
          <h3>{{ selectedImage.title }}</h3>
          <p v-if="selectedImage.description">{{ selectedImage.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BusinessShowcase',
  
  props: {
    businessData: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  
  data() {
    return {
      showImageModal: false,
      selectedImage: null
    }
  },
  
  methods: {
    handlePortfolioClick(item) {
      this.$emit('portfolio-click', item)
    },
    
    openImageModal(item) {
      this.selectedImage = item
      this.showImageModal = true
      // 防止背景滚动
      document.body.style.overflow = 'hidden'
    },
    
    closeImageModal() {
      this.showImageModal = false
      this.selectedImage = null
      // 恢复背景滚动
      document.body.style.overflow = ''
    }
  },
  
  beforeUnmount() {
    // 组件销毁时恢复滚动
    document.body.style.overflow = ''
  }
}
</script>

<style lang="scss" scoped>
.business-showcase {
  padding: 16px 20px;
  background: #ffffff;
  margin: 12px 16px;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,.08);
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}

.section-header {
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.company-intro,
.personal-intro {
  margin-bottom: 20px;
  
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: #595959;
    margin: 0 0 8px 0;
  }
  
  p {
    font-size: 14px;
    line-height: 1.6;
    color: #262626;
    margin: 0;
  }
}

.services {
  margin-bottom: 20px;
  
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: #595959;
    margin: 0 0 12px 0;
  }
}

.services-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.service-tag {
  display: inline-block;
  padding: 6px 12px;
  background: var(--secondary-color, #F0F7FF);
  color: var(--primary-color, #1890FF);
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.achievements {
  margin-bottom: 20px;
  
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: #595959;
    margin: 0 0 12px 0;
  }
}

.achievements-list {
  margin: 0;
  padding-left: 16px;
  
  li {
    font-size: 14px;
    line-height: 1.6;
    color: #262626;
    margin-bottom: 4px;
  }
}

.portfolio {
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: #595959;
    margin: 0 0 16px 0;
  }
}

.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.portfolio-item {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: var(--primary-color, #1890FF);
  }
}

.portfolio-image {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
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

.portfolio-content {
  padding: 12px;
}

.portfolio-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 6px 0;
}

.portfolio-description {
  font-size: 12px;
  line-height: 1.5;
  color: #8c8c8c;
  margin: 0;
}

/* 图片模态框样式 */
.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: modalFadeIn 0.3s ease-out;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
  
  &:hover {
    background: rgba(0, 0, 0, 0.9);
  }
}

.modal-image {
  width: 100%;
  max-height: 70vh;
  object-fit: contain;
  display: block;
}

.modal-info {
  padding: 16px 20px;
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #262626;
    margin: 0 0 8px 0;
  }
  
  p {
    font-size: 14px;
    color: #8c8c8c;
    line-height: 1.5;
    margin: 0;
  }
}

@keyframes modalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalSlideIn {
  from { 
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to { 
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

// 响应式设计
@media (max-width: 480px) {
  .business-showcase {
    padding: 16px;
  }
  
  .portfolio-grid {
    grid-template-columns: 1fr;
  }
  
  .portfolio-image {
    height: 120px;
  }
  
  .modal-content {
    max-width: 95vw;
    max-height: 95vh;
  }
  
  .modal-info {
    padding: 12px 16px;
    
    h3 {
      font-size: 16px;
    }
    
    p {
      font-size: 13px;
    }
  }
}

/* 图标字体 */
.icon-zoom-in::before { content: "🔍"; }
</style>
