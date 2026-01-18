<template>
  <div class="asset-filters">
    <div class="filter-row">
      <div class="filter-group">
        <label>搜索</label>
        <input
          v-model="filters.search"
          type="text"
          placeholder="搜索素材名称或描述"
          class="filter-input"
          @input="onFilterChange"
        >
      </div>
      
      <div class="filter-group">
        <label>分类</label>
        <select v-model="filters.category" class="filter-select" @change="onFilterChange">
          <option value="">全部分类</option>
          <option value="image">图片</option>
          <option value="video">视频</option>
          <option value="document">文档</option>
          <option value="other">其他</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>标签</label>
        <select v-model="filters.tag" class="filter-select" @change="onFilterChange">
          <option value="">全部标签</option>
          <option v-for="tag in availableTags" :key="tag" :value="tag">
            {{ tag }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>可见性</label>
        <select v-model="filters.visibility" class="filter-select" @change="onFilterChange">
          <option value="">全部</option>
          <option value="public">公开</option>
          <option value="private">私有</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>排序</label>
        <select v-model="filters.sortBy" class="filter-select" @change="onFilterChange">
          <option value="created_at">上传时间</option>
          <option value="name">名称</option>
          <option value="file_size">文件大小</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>顺序</label>
        <select v-model="filters.sortOrder" class="filter-select" @change="onFilterChange">
          <option value="desc">降序</option>
          <option value="asc">升序</option>
        </select>
      </div>
    </div>
    
    <div class="filter-actions">
      <button class="btn btn-secondary" @click="resetFilters">
        重置筛选
      </button>
      <button class="btn btn-primary" @click="applyFilters">
        应用筛选
      </button>
    </div>
    
    <div v-if="hasActiveFilters" class="active-filters">
      <span class="active-filters-label">当前筛选：</span>
      <span v-if="filters.search" class="filter-tag">
        搜索: "{{ filters.search }}"
        <button @click="clearSearch" class="filter-tag-remove">&times;</button>
      </span>
      <span v-if="filters.category" class="filter-tag">
        分类: {{ getCategoryName(filters.category) }}
        <button @click="clearCategory" class="filter-tag-remove">&times;</button>
      </span>
      <span v-if="filters.tag" class="filter-tag">
        标签: {{ filters.tag }}
        <button @click="clearTag" class="filter-tag-remove">&times;</button>
      </span>
      <span v-if="filters.visibility" class="filter-tag">
        可见性: {{ filters.visibility === 'public' ? '公开' : '私有' }}
        <button @click="clearVisibility" class="filter-tag-remove">&times;</button>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetFilters',
  props: {
    availableTags: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      filters: {
        search: '',
        category: '',
        tag: '',
        visibility: '',
        sortBy: 'created_at',
        sortOrder: 'desc'
      }
    }
  },
  computed: {
    hasActiveFilters() {
      return this.filters.search || 
             this.filters.category || 
             this.filters.tag || 
             this.filters.visibility
    }
  },
  methods: {
    onFilterChange() {
      // 防抖处理
      clearTimeout(this.filterTimeout)
      this.filterTimeout = setTimeout(() => {
        this.$emit('filter-change', { ...this.filters })
      }, 300)
    },
    
    applyFilters() {
      this.$emit('filter-change', { ...this.filters })
    },
    
    resetFilters() {
      this.filters = {
        search: '',
        category: '',
        tag: '',
        visibility: '',
        sortBy: 'created_at',
        sortOrder: 'desc'
      }
      this.$emit('filter-change', { ...this.filters })
    },
    
    clearSearch() {
      this.filters.search = ''
      this.onFilterChange()
    },
    
    clearCategory() {
      this.filters.category = ''
      this.onFilterChange()
    },
    
    clearTag() {
      this.filters.tag = ''
      this.onFilterChange()
    },
    
    clearVisibility() {
      this.filters.visibility = ''
      this.onFilterChange()
    },
    
    getCategoryName(category) {
      const categoryMap = {
        'image': '图片',
        'video': '视频',
        'document': '文档',
        'other': '其他'
      }
      return categoryMap[category] || category
    }
  },
  
  beforeDestroy() {
    if (this.filterTimeout) {
      clearTimeout(this.filterTimeout)
    }
  }
}
</script>

<style scoped>
.asset-filters {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.filter-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.filter-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}

.active-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
}

.active-filters-label {
  font-weight: 500;
  color: #1890ff;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  background: #1890ff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.filter-tag-remove {
  background: none;
  border: none;
  color: white;
  margin-left: 6px;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.filter-tag-remove:hover {
  opacity: 0.8;
}

@media (max-width: 768px) {
  .filter-row {
    grid-template-columns: 1fr;
  }
  
  .filter-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
