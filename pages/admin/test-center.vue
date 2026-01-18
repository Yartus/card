<template>
  <div class="test-center-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>WeCard 测试中心</h1>
      <p>快速创建测试租户，验证名片和素材库效果</p>
    </div>
    
    <!-- 快速测试区 -->
    <div class="quick-test-section">
      <div class="test-card">
        <h2>🚀 快速测试</h2>
        <p>一键创建测试租户并查看效果</p>
        
        <div class="quick-form">
          <div class="form-row">
            <input 
              v-model="quickForm.companyName" 
              type="text" 
              placeholder="企业名称（如：科技创新公司）"
              class="form-input"
            />
            <select v-model="quickForm.industry" class="form-select">
              <option value="technology">科技互联网</option>
              <option value="finance">金融服务</option>
              <option value="manufacturing">制造业</option>
              <option value="education">教育培训</option>
              <option value="healthcare">医疗健康</option>
            </select>
          </div>
          
          <div class="form-row">
            <input 
              v-model="quickForm.employeeName" 
              type="text" 
              placeholder="员工姓名（如：张经理）"
              class="form-input"
            />
            <input 
              v-model="quickForm.employeeTitle" 
              type="text" 
              placeholder="职位（如：销售总监）"
              class="form-input"
            />
          </div>
          
          <button 
            @click="createQuickTest" 
            :disabled="creating"
            class="create-btn"
          >
            {{ creating ? '创建中...' : '🎯 创建测试租户' }}
          </button>
        </div>
      </div>
      
      <!-- 测试结果展示 -->
      <div v-if="lastCreatedTenant" class="test-result">
        <h3>✅ 测试租户创建成功</h3>
        <div class="tenant-info">
          <div class="info-item">
            <strong>企业名称：</strong>{{ lastCreatedTenant.company_name }}
          </div>
          <div class="info-item">
            <strong>租户ID：</strong>{{ lastCreatedTenant.id }}
          </div>
          <div class="info-item">
            <strong>创建时间：</strong>{{ formatDate(lastCreatedTenant.created_at) }}
          </div>
        </div>
        
        <div class="test-actions">
          <button @click="previewCard(lastCreatedTenant)" class="action-btn primary">
            📱 预览名片
          </button>
          <button @click="viewAssets(lastCreatedTenant)" class="action-btn secondary">
            📁 查看素材库
          </button>
          <button @click="testShare(lastCreatedTenant)" class="action-btn info">
            📤 测试分享
          </button>
          <button @click="copyUrls(lastCreatedTenant)" class="action-btn success">
            📋 复制链接
          </button>
        </div>
      </div>
    </div>
    
    <!-- 现有测试租户 -->
    <div class="existing-tenants-section">
      <h2>📋 现有测试租户</h2>
      
      <div v-if="testTenants.length === 0" class="empty-state">
        <p>暂无测试租户，请先创建一个测试租户</p>
      </div>
      
      <div v-else class="tenants-grid">
        <div 
          v-for="tenant in testTenants" 
          :key="tenant.id"
          class="tenant-card"
        >
          <div class="tenant-header">
            <div class="company-info">
              <h3>{{ tenant.company_name }}</h3>
              <p>{{ tenant.industry }} | {{ tenant.id }}</p>
            </div>
            <div class="tenant-status">
              <span class="status-badge active">活跃</span>
            </div>
          </div>
          
          <div class="tenant-stats">
            <div class="stat-item">
              <span class="stat-value">{{ tenant.asset_count || 0 }}</span>
              <span class="stat-label">素材数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ tenant.view_count || 0 }}</span>
              <span class="stat-label">浏览量</span>
            </div>
          </div>
          
          <div class="tenant-actions">
            <button @click="previewCard(tenant)" class="mini-btn">
              📱 名片
            </button>
            <button @click="viewAssets(tenant)" class="mini-btn">
              📁 素材库
            </button>
            <button @click="testShare(tenant)" class="mini-btn">
              📤 分享
            </button>
            <button @click="deleteTenant(tenant)" class="mini-btn danger">
              🗑️ 删除
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分享测试模态框 -->
    <div v-if="sharingTenant" class="modal-overlay" @click="sharingTenant = null">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ sharingTenant.company_name }} - 分享测试</h3>
          <button @click="sharingTenant = null" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="share-links">
            <div class="link-item">
              <label>名片链接：</label>
              <div class="link-input">
                <input :value="getCardUrl(sharingTenant)" readonly />
                <button @click="copyLink(getCardUrl(sharingTenant))" class="copy-btn">复制</button>
                <button @click="openLink(getCardUrl(sharingTenant))" class="open-btn">打开</button>
              </div>
            </div>
            
            <div class="link-item">
              <label>素材库链接：</label>
              <div class="link-input">
                <input :value="getAssetsUrl(sharingTenant)" readonly />
                <button @click="copyLink(getAssetsUrl(sharingTenant))" class="copy-btn">复制</button>
                <button @click="openLink(getAssetsUrl(sharingTenant))" class="open-btn">打开</button>
              </div>
            </div>
          </div>
          
          <div class="share-preview">
            <h4>微信分享预览</h4>
            <div class="wechat-card">
              <div class="wechat-image">🏢</div>
              <div class="wechat-content">
                <h5>{{ sharingTenant.company_name }} - 企业名片</h5>
                <p>{{ sharingTenant.company_name }}的数字名片，了解我们的产品服务和企业信息。</p>
                <small>来自 WeCard</small>
              </div>
            </div>
          </div>
          
          <div class="test-tools">
            <h4>测试工具</h4>
            <div class="tool-buttons">
              <button @click="testSEO(sharingTenant)" class="tool-btn">
                🔍 SEO检查
              </button>
              <button @click="testSpeed(sharingTenant)" class="tool-btn">
                ⚡ 速度测试
              </button>
              <button @click="generateQR(sharingTenant)" class="tool-btn">
                📱 生成二维码
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestCenterPage',
  
  middleware: 'auth',
  
  data() {
    return {
      creating: false,
      testTenants: [],
      lastCreatedTenant: null,
      sharingTenant: null,
      quickForm: {
        companyName: '',
        industry: 'technology',
        employeeName: '',
        employeeTitle: ''
      }
    }
  },
  
  async mounted() {
    await this.loadTestTenants()
  },
  
  methods: {
    async loadTestTenants() {
      try {
        // 模拟API调用 - 实际应该调用真实API
        // const { data } = await this.$axios.get('/api/admin/test-tenants')
        // this.testTenants = data.tenants
        
        // 临时模拟数据
        this.testTenants = JSON.parse(localStorage.getItem('wecard_test_tenants') || '[]')
      } catch (error) {
        console.error('加载测试租户失败:', error)
      }
    },
    
    async createQuickTest() {
      if (!this.quickForm.companyName || !this.quickForm.employeeName) {
        this.$toast.error('请填写企业名称和员工姓名')
        return
      }
      
      this.creating = true
      
      try {
        // 生成测试租户数据
        const tenantId = `test_${Date.now()}`
        const tenant = {
          id: tenantId,
          company_name: this.quickForm.companyName,
          industry: this.quickForm.industry,
          employee_name: this.quickForm.employeeName,
          employee_title: this.quickForm.employeeTitle,
          created_at: new Date().toISOString(),
          asset_count: Math.floor(Math.random() * 10) + 3,
          view_count: Math.floor(Math.random() * 100) + 10
        }
        
        // 保存到本地存储（实际应该调用API）
        this.testTenants.unshift(tenant)
        localStorage.setItem('wecard_test_tenants', JSON.stringify(this.testTenants))
        
        this.lastCreatedTenant = tenant
        this.$toast.success('测试租户创建成功！')
        
        // 清空表单
        this.quickForm = {
          companyName: '',
          industry: 'technology',
          employeeName: '',
          employeeTitle: ''
        }
        
      } catch (error) {
        console.error('创建失败:', error)
        this.$toast.error('创建失败，请重试')
      } finally {
        this.creating = false
      }
    },
    
    previewCard(tenant) {
      // 使用现有的完善预览系统
      const url = `/card-preview?test_tenant=${tenant.id}&company=${encodeURIComponent(tenant.company_name)}&employee=${encodeURIComponent(tenant.employee_name)}&title=${encodeURIComponent(tenant.employee_title)}`
      if (typeof window !== 'undefined') window.open(url, '_blank')
    },
    
    viewAssets(tenant) {
      const url = `/assets/${tenant.id}`
      if (typeof window !== 'undefined') window.open(url, '_blank')
    },
    
    testShare(tenant) {
      this.sharingTenant = tenant
    },
    
    async copyUrls(tenant) {
      const cardUrl = this.getCardUrl(tenant)
      const assetsUrl = this.getAssetsUrl(tenant)
      const text = `${tenant.company_name} 测试链接：\n名片：${cardUrl}\n素材库：${assetsUrl}`
      
      try {
        await navigator.clipboard.writeText(text)
        this.$toast.success('链接已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        this.$toast.error('复制失败')
      }
    },
    
    async deleteTenant(tenant) {
      if (!confirm(`确定要删除测试租户"${tenant.company_name}"吗？`)) return
      
      try {
        // 从本地存储删除（实际应该调用API）
        const index = this.testTenants.findIndex(t => t.id === tenant.id)
        if (index > -1) {
          this.testTenants.splice(index, 1)
          localStorage.setItem('wecard_test_tenants', JSON.stringify(this.testTenants))
        }
        
        this.$toast.success('删除成功')
      } catch (error) {
        console.error('删除失败:', error)
        this.$toast.error('删除失败')
      }
    },
    
    getCardUrl(tenant) {
      return typeof window !== 'undefined' ? `${window.location.origin}/card/${tenant.id}` : ''
    },
    
    getAssetsUrl(tenant) {
      return typeof window !== 'undefined' ? `${window.location.origin}/assets/${tenant.id}` : ''
    },
    
    async copyLink(url) {
      try {
        await navigator.clipboard.writeText(url)
        this.$toast.success('链接已复制')
      } catch (error) {
        this.$toast.error('复制失败')
      }
    },
    
    openLink(url) {
      if (typeof window !== 'undefined') window.open(url, '_blank')
    },
    
    testSEO(tenant) {
      const url = `https://www.google.com/search?q=site:${encodeURIComponent(this.getCardUrl(tenant))}`
      if (typeof window !== 'undefined') window.open(url, '_blank')
    },
    
    testSpeed(tenant) {
      const url = `https://pagespeed.web.dev/report?url=${encodeURIComponent(this.getCardUrl(tenant))}`
      if (typeof window !== 'undefined') window.open(url, '_blank')
    },
    
    generateQR(tenant) {
      // 简单的二维码生成（实际应该使用专业的二维码库）
      const url = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(this.getCardUrl(tenant))}`
      if (typeof window !== 'undefined') window.open(url, '_blank')
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style lang="scss" scoped>
.test-center-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  
  h1 {
    font-size: 32px;
    color: #262626;
    margin-bottom: 8px;
  }
  
  p {
    color: #8c8c8c;
    font-size: 16px;
  }
}

.quick-test-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  h2 {
    color: #262626;
    margin-bottom: 8px;
  }
  
  p {
    color: #8c8c8c;
    margin-bottom: 20px;
  }
}

.quick-form {
  .form-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .form-input, .form-select {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    font-size: 14px;
    
    &:focus {
      border-color: #1890FF;
      outline: none;
    }
  }
  
  .create-btn {
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, #1890FF, #40a9ff);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
    }
    
    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  }
}

.test-result {
  margin-top: 24px;
  padding: 20px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
  
  h3 {
    color: #52c41a;
    margin-bottom: 16px;
  }
  
  .tenant-info {
    margin-bottom: 16px;
    
    .info-item {
      margin-bottom: 8px;
      font-size: 14px;
      
      strong {
        color: #262626;
      }
    }
  }
  
  .test-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  
  .action-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    
    &.primary {
      background: #1890FF;
      color: white;
      
      &:hover {
        background: #40a9ff;
      }
    }
    
    &.secondary {
      background: #f0f0f0;
      color: #595959;
      
      &:hover {
        background: #e6e6e6;
      }
    }
    
    &.info {
      background: #e6f7ff;
      color: #1890FF;
      
      &:hover {
        background: #bae7ff;
      }
    }
    
    &.success {
      background: #f6ffed;
      color: #52c41a;
      
      &:hover {
        background: #d9f7be;
      }
    }
  }
}

.existing-tenants-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  h2 {
    color: #262626;
    margin-bottom: 20px;
  }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #8c8c8c;
}

.tenants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.tenant-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
  
  &:hover {
    border-color: #1890FF;
    box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  }
}

.tenant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  
  .company-info {
    h3 {
      font-size: 16px;
      color: #262626;
      margin-bottom: 4px;
    }
    
    p {
      font-size: 12px;
      color: #8c8c8c;
    }
  }
  
  .status-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    
    &.active {
      background: #f6ffed;
      color: #52c41a;
    }
  }
}

.tenant-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  
  .stat-item {
    text-align: center;
    
    .stat-value {
      display: block;
      font-size: 18px;
      font-weight: 600;
      color: #262626;
    }
    
    .stat-label {
      font-size: 11px;
      color: #8c8c8c;
    }
  }
}

.tenant-actions {
  display: flex;
  gap: 6px;
  
  .mini-btn {
    flex: 1;
    padding: 6px 8px;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    background: white;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      border-color: #1890FF;
      color: #1890FF;
    }
    
    &.danger:hover {
      border-color: #ff4d4f;
      color: #ff4d4f;
    }
  }
}

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
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    color: #262626;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #8c8c8c;
    
    &:hover {
      color: #262626;
    }
  }
}

.modal-body {
  padding: 20px;
}

.share-links {
  margin-bottom: 24px;
  
  .link-item {
    margin-bottom: 16px;
    
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: #262626;
    }
    
    .link-input {
      display: flex;
      gap: 8px;
      
      input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #d9d9d9;
        border-radius: 4px;
        font-size: 12px;
        background: #fafafa;
      }
      
      button {
        padding: 8px 12px;
        border: 1px solid #d9d9d9;
        border-radius: 4px;
        background: white;
        font-size: 12px;
        cursor: pointer;
        
        &:hover {
          border-color: #1890FF;
          color: #1890FF;
        }
      }
    }
  }
}

.share-preview {
  margin-bottom: 24px;
  
  h4 {
    margin-bottom: 12px;
    color: #262626;
  }
  
  .wechat-card {
    display: flex;
    gap: 12px;
    padding: 12px;
    border: 1px solid #e6e6e6;
    border-radius: 8px;
    background: #fafafa;
    
    .wechat-image {
      width: 60px;
      height: 60px;
      background: #f0f0f0;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
    }
    
    .wechat-content {
      flex: 1;
      
      h5 {
        margin: 0 0 4px 0;
        font-size: 14px;
        color: #262626;
      }
      
      p {
        margin: 0 0 8px 0;
        font-size: 12px;
        color: #8c8c8c;
        line-height: 1.4;
      }
      
      small {
        font-size: 11px;
        color: #bfbfbf;
      }
    }
  }
}

.test-tools {
  h4 {
    margin-bottom: 12px;
    color: #262626;
  }
  
  .tool-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    
    .tool-btn {
      padding: 8px 12px;
      border: 1px solid #d9d9d9;
      border-radius: 4px;
      background: white;
      font-size: 12px;
      cursor: pointer;
      
      &:hover {
        border-color: #1890FF;
        color: #1890FF;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .test-center-page {
    padding: 16px;
  }
  
  .quick-form .form-row {
    flex-direction: column;
  }
  
  .test-actions {
    flex-direction: column;
    
    .action-btn {
      width: 100%;
    }
  }
  
  .tenants-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>
