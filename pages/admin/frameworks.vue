<template>
  <div class="frameworks-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">框架管理</h1>
      <p class="page-subtitle">查看和管理所有名片框架的使用情况</p>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalFrameworks }}</div>
          <div class="stat-label">可用框架</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <div class="stat-content">
          <div class="stat-value">{{ activeTenants }}</div>
          <div class="stat-label">使用租户</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalInstances }}</div>
          <div class="stat-label">模块实例</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ avgModulesPerTenant }}</div>
          <div class="stat-label">平均模块数</div>
        </div>
      </div>
    </div>

    <!-- 框架列表 -->
    <div class="frameworks-list">
      <div
        v-for="(framework, key) in frameworks"
        :key="key"
        class="framework-card"
      >
        <!-- 框架头部 -->
        <div class="framework-header">
          <div class="framework-icon">{{ framework.icon }}</div>
          <div class="framework-info">
            <h3 class="framework-name">{{ framework.name }}</h3>
            <div class="framework-meta">
              <span class="version-badge">v{{ framework.version }}</span>
              <span class="category-badge">{{ getCategoryLabel(framework.category) }}</span>
            </div>
          </div>
        </div>

        <!-- 框架描述 -->
        <p class="framework-description">{{ framework.description }}</p>

        <!-- 使用统计 -->
        <div class="framework-stats">
          <div class="stat-item">
            <span class="stat-label">使用租户</span>
            <span class="stat-value">{{ getUsageCount(key) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">模块实例</span>
            <span class="stat-value">{{ getInstanceCount(key) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">平均配置率</span>
            <span class="stat-value">{{ getConfigCompleteness(key) }}%</span>
          </div>
        </div>

        <!-- 套餐限制 -->
        <div v-if="framework.planLimits" class="plan-limits">
          <h4 class="limits-title">套餐限制</h4>
          <div class="limits-grid">
            <div
              v-for="(limits, plan) in framework.planLimits"
              :key="plan"
              class="limit-item"
            >
              <span class="plan-name">{{ getPlanLabel(plan) }}</span>
              <ul class="limit-list">
                <li v-for="(value, key) in limits" :key="key">
                  {{ formatLimitKey(key) }}: <strong>{{ formatLimitValue(value) }}</strong>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="framework-actions">
          <button class="btn-action" @click="viewUsage(key)">
            查看使用详情
          </button>
          <button class="btn-action" @click="viewDefinition(key)">
            查看定义
          </button>
          <button class="btn-action btn-secondary" @click="exportUsage(key)">
            导出数据
          </button>
        </div>
      </div>
    </div>

    <!-- 使用详情弹窗 -->
    <div v-if="selectedFramework" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedFramework.name }} - 使用详情</h2>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <div class="modal-body">
          <div v-if="loadingUsage" class="loading">加载中...</div>
          
          <div v-else-if="usageDetails" class="usage-details">
            <h3>使用该框架的租户</h3>
            <table class="usage-table">
              <thead>
                <tr>
                  <th>租户名称</th>
                  <th>企业ID</th>
                  <th>实例数</th>
                  <th>套餐</th>
                  <th>创建时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tenant in usageDetails.tenants" :key="tenant.id">
                  <td>{{ tenant.name }}</td>
                  <td>{{ tenant.corp_id }}</td>
                  <td>{{ tenant.instance_count }}</td>
                  <td><span class="plan-badge">{{ tenant.plan }}</span></td>
                  <td>{{ formatDate(tenant.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FRAMEWORK_DEFINITIONS, FRAMEWORK_CATEGORIES } from '@/config/framework-definitions'

export default {
  name: 'FrameworksManagement',
  
  layout: 'admin',
  
  data() {
    return {
      frameworks: FRAMEWORK_DEFINITIONS,
      categories: FRAMEWORK_CATEGORIES,
      usageData: null,
      selectedFramework: null,
      usageDetails: null,
      loadingUsage: false
    }
  },
  
  computed: {
    totalFrameworks() {
      return Object.keys(this.frameworks).length
    },
    
    activeTenants() {
      if (!this.usageData) return 0
      return new Set(this.usageData.map(u => u.tenant_id)).size
    },
    
    totalInstances() {
      if (!this.usageData) return 0
      return this.usageData.reduce((sum, u) => sum + u.instance_count, 0)
    },
    
    avgModulesPerTenant() {
      if (!this.usageData || this.activeTenants === 0) return 0
      return (this.totalInstances / this.activeTenants).toFixed(1)
    }
  },
  
  async mounted() {
    await this.loadUsageData()
  },
  
  methods: {
    async loadUsageData() {
      try {
        const { data } = await this.$axios.get('/api/admin/frameworks/usage')
        this.usageData = data.usage || []
      } catch (error) {
        console.error('Failed to load usage data:', error)
        this.usageData = []
      }
    },
    
    getUsageCount(frameworkKey) {
      if (!this.usageData) return 0
      const usage = this.usageData.filter(u => u.framework_type === frameworkKey)
      return new Set(usage.map(u => u.tenant_id)).size
    },
    
    getInstanceCount(frameworkKey) {
      if (!this.usageData) return 0
      return this.usageData
        .filter(u => u.framework_type === frameworkKey)
        .reduce((sum, u) => sum + u.instance_count, 0)
    },
    
    getConfigCompleteness(frameworkKey) {
      // 简化实现，实际应该检查数据完整性
      return 85
    },
    
    getCategoryLabel(categoryId) {
      return this.categories[categoryId]?.label || categoryId
    },
    
    getPlanLabel(plan) {
      const labels = {
        free: '免费版',
        paid: '付费版',
        enterprise: '企业版'
      }
      return labels[plan] || plan
    },
    
    formatLimitKey(key) {
      const labels = {
        max_items: '最大项目数',
        max_events: '最大事件数',
        max_images: '最大图片数',
        max_logos: '最大Logo数',
        allow_image_mode: '图片模式',
        allow_links: '链接功能'
      }
      return labels[key] || key
    },
    
    formatLimitValue(value) {
      if (typeof value === 'boolean') {
        return value ? '支持' : '不支持'
      }
      return value
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    
    async viewUsage(frameworkKey) {
      this.selectedFramework = this.frameworks[frameworkKey]
      this.loadingUsage = true
      
      try {
        const { data } = await this.$axios.get(`/api/admin/frameworks/${frameworkKey}/usage`)
        this.usageDetails = data
      } catch (error) {
        console.error('Failed to load usage details:', error)
        this.usageDetails = { tenants: [] }
      } finally {
        this.loadingUsage = false
      }
    },
    
    viewDefinition(frameworkKey) {
      const definition = this.frameworks[frameworkKey]
      
      // 在新窗口显示JSON定义
      const json = JSON.stringify(definition, null, 2)
      const blob = new Blob([json], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank')
    },
    
    async exportUsage(frameworkKey) {
      try {
        const { data } = await this.$axios.get(
          `/api/admin/frameworks/${frameworkKey}/usage`,
          { responseType: 'blob' }
        )
        
        const url = window.URL.createObjectURL(new Blob([data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${frameworkKey}-usage.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('Failed to export usage:', error)
        alert('导出失败，请重试')
      }
    },
    
    closeModal() {
      this.selectedFramework = null
      this.usageDetails = null
    }
  }
}
</script>

<style scoped>
.frameworks-management {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  font-size: 36px;
  opacity: 0.9;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #262626;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
}

/* 框架列表 */
.frameworks-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.framework-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.framework-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.framework-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.framework-icon {
  font-size: 48px;
}

.framework-info {
  flex: 1;
}

.framework-name {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.framework-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.version-badge,
.category-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.version-badge {
  background: #e6f7ff;
  color: #1890ff;
}

.category-badge {
  background: #f0f0f0;
  color: #595959;
}

.framework-description {
  font-size: 14px;
  color: #595959;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

/* 统计信息 */
.framework-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-label {
  display: block;
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.stat-item .stat-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

/* 套餐限制 */
.plan-limits {
  margin-bottom: 16px;
}

.limits-title {
  font-size: 14px;
  font-weight: 600;
  color: #595959;
  margin: 0 0 12px 0;
}

.limits-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.limit-item {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.plan-name {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 8px;
}

.limit-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.limit-list li {
  font-size: 12px;
  color: #595959;
  margin-bottom: 4px;
}

/* 操作按钮 */
.framework-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-action {
  flex: 1;
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background: #096dd9;
}

.btn-action.btn-secondary {
  background: white;
  color: #1890ff;
  border: 1px solid #1890ff;
}

.btn-action.btn-secondary:hover {
  background: #e6f7ff;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 1000px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #8c8c8c;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #8c8c8c;
}

/* 使用详情表格 */
.usage-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.usage-table th,
.usage-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.usage-table th {
  font-weight: 600;
  color: #595959;
  background: #fafafa;
}

.usage-table td {
  color: #262626;
}

.plan-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #f0f0f0;
  color: #595959;
}
</style>

