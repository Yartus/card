<template>
  <div class="asset-card" @click="handleClick">
    <!-- 封面图片 -->
    <div class="asset-cover">
      <img 
        v-if="asset.cover" 
        :src="asset.cover" 
        :alt="asset.title"
        class="cover-image"
        @error="handleImageError"
      />
      <div v-else class="cover-placeholder">
        <i :class="getTypeIcon(asset.content_type)"></i>
      </div>
      
      <!-- 悬停遮罩 -->
      <div class="asset-overlay">
        <div class="overlay-content">
          <i class="icon-view"></i>
          <span>查看详情</span>
        </div>
      </div>
      
      <!-- 类型标签 -->
      <div class="type-badge" :class="`type-${asset.content_type}`">
        <i :class="getTypeIcon(asset.content_type)"></i>
        <span>{{ asset.content_type_label }}</span>
      </div>
    </div>
    
    <!-- 内容区域 -->
    <div class="asset-content">
      <h3 class="asset-title" :title="asset.title">{{ asset.title }}</h3>
      <p v-if="asset.summary" class="asset-summary" :title="asset.summary">
        {{ asset.summary }}
      </p>
      
      <!-- 标签 -->
      <div v-if="asset.tags && asset.tags.length" class="asset-tags">
        <span 
          v-for="tag in asset.tags.slice(0, 3)" 
          :key="tag" 
          class="tag"
        >
          {{ tag }}
        </span>
        <span v-if="asset.tags.length > 3" class="tag-more">
          +{{ asset.tags.length - 3 }}
        </span>
      </div>
      
      <!-- 元信息 -->
      <div class="asset-meta">
        <div class="meta-left">
          <span class="file-size" v-if="asset.file_size_formatted">
            {{ asset.file_size_formatted }}
          </span>
          <span class="view-count">
            <i class="icon-eye"></i>
            {{ formatViewCount(asset.view_count) }}
          </span>
        </div>
        <div class="meta-right">
          <span class="created-date">{{ asset.formatted_date }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetCard',
  
  props: {
    asset: {
      type: Object,
      required: true
    }
  },
  
  emits: ['click'],
  
  methods: {
    handleClick() {
      this.$emit('click', this.asset)
    },
    
    handleImageError(event) {
      // 图片加载失败时显示占位符
      event.target.style.display = 'none'
      event.target.parentElement.classList.add('image-error')
    },
    
    getTypeIcon(type) {
      const iconMap = {
        'document': 'icon-document',
        'image': 'icon-image',
        'video': 'icon-video',
        'link': 'icon-link',
        'presentation': 'icon-presentation'
      }
      return iconMap[type] || 'icon-document'
    },
    
    formatViewCount(count) {
      if (!count) return '0'
      
      if (count >= 10000) {
        return (count / 10000).toFixed(1) + '万'
      } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'k'
      }
      
      return count.toString()
    }
  }
}
</script>

<style lang="scss" scoped>
.asset-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border-color: var(--library-primary-color, #1890FF);
    
    .asset-overlay {
      opacity: 1;
    }
    
    .cover-image {
      transform: scale(1.05);
    }
  }
}

.asset-cover {
  position: relative;
  height: 160px;
  overflow: hidden;
  background: #f5f5f5;
  
  &.image-error {
    display: flex;
    align-items: center;
    justify-content: center;
    
    &::after {
      content: '图片加载失败';
      color: #bfbfbf;
      font-size: 12px;
    }
  }
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  
  i {
    font-size: 48px;
    color: #bfbfbf;
  }
}

.asset-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  
  .overlay-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    color: white;
    
    i {
      font-size: 24px;
    }
    
    span {
      font-size: 14px;
      font-weight: 500;
    }
  }
}

.type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  color: white;
  backdrop-filter: blur(10px);
  
  &.type-document {
    background: rgba(24, 144, 255, 0.9);
  }
  
  &.type-image {
    background: rgba(82, 196, 26, 0.9);
  }
  
  &.type-video {
    background: rgba(250, 140, 22, 0.9);
  }
  
  &.type-link {
    background: rgba(114, 46, 209, 0.9);
  }
  
  &.type-presentation {
    background: rgba(235, 47, 150, 0.9);
  }
  
  i {
    font-size: 12px;
  }
}

.asset-content {
  padding: 16px;
}

.asset-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
  line-height: 1.4;
  
  // 标题截断
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.asset-summary {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0 0 12px 0;
  line-height: 1.5;
  
  // 摘要截断
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.asset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  
  .tag {
    padding: 2px 6px;
    background: #f0f0f0;
    color: #595959;
    font-size: 11px;
    border-radius: 3px;
    font-weight: 500;
  }
  
  .tag-more {
    padding: 2px 6px;
    background: #e6f7ff;
    color: var(--library-primary-color, #1890FF);
    font-size: 11px;
    border-radius: 3px;
    font-weight: 500;
  }
}

.asset-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #bfbfbf;
}

.meta-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-size {
  &::before {
    content: '📄';
    margin-right: 4px;
  }
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
  
  i {
    font-size: 12px;
  }
}

.created-date {
  color: #d9d9d9;
}

// 响应式设计
@media (max-width: 768px) {
  .asset-cover {
    height: 140px;
  }
  
  .asset-content {
    padding: 14px;
  }
  
  .asset-title {
    font-size: 15px;
  }
  
  .asset-summary {
    font-size: 13px;
  }
  
  .type-badge {
    top: 8px;
    right: 8px;
    padding: 3px 6px;
    font-size: 10px;
    
    span {
      display: none;
    }
  }
}

@media (max-width: 480px) {
  .asset-cover {
    height: 120px;
  }
  
  .asset-content {
    padding: 12px;
  }
  
  .asset-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .meta-left {
    gap: 8px;
  }
}
</style>
