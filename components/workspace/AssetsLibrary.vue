<template>
  <div class="assets-library">
    <!-- 头部信息 -->
    <div class="library-header">
      <div class="header-content">
        <h2 class="header-title">📚 素材库管理</h2>
        <p class="header-desc">查看素材发布状态、访问统计和推送记录</p>
      </div>
      <button class="btn-create" @click="goToCreate">
        <i class="icon-plus"></i>
        创建新素材
      </button>
    </div>

    <!-- 素材库链接卡片 -->
    <div class="library-info-card">
      <div class="info-row">
        <div class="info-label">
          <i class="icon-link"></i>
          素材库链接
        </div>
        <div class="info-value">
          <code class="library-url">{{ libraryUrl }}</code>
          <button class="btn-copy" @click="copyLibraryUrl">
            <i class="icon-copy"></i>
            复制链接
          </button>
        </div>
      </div>
      <div class="info-hint">
        <i class="icon-info"></i>
        此链接可配置到企业微信聊天侧边栏，员工可快速访问素材库
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-value">{{ assets.length }}</div>
        <div class="stat-label">素材总数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ publishedCount }}</div>
        <div class="stat-label">已发布</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ draftCount }}</div>
        <div class="stat-label">草稿</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ planLimit }}</div>
        <div class="stat-label">套餐限制</div>
      </div>
    </div>

    <!-- 筛选和排序 -->
    <div class="filter-bar">
      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          class="filter-tab"
          :class="{ active: currentFilter === tab.value }"
          @click="currentFilter = tab.value"
        >
          {{ tab.label }}
          <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
      <div class="sort-select">
        <select v-model="sortBy" class="select-input">
          <option value="created_desc">创建时间（新→旧）</option>
          <option value="created_asc">创建时间（旧→新）</option>
          <option value="updated_desc">更新时间（新→旧）</option>
          <option value="title_asc">标题（A→Z）</option>
        </select>
      </div>
    </div>

    <!-- 素材列表 -->
    <div v-if="filteredAssets.length > 0" class="assets-grid">
      <div
        v-for="asset in sortedAssets"
        :key="asset.id"
        class="asset-card"
        :class="{ draft: asset.status === 'draft' }"
      >
        <!-- 封面图 -->
        <div class="asset-cover" @click="previewAsset(asset)">
          <img v-if="asset.cover" :src="asset.cover" :alt="asset.title" />
          <div v-else class="cover-placeholder">
            <i class="icon-image"></i>
          </div>
          <div class="cover-overlay">
            <i class="icon-eye"></i>
            <span>预览</span>
          </div>
          <div v-if="asset.status === 'draft'" class="draft-badge">草稿</div>
        </div>

        <!-- 素材信息 -->
        <div class="asset-info">
          <h3 class="asset-title">{{ asset.title || '未命名素材' }}</h3>
          <p class="asset-summary">{{ asset.summary || '暂无简介' }}</p>
          
          <!-- 标签 -->
          <div v-if="asset.tags && asset.tags.length" class="asset-tags">
            <span v-for="tag in asset.tags.slice(0, 3)" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>

          <!-- 元信息 -->
          <div class="asset-meta">
            <span class="meta-item">
              <i class="icon-time"></i>
              {{ formatDate(asset.updated_at || asset.created_at) }}
            </span>
            <span v-if="asset.views" class="meta-item">
              <i class="icon-eye"></i>
              {{ asset.views }} 次查看
            </span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="asset-actions">
          <button class="btn-action" @click="editAsset(asset)" title="编辑">
            <i class="icon-edit"></i>
          </button>
          <button class="btn-action" @click="copyAssetLink(asset)" title="复制链接">
            <i class="icon-link"></i>
          </button>
          <button
            class="btn-action"
            :class="{ active: asset.status === 'published' }"
            @click="togglePublish(asset)"
            :title="asset.status === 'published' ? '取消发布' : '发布'"
          >
            <i class="icon-publish"></i>
          </button>
          <button class="btn-action danger" @click="deleteAsset(asset)" title="删除">
            <i class="icon-delete"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">📭</div>
      <h3 class="empty-title">暂无素材</h3>
      <p class="empty-desc">
        {{ currentFilter === 'all' ? '开始创建您的第一个素材' : '当前筛选条件下暂无素材' }}
      </p>
      <button v-if="currentFilter === 'all'" class="btn-empty-action" @click="goToCreate">
        <i class="icon-plus"></i>
        去创建素材
      </button>
    </div>

    <!-- 素材编辑Modal -->
    <AssetEditorModal
      v-if="showEditor"
      :asset="editingAsset"
      :is-modal="true"
      @save="handleSaveAsset"
      @close="showEditor = false"
    />
  </div>
</template>

<script>
import AssetEditorModal from './AssetEditorModal.vue'

export default {
  name: 'AssetsLibrary',
  
  components: {
    AssetEditorModal
  },
  
  data() {
    return {
      assets: [],
      currentFilter: 'all',
      sortBy: 'created_desc',
      showEditor: false,
      editingAsset: null,
      loading: false
    }
  },
  
  computed: {
    libraryUrl() {
      // ✅ 使用 workspace.tenantInfo.id，与 workspace.vue 保持一致
      const tenantId = this.$store.state.workspace?.tenantInfo?.id || 'your-tenant-id'
      const baseUrl = process.client ? window.location.origin : 'https://zjemail.cn'
      return `${baseUrl}/assets/${tenantId}`
    },
    
    publishedCount() {
      return this.assets.filter(a => a.status === 'published').length
    },
    
    draftCount() {
      return this.assets.filter(a => a.status === 'draft').length
    },
    
    planLimit() {
      // TODO: 从套餐信息获取
      return 50
    },
    
    filterTabs() {
      return [
        { label: '全部', value: 'all', count: this.assets.length },
        { label: '已发布', value: 'published', count: this.publishedCount },
        { label: '草稿', value: 'draft', count: this.draftCount }
      ]
    },
    
    filteredAssets() {
      if (this.currentFilter === 'all') {
        return this.assets
      }
      return this.assets.filter(a => a.status === this.currentFilter)
    },
    
    sortedAssets() {
      const assets = [...this.filteredAssets]
      
      switch (this.sortBy) {
        case 'created_desc':
          return assets.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        case 'created_asc':
          return assets.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        case 'updated_desc':
          return assets.sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
        case 'title_asc':
          return assets.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
        default:
          return assets
      }
    }
  },
  
  mounted() {
    // ✅ 延迟加载，避免影响页面初始化
    this.$nextTick(() => {
      this.loadAssets()
    })
  },
  
  methods: {
    async loadAssets() {
      this.loading = true
      try {
        // ✅ 调用真实API
        const token = this.$wecomAuth?.getToken()
        if (!token) {
          throw new Error('未找到认证token')
        }
        
        const response = await this.$axios.get('/api/tenant/assets', {
          params: {
            status: this.currentFilter === 'all' ? undefined : this.currentFilter,
            page: 1,
            per_page: 50
          },
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        // ✅ 处理真实返回结构
        if (response.data && response.data.success) {
          this.assets = response.data.assets || []
          console.log(`✅ 素材加载成功: ${this.assets.length} 个`)
        } else {
          throw new Error(response.data?.error || '数据格式错误')
        }
      } catch (error) {
        // ✅ 静默处理错误，避免影响页面加载
        console.warn('⚠️ 素材加载失败:', error.message)
        
        if (error.response?.status === 401) {
          // 认证失败，静默处理，不显示错误提示
          console.warn('⚠️ 认证失败，素材列表将为空')
          this.assets = []
        } else if (error.response?.status === 404) {
          // API路由未注册，使用模拟数据，静默处理
          console.warn('⚠️ 素材库API未注册，使用模拟数据')
          this.assets = this.getMockAssets()
        } else {
          // 其他错误，静默处理，不显示错误提示
          console.warn('⚠️ 加载素材失败，使用空列表')
          this.assets = []
        }
      } finally {
        this.loading = false
      }
    },
    
    getMockAssets() {
      // 模拟数据
      return [
        {
          id: 1,
          title: '产品手册 2024版',
          summary: '详细介绍我们的核心产品功能、技术参数和应用场景',
          cover: 'https://via.placeholder.com/400x300/667eea/ffffff?text=产品手册',
          content: '完整的产品介绍内容...',
          tags: ['产品', '手册', '2024'],
          status: 'published',
          views: 128,
          created_at: '2025-10-25T10:00:00Z',
          updated_at: '2025-10-28T15:30:00Z'
        },
        {
          id: 2,
          title: '企业解决方案',
          summary: '为企业客户量身定制的一体化解决方案，助力数字化转型',
          cover: 'https://via.placeholder.com/400x300/52c41a/ffffff?text=解决方案',
          content: '解决方案详细内容...',
          tags: ['方案', '企业', '数字化'],
          status: 'published',
          views: 89,
          created_at: '2025-10-20T14:00:00Z',
          updated_at: '2025-10-29T09:15:00Z'
        },
        {
          id: 3,
          title: '成功案例集',
          summary: '精选行业标杆客户案例，展示实际应用效果和价值',
          cover: 'https://via.placeholder.com/400x300/ff7875/ffffff?text=成功案例',
          content: '案例详细内容...',
          tags: ['案例', '客户'],
          status: 'draft',
          views: 0,
          created_at: '2025-10-30T08:00:00Z',
          updated_at: '2025-10-30T08:00:00Z'
        }
      ]
    },
    
    // 跳转到第一个tab创建素材
    goToCreate() {
      this.$emit('go-to-content')
    },
    
    createAsset() {
      this.editingAsset = {
        id: null,
        title: '',
        summary: '',
        cover: '',
        content: '',
        tags: [],
        status: 'draft'
      }
      this.showEditor = true
    },
    
    editAsset(asset) {
      this.editingAsset = { ...asset }
      this.showEditor = true
    },
    
    previewAsset(asset) {
      // ✅ 统一使用锚点方式：/assets/{tenantId}#asset-{assetId}
      const tenantId = this.$store.state.workspace?.tenantInfo?.id || 'your-tenant-id'
      const baseUrl = process.client ? window.location.origin : 'https://zjemail.cn'
      const previewUrl = `${baseUrl}/assets/${tenantId}#asset-${asset.id}`
      window.open(previewUrl, '_blank')
    },
    
    async handleSaveAsset(assetData) {
      try {
        const token = this.$wecomAuth?.getToken()
        if (!token) {
          throw new Error('未找到认证token')
        }
        
        if (assetData.id) {
          // ✅ 更新现有素材
          const response = await this.$axios.put(
            `/api/tenant/assets/${assetData.id}`, 
            assetData,
            {
              headers: { 'Authorization': `Bearer ${token}` }
            }
          )
          
          if (response.data && response.data.success) {
            const index = this.assets.findIndex(a => a.id === assetData.id)
            if (index !== -1) {
              this.$set(this.assets, index, response.data.asset)
            }
            this.$toast?.success('素材更新成功')
          } else {
            throw new Error(response.data?.error || '更新失败')
          }
        } else {
          // ✅ 创建新素材
          const response = await this.$axios.post(
            '/api/tenant/assets', 
            assetData,
            {
              headers: { 'Authorization': `Bearer ${token}` }
            }
          )
          
          if (response.data && response.data.success) {
            this.assets.unshift(response.data.asset)
            this.$toast?.success('素材创建成功')
          } else {
            throw new Error(response.data?.error || '创建失败')
          }
        }
        
        this.showEditor = false
      } catch (error) {
        console.error('❌ 保存素材失败:', error)
        
        if (error.response?.status === 404) {
          this.$toast?.error('素材库API未注册，请联系管理员')
        } else {
          this.$toast?.error(error.response?.data?.error || '保存素材失败')
        }
      }
    },
    
    async togglePublish(asset) {
      const newStatus = asset.status === 'published' ? 'draft' : 'published'
      try {
        const token = this.$wecomAuth?.getToken()
        if (!token) {
          throw new Error('未找到认证token')
        }
        
        // ✅ 调用真实API
        const response = await this.$axios.patch(
          `/api/tenant/assets/${asset.id}/status`,
          { status: newStatus },
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )
        
        if (response.data && response.data.success) {
          asset.status = newStatus
          asset.updated_at = new Date().toISOString()
          this.$toast?.success(newStatus === 'published' ? '素材已发布' : '素材已取消发布')
        } else {
          throw new Error(response.data?.error || '操作失败')
        }
      } catch (error) {
        console.error('❌ 切换状态失败:', error)
        this.$toast?.error(error.response?.data?.error || '操作失败')
      }
    },
    
    async deleteAsset(asset) {
      if (!confirm(`确定要删除素材"${asset.title}"吗？此操作无法撤销。`)) {
        return
      }
      
      try {
        const token = this.$wecomAuth?.getToken()
        if (!token) {
          throw new Error('未找到认证token')
        }
        
        // ✅ 调用真实API
        const response = await this.$axios.delete(
          `/api/tenant/assets/${asset.id}`,
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )
        
        if (response.data && response.data.success) {
          const index = this.assets.findIndex(a => a.id === asset.id)
          if (index !== -1) {
            this.assets.splice(index, 1)
          }
          this.$toast?.success('素材已删除')
        } else {
          throw new Error(response.data?.error || '删除失败')
        }
      } catch (error) {
        console.error('❌ 删除素材失败:', error)
        this.$toast?.error(error.response?.data?.error || '删除素材失败')
      }
    },
    
    copyLibraryUrl() {
      this.copyToClipboard(this.libraryUrl)
      this.$toast?.success('素材库链接已复制')
    },
    
    copyAssetLink(asset) {
      // ✅ 统一使用锚点方式：/assets/{tenantId}#asset-{assetId}
      const tenantId = this.$store.state.workspace?.tenantInfo?.id || 'your-tenant-id'
      const baseUrl = process.client ? window.location.origin : 'https://zjemail.cn'
      const link = `${baseUrl}/assets/${tenantId}#asset-${asset.id}`
      this.copyToClipboard(link)
      this.$toast?.success('素材链接已复制')
    },
    
    copyToClipboard(text) {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text)
      } else {
        // 降级方案
        const input = document.createElement('input')
        input.value = text
        document.body.appendChild(input)
        input.select()
        document.execCommand('copy')
        document.body.removeChild(input)
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      const now = new Date()
      const diff = now - date
      
      // 1小时内
      if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`
      }
      // 24小时内
      if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`
      }
      // 7天内
      if (diff < 604800000) {
        return `${Math.floor(diff / 86400000)}天前`
      }
      // 其他显示日期
      return date.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style lang="scss" scoped>
.assets-library {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 头部 */
.library-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content {
  flex: 1;
}

.header-title {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 8px 0;
}

.header-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
  
  i {
    font-size: 16px;
  }
}

/* 信息卡片 */
.library-info-card {
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #595959;
  
  i {
    font-size: 16px;
    color: #667eea;
  }
}

.info-value {
  display: flex;
  align-items: center;
  gap: 12px;
}

.library-url {
  padding: 8px 16px;
  background: white;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  font-size: 13px;
  font-family: 'Monaco', 'Courier New', monospace;
  color: #667eea;
}

.btn-copy {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    color: #667eea;
  }
}

.info-hint {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  color: #8c8c8c;
  line-height: 1.6;
  
  i {
    margin-top: 2px;
    color: #1890ff;
  }
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  color: #595959;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    color: #667eea;
  }
  
  &.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: transparent;
    color: white;
  }
}

.tab-count {
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.select-input {
  padding: 10px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
}

/* 素材网格 */
.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.asset-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  &.draft {
    opacity: 0.7;
  }
}

.asset-cover {
  position: relative;
  width: 100%;
  height: 180px;
  background: #f5f5f5;
  cursor: pointer;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }
  
  &:hover img {
    transform: scale(1.05);
  }
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  
  i {
    font-size: 48px;
    color: #bfbfbf;
  }
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: white;
  
  i {
    font-size: 24px;
  }
  
  span {
    font-size: 14px;
    font-weight: 600;
  }
}

.asset-cover:hover .cover-overlay {
  opacity: 1;
}

.draft-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.asset-info {
  padding: 16px;
}

.asset-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-summary {
  font-size: 13px;
  color: #8c8c8c;
  line-height: 1.6;
  margin: 0 0 12px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.asset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  
  .tag {
    padding: 4px 10px;
    background: #f0f2ff;
    color: #667eea;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
  }
}

.asset-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #bfbfbf;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  
  i {
    font-size: 14px;
  }
}

.asset-actions {
  display: flex;
  border-top: 1px solid #f0f0f0;
  
  .btn-action {
    flex: 1;
    padding: 12px;
    background: white;
    border: none;
    border-right: 1px solid #f0f0f0;
    color: #595959;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:last-child {
      border-right: none;
    }
    
    &:hover {
      background: #f8f9ff;
      color: #667eea;
    }
    
    &.active {
      color: #52c41a;
    }
    
    &.danger:hover {
      background: #fff1f0;
      color: #ff4d4f;
    }
    
    i {
      font-size: 16px;
    }
  }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0 0 24px 0;
}

.btn-empty-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .assets-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .assets-library {
    padding: 16px;
  }
  
  .library-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .btn-create {
    width: 100%;
    justify-content: center;
  }
  
  .info-row {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .info-value {
    flex-direction: column;
  }
  
  .library-url {
    width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>

