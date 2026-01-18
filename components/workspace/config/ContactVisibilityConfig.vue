<template>
  <div class="config-section contact-visibility-config">
    <div class="section-header">
      <h3 class="section-title">
        <span class="icon">👁️</span>
        联系方式显示控制
      </h3>
      <p class="section-desc">
        选择在名片中显示哪些联系方式，数据将从企业微信组织架构自动同步
      </p>
    </div>

    <div class="section-body">
      <!-- 联系方式切换开关 -->
      <div class="contact-toggles">
        <div 
          v-for="contact in contactFields"
          :key="contact.key"
          class="toggle-item"
        >
          <div class="toggle-content">
            <div class="toggle-icon">
              <i :class="contact.icon"></i>
            </div>
            <div class="toggle-info">
              <div class="toggle-label">{{ contact.label }}</div>
              <div class="toggle-hint">{{ contact.hint }}</div>
            </div>
          </div>
          <label class="switch">
            <input
              v-model="localVisibility[contact.key]"
              type="checkbox"
              @change="handleChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <!-- 同步提示 -->
      <div class="sync-notice">
        <i class="icon-info"></i>
        <div class="notice-content">
          <strong>自动同步说明：</strong>
          <p>手机号、邮箱、座机、地址等信息将从企业微信通讯录自动同步。微信号需要员工自行填写。</p>
        </div>
      </div>

      <!-- 同步按钮 -->
      <div class="sync-actions">
        <button 
          class="btn-sync"
          @click="triggerSync"
          :disabled="syncing"
        >
          <i class="icon-refresh" :class="{ spinning: syncing }"></i>
          {{ syncing ? '同步中...' : '立即从企微同步' }}
        </button>
        <span v-if="lastSyncTime" class="sync-time">
          上次同步：{{ formatTime(lastSyncTime) }}
        </span>
      </div>

      <!-- 企业联系信息配置 -->
      <div class="section-divider"></div>
      
      <div class="section-header">
        <h3 class="section-title">
          <span class="icon">🏢</span>
          企业联系信息
        </h3>
        <p class="section-desc">
          设置企业级联系信息（全体员工共享），这些信息将显示在所有员工的名片中
        </p>
      </div>

      <div class="company-info-form">
        <div class="form-group">
          <label class="form-label">
            <i class="icon-phone"></i>
            公司座机
          </label>
          <input
            v-model="localCompanyInfo.phone"
            type="tel"
            class="form-input"
            placeholder="如：0571-88888888"
            @input="handleCompanyInfoChange"
          />
          <span class="form-hint">显示在名片的联系方式中（需开启"座机号码"显示）</span>
        </div>

        <div class="form-group">
          <label class="form-label">
            <i class="icon-location"></i>
            办公地址
          </label>
          <input
            v-model="localCompanyInfo.address"
            type="text"
            class="form-input"
            placeholder="如：浙江省杭州市滨江区XX路XX号"
            @input="handleCompanyInfoChange"
          />
          <span class="form-hint">显示在名片的联系方式中（需开启"办公地址"显示）</span>
        </div>

        <div class="form-group">
          <label class="form-label">
            <i class="icon-website"></i>
            公司官网
          </label>
          <input
            v-model="localCompanyInfo.website"
            type="url"
            class="form-input"
            placeholder="如：https://www.example.com"
            @input="handleCompanyInfoChange"
          />
          <span class="form-hint">显示在名片的联系方式中（需开启"公司官网"显示）</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactVisibilityConfig',
  
  props: {
    value: {
      type: Object,
      default: () => ({
        mobile: true,
        email: true,
        wechat: true,
        phone: false,
        address: true,
        website: true
      })
    },
    companyInfo: {
      type: Object,
      default: () => ({
        phone: '',
        address: '',
        website: ''
      })
    },
    lastSyncTime: {
      type: [String, Number, Date],
      default: null
    }
  },
  
  data() {
    return {
      localVisibility: { ...this.value },
      localCompanyInfo: { ...this.companyInfo },
      syncing: false,
      contactFields: [
        {
          key: 'mobile',
          label: '手机号码',
          hint: '从企微自动同步',
          icon: 'icon-mobile'
        },
        {
          key: 'email',
          label: '邮箱地址',
          hint: '从企微自动同步',
          icon: 'icon-email'
        },
        {
          key: 'wechat',
          label: '微信号',
          hint: '需要员工手动填写',
          icon: 'icon-wechat'
        },
        {
          key: 'phone',
          label: '座机号码',
          hint: '从企微自动同步',
          icon: 'icon-phone'
        },
        {
          key: 'address',
          label: '办公地址',
          hint: '从企微自动同步',
          icon: 'icon-location'
        },
        {
          key: 'website',
          label: '公司官网',
          hint: '从企微自动同步',
          icon: 'icon-website'
        }
      ]
    }
  },
  
  watch: {
    value: {
      handler(newVal) {
        this.localVisibility = { ...newVal }
      },
      deep: true
    },
    companyInfo: {
      handler(newVal) {
        this.localCompanyInfo = { ...newVal }
      },
      deep: true
    }
  },
  
  methods: {
    handleChange() {
      this.$emit('input', { ...this.localVisibility })
    },
    
    handleCompanyInfoChange() {
      this.$emit('company-info-change', { ...this.localCompanyInfo })
    },
    
    async triggerSync() {
      this.syncing = true
      
      // 防止页面跳转或关闭
      const originalOnBeforeUnload = window.onbeforeunload
      window.onbeforeunload = () => {
        if (this.syncing) {
          return '正在同步数据，请稍候...'
        }
      }
      
      try {
        console.log('🔄 开始同步企微通讯录...')
        console.log('🔑 当前token:', this.$wecomAuth?.getToken()?.substring(0, 20) + '...')
        
        // 检查token是否存在
        const token = this.$wecomAuth?.getToken()
        if (!token) {
          throw new Error('登录状态已失效，请刷新页面重新登录')
        }
        
        // 调用同步API（禁用axios拦截器的自动重定向）
        const response = await this.$axios.post('/api/v1/wecom/sync-members', {}, {
          timeout: 60000, // 60秒超时
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          // 添加标记防止401自动跳转
          skipAuthRedirect: true
        })
        
        console.log('✅ 同步响应:', response.data)
        
        if (response.data && response.data.success) {
          const count = response.data.count || 0
          const created = response.data.created || 0
          const updated = response.data.updated || 0
          const deactivated = response.data.deactivated || 0
          
          // 构建消息
          let message = `成功同步 ${count} 位在职成员`
          const details = []
          if (created > 0) details.push(`新增${created}位`)
          if (updated > 0) details.push(`更新${updated}位`)
          if (deactivated > 0) details.push(`停用${deactivated}位`)
          if (details.length > 0) {
            message += `（${details.join('，')}）`
          }
          
          this.$toast?.success(message)
          this.$emit('sync-complete', response.data)
        } else {
          throw new Error(response.data?.message || response.data?.error || '同步失败')
        }
      } catch (error) {
        console.error('❌ 同步失败:', error)
        console.error('❌ 错误详情:', error.response?.data)
        
        let errorMsg = '同步失败，请重试'
        let shouldRefresh = false
        
        if (error.response) {
          // 服务器返回错误
          const data = error.response.data
          errorMsg = data?.message || data?.error || errorMsg
          
          // 处理特定错误码
          if (error.response.status === 401) {
            errorMsg = data?.message || '登录已过期，请刷新页面重新登录'
            shouldRefresh = true
          } else if (data?.code === 'PERMANENT_CODE_MISSING') {
            errorMsg = '企业授权信息不完整，请重新安装应用'
          } else if (data?.code === 'TENANT_NOT_FOUND') {
            errorMsg = '未找到企业信息，请联系管理员'
          }
        } else if (error.request) {
          // 请求发送但没有响应
          errorMsg = '网络请求超时，请检查网络连接'
        } else if (error.message) {
          errorMsg = error.message
        }
        
        this.$toast?.error(errorMsg)
        
        // 如果是认证问题，提示用户刷新
        if (shouldRefresh) {
          setTimeout(() => {
            if (confirm('登录已过期，是否刷新页面重新登录？')) {
              window.location.reload()
            }
          }, 1500)
        }
      } finally {
        this.syncing = false
        // 恢复原来的beforeunload处理
        window.onbeforeunload = originalOnBeforeUnload
        console.log('🔄 同步操作结束')
      }
    },
    
    formatTime(time) {
      if (!time) return '从未同步'
      const date = new Date(time)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style lang="scss" scoped>
.contact-visibility-config {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 8px 0;
}

.section-title .icon {
  font-size: 24px;
}

.section-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

.contact-toggles {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: white;
  border-radius: 14px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.toggle-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.toggle-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.toggle-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}

.toggle-info {
  flex: 1;
}

.toggle-label {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.toggle-hint {
  font-size: 12px;
  color: #94a3b8;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: 0.3s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

input:checked + .slider {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

input:checked + .slider:before {
  transform: translateX(22px);
}

/* 同步提示 */
.sync-notice {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  border-left: 4px solid #f59e0b;
  margin-bottom: 20px;
}

.sync-notice .icon-info {
  font-size: 20px;
  color: #92400e;
  flex-shrink: 0;
}

.sync-notice .icon-info::before {
  content: 'ℹ️';
}

.notice-content {
  flex: 1;
}

.notice-content strong {
  font-size: 14px;
  color: #92400e;
  display: block;
  margin-bottom: 4px;
}

.notice-content p {
  font-size: 13px;
  color: #78350f;
  margin: 0;
  line-height: 1.5;
}

/* 同步操作 */
.sync-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-sync {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-sync:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-sync:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.icon-refresh::before {
  content: '🔄';
}

.icon-refresh.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.sync-time {
  font-size: 13px;
  color: #64748b;
}

/* 图标字体 */
.icon-mobile::before { content: "📱"; }
.icon-email::before { content: "✉️"; }
.icon-wechat::before { content: "💬"; }
.icon-phone::before { content: "☎️"; }
.icon-location::before { content: "📍"; }
.icon-website::before { content: "🌐"; }

/* 分隔线 */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
  margin: 32px 0;
}

/* 企业信息表单 */
.company-info-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label i {
  font-size: 16px;
}

.form-input {
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: #1f2937;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-hint {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.5;
}
</style>

