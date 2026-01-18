<template>
  <div class="asset-management-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">素材库管理</h1>
        <p class="page-description">管理您的企业素材库，提升客户体验</p>
      </div>
      <div class="header-right">
        <button @click="showUploadModal = true" class="btn-primary">
          <i class="icon-plus"></i>
          添加素材
        </button>
        <button @click="openPublicLibrary" class="btn-outline">
          <i class="icon-external-link"></i>
          查看公开页面
        </button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">📁</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_assets }}</div>
          <div class="stat-label">总素材数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👁️</div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(stats.total_views) }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📤</div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(stats.total_shares) }}</div>
          <div class="stat-label">总分享数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.recent_views }}</div>
          <div class="stat-label">近30天浏览</div>
        </div>
      </div>
    </div>
    
    <!-- 筛选和搜索 -->
    <div class="filters-section">
      <div class="filters-left">
        <select v-model="selectedStatus" @change="handleFilterChange" class="filter-select">
          <option value="">全部状态</option>
          <option value="active">已发布</option>
          <option value="draft">草稿</option>
          <option value="inactive">已下线</option>
        </select>
        
        <select v-model="selectedType" @change="handleFilterChange" class="filter-select">
          <option value="">全部类型</option>
          <option value="document">文档资料</option>
          <option value="image">图片素材</option>
          <option value="video">视频内容</option>
          <option value="link">链接资源</option>
          <option value="presentation">演示文稿</option>
        </select>
      </div>
      
      <div class="filters-right">
        <div class="search-box">
          <i class="icon-search"></i>
          <input 
            v-model="searchQuery"
            @input="debounceSearch"
            type="text" 
            placeholder="搜索素材标题或摘要..."
            class="search-input"
          />
        </div>
      </div>
    </div>
    
    <!-- 素材列表 -->
    <div class="assets-table-container">
      <table class="assets-table">
        <thead>
          <tr>
            <th>素材信息</th>
            <th>类型</th>
            <th>状态</th>
            <th>统计</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="asset in assets" :key="asset.id" class="asset-row">
            <td class="asset-info">
              <div class="asset-preview">
                <img 
                  v-if="asset.cover" 
                  :src="asset.cover" 
                  :alt="asset.title"
                  class="preview-image"
                />
                <div v-else class="preview-placeholder">
                  <i :class="getTypeIcon(asset.content_type)"></i>
                </div>
              </div>
              <div class="asset-details">
                <h4 class="asset-title">{{ asset.title }}</h4>
                <p class="asset-summary">{{ asset.summary || '暂无摘要' }}</p>
                <div class="asset-tags" v-if="asset.tags && asset.tags.length">
                  <span v-for="tag in asset.tags.slice(0, 2)" :key="tag" class="tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </td>
            <td>
              <div class="type-badge" :class="`type-${asset.content_type}`">
                <i :class="getTypeIcon(asset.content_type)"></i>
                {{ asset.content_type_label }}
              </div>
            </td>
            <td>
              <div class="status-badge" :class="`status-${asset.status}`">
                {{ getStatusLabel(asset.status) }}
              </div>
            </td>
            <td class="stats-cell">
              <div class="stat-item">
                <i class="icon-eye"></i>
                {{ asset.view_count }}
              </div>
              <div class="stat-item">
                <i class="icon-share"></i>
                {{ asset.share_count }}
              </div>
            </td>
            <td class="date-cell">
              {{ formatDate(asset.updated_at) }}
            </td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button 
                  @click="editAsset(asset)" 
                  class="action-btn edit-btn"
                  title="编辑"
                >
                  <i class="icon-edit"></i>
                </button>
                <button 
                  @click="previewAsset(asset)" 
                  class="action-btn preview-btn"
                  title="预览"
                >
                  <i class="icon-eye"></i>
                </button>
                <button 
                  @click="toggleAssetStatus(asset)" 
                  class="action-btn status-btn"
                  :title="asset.status === 'active' ? '下线' : '上线'"
                >
                  <i :class="asset.status === 'active' ? 'icon-pause' : 'icon-play'"></i>
                </button>
                <button 
                  @click="deleteAsset(asset)" 
                  class="action-btn delete-btn"
                  title="删除"
                >
                  <i class="icon-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 空状态 -->
      <div v-if="!loading && assets.length === 0" class="empty-state">
        <div class="empty-icon">📁</div>
        <h3>暂无素材</h3>
        <p>开始添加您的第一个素材吧</p>
        <button @click="showUploadModal = true" class="btn-primary">
          添加素材
        </button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="pagination.pages > 1" class="pagination">
      <button 
        @click="changePage(pagination.page - 1)"
        :disabled="!pagination.has_prev"
        class="page-btn"
      >
        上一页
      </button>
      
      <div class="page-numbers">
        <button
          v-for="page in getPageNumbers()"
          :key="page"
          @click="changePage(page)"
          :class="['page-number', { active: page === pagination.page }]"
        >
          {{ page }}
        </button>
      </div>
      
      <button 
        @click="changePage(pagination.page + 1)"
        :disabled="!pagination.has_next"
        class="page-btn"
      >
        下一页
      </button>
    </div>
    
    <!-- 上传素材模态框 -->
    <AssetUploadModal
      v-if="showUploadModal"
      @close="showUploadModal = false"
      @success="handleUploadSuccess"
    />
    
    <!-- 编辑素材模态框 -->
    <AssetEditModal
      v-if="editingAsset"
      :asset="editingAsset"
      @close="editingAsset = null"
      @success="handleEditSuccess"
    />
    
    <!-- 预览模态框 -->
    <AssetPreviewModal
      v-if="previewingAsset"
      :asset="previewingAsset"
      @close="previewingAsset = null"
    />
  </div>
</template>

<script>
import AssetUploadModal from '~/components/admin/AssetUploadModal.vue'
import AssetEditModal from '~/components/admin/AssetEditModal.vue'
import AssetPreviewModal from '~/components/admin/AssetPreviewModal.vue'

export default {
  name: 'AssetManagementPage',
  
  components: {
    AssetUploadModal,
    AssetEditModal,
    AssetPreviewModal
  },
  
  middleware: 'auth',
  
  async asyncData({ $axios }) {
    try {
      const { data } = await $axios.get('/api/tenant/assets', {
        params: { page: 1, limit: 20 }
      })
      
      return {
        assets: data.assets,
        pagination: data.pagination,
        stats: data.stats,
        planLimits: data.plan_limits
      }
    } catch (error) {
      console.error('Error loading assets:', error)
      return {
        assets: [],
        pagination: {},
        stats: {},
        planLimits: {}
      }
    }
  },
  
  data() {
    return {
      selectedStatus: '',
      selectedType: '',
      searchQuery: '',
      loading: false,
      showUploadModal: false,
      editingAsset: null,
      previewingAsset: null,
      searchTimeout: null
    }
  },
  
  methods: {
    async handleFilterChange() {
      this.loading = true
      
      try {
        const { data } = await this.$axios.get('/api/tenant/assets', {
          params: {
            page: 1,
            limit: 20,
            status: this.selectedStatus,
            type: this.selectedType,
            search: this.searchQuery
          }
        })
        
        this.assets = data.assets
        this.pagination = data.pagination
        
      } catch (error) {
        console.error('筛选失败:', error)
        this.$toast.error('筛选失败')
      } finally {
        this.loading = false
      }
    },
    
    debounceSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.handleFilterChange()
      }, 500)
    },
    
    async changePage(page) {
      if (page < 1 || page > this.pagination.pages) return
      
      this.loading = true
      
      try {
        const { data } = await this.$axios.get('/api/tenant/assets', {
          params: {
            page,
            limit: 20,
            status: this.selectedStatus,
            type: this.selectedType,
            search: this.searchQuery
          }
        })
        
        this.assets = data.assets
        this.pagination = data.pagination
        
      } catch (error) {
        console.error('翻页失败:', error)
        this.$toast.error('翻页失败')
      } finally {
        this.loading = false
      }
    },
    
    editAsset(asset) {
      this.editingAsset = { ...asset }
    },
    
    previewAsset(asset) {
      this.previewingAsset = asset
    },
    
    async toggleAssetStatus(asset) {
      try {
        const newStatus = asset.status === 'active' ? 'inactive' : 'active'
        
        await this.$axios.put(`/api/tenant/assets/${asset.id}`, {
          status: newStatus
        })
        
        asset.status = newStatus
        this.$toast.success(`素材已${newStatus === 'active' ? '上线' : '下线'}`)
        
      } catch (error) {
        console.error('状态切换失败:', error)
        this.$toast.error('状态切换失败')
      }
    },
    
    async deleteAsset(asset) {
      if (!confirm(`确定要删除素材"${asset.title}"吗？`)) return
      
      try {
        await this.$axios.delete(`/api/tenant/assets/${asset.id}`)
        
        // 从列表中移除
        const index = this.assets.findIndex(a => a.id === asset.id)
        if (index > -1) {
          this.assets.splice(index, 1)
        }
        
        this.$toast.success('素材已删除')
        
      } catch (error) {
        console.error('删除失败:', error)
        this.$toast.error('删除失败')
      }
    },
    
    handleUploadSuccess(newAsset) {
      this.assets.unshift(newAsset)
      this.showUploadModal = false
      this.$toast.success('素材添加成功')
    },
    
    handleEditSuccess(updatedAsset) {
      const index = this.assets.findIndex(a => a.id === updatedAsset.id)
      if (index > -1) {
        this.assets.splice(index, 1, updatedAsset)
      }
      this.editingAsset = null
      this.$toast.success('素材更新成功')
    },
    
    openPublicLibrary() {
      const url = `/assets/${this.$auth.user.tenant_id}`
      if (typeof window !== 'undefined') window.open(url, '_blank')
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
    
    getStatusLabel(status) {
      const labelMap = {
        'active': '已发布',
        'draft': '草稿',
        'inactive': '已下线'
      }
      return labelMap[status] || status
    },
    
    formatNumber(num) {
      if (!num) return '0'
      
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k'
      }
      
      return num.toString()
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      const now = new Date()
      const diff = now - date
      
      if (diff < 24 * 60 * 60 * 1000) {
        return '今天'
      } else if (diff < 2 * 24 * 60 * 60 * 1000) {
        return '昨天'
      } else {
        return date.toLocaleDateString('zh-CN')
      }
    },
    
    getPageNumbers() {
      const current = this.pagination.page
      const total = this.pagination.pages
      const delta = 2
      
      const range = []
      const rangeWithDots = []
      
      for (let i = Math.max(2, current - delta); 
           i <= Math.min(total - 1, current + delta); 
           i++) {
        range.push(i)
      }
      
      if (current - delta > 2) {
        rangeWithDots.push(1, '...')
      } else {
        rangeWithDots.push(1)
      }
      
      rangeWithDots.push(...range)
      
      if (current + delta < total - 1) {
        rangeWithDots.push('...', total)
      } else {
        rangeWithDots.push(total)
      }
      
      return rangeWithDots
    }
  }
}
</script>

<style lang="scss" scoped>
.asset-management-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  .header-left {
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #262626;
      margin: 0 0 4px 0;
    }
    
    .page-description {
      color: #8c8c8c;
      margin: 0;
    }
  }
  
  .header-right {
    display: flex;
    gap: 12px;
  }
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  
  .stat-icon {
    font-size: 32px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    border-radius: 8px;
  }
  
  .stat-content {
    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: #262626;
      margin-bottom: 4px;
    }
    
    .stat-label {
      font-size: 14px;
      color: #8c8c8c;
    }
  }
}

.filters-section {
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.filters-left {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  min-width: 120px;
  
  &:focus {
    border-color: #1890FF;
    outline: none;
  }
}

.search-box {
  position: relative;
  
  .icon-search {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #bfbfbf;
    font-size: 14px;
  }
  
  .search-input {
    padding: 8px 12px 8px 36px;
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    font-size: 14px;
    width: 300px;
    
    &:focus {
      border-color: #1890FF;
      outline: none;
    }
    
    &::placeholder {
      color: #bfbfbf;
    }
  }
}

.assets-table-container {
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.assets-table {
  width: 100%;
  border-collapse: collapse;
  
  th {
    background: #fafafa;
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #262626;
    border-bottom: 1px solid #f0f0f0;
    font-size: 14px;
  }
  
  td {
    padding: 16px;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: top;
  }
  
  .asset-row:hover {
    background: #fafafa;
  }
}

.asset-info {
  display: flex;
  gap: 12px;
  min-width: 300px;
}

.asset-preview {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  background: #f5f5f5;
  
  .preview-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .preview-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    i {
      font-size: 24px;
      color: #bfbfbf;
    }
  }
}

.asset-details {
  flex: 1;
  min-width: 0;
}

.asset-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
  
  // 标题截断
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.asset-summary {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0 0 8px 0;
  line-height: 1.4;
  
  // 摘要截断
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.asset-tags {
  display: flex;
  gap: 4px;
  
  .tag {
    padding: 2px 6px;
    background: #f0f0f0;
    color: #595959;
    font-size: 11px;
    border-radius: 3px;
    font-weight: 500;
  }
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  
  &.type-document {
    background: #e6f7ff;
    color: #1890FF;
  }
  
  &.type-image {
    background: #f6ffed;
    color: #52c41a;
  }
  
  &.type-video {
    background: #fff7e6;
    color: #fa8c16;
  }
  
  &.type-link {
    background: #f9f0ff;
    color: #722ed1;
  }
  
  &.type-presentation {
    background: #fff0f6;
    color: #eb2f96;
  }
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  
  &.status-active {
    background: #f6ffed;
    color: #52c41a;
  }
  
  &.status-draft {
    background: #fff7e6;
    color: #fa8c16;
  }
  
  &.status-inactive {
    background: #fff1f0;
    color: #ff4d4f;
  }
}

.stats-cell {
  .stat-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    color: #8c8c8c;
    margin-bottom: 4px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    i {
      font-size: 12px;
    }
  }
}

.date-cell {
  font-size: 14px;
  color: #8c8c8c;
  white-space: nowrap;
}

.actions-cell {
  .action-buttons {
    display: flex;
    gap: 4px;
  }
  
  .action-btn {
    width: 32px;
    height: 32px;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      border-color: #1890FF;
      color: #1890FF;
    }
    
    &.delete-btn:hover {
      border-color: #ff4d4f;
      color: #ff4d4f;
    }
    
    i {
      font-size: 14px;
    }
  }
}

.empty-state, .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #1890FF;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }
  
  h3 {
    font-size: 18px;
    color: #262626;
    margin: 0 0 8px 0;
  }
  
  p {
    color: #8c8c8c;
    margin: 0 0 20px 0;
  }
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  
  .page-btn {
    padding: 8px 16px;
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    background: white;
    color: #262626;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover:not(:disabled) {
      border-color: #1890FF;
      color: #1890FF;
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  .page-numbers {
    display: flex;
    gap: 4px;
  }
  
  .page-number {
    width: 32px;
    height: 32px;
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    background: white;
    color: #262626;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    
    &:hover {
      border-color: #1890FF;
      color: #1890FF;
    }
    
    &.active {
      background: #1890FF;
      border-color: #1890FF;
      color: white;
    }
  }
}

// 按钮样式
.btn-primary {
  padding: 8px 16px;
  background: #1890FF;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: #40a9ff;
  }
  
  i {
    font-size: 14px;
  }
}

.btn-outline {
  padding: 8px 16px;
  background: white;
  color: #1890FF;
  border: 1px solid #1890FF;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: #1890FF;
    color: white;
  }
  
  i {
    font-size: 14px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 响应式设计
@media (max-width: 1024px) {
  .asset-management-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .filters-left {
    flex-wrap: wrap;
  }
  
  .search-box .search-input {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .assets-table-container {
    overflow-x: auto;
  }
  
  .assets-table {
    min-width: 800px;
  }
}
</style>
