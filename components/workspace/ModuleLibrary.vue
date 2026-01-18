<template>
  <div class="module-library">
    <!-- 标题 -->
    <div class="library-header">
      <h3 class="library-title">
        <span class="icon">📦</span>
        模块库
      </h3>
      <span class="module-count">{{ totalFrameworks }}个框架</span>
    </div>

    <!-- 搜索 -->
    <div class="library-search">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索框架..."
        class="search-input"
      />
    </div>

    <!-- 分类导航 -->
    <div class="category-tabs">
      <button
        v-for="(category, key) in categories"
        :key="key"
        :class="['category-tab', { active: selectedCategory === key }]"
        @click="selectedCategory = key"
      >
        <span class="tab-icon">{{ category.icon }}</span>
        <span class="tab-label">{{ category.label }}</span>
      </button>
    </div>

    <!-- 框架列表 -->
    <div class="framework-list">
      <div
        v-for="framework in filteredFrameworks"
        :key="framework.id"
        class="framework-card"
        draggable="true"
        @dragstart="onDragStart($event, framework)"
        @dragend="onDragEnd"
      >
        <div class="framework-header">
          <span class="framework-icon">{{ framework.icon }}</span>
          <div class="framework-info">
            <h4 class="framework-name">{{ framework.name }}</h4>
            <span class="framework-version">v{{ framework.version }}</span>
          </div>
        </div>
        
        <p class="framework-description">{{ framework.description }}</p>
        
        <button class="add-btn" @click="addFramework(framework.id)">
          <span class="icon">+</span>
          添加
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredFrameworks.length === 0" class="empty-state">
        <span class="empty-icon">🔍</span>
        <p>未找到匹配的框架</p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import {
  FRAMEWORK_DEFINITIONS,
  FRAMEWORK_CATEGORIES
} from '@/config/framework-definitions'

export default {
  name: 'ModuleLibrary',
  
  data() {
    return {
      searchQuery: '',
      selectedCategory: 'all',
      draggingFramework: null,
      categories: {
        all: { label: '全部', icon: '📚', order: 0 },
        ...FRAMEWORK_CATEGORIES
      }
    }
  },
  
  computed: {
    frameworks() {
      return Object.values(FRAMEWORK_DEFINITIONS)
    },
    
    totalFrameworks() {
      return this.frameworks.length
    },
    
    filteredFrameworks() {
      let filtered = this.frameworks
      
      // 按分类筛选
      if (this.selectedCategory && this.selectedCategory !== 'all') {
        filtered = filtered.filter(f => f.category === this.selectedCategory)
      }
      
      // 按搜索关键词筛选
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(f =>
          f.name.toLowerCase().includes(query) ||
          f.description.toLowerCase().includes(query) ||
          f.id.toLowerCase().includes(query)
        )
      }
      
      return filtered
    }
  },
  
  methods: {
    ...mapActions('workspace', ['addModule']),
    
    addFramework(frameworkId) {
      this.addModule(frameworkId)
      this.$toast?.success('模块已添加')
    },
    
    onDragStart(event, framework) {
      this.draggingFramework = framework
      // 设置拖拽数据
      event.dataTransfer.effectAllowed = 'copy'
      event.dataTransfer.setData('framework-id', framework.id)
    },
    
    onDragEnd() {
      this.draggingFramework = null
    }
  }
}
</script>

<style scoped>
.module-library {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 头部 */
.library-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.library-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.module-count {
  font-size: 12px;
  color: #8c8c8c;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 10px;
}

/* 搜索 */
.library-search {
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.search-input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* 分类标签 */
.category-tabs {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #595959;
  text-align: left;
  transition: all 0.2s ease;
}

.category-tab:hover {
  background: #f5f5f5;
}

.category-tab.active {
  background: #e6f7ff;
  color: #1890ff;
}

.tab-icon {
  font-size: 16px;
}

.tab-label {
  flex: 1;
}

/* 框架列表 */
.framework-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.framework-card {
  padding: 16px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: grab;
  transition: all 0.2s ease;
}

.framework-card:hover {
  background: white;
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.framework-card:active {
  cursor: grabbing;
}

.framework-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.framework-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.framework-info {
  flex: 1;
  min-width: 0;
}

.framework-name {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.framework-version {
  font-size: 11px;
  color: #8c8c8c;
  background: white;
  padding: 2px 6px;
  border-radius: 4px;
}

.framework-description {
  font-size: 12px;
  color: #595959;
  line-height: 1.5;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.add-btn {
  width: 100%;
  padding: 6px 12px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #1890ff;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.add-btn:hover {
  border-color: #1890ff;
  background: #e6f7ff;
}

.add-btn .icon {
  font-size: 16px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #8c8c8c;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 滚动条样式 */
.framework-list::-webkit-scrollbar {
  width: 6px;
}

.framework-list::-webkit-scrollbar-track {
  background: transparent;
}

.framework-list::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.framework-list::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}
</style>

