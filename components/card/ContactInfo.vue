<template>
  <div class="contact-info ci-light">
    <div class="section-header">
      <h3 class="section-title">联系方式</h3>
      <button 
        v-if="hasHiddenContacts"
        class="toggle-btn"
        @click="toggleDetails"
      >
        {{ showDetails ? '收起' : '展开' }}
      </button>
    </div>
    
    <div class="contact-list">
      <!-- 主要联系方式（始终显示） -->
      <div 
        v-for="contact in primaryContacts"
        :key="contact.type"
        :class="['contact-item', 'primary', contact.themeClass]"
        @click="handleContactClick(contact)"
      >
        <div class="contact-icon">
          <i :class="contact.icon"></i>
        </div>
        <div class="contact-content">
          <div class="contact-label">{{ contact.label }}</div>
          <div class="contact-value">{{ contact.displayValue || contact.value }}</div>
        </div>
        <div class="contact-action">
          <i class="icon-arrow-right"></i>
        </div>
      </div>
      
      <!-- 次要联系方式（可折叠） -->
      <div 
        v-if="showDetails"
        class="secondary-contacts"
      >
        <div 
          v-for="contact in secondaryContacts"
          :key="contact.type"
          :class="['contact-item', 'secondary', contact.themeClass]"
          @click="handleContactClick(contact)"
        >
          <div class="contact-icon">
            <i :class="contact.icon"></i>
          </div>
          <div class="contact-content">
            <div class="contact-label">{{ contact.label }}</div>
            <div class="contact-value">{{ contact.displayValue || contact.value }}</div>
          </div>
          <div class="contact-action">
            <i class="icon-arrow-right"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactInfo',
  
  props: {
    contactInfo: {
      type: Object,
      required: true,
      default: () => ({})
    },
    initialShowDetails: {
      type: Boolean,
      default: true
    },
    // 隐藏指定类型（用于避免与 QuickActions 重复展示）
    hideTypes: {
      type: Array,
      default: () => []
    },
    // 联系方式显示控制（从workspace配置传入）
    contactVisibility: {
      type: Object,
      default: () => ({
        mobile: true,
        email: true,
        wechat: true,
        phone: true,
        address: true,
        website: true
      })
    }
  },
  
  data() {
    return {
      detailsVisible: this.initialShowDetails
    }
  },
  
  computed: {
    // 主要联系方式（手机号码 - 根据配置显示）
    primaryContacts() {
      const contacts = []
      
      // 手机号始终作为主要联系方式
      if (
        this.contactInfo.mobile &&
        !this.hideTypes.includes('mobile') &&
        this.isFieldVisible('mobile')
      ) {
        contacts.push({
          type: 'mobile',
          label: '手机号码',
          value: this.contactInfo.mobile,
          displayValue: this.formatPhone(this.contactInfo.mobile),
          icon: 'icon-mobile',
          action: this.getDefaultAction('mobile'),
          themeClass: this.getThemeClass('mobile')
        })
      }
      
      return contacts
    },
    
    // 次要联系方式（根据配置显示/隐藏）
    secondaryContacts() {
      const contacts = []
      
      // 邮箱
      if (
        this.contactInfo.email &&
        !this.hideTypes.includes('email') &&
        this.isFieldVisible('email')
      ) {
        contacts.push({
          type: 'email',
          label: '邮箱地址',
          value: this.contactInfo.email,
          icon: 'icon-email',
          action: this.getDefaultAction('email'),
          themeClass: this.getThemeClass('email')
        })
      }
      
      // 微信
      if (
        this.contactInfo.wechat &&
        !this.hideTypes.includes('wechat') &&
        this.isFieldVisible('wechat')
      ) {
        contacts.push({
          type: 'wechat',
          label: '微信号',
          value: this.contactInfo.wechat,
          icon: 'icon-wechat',
          action: this.getDefaultAction('wechat'),
          themeClass: this.getThemeClass('wechat')
        })
      }
      
      // 座机
      if (this.contactInfo.phone && this.isFieldVisible('phone')) {
        contacts.push({
          type: 'phone',
          label: '座机号码',
          value: this.contactInfo.phone,
          displayValue: this.formatPhone(this.contactInfo.phone),
          icon: 'icon-phone',
          action: this.getDefaultAction('phone'),
          themeClass: this.getThemeClass('phone')
        })
      }
      
      // 地址
      if (
        this.contactInfo.address &&
        !this.hideTypes.includes('address') &&
        this.isFieldVisible('address')
      ) {
        contacts.push({
          type: 'address',
          label: '办公地址',
          value: this.contactInfo.address,
          icon: 'icon-location',
          action: this.getDefaultAction('address'),
          themeClass: this.getThemeClass('address')
        })
      }
      
      // 官网
      if (this.contactInfo.website && this.isFieldVisible('website')) {
        contacts.push({
          type: 'website',
          label: '公司官网',
          value: this.contactInfo.website,
          displayValue: this.formatWebsite(this.contactInfo.website),
          icon: 'icon-website',
          action: this.getDefaultAction('website'),
          themeClass: this.getThemeClass('website')
        })
      }

      // 自定义信息（可配置数组）
      if (Array.isArray(this.contactInfo.custom_items)) {
        for (const item of this.contactInfo.custom_items) {
          if (!item || !item.value) continue
          const t = item.type || 'custom'
          if (this.hideTypes.includes(t)) continue
          contacts.push({
            type: t,
            label: item.label || '其他信息',
            value: item.value,
            displayValue: item.displayValue || item.value,
            icon: item.icon || 'icon-custom',
            action: item.action || this.getDefaultAction(t),
            themeClass: this.getThemeClass(t, item.themeClass)
          })
        }
      }
      
      return contacts
    },
    
    // 合并后的可见性配置
    resolvedVisibility() {
      const defaults = {
        mobile: true,
        email: true,
        wechat: true,
        phone: true,
        address: true,
        website: true
      }
      return {
        ...defaults,
        ...(this.contactVisibility || {})
      }
    },
    
    // 是否有隐藏的联系方式
    hasHiddenContacts() {
      return this.secondaryContacts.length > 0
    },
    
    // 当前是否显示详情
    showDetails() {
      return this.detailsVisible
    }
  },
  
  methods: {
    // 切换详情显示
    toggleDetails() {
      this.detailsVisible = !this.detailsVisible
    },
    
    // 处理联系方式点击
    handleContactClick(contact) {
      this.$emit('contact-click', contact.type, contact.value, contact.action)
    },
    
    // 格式化电话号码
    formatPhone(phone) {
      if (!phone) return ''
      
      // 中国手机号格式化：138 0013 8000
      if (/^1[3-9]\d{9}$/.test(phone)) {
        return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1 $2 $3')
      }
      
      // 其他号码保持原样
      return phone
    },
    
    // 格式化网站地址
    formatWebsite(website) {
      if (!website) return ''
      
      // 移除协议前缀显示
      return website.replace(/^https?:\/\//, '')
    },

    getThemeClass(type, fallback) {
      if (fallback) return fallback
      
      const themeMap = {
        mobile: 'theme-mobile',
        phone: 'theme-phone',
        email: 'theme-email',
        wechat: 'theme-wechat',
        address: 'theme-address',
        website: 'theme-website',
        custom: 'theme-custom'
      }
      
      return themeMap[type] || 'theme-custom'
    },

    getDefaultAction(type) {
      switch (type) {
        case 'mobile':
        case 'phone':
          return 'call'
        case 'email':
          return 'email'
        case 'wechat':
          return 'copy'
        case 'address':
          return 'map'
        case 'website':
          return 'website'
        default:
          return 'none'
      }
    },

    isFieldVisible(type) {
      const visibility = this.resolvedVisibility
      return visibility[type] !== false
    }
  }
}
</script>

<style lang="scss" scoped>
.ci-light { 
  padding: 0;
  margin: 12px 16px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-header {
  padding: 20px 20px 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  border-bottom: 1px solid #f0f2f5;
}

.section-title { 
  font-size: 16px;
  font-weight: 700; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0; 
}

.toggle-btn {
  background: none;
  border: none;
  color: var(--primary-color, #1890FF);
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  
  &:hover {
    background: rgba(24, 144, 255, 0.1);
  }
}

.contact-list { 
  padding: 20px;
  padding-top: 0;
  display: flex; 
  flex-direction: column; 
  gap: 10px; 
}

.contact-item { 
  display:flex; 
  align-items:center; 
  gap:12px; 
  padding:12px 14px; 
  border-radius:14px; 
  cursor:pointer; 
  transition:all .3s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
  border: 1px solid rgba(102,126,234,.08);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}
.contact-item:hover { 
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
  border-color: #667eea;
  background: white;
}
.contact-item.primary { 
  background:white; 
  border:1px solid rgba(102,126,234,.14);
}
.contact-item.primary:hover { 
  border-color:#667eea; 
  background:white;
}

.contact-icon { 
  width:42px; 
  height:42px; 
  display:flex; 
  align-items:center; 
  justify-content:center; 
  border-radius:12px; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink:0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
.contact-icon i { 
  font-size:22px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.contact-content {
  flex: 1;
  min-width: 0;
}

.contact-label { font-size:11px; color:#8c8c8c; margin-bottom:2px; font-weight: 500; }

.contact-value { font-size:14px; color:#1f1f1f; font-weight:600; word-break:break-all; }

.contact-action {
  color: #bfbfbf;
  font-size: 12px;
  flex-shrink: 0;
}

.secondary-contacts { 
  display:flex; 
  flex-direction:column; 
  gap:6px; 
  margin-top:6px; 
  padding-top:8px; 
  border-top:1px solid #f0f2f5; 
}

// 统一胶囊主题颜色
.theme-mobile .contact-icon,
.theme-phone .contact-icon {
  background: linear-gradient(135deg, #13c2c2 0%, #0a9e9e 100%);
}

.theme-email .contact-icon {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
}

.theme-wechat .contact-icon {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
}

.theme-address .contact-icon {
  background: linear-gradient(135deg, #722ed1 0%, #531dab 100%);
}

.theme-website .contact-icon {
  background: linear-gradient(135deg, #fa8c16 0%, #d46b08 100%);
}

.theme-custom .contact-icon {
  background: linear-gradient(135deg, #eb2f96 0%, #c41d7f 100%);
}

// 响应式设计
@media (max-width: 480px) {
  .contact-info {
    padding: 16px;
  }
  
  .contact-item {
    padding: 10px;
    gap: 10px;
  }
  
  .contact-icon {
    width: 36px;
    height: 36px;
    
    i {
      font-size: 16px;
    }
  }
  
  .contact-value {
    font-size: 13px;
  }
}

// 图标字体
.icon-mobile::before { content: "📱"; }
.icon-wechat::before { content: "💬"; }
.icon-email::before { content: "✉️"; }
.icon-phone::before { content: "☎️"; }
.icon-website::before { content: "🌐"; }
.icon-location::before { content: "📍"; }
.icon-arrow-right::before { content: "›"; }
</style>
