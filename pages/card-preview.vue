<template>
  <div class="card-preview-page">
    <!-- 调试覆盖层：当出现运行时错误时可视化展示 -->
    <div v-if="uiError" class="debug-overlay">
      <div class="debug-card">
        <div class="debug-title">页面运行时错误</div>
        <div class="debug-body">
          <div class="debug-item"><strong>message:</strong> {{ uiError.message }}</div>
          <div class="debug-item" v-if="uiError.info"><strong>info:</strong> {{ uiError.info }}</div>
          <div class="debug-item" v-if="uiError.stack"><strong>stack:</strong>
            <pre class="debug-pre">{{ uiError.stack }}</pre>
          </div>
          <div class="debug-item" v-if="lastApiProbe"><strong>lastApiProbe:</strong>
            <pre class="debug-pre">{{ lastApiProbe }}</pre>
          </div>
        </div>
        <div class="debug-actions">
          <button class="debug-btn" @click="dismissError">我知道了（隐藏）</button>
        </div>
      </div>
    </div>
    <!-- 页面头部 -->
    <div class="preview-header">
      <h1>WeCard 名片预览</h1>
      <p>优化版名片组件效果预览</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="theme-selector">
        <label>主题选择：</label>
        <select v-model="currentTheme" @change="updateTheme">
          <option value="light">浅色科技</option>
          <option value="corporate">企业蓝</option>
          <option value="professional">专业灰</option>
          <option value="creative">创意橙</option>
          <option value="minimal">简约黑</option>
        </select>
      </div>
      
      <div class="data-selector">
        <label>测试数据：</label>
        <select v-model="currentDataSet" @change="updateData">
          <option value="demo1">张经理 - 科技公司</option>
          <option value="demo2">李总监 - 金融行业</option>
          <option value="demo3">王设计师 - 创意工作室</option>
          <option value="empty">空数据测试</option>
        </select>
      </div>
      
      <div class="view-mode">
        <label>
          <input type="checkbox" v-model="showBusinessSection" />
          显示业务展示
        </label>
        <label>
          <input type="checkbox" v-model="showSocialLinks" />
          显示社交媒体
        </label>
      </div>

      <div class="api-toggle">
        <label>
          <input type="checkbox" v-model="useApiData" />
          使用API数据（stub）
        </label>
        <button @click="loadFromApi" :disabled="loadingApi" style="margin-left:8px;">
          {{ loadingApi ? '加载中...' : '加载API' }}
        </button>
        <button @click="saveToApi" :disabled="savingApi || !currentCardData" style="margin-left:8px;">
          {{ savingApi ? '保存中...' : '保存到API（stub）' }}
        </button>
      </div>

      <div class="api-actions">
        <label style="margin-right:8px;">联系方式显示：</label>
        <label style="margin-right:8px;">
          <input type="checkbox" v-model="visibility.mobile" /> 手机
        </label>
        <label style="margin-right:8px;">
          <input type="checkbox" v-model="visibility.email" /> 邮箱
        </label>
        <label style="margin-right:8px;">
          <input type="checkbox" v-model="visibility.wechat" /> 微信
        </label>
        <button @click="saveVisibility" :disabled="savingVisibility" style="margin-left:8px;">
          {{ savingVisibility ? '同步中...' : '同步显示开关' }}
        </button>
      </div>
    </div>

    <!-- 名片预览区域 -->
    <div class="preview-container">
      <div class="device-frame" :class="deviceClass">
        <div class="device-screen">
          <!-- 恢复WecardOptimized组件 -->
          <WecardOptimized
            :card-data="effectiveCardData"
            :card-id="'preview-001'"
            :theme="currentTheme"
            :show-options="{
              showContactDetails: true,
              showBusinessSection: showBusinessSection,
              showSocialLinks: showSocialLinks,
              showSaveButton: true
            }"
            @track-event="handleTrackEvent"
            @analytics-event="handleAnalyticsEvent"
          />
        </div>
      </div>
    </div>

    <!-- 设备切换 -->
    <div class="device-switcher">
      <button 
        v-for="device in devices"
        :key="device.name"
        :class="{ active: currentDevice === device.name }"
        @click="switchDevice(device.name)"
      >
        {{ device.label }}
      </button>
    </div>

    <!-- 数据编辑器 -->
    <div class="data-editor">
      <h3>实时数据编辑</h3>
      <div class="editor-tabs">
        <button 
          v-for="tab in editorTabs"
          :key="tab.key"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="editor-content">
        <textarea
          v-model="editableData"
          @input="updateCardData"
          rows="10"
          placeholder="编辑JSON数据..."
        ></textarea>
      </div>
    </div>

    <!-- 事件日志 -->
    <div class="event-log">
      <h3>事件日志</h3>
      <div class="log-container">
        <div 
          v-for="(event, index) in eventLog"
          :key="index"
          class="log-item"
        >
          <span class="log-time">{{ formatTime(event.timestamp) }}</span>
          <span class="log-type">{{ event.event_type }}</span>
          <span class="log-data">{{ JSON.stringify(event.event_data) }}</span>
        </div>
      </div>
      <button @click="clearLog" class="clear-btn">清空日志</button>
    </div>
  </div>
</template>

<script>
// 注意：这里需要导入我们创建的组件
import WecardOptimized from '@/components/WecardOptimized.vue'

export default {
  name: 'CardPreview',
  
  components: {
    WecardOptimized
  },
  
  data() {
    return {
      // 当前主题
      currentTheme: 'light',
      
      // 当前数据集
      currentDataSet: 'demo1',
      
      // 当前设备
      currentDevice: 'mobile',
      
      // 显示选项
      showBusinessSection: true,
      showSocialLinks: true,
      useApiData: false,
      loadingApi: false,
      apiCardData: null,
      tenantId: 1,
      memberId: 1,

      // 调试：错误与探针
      uiError: null,
      lastApiProbe: '',

      // 保存API
      savingApi: false,
      savingVisibility: false,
      visibility: { mobile: true, email: true, wechat: true },
      
      // 编辑器
      activeTab: 'basic',
      editableData: '',
      
      // 事件日志
      eventLog: [],
      
      // 设备列表
      devices: [
        { name: 'mobile', label: '手机' },
        { name: 'tablet', label: '平板' },
        { name: 'desktop', label: '桌面' }
      ],
      
      // 编辑器标签
      editorTabs: [
        { key: 'basic', label: '基础信息' },
        { key: 'contact', label: '联系方式' },
        { key: 'business', label: '业务展示' },
        { key: 'full', label: '完整数据' }
      ],
      
      // 测试数据集
      testDataSets: {
        demo1: {
          basic_info: {
            name: '张建国',
            name_en: 'Jack Zhang',
            title: '产品经理',
            department: '产品研发部',
            company: '创新科技有限公司',
            avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
            company_logo: 'https://images.unsplash.com/photo-1549924231-f129b911e442?w=60&h=60&fit=crop',
            slogan: '以白为底，科技为线'
          },
          header_options: {
            backgroundImage: 'https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=1200&auto=format&fit=crop',
            headerGlow: true,
            scanLine: false
          },
          contact_info: {
            mobile: '13800138000',
            email: 'jack.zhang@company.com',
            wechat: 'jackzhang2024',
            phone: '010-12345678',
            address: '北京市朝阳区创新大厦A座15层',
            website: 'https://company.com'
          },
          interactive_features: {
            quick_call: true,
            add_wechat: true,
            save_contact: true,
            share_card: true,
            wechat_qr: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=200&h=200&fit=crop'
          },
          business_showcase: {
            company_intro: '专注于企业数字化转型解决方案，为客户提供一站式技术服务。',
            personal_intro: '10年产品经验，专注用户体验设计和产品策略规划。',
            services: ['产品策略咨询', '用户体验设计', '数字化转型'],
            portfolio: [
              {
                id: 1,
                title: '企业管理系统',
                image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=300&h=200&fit=crop',
                description: '为大型企业定制的管理系统解决方案',
                link: 'https://example.com/portfolio1'
              }
            ]
          },
          social_media: [
            { platform: 'LinkedIn', url: 'https://linkedin.com/in/jackzhang', icon: 'linkedin' },
            { platform: '微博', url: 'https://weibo.com/jackzhang', icon: 'weibo' }
          ]
        ,
          modules: {
            company_intro: {
              title: '公司简介',
              summary: '专注于企业数字化转型解决方案，为客户提供一站式技术服务。',
              points: ['10+年行业经验', '覆盖制造/金融/零售', '全国7个交付中心']
            },
            product_gallery: {
              layout: 'grid',
              items: [
                { title: '智能中台', image: 'https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=600&h=450&fit=crop', desc: '企业级数据中台' },
                { title: '移动门户', image: 'https://images.unsplash.com/photo-1526378722484-bd91ca387e72?w=600&h=450&fit=crop', desc: '多端统一门户' },
                { title: '可视化大屏', image: 'https://images.unsplash.com/photo-1508612761958-e931d843bddb?w=600&h=450&fit=crop', desc: '经营驾驶舱' }
              ]
            },
            solution_intro: {
              title: '行业数字化解决方案',
              summary: '以业务为核心，沉淀可复用模块与最佳实践。',
              points: ['快速交付', '低成本维护', '高可用架构'],
              image: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&h=600&fit=crop'
            },
            environment: {
              items: [
                { title: '办公环境', image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=600&fit=crop' },
                { title: '生产车间', image: 'https://images.unsplash.com/photo-1581094651181-3592d89b63d3?w=800&h=600&fit=crop' }
              ]
            },
            timeline: {
              enableShimmer: true,
              items: [
                { title: '2021-01 产品立项', desc: '成立项目团队，明确核心方向。' },
                { title: '2022-06 首个客户上线', desc: '完成 MVP 并开始迭代。' },
                { title: '2024-03 功能整合发布', desc: '推出统一名片与预览系统。' }
              ]
            },
            logo_wall: {
              duration: 30,
              logos: [
                { src: 'https://dummyimage.com/120x42/ddd/555&text=ACME' },
                { src: 'https://dummyimage.com/120x42/eee/555&text=Globex' },
                { src: 'https://dummyimage.com/120x42/e5e/555&text=Soylent' }
              ]
            }
          }
        },
        
        demo2: {
          basic_info: {
            name: '李美华',
            title: '投资总监',
            department: '投资银行部',
            company: '华信金融集团',
            avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
            company_logo: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=60&h=60&fit=crop'
          },
          header_options: {
            backgroundImage: 'https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?w=1200&auto=format&fit=crop',
            headerGlow: true,
            scanLine: true
          },
          contact_info: {
            mobile: '13900139000',
            email: 'meihua.li@huaxin.com',
            phone: '021-88888888',
            address: '上海市浦东新区金融街88号',
            website: 'https://huaxin.com'
          },
          interactive_features: {
            quick_call: true,
            save_contact: true,
            share_card: true
          },
          business_showcase: {
            company_intro: '华信金融集团是国内领先的综合性金融服务机构。',
            personal_intro: '15年金融行业经验，专注股权投资和企业并购。',
            services: ['股权投资', '企业并购', '财务顾问'],
            achievements: ['管理资产超过100亿', '成功投资项目200+', '金融行业专家']
          }
        ,
          modules: {
            company_intro: '华信金融集团是国内领先的综合性金融服务机构。',
            product_gallery: {
              layout: 'hscroll',
              items: [
                { title: '投研平台', image: 'https://images.unsplash.com/photo-1559523182-a284c3fb7cff?w=800&h=600&fit=crop' },
                { title: '风控体系', image: 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&h=600&fit=crop' }
              ]
            },
            timeline: { items: [ { title: '2019-09 成立投研中心' }, { title: '2021-12 AUM 破 100亿' } ] }
          }
        },
        
        demo3: {
          basic_info: {
            name: '王创意',
            title: '创意总监',
            department: '设计部',
            company: '灵感创意工作室',
            avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
            company_logo: 'https://images.unsplash.com/photo-1558655146-364adaf25c32?w=60&h=60&fit=crop'
          },
          header_options: {
            backgroundImage: 'https://images.unsplash.com/photo-1517816743773-6e0fd518b4a6?w=1200&auto=format&fit=crop',
            headerGlow: true,
            scanLine: false
          },
          contact_info: {
            mobile: '13700137000',
            email: 'creative@studio.com',
            wechat: 'creativewang',
            address: '深圳市南山区创意园区',
            website: 'https://creativestudio.com'
          },
          interactive_features: {
            quick_call: true,
            add_wechat: true,
            save_contact: true,
            share_card: true
          },
          business_showcase: {
            company_intro: '专业的品牌设计和创意服务工作室。',
            personal_intro: '资深设计师，擅长品牌视觉和用户体验设计。',
            services: ['品牌设计', 'UI/UX设计', '创意策划'],
            portfolio: [
              {
                id: 1,
                title: '品牌视觉设计',
                image: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=300&h=200&fit=crop',
                description: '为知名品牌打造的视觉识别系统'
              },
              {
                id: 2,
                title: 'APP界面设计',
                image: 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=300&h=200&fit=crop',
                description: '移动应用的用户界面设计'
              }
            ]
          },
          social_media: [
            { platform: 'Dribbble', url: 'https://dribbble.com/creativewang', icon: 'dribbble' },
            { platform: 'Behance', url: 'https://behance.net/creativewang', icon: 'behance' },
            { platform: '小红书', url: 'https://xiaohongshu.com/creativewang', icon: 'xiaohongshu' }
          ],
          modules: {
            company_intro: {
              title: '工作室介绍',
              summary: '专业的品牌设计和创意服务工作室。'
            },
            logo_wall: {
              duration: 26,
              logos: [
                { src: 'https://dummyimage.com/120x42/dde/555&text=BrandA' },
                { src: 'https://dummyimage.com/120x42/ccd/555&text=BrandB' }
              ]
            }
          }
        },
        
        empty: {
          basic_info: {
            name: '测试用户',
            company: '测试公司'
          },
          contact_info: {},
          interactive_features: {},
          business_showcase: {},
          social_media: []
        }
      }
    }
  },
  
  computed: {
    // 当前名片数据
    currentCardData() {
      if (this.useApiData && this.apiCardData) {
        return this.apiCardData
      }
      return this.testDataSets[this.currentDataSet] || this.testDataSets.demo1
    },
    // 应用联系方式显示开关后的名片数据
    effectiveCardData() {
      const src = this.currentCardData || {}
      const clone = JSON.parse(JSON.stringify(src))
      if (!clone.contact_info) clone.contact_info = {}
      if (this.visibility && clone.contact_info) {
        if (this.visibility.mobile === false) clone.contact_info.mobile = ''
        if (this.visibility.email === false) clone.contact_info.email = ''
        if (this.visibility.wechat === false) clone.contact_info.wechat = ''
      }
      return clone
    },
    
    // 设备样式类
    deviceClass() {
      return `device-${this.currentDevice}`
    }
  },
  
  mounted() {
    // 初始化编辑器数据
    this.updateEditableData()

    // 前端全局错误捕获（网络正常但页面白圈转动常因运行时错误导致未挂载）
    this._onWindowError = (e) => {
      const err = e && (e.error || e.message) || 'unknown'
      this.uiError = {
        message: String(err && err.message ? err.message : err),
        stack: err && err.stack ? err.stack : '',
        info: 'window.error'
      }
    }
    this._onUnhandledRejection = (e) => {
      const reason = e && (e.reason || e)
      this.uiError = {
        message: String(reason && reason.message ? reason.message : reason),
        stack: reason && reason.stack ? reason.stack : '',
        info: 'unhandledrejection'
      }
    }
    if (typeof window !== 'undefined') {
      window.addEventListener('error', this._onWindowError)
      window.addEventListener('unhandledrejection', this._onUnhandledRejection)
    }
  },

  beforeDestroy() {
    if (typeof window !== 'undefined') {
      window.removeEventListener('error', this._onWindowError)
      window.removeEventListener('unhandledrejection', this._onUnhandledRejection)
    }
  },
  
  methods: {
    // 隐藏调试覆盖层
    dismissError() {
      this.uiError = null
    },
    // 从后端API加载数据（演示模式）
    async loadFromApi() {
      this.loadingApi = true
      try {
        const url = `/api/card/profile?tenant_id=${this.tenantId}&member_id=${this.memberId}&stub=1`
        const resp = await fetch(url)
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const ct = resp.headers.get('content-type') || ''
        // 记录探针
        this.lastApiProbe = `status=${resp.status}; content-type=${ct}`
        if (!ct.includes('application/json')) {
          const txt = await resp.text()
          this.lastApiProbe += `\nbody=${txt.slice(0, 300)}`
          throw new Error('invalid_content_type')
        }
        const json = await resp.json()
        if (json && json.card_profile) {
          this.apiCardData = json.card_profile
          this.useApiData = true
          this.logEvent('api_load_success', { tenant_id: this.tenantId, member_id: this.memberId })
        } else {
          throw new Error('invalid_response')
        }
      } catch (e) {
        console.error('加载API失败:', e)
        this.logEvent('api_load_error', { message: String(e) })
        // 将错误抬升至覆盖层显示
        this.uiError = {
          message: e && e.message ? e.message : String(e),
          stack: e && e.stack ? e.stack : '',
          info: 'loadFromApi'
        }
      } finally {
        this.loadingApi = false
      }
    },
    // 保存当前名片到 API（演示模式回显）
    async saveToApi() {
      this.savingApi = true
      try {
        const url = `/api/card/profile?stub=1`
        const payload = {
          tenant_id: this.tenantId,
          member_id: this.memberId,
          card_profile: this.currentCardData
        }
        const resp = await fetch(url, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        this.logEvent('api_put_success', { tenant_id: this.tenantId, member_id: this.memberId })
        alert('已保存（stub 回显）。')
      } catch (e) {
        console.error('保存API失败:', e)
        this.logEvent('api_put_error', { message: String(e) })
        this.uiError = { message: e && e.message ? e.message : String(e), stack: e && e.stack ? e.stack : '', info: 'saveToApi' }
      } finally {
        this.savingApi = false
      }
    },
    // 提交联系方式显示开关
    async saveVisibility() {
      this.savingVisibility = true
      try {
        const url = `/api/card/settings/contact-visibility`
        const payload = {
          tenant_id: this.tenantId,
          member_id: this.memberId,
          visibility: this.visibility
        }
        const resp = await fetch(url, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        this.logEvent('api_visibility_success', { visibility: this.visibility })
        alert('显示开关已同步。')
      } catch (e) {
        console.error('显示开关同步失败:', e)
        this.logEvent('api_visibility_error', { message: String(e) })
        this.uiError = { message: e && e.message ? e.message : String(e), stack: e && e.stack ? e.stack : '', info: 'saveVisibility' }
      } finally {
        this.savingVisibility = false
      }
    },
    // 更新主题
    updateTheme() {
      this.logEvent('theme_change', { theme: this.currentTheme })
    },
    
    // 更新数据
    updateData() {
      this.updateEditableData()
      this.logEvent('data_change', { dataset: this.currentDataSet })
    },
    
    // 切换设备
    switchDevice(device) {
      this.currentDevice = device
      this.logEvent('device_change', { device })
    },
    
    // 更新可编辑数据
    updateEditableData() {
      if (this.activeTab === 'full') {
        this.editableData = JSON.stringify(this.currentCardData, null, 2)
      } else {
        const section = this.activeTab === 'basic' ? 'basic_info' :
                       this.activeTab === 'contact' ? 'contact_info' :
                       this.activeTab === 'business' ? 'business_showcase' : 'basic_info'
        this.editableData = JSON.stringify(this.currentCardData[section] || {}, null, 2)
      }
    },
    
    // 更新名片数据
    updateCardData() {
      try {
        const newData = JSON.parse(this.editableData)
        if (this.activeTab === 'full') {
          this.testDataSets[this.currentDataSet] = newData
        } else {
          const section = this.activeTab === 'basic' ? 'basic_info' :
                         this.activeTab === 'contact' ? 'contact_info' :
                         this.activeTab === 'business' ? 'business_showcase' : 'basic_info'
          this.testDataSets[this.currentDataSet][section] = newData
        }
        this.logEvent('data_edit', { section: this.activeTab })
      } catch (error) {
        console.error('JSON格式错误:', error)
      }
    },
    
    // 处理追踪事件
    handleTrackEvent(eventData) {
      this.logEvent(eventData.event_type, eventData.event_data)
    },
    
    // 处理分析事件
    handleAnalyticsEvent(eventData) {
      this.logEvent('analytics', eventData)
    },
    
    // 记录事件
    logEvent(type, data = {}) {
      this.eventLog.unshift({
        timestamp: Date.now(),
        event_type: type,
        event_data: data
      })
      
      // 限制日志数量
      if (this.eventLog.length > 50) {
        this.eventLog = this.eventLog.slice(0, 50)
      }
    },
    
    // 清空日志
    clearLog() {
      this.eventLog = []
    },
    
    // 格式化时间
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    }
  },
  
  watch: {
    activeTab() {
      this.updateEditableData()
    }
  }
}
</script>

<style lang="scss" scoped>
.card-preview-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 调试覆盖层样式（仅预览页使用） */
.debug-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.debug-card {
  width: min(92vw, 820px);
  max-height: 80vh;
  overflow: auto;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}
.debug-title {
  font-weight: 600;
  padding: 12px 16px;
  border-bottom: 1px solid #eef0f3;
}
.debug-body { padding: 12px 16px; }
.debug-item { font-size: 12px; color: #111; margin-bottom: 8px; }
.debug-pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #f7f7f9;
  border: 1px dashed #e5e7eb;
  padding: 8px;
  border-radius: 6px;
}
.debug-actions { padding: 0 16px 12px; display: flex; justify-content: flex-end; }
.debug-btn {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
}

.preview-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 28px;
    color: #262626;
    margin: 0 0 8px 0;
  }
  
  p {
    color: #8c8c8c;
    font-size: 16px;
    margin: 0;
  }
}

.control-panel {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  flex-wrap: wrap;
  
  > div {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  label {
    font-weight: 500;
    color: #262626;
  }
  
  select {
    padding: 6px 12px;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    background: white;
  }
}

.preview-container {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.device-frame {
  position: relative;
  background: #333;
  border-radius: 20px;
  padding: 20px;
  
  &.device-mobile {
    width: 375px;
    
    .device-screen {
      width: 335px;
      height: 600px;
    }
  }
  
  &.device-tablet {
    width: 768px;
    
    .device-screen {
      width: 728px;
      height: 600px;
    }
  }
  
  &.device-desktop {
    width: 1024px;
    
    .device-screen {
      width: 984px;
      height: 600px;
    }
  }
}

.device-screen {
  background: white;
  border-radius: 12px;
  overflow-y: auto;
  overflow-x: hidden;
}

.device-switcher {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 30px;
  
  button {
    padding: 8px 16px;
    border: 1px solid #d9d9d9;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: #1890ff;
      color: #1890ff;
    }
    
    &.active {
      background: #1890ff;
      color: white;
      border-color: #1890ff;
    }
  }
}

.data-editor {
  margin-bottom: 30px;
  
  h3 {
    margin: 0 0 16px 0;
    color: #262626;
  }
}

.editor-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  
  button {
    padding: 8px 16px;
    border: 1px solid #d9d9d9;
    background: #fafafa;
    cursor: pointer;
    border-radius: 4px 4px 0 0;
    
    &.active {
      background: white;
      border-bottom-color: white;
    }
  }
}

.editor-content {
  textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #d9d9d9;
    border-radius: 0 4px 4px 4px;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 12px;
    resize: vertical;
  }
}

.event-log {
  h3 {
    margin: 0 0 16px 0;
    color: #262626;
  }
}

.log-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fafafa;
  padding: 12px;
  margin-bottom: 12px;
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 4px 0;
  font-size: 12px;
  font-family: monospace;
  
  .log-time {
    color: #8c8c8c;
    width: 80px;
    flex-shrink: 0;
  }
  
  .log-type {
    color: #1890ff;
    width: 120px;
    flex-shrink: 0;
  }
  
  .log-data {
    color: #262626;
    flex: 1;
    word-break: break-all;
  }
}

.clear-btn {
  padding: 6px 12px;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  
  &:hover {
    background: #ff7875;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .card-preview-page {
    padding: 12px;
  }
  
  .control-panel {
    flex-direction: column;
    gap: 12px;
  }
  
  .device-frame {
    &.device-mobile,
    &.device-tablet,
    &.device-desktop {
      width: 100%;
      max-width: 375px;
      
      .device-screen {
        width: calc(100% - 40px);
        height: 500px;
      }
    }
  }
}
</style>
