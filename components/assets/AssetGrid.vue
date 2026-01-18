<template>
  <div class="asset-grid-container">
    <div class="asset-grid" :class="{ 'loading': loading }">
      <AssetCard
        v-for="asset in assets"
        :key="asset.id"
        :asset="asset"
        @click="$emit('asset-click', asset)"
      />
    </div>
    
    <!-- 加载更多按钮 -->
    <div v-if="hasMore && !loading" class="load-more-section">
      <button @click="$emit('load-more')" class="load-more-btn">
        加载更多
      </button>
    </div>
    
    <!-- 加载中状态 -->
    <div v-if="loading && assets.length > 0" class="loading-more">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
    
    <!-- 没有更多内容 -->
    <div v-if="!hasMore && assets.length > 0" class="no-more">
      <span>已显示全部内容</span>
    </div>
  </div>
</template>

<script>
import AssetCard from './AssetCard.vue'

export default {
  name: 'AssetGrid',
  
  components: {
    AssetCard
  },
  
  props: {
    assets: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    hasMore: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['asset-click', 'load-more']
}
</script>

<style lang="scss" scoped>
.asset-grid-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
  
  &.loading {
    opacity: 0.7;
    pointer-events: none;
  }
}

.load-more-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.load-more-btn {
  padding: 12px 32px;
  background: var(--library-primary-color, #1890FF);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: var(--library-primary-hover, #40a9ff);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  color: #8c8c8c;
  font-size: 14px;
  
  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid var(--library-primary-color, #1890FF);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

.no-more {
  display: flex;
  justify-content: center;
  padding: 20px;
  color: #bfbfbf;
  font-size: 14px;
  
  span {
    position: relative;
    padding: 0 20px;
    background: #f5f5f5;
    
    &::before,
    &::after {
      content: '';
      position: absolute;
      top: 50%;
      width: 60px;
      height: 1px;
      background: #e8e8e8;
    }
    
    &::before {
      left: -80px;
    }
    
    &::after {
      right: -80px;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 响应式设计
@media (max-width: 1024px) {
  .asset-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .asset-grid-container {
    padding: 0 16px;
  }
  
  .asset-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 30px;
  }
  
  .load-more-btn {
    padding: 10px 24px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .asset-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .no-more span {
    &::before,
    &::after {
      width: 40px;
    }
    
    &::before {
      left: -60px;
    }
    
    &::after {
      right: -60px;
    }
  }
}
</style>
