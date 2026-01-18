<template>
  <div class="wecard-optimized" :class="themeClass">
    
    <!-- 主要内容区域 -->
    <div class="card-content">
      <!-- 顶部功能条（粘性）（仅在非预览模式显示） -->
      <div v-if="showSharePanel" class="top-sticky-bar">
        <!-- 左侧：企业名片信息 -->
        <div class="brand-info">
          <span class="brand-text">
            {{ cardData.basic_info?.slogan || (cardData.basic_info?.company + ' 企业名片') || 'WeCard 企业名片' }}
          </span>
        </div>
        
        <!-- 右侧：操作按钮 -->
        <div class="action-buttons">
          <!-- 电话按钮 -->
          <button 
            v-if="cardData.contact_info?.mobile"
            class="action-btn phone-btn"
            @click="handleQuickCall"
            title="拨打电话"
          >
            <LottieIcon
              v-if="lottieAnimations.phoneRing && !shouldDisableAnimations"
              :animation-data="lottieAnimations.phoneRing"
              :width="16"
              :height="16"
              :autoplay="true"
              :loop="true"
              :speed="1"
              fallback-icon="icon-phone-animated"
              @error="onLottieError"
            />
            <i v-else class="icon-phone-animated"></i>
            <span>电话</span>
          </button>
          
          <!-- 分享按钮 -->
          <button 
            class="action-btn share-btn"
            @click="handleQuickShare"
            title="分享名片"
          >
            <LottieIcon
              v-if="lottieAnimations.shareFloat && !shouldDisableAnimations"
              :animation-data="lottieAnimations.shareFloat"
              :width="16"
              :height="16"
              :autoplay="true"
              :loop="true"
              :speed="0.8"
              fallback-icon="icon-share-animated"
              @error="onLottieError"
            />
            <i v-else class="icon-share-animated"></i>
            <span>分享</span>
          </button>
        </div>
      </div>
      
      <!-- 名片头部（全新设计：居中头像+背景+按钮） -->
      <CardHeader 
        :basic-info="cardData.basic_info"
        :company-short="companyShort"
        :slogan="sloganText"
        :header-background="headerBackgroundConfig"
        :avatar-config="avatarConfig"
        @avatar-click="handleAvatarClick"
        @save-contact="saveToContacts"
        @share="handleQuickShare"
        class="enhanced-header"
      />
      
      <!-- 快速操作按钮（隐藏，顶部粘性条替代） -->
      <div class="actions-container is-light qa-hidden">
        <QuickActions 
          :contact-info="cardData.contact_info"
          :interactive-features="cardData.interactive_features"
          @action-click="handleQuickAction"
          class="enhanced-actions"
        />
      </div>
      
      <!-- 联系信息（浅色主题包裹容器） -->
      <div class="contact-container" :class="{ 'is-light': currentTheme === 'light' }">
        <ContactInfo 
          :contact-info="cardData.contact_info"
          :show-details="showContactDetails"
          :contact-visibility="contactVisibility"
          @contact-click="handleContactClick"
          class="enhanced-contact"
        />
      </div>
      
      <!-- 业务展示 -->
      <BusinessShowcase 
        v-if="cardData.business_showcase && showBusinessSection"
        :business-data="cardData.business_showcase"
        @portfolio-click="handlePortfolioClick"
        class="enhanced-business"
      />

      <!-- 企业/业务简介模块（旧版格式，仅在没有modules_list时使用） -->
      <CompanyIntro
        v-if="(!sortedModulesList || sortedModulesList.length === 0) && cardData.modules && (cardData.modules.company_intro || cardData.modules.companyintro)"
        :config="cardData.modules.company_intro || cardData.modules.companyintro"
        class="enhanced-company-intro"
      />

      <!-- 产品展示模块（支持 grid / hscroll） -->
      <ProductGallery
        v-if="cardData.modules && cardData.modules.product_gallery && cardData.modules.product_gallery.items"
        :items="cardData.modules.product_gallery.items"
        :layout="cardData.modules.product_gallery.layout || 'grid'"
        class="enhanced-product-gallery"
      />

      <!-- 方案介绍模块（左右布局） -->
      <SolutionIntro
        v-if="cardData.modules && cardData.modules.solution_intro"
        :solution="cardData.modules.solution_intro"
        class="enhanced-solution-intro"
      />

      <!-- 环境/工厂展示（横向滑动） -->
      <EnvironmentShowcase
        v-if="cardData.modules && cardData.modules.environment && cardData.modules.environment.items"
        :items="cardData.modules.environment.items"
        class="enhanced-environment"
      />

      <!-- 🔧 新版：支持多个相同类型模块（从 modules_list 渲染） -->
      <template v-if="sortedModulesList && sortedModulesList.length > 0">
        <template v-for="module in sortedModulesList">
          <!-- 企业简介模块 -->
          <CompanyIntro
            v-if="module.type === 'CompanyIntro' && module.data"
            :key="module.id"
            :config="module.data"
            class="enhanced-company-intro"
          />
          
          <!-- 信任背书模块 -->
          <TrustCredentials
            v-if="module.type === 'TrustCredentials' && module.data"
            :key="module.id"
            :title="module.data.title || module.title"
            :logos="module.data.logos || []"
            :credentials="module.data.credentials || []"
            :layout="module.data.layout || 'grid'"
            :show-date="module.data.showDate"
            :enable-zoom="module.data.enableZoom"
            @logo-click="handleClientClick"
            @credential-click="handleCertClick"
          />
          
          <!-- 通用网格展示组件 -->
          <StandardGrid
            v-if="module.type === 'StandardGrid' && module.data"
            :key="module.id"
            :title="module.data.title || module.title"
            :subtitle="module.data.subtitle || ''"
            :items="module.data.items || []"
            :display-mode="module.data.mode || 'icon'"
            :columns="module.data.columns || module.data.grid_columns || 2"
            @item-click="handleGridItemClick"
          />
          
          <!-- 多媒体展示组件 -->
          <VideoShowcase
            v-if="module.type === 'VideoShowcase' && module.data"
            :key="module.id"
            :data="{ title: module.title, ...module.data }"
            class="enhanced-video-showcase"
          />
          
          <!-- 网店直达模块 -->
          <ShopDirect
            v-if="module.type === 'ShopDirect' && module.data"
            :key="module.id"
            :title="module.data.title || module.title"
            :subtitle="module.data.subtitle || ''"
            :shops="module.data.shops || []"
            class="enhanced-shop-direct"
          />
          
          <!-- 时间线模块 -->
          <Timeline
            v-if="module.type === 'Timeline' && module.data"
            :key="module.id"
            :title="module.data.title || module.title"
            :subtitle="module.data.subtitle || ''"
            :events="module.data.events || []"
            :layout="module.data.layout || 'vertical'"
            :line-style="module.data.lineStyle || 'solid'"
            :accent-color="module.data.accentColor || '#1890FF'"
            class="enhanced-timeline"
          />
          
          <!-- Logo 墙模块 -->
          <LogoWall
            v-if="module.type === 'LogoWall' && module.data && module.data.logos && module.data.logos.length > 0"
            :key="module.id"
            :title="module.data.title || module.title || '合作客户'"
            :logos="module.data.logos"
            :layout="module.data.layout || 'scroll'"
            :duration="module.data.duration || 30"
            :pause-on-hover="module.data.pauseOnHover !== false"
            :gap="module.data.gap || 24"
            :default-style="module.data.defaultStyle || 'grayscale'"
            class="enhanced-logo-wall"
          />
        </template>
      </template>
      
      <!-- 🔄 旧版兼容：当没有 modules_list 时，使用旧版格式渲染 -->
      <template v-if="!sortedModulesList || sortedModulesList.length === 0">
        <!-- 时间线（旧版格式） -->
        <Timeline
          v-if="cardData.modules && cardData.modules.timeline"
          :title="cardData.modules.timeline.title"
          :subtitle="cardData.modules.timeline.subtitle"
          :events="cardData.modules.timeline.events || []"
          :layout="cardData.modules.timeline.layout || 'vertical'"
          :line-style="cardData.modules.timeline.lineStyle || 'solid'"
          :accent-color="cardData.modules.timeline.accentColor || '#1890FF'"
          class="enhanced-timeline"
        />

        <!-- Logo 墙（旧版格式） -->
        <LogoWall
          v-if="cardData.modules && cardData.modules.logo_wall && cardData.modules.logo_wall.logos && cardData.modules.logo_wall.logos.length > 0"
          :title="cardData.modules.logo_wall.title || '合作客户'"
          :logos="cardData.modules.logo_wall.logos"
          :layout="cardData.modules.logo_wall.layout || 'scroll'"
          :duration="cardData.modules.logo_wall.duration || 30"
          :pause-on-hover="cardData.modules.logo_wall.pauseOnHover !== false"
          :gap="cardData.modules.logo_wall.gap || 24"
          :default-style="cardData.modules.logo_wall.defaultStyle || 'grayscale'"
          class="enhanced-logo-wall"
        />
        
        <!-- 信任背书模块（旧版格式） -->
        <TrustCredentials
          v-if="trustCredentialsData"
          :title="trustCredentialsData.title"
          :logos="trustCredentialsData.logos || []"
          :credentials="trustCredentialsData.credentials || []"
          :layout="trustCredentialsData.layout || 'grid'"
          :show-date="trustCredentialsData.showDate"
          :enable-zoom="trustCredentialsData.enableZoom"
          @logo-click="handleClientClick"
          @credential-click="handleCertClick"
        />
        
        <!-- 通用网格展示组件（旧版格式） -->
        <StandardGrid
          v-if="standardGridData"
          :title="standardGridData.title"
          :subtitle="standardGridData.subtitle"
          :items="standardGridData.items || []"
          :display-mode="standardGridData.mode || 'icon'"
          :columns="standardGridData.columns || standardGridData.grid_columns || 2"
          @item-click="handleGridItemClick"
        />
        
        <!-- 多媒体展示组件（旧版格式） -->
        <VideoShowcase
          v-if="videoShowcaseData"
          :data="videoShowcaseData"
          class="enhanced-video-showcase"
        />
      </template>
      
      <!-- 社交媒体链接 -->
      <SocialLinks 
        v-if="cardData.social_media && cardData.social_media.length > 0"
        :social-data="cardData.social_media"
        :region="socialRegion"
        :allow-platforms="socialAllowPlatforms"
        @social-click="handleSocialClick"
        class="enhanced-social"
      />

      <!-- 分享模块（国内优先：复制链接/二维码/刷新缩略图） -->
      <!-- 只在非预览模式下且非移动端显示 -->
      <SharePanel
        v-if="showSharePanel && !isMobileDevice()"
        :card-id="cardId"
        :card-data="cardData"
        :is-wecom-env="isWecomEnv"
        @track-event="handleAnalyticsEvent"
        ref="sharePanel"
        class="enhanced-share"
      />
      
      <!-- 新的融入式底部操作区（使用CardHeader按钮样式） -->
      <div class="contact-actions-footer">
        <button 
          class="contact-action-btn card-btn-style"
          @click="saveToContacts"
          :disabled="saving"
        >
          <span>{{ saving ? '保存中...' : '保存到通讯录' }}</span>
        </button>
        <button 
          class="contact-action-btn card-btn-style card-btn-solid"
          @click="handleQuickShare"
        >
          <span>分享</span>
        </button>
      </div>
      
      <!-- 简洁的页脚 -->
      <div class="card-footer-simple">
        <!-- 品牌横幅（Logo + Slogan）- 仅在PC端显示 -->
        <div 
          v-if="!isMobileDevice() && logoConfig.showInFooter && (footerLogoUrl || footerSlogan)" 
          class="brand-banner"
        >
          <!-- Lottie Logo -->
          <LottieIcon
            v-if="footerLogoUrl && isFooterLottie"
            :animation-data="footerLogoUrl"
            :width="parseInt(footerLogoHeight)"
            :height="parseInt(footerLogoHeight)"
            :autoplay="true"
            :loop="true"
            class="brand-icon"
          />
          <!-- 图片 Logo -->
          <img 
            v-else-if="footerLogoUrl"
            :src="footerLogoUrl" 
            alt="品牌图标"
            class="brand-icon"
            :style="{ height: footerLogoHeight }"
          />
          <span v-if="footerSlogan" class="brand-slogan">{{ footerSlogan }}</span>
        </div>
        <div class="powered-by">WeCard 数字名片</div>
      </div>
    </div>
    
    <!-- 隐藏的vCard生成器（保持兼容性） -->
    <VcardGenerator 
      ref="vcardGenerator"
      :card-data="legacyVcardData"
      v-show="false"
    />
    
    <!-- 数据统计埋点 -->
    <AnalyticsTracker 
      :card-id="cardId"
      :visitor-info="visitorInfo"
      @track-event="handleAnalyticsEvent"
    />
  </div>
</template>

<script>
import CardHeader from './card/CardHeader.vue'
import SloganSection from './card/SloganSection.vue'
import QuickActions from './card/QuickActions.vue'
import ContactInfo from './card/ContactInfo.vue'
import BusinessShowcase from './card/BusinessShowcase.vue'
import SocialLinks from './card/SocialLinks.vue'
import SharePanel from './card/SharePanel.vue'
import VcardGenerator from './card/VcardGenerator.vue'
import AnalyticsTracker from './card/AnalyticsTracker.vue'
import CompanyIntro from './card/CompanyIntro.vue'
import ProductGallery from './card/ProductGallery.vue'
import SolutionIntro from './card/SolutionIntro.vue'
import EnvironmentShowcase from './card/EnvironmentShowcase.vue'
import Timeline from './card/Timeline.vue'
import LogoWall from './card/LogoWall.vue'
import StandardGrid from './card/StandardGrid.vue'
import TrustCredentials from './card/TrustCredentials.vue'
import VideoShowcase from './card/VideoShowcase.vue'
import ShopDirect from './card/ShopDirect.vue'
import LottieIcon from './LottieIcon.vue'
import LottieService from '../services/LottieService.js'
import { shouldDisableAnimations } from '../config/lottie.config.js'
import { 
  isClient, 
  safeWindow, 
  safeWindowOperation, 
  safeOpenWindow, 
  safeRedirect,
  safeNavigator,
  safeDocument,
  isMobileDevice as checkIsMobileDevice,
  isWecomEnvironment,
  isWechatEnvironment,
  safeCopyToClipboard,
  safeNativeShare,
  getCurrentUrl
} from '../utils/client-utils.js'

export default {
  name: 'WecardOptimized',
  
  components: {
    CardHeader,
    SloganSection,
    QuickActions,
    ContactInfo,
    BusinessShowcase,
    SocialLinks,
    SharePanel,
    VcardGenerator,
    AnalyticsTracker,
    CompanyIntro,
    ProductGallery,
    SolutionIntro,
    EnvironmentShowcase,
    Timeline,
    LogoWall,
    StandardGrid,
    TrustCredentials,
    VideoShowcase,
    ShopDirect,
    LottieIcon
  },
  
  props: {
    // 名片数据
    cardData: {
      type: Object,
      required: true,
      default: () => ({
        basic_info: {},
        contact_info: {},
        interactive_features: {},
        business_showcase: {},
        social_media: []
      })
    },
    // 名片ID
    cardId: { type: [String, Number], required: true },
    // 主题配置
    theme: { type: String, default: 'corporate', validator: v => ['corporate','professional','creative','minimal','light','tech','modern','business'].includes(v) },
    // 显示配置
    showOptions: { type: Object, default: () => ({ showContactDetails:true, showBusinessSection:true, showSocialLinks:true, showSaveButton:true }) },
    // 企业微信环境标识
    isWecomEnv: { type: Boolean, default: false },
    // 社交链接展示区域（国内默认隐藏海外）
    socialRegion: { type: String, default: 'cn' },
    // 额外允许展示的平台白名单
    socialAllowPlatforms: { type: Array, default: () => [] },
    // ✅ 新增：是否显示分享面板（管理员预览时设为false）
    showSharePanel: { type: Boolean, default: true },
    // ✅ 新增：联系方式可见性配置
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
    },
    // ✅ 新增：头部背景配置
    headerBackground: { type: Object, default: () => ({}) },
    // ✅ 新增：Logo配置
    logoConfig: { type: Object, default: () => ({}) }
  },
  
  data() {
    return {
      currentTheme: this.theme,
      showContactDetails: this.showOptions.showContactDetails,
      showBusinessSection: this.showOptions.showBusinessSection,
      saving: false,
      loading: false,
      visitorInfo: { ip: null, userAgent: '', referrer: '', timestamp: Date.now(), sessionId: this.generateSessionId() },
      themes: {
        light: { primaryColor: '#1890FF', secondaryColor: '#F5F7FA', accentColor: '#E6F4FF', textPrimary: '#1F1F1F', textSecondary: '#8C8C8C' },
        corporate: { primaryColor: '#1890FF', secondaryColor: '#F0F7FF', accentColor: '#096DD9', textPrimary: '#262626', textSecondary: '#8C8C8C' },
        professional: { primaryColor: '#434343', secondaryColor: '#F5F5F5', accentColor: '#1890FF', textPrimary: '#262626', textSecondary: '#8C8C8C' },
        creative: { primaryColor: '#FA8C16', secondaryColor: '#FFF7E6', accentColor: '#D46B08', textPrimary: '#262626', textSecondary: '#8C8C8C' },
        minimal: { primaryColor: '#000000', secondaryColor: '#FFFFFF', accentColor: '#666666', textPrimary: '#000000', textSecondary: '#666666' }
      },
      // Lottie动画相关
      lottieAnimations: {
        phoneRing: null,
        shareFloat: null
      },
      lottieLoading: false,
      lottieErrors: []
    }
  },
  
  computed: {
    themeClass() { return `theme-${this.currentTheme}` },
    legacyVcardData() { return this.mapToLegacyFormat(this.cardData) },
    dataCompleteness() {
      const req=['basic_info.name','basic_info.title','basic_info.company','contact_info.mobile']
      const ok=req.filter(f=>this.getNestedValue(this.cardData,f))
      return Math.round((ok.length/req.length)*100)
    },
    showCompletionTips() { return this.dataCompleteness < 80 },
    shouldDisableAnimations() {
      return shouldDisableAnimations()
    },
    // 信任背书数据（支持snake_case和老格式）
    // 注意：仅在 modules_list 不存在或为空时使用，避免与 modules_list 重复渲染
    trustCredentialsData() {
      // 如果 modules_list 存在且有数据，不使用旧版格式
      if (this.sortedModulesList && this.sortedModulesList.length > 0) return null
      if (!this.cardData.modules) return null
      return this.cardData.modules.trust_credentials || this.cardData.modules.trustcredentials
    },
    // 通用网格数据（支持snake_case和老格式）
    // 注意：仅在 modules_list 不存在或为空时使用，避免与 modules_list 重复渲染
    standardGridData() {
      // 如果 modules_list 存在且有数据，不使用旧版格式
      if (this.sortedModulesList && this.sortedModulesList.length > 0) return null
      if (!this.cardData.modules) return null
      return this.cardData.modules.standard_grid || this.cardData.modules.standardgrid
    },
    // 多媒体展示数据（支持snake_case和老格式）
    // 注意：仅在 modules_list 不存在或为空时使用，避免与 modules_list 重复渲染
    videoShowcaseData() {
      // 如果 modules_list 存在且有数据，不使用旧版格式
      if (this.sortedModulesList && this.sortedModulesList.length > 0) return null
      if (!this.cardData.modules) return null
      return this.cardData.modules.video_showcase || this.cardData.modules.videoshowcase
    },
    // 底部Logo URL（独立配置，如果未设置则使用头部Logo）
    footerLogoUrl() {
      return this.logoConfig.footerLogoUrl || this.logoConfig.logoUrl || ''
    },
    // 底部Logo高度
    footerLogoHeight() {
      return `${this.logoConfig.footerLogoSize || 32}px`
    },
    // 底部品牌口号
    footerSlogan() {
      return this.logoConfig.footerSlogan || ''
    },
    // 底部Logo是否为Lottie动画
    isFooterLottie() {
      return (this.logoConfig.footerLogoType || this.logoConfig.logoType) === 'lottie'
    },
    // 🔧 排序后的模块列表（确保按sort_order排序）
    sortedModulesList() {
      if (!this.cardData.modules_list || !Array.isArray(this.cardData.modules_list)) {
        return []
      }
      // 按sort_order排序，如果sort_order不存在则使用数组索引
      return [...this.cardData.modules_list].sort((a, b) => {
        const orderA = a.sort_order !== undefined ? a.sort_order : 999999
        const orderB = b.sort_order !== undefined ? b.sort_order : 999999
        return orderA - orderB
      })
    },
    // ✅ 公司简称（从basic_info.company获取）
    companyShort() {
      return this.cardData.basic_info?.company || ''
    },
    // ✅ Slogan文本（优先从headerOptions，其次basicInfo）
    sloganText() {
      return this.cardData.header_options?.slogan || 
             this.cardData.basic_info?.slogan || 
             ''
    },
    // ✅ 头部背景配置（合并headerBackground prop和cardData中的配置）
    headerBackgroundConfig() {
      // 优先使用prop传入的配置
      if (this.headerBackground && Object.keys(this.headerBackground).length > 0) {
        return this.headerBackground
      }
      // 其次从cardData中获取
      if (this.cardData.header_background) {
        return this.cardData.header_background
      }
      // 默认配置
      return {
        backgroundType: 'svg',
        svgPattern: 'geometric',
        svgGradientStart: '#ffffff',
        svgGradientEnd: '#FC726E',
        svgDensity: 300,
        svgOpacity: 0.5
      }
    },
    // ✅ 头像配置（合并cardData中的配置）
    avatarConfig() {
      // 从cardData中获取
      if (this.cardData.avatar_config) {
        return {
          ...this.cardData.avatar_config,
          wecomAvatar: this.cardData.avatar_config.wecomAvatar || this.cardData.basic_info?.avatar || ''
        }
      }
      // 默认配置：使用企业微信头像
      return {
        useWecomAvatar: true,
        customAvatar: '',
        wecomAvatar: this.cardData.basic_info?.avatar || ''
      }
    }
  },
  
  mounted() { 
    this.initVisitorInfo(); 
    try{this.trackPageView()}catch(e){}; 
    try{this.detectEnvironment()}catch(e){}; 
    this.loadLottieAnimations();
  },
  
  methods: {
    onTopCall(){ const m=this.cardData?.contact_info?.mobile; if(m) this.makePhoneCall(m) },
    onTopShare(){ try{ const p=this.$refs.sharePanel; if(p&&p.toggleQr) p.toggleQr(); else this.shareCard() }catch(e){ this.shareCard() } },
    handleQuickCall(){ const m=this.cardData?.contact_info?.mobile; if(m) this.makePhoneCall(m) },
    handleQuickShare(){ try{ const p=this.$refs.sharePanel; if(p&&p.toggleQr) p.toggleQr(); else this.shareCard() }catch(e){ this.shareCard() } },
    handleAvatarClick(){ this.trackEvent('avatar_click') },
    handleQuickAction(action){ this.trackEvent('quick_action',{ action_type: action.type }); switch(action.type){ case 'call': this.makePhoneCall(action.value); break; case 'wechat': this.copyWechatId(action.value); break; case 'email': this.sendEmail(action.value); break; case 'save': this.saveToContacts(); break; case 'share': this.onTopShare(); break; default: break } },
    handleContactClick(type,value,action){ 
      const resolvedAction = action || this.resolveContactAction(type)
      this.trackEvent('contact_click',{ contact_type:type, contact_action: resolvedAction })
      switch(resolvedAction){
        case 'call':
          this.makePhoneCall(value)
          break
        case 'email':
          this.sendEmail(value)
          break
        case 'website':
          this.openWebsite(value)
          break
        case 'map':
          this.openMap(value)
          break
        case 'wechat':
        case 'copy':
          if (type === 'wechat' || resolvedAction === 'wechat') {
            this.copyWechatId(value)
          } else {
            this.copyToClipboard(value)
            this.showToast('信息已复制')
          }
          break
        default:
          break
      }
    },
    resolveContactAction(type){
      switch(type){
        case 'mobile':
        case 'phone':
          return 'call'
        case 'email':
          return 'email'
        case 'website':
          return 'website'
        case 'address':
          return 'map'
        case 'wechat':
          return 'wechat'
        default:
          return 'none'
      }
    },
    handlePortfolioClick(i){ this.trackEvent('portfolio_click',{ portfolio_id:i.id }); if(i.link) safeOpenWindow(i.link,'_blank') },
    handleSocialClick(s){ this.trackEvent('social_click',{ platform:s.platform }); safeOpenWindow(s.url,'_blank') },
    makePhoneCall(n){ 
      if(this.isWecomEnv && isClient()){ 
        safeWindow((win) => win.wx.invoke('makePhoneCall',{number:n}))
      } else if(this.isMobileDevice()){ 
        safeRedirect(`tel:${n}`)
      } else { 
        this.copyToClipboard(n); 
        this.showToast('电话号码已复制') 
      } 
    },
    copyWechatId(id){ this.copyToClipboard(id); this.showToast('微信号已复制') },
    sendEmail(e){ safeRedirect(`mailto:${e}`) },
    openWebsite(url) {
      // 确保URL格式正确
      let fullUrl = url;
      
      // 如果URL不包含协议，添加https://
      if (!/^https?:\/\//i.test(url)) {
        fullUrl = 'https://' + url;
      }
      
      // 企微环境使用特殊方式打开
      if (this.isWecomEnv && process.client && isClient()) {
        try {
          safeWindow((win) => {
            if (win.wx && win.wx.invoke) {
              win.wx.invoke('openEnterpriseChat', {
                externalContact: fullUrl
              }, () => {
                // 如果失败，使用普通方式打开
                safeOpenWindow(fullUrl, '_blank');
              });
            } else {
              safeOpenWindow(fullUrl, '_blank');
            }
          });
        } catch (e) {
          console.error('打开网站失败:', e);
          safeOpenWindow(fullUrl, '_blank');
        }
      } else {
        safeOpenWindow(fullUrl, '_blank');
      }
    },
    
    openMap(address) {
      // 优化后的地图导航功能
      const q = encodeURIComponent(address);
      
      // 检测是否在移动设备上
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      
      if (isMobile) {
        // 移动端：显示地图选择菜单
        this.showMapOptions(address);
      } else {
        // PC端：复制地址并打开默认地图
        this.copyToClipboard(address);
        this.showToast('地址已复制到剪贴板');
        
        // 同时打开地图（使用高德地图搜索页面）
        safeOpenWindow(`https://www.amap.com/search?query=${q}`, '_blank');
      }
    },
    
    showMapOptions(address) {
      // 移动端地图选择
      const q = encodeURIComponent(address);
      
      // 简单的选择对话框
      const choice = confirm(`📍 ${address}\n\n点击"确定"打开地图搜索\n点击"取消"复制地址`);
      
      if (choice) {
        this.openAmapSearch(address);
      } else {
        this.copyToClipboard(address);
        this.showToast('地址已复制');
      }
    },
    
    openAmapSearch(address) {
      // 打开高德地图搜索页面（显示地址搜索结果，避免APP跳转问题）
      const q = encodeURIComponent(address);
      
      // 使用高德地图搜索URL，默认搜索并显示该地址
      // 这个URL不会触发"打开高德APP"的跳转，避免load.doc错误
      const mapUrl = `https://www.amap.com/search?query=${q}`;
      
      // 在企微环境中，使用安全的方式打开
      if (this.isWecomEnv && process.client && isClient()) {
        // 企微环境：直接在当前窗口打开，避免_blank导致的问题
        safeRedirect(mapUrl);
      } else {
        // 其他环境：新窗口打开
        safeOpenWindow(mapUrl, '_blank');
      }
    },
    async saveToContacts(){ 
      const mobile = this.cardData?.contact_info?.mobile
      if(!mobile){ 
        this.showToast('暂无可保存的手机号'); 
        return 
      }
      this.saving=true; 
      this.trackEvent('save_contact_start'); 
      try{ 
        const v=this.generateMinimalVcard(mobile); 
        if(this.isWecomEnv && process.client && isClient()){ 
          await this.saveToWecomContacts(v) 
        } else if(this.isMobileDevice()){ 
          await this.saveToMobileContacts(v) 
        } else { 
          this.downloadVcard(v) 
        } 
        this.showToast('手机号已保存到通讯录'); 
        this.trackEvent('save_contact_success') 
      }catch(e){ 
        this.showToast('保存失败，请重试'); 
        this.trackEvent('save_contact_error',{error:e.message}) 
      } finally{ 
        this.saving=false 
      } 
    },
    generateMinimalVcard(mobile){
      const name = (this.cardData?.basic_info?.name || '联系人').trim()
      const safeName = name || '联系人'
      return [
        'BEGIN:VCARD',
        'VERSION:3.0',
        `FN:${safeName}`,
        `TEL;TYPE=CELL:${mobile}`,
        'END:VCARD'
      ].join('\n')
    },
    getVcardFilename() {
      const name = (this.cardData.basic_info?.name || 'contact').trim() || 'contact'
      return `${name.replace(/\s+/g, '_')}.vcf`
    },
    encodeVcardToBase64(vcardString) {
      try {
        if (typeof window !== 'undefined' && window.btoa) {
          return window.btoa(unescape(encodeURIComponent(vcardString)))
        }
        if (typeof Buffer !== 'undefined') {
          return Buffer.from(vcardString, 'utf8').toString('base64')
        }
      } catch (error) {
        console.warn('encodeVcardToBase64 failed', error)
      }
      return ''
    },
    downloadVcard(vcardString) {
      if (!process.client) return
      const filename = this.getVcardFilename()
      try {
        const blob = new Blob([vcardString], { type: 'text/vcard;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      } catch (error) {
        console.warn('downloadVcard failed', error)
        if (this.$refs.vcardGenerator?.downloadVcard) {
          this.$refs.vcardGenerator.downloadVcard(filename)
        }
      }
    },
    async saveToMobileContacts(vcardString) {
      if (!process.client) {
        this.downloadVcard(vcardString)
        return
      }
      const filename = this.getVcardFilename()
      try {
        const file = new File([vcardString], filename, { type: 'text/vcard;charset=utf-8' })
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({
            files: [file],
            title: `${this.cardData.basic_info?.name || '联系信息'}`,
            text: this.cardData.basic_info?.title || ''
          })
          return
        }
      } catch (error) {
        console.warn('saveToMobileContacts share failed, fallback to download', error)
      }
      this.downloadVcard(vcardString)
    },
    async saveToWecomContacts(vcardString) {
      const filename = this.getVcardFilename()
      const fileData = this.encodeVcardToBase64(vcardString)
      if (!fileData) {
        this.downloadVcard(vcardString)
        return
      }
      await new Promise((resolve) => {
        let handled = false
        safeWindow((win) => {
          if (win && win.wx && typeof win.wx.invoke === 'function') {
            try {
              win.wx.invoke(
                'saveFileToDisk',
                {
                  fileData,
                  fileName: filename,
                  fileType: 'vcf'
                },
                (res = {}) => {
                  handled = true
                  if (res.err_msg && res.err_msg.indexOf('ok') > -1) {
                    resolve()
                  } else {
                    this.downloadVcard(vcardString)
                    resolve()
                  }
                }
              )
              return
            } catch (error) {
              console.warn('saveToWecomContacts invoke failed, fallback to download', error)
            }
          }
          if (!handled) {
            this.downloadVcard(vcardString)
            resolve()
          }
        })
      })
    },
    async shareCard(){ 
      this.trackEvent('share_card'); 
      if(!process.client || typeof window==='undefined'){ 
        return 
      }
      const meta = this.getShareMeta()
      if((this.isWechatEnv || this.isWecomEnv) && await this.invokeWeChatShare(meta)){ 
        return 
      }
      if(navigator.share){ 
        try{ 
          await navigator.share({
            title: meta.title,
            text: meta.text,
            url: meta.url
          }); 
          return
        }catch(e){ 
          // ignore & fallback
        } 
      } 
      this.copyToClipboard(meta.url); 
      this.showToast('名片链接已复制'); 
    },
    getShareMeta(){
      const name = this.cardData.basic_info?.name || '我的名片'
      const title = `${name}的名片`
      const textParts = []
      if(this.cardData.basic_info?.title) textParts.push(this.cardData.basic_info.title)
      if(this.cardData.basic_info?.company) textParts.push(this.cardData.basic_info.company)
      const text = textParts.join(' · ') || title
      return {
        title,
        text,
        url: getCurrentUrl(),
        image: this.cardData.basic_info?.avatar || ''
      }
    },
    copyToClipboard(t){ if(process.client) { if(navigator.clipboard) navigator.clipboard.writeText(t); else { const ta=document.createElement('textarea'); ta.value=t; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta) } } },
    showToast(m,d=2000){ if(process.client) { const x=document.createElement('div'); x.className='wecard-toast'; x.textContent=m; document.body.appendChild(x); setTimeout(()=>{ try{document.body.removeChild(x)}catch(e){} }, d) } },
    invokeWeChatShare(meta){
      return new Promise((resolve)=>{
        safeWindow((win)=>{
          if(!win || !win.wx || typeof win.wx.invoke!=='function'){ 
            resolve(false); 
            return; 
          }
          try{
            win.wx.invoke('shareAppMessage',{
              title: meta.title,
              desc: meta.text,
              link: meta.url,
              imgUrl: meta.image
            },(res={})=>{
              if(res.err_msg && res.err_msg.indexOf('ok')>-1){
                this.showToast('已分享至微信');
                resolve(true);
              }else{
                resolve(false);
              }
            })
          }catch(e){
            console.warn('invokeWeChatShare failed',e);
            resolve(false);
          }
        })
      })
    },
    isMobileDevice(){ return checkIsMobileDevice() },
    getNestedValue(o,p){ return p.split('.').reduce((c,k)=>c&&c[k],o) },
    mapToLegacyFormat(cd){ const b=cd.basic_info||{}, c=cd.contact_info||{}; return { fn:b.name?b.name.split(' ')[0]:'', ln:b.name?b.name.split(' ').slice(1).join(' '):'', TITLE:b.title||'', ORG:b.company||'', EMAIL:c.email||'', MOB:c.mobile||'', WORK:c.phone||'', website:c.website||'', WeChat:c.wechat||'', ADDRESS:c.address||'', PHOTO:b.avatar||'' } },
    async initVisitorInfo(){ try{ if(typeof navigator!=='undefined') this.visitorInfo.userAgent=navigator.userAgent||''; if(typeof document!=='undefined') this.visitorInfo.referrer=document.referrer||'' }catch(e){} },
    generateSessionId(){ return 'wecard_'+Date.now()+'_'+Math.random().toString(36).substr(2,9) },
    detectEnvironment(){ 
      if(isClient()) {
        // 安全检测企业微信环境
        this.isWecomEnv = isWecomEnvironment()
        // 检测微信环境
        this.isWechatEnv = isWechatEnvironment()
      }
    },
    trackPageView(){ if(process.client) this.trackEvent('page_view',{ card_id:this.cardId, referrer:document.referrer, user_agent:navigator.userAgent }) },
    trackEvent(et,ed={}){ this.$emit('track-event',{ event_type:et, event_data:ed, card_id:this.cardId, timestamp:Date.now(), session_id:this.visitorInfo.sessionId }) },
    handleAnalyticsEvent(e){ this.$emit('analytics-event', e) },
    getParticleStyle(i){ const s=Math.random()*4+2,l=Math.random()*100,d=Math.random()*10,u=Math.random()*20+10; return { width:`${s}px`, height:`${s}px`, left:`${l}%`, animationDelay:`${d}s`, animationDuration:`${u}s` } },
    
    // Lottie动画相关方法
    async loadLottieAnimations() {
      this.lottieLoading = true
      try {
        const [phoneRing, shareFloat] = await Promise.all([
          LottieService.getAnimation('phone-ring'),
          LottieService.getAnimation('share-float')
        ])
        this.lottieAnimations.phoneRing = phoneRing
        this.lottieAnimations.shareFloat = shareFloat
        console.log('Lottie animations loaded successfully')
      } catch (error) {
        console.warn('Failed to load Lottie animations:', error)
        this.lottieErrors.push(error)
      } finally {
        this.lottieLoading = false
      }
    },
    
    onLottieError(error) {
      console.warn('Lottie animation error:', error)
      this.lottieErrors.push(error)
    },
    
    // 新组件事件处理
    handleServiceClick(service) {
      this.trackEvent('service_click', { service_id: service.id, service_title: service.title })
      // 可以打开服务详情或跳转到服务页面
      if (service.link) {
        safeOpenWindow(service.link, '_blank')
      }
    },
    
    handleProductClick(product) {
      this.trackEvent('product_click', { product_id: product.id, product_title: product.title })
      // 可以打开产品详情
      if (product.link) {
        safeOpenWindow(product.link, '_blank')
      }
    },
    
    handleClientClick(client) {
      this.trackEvent('client_click', { client_id: client.id, client_name: client.name })
      if (client.website) {
        safeOpenWindow(client.website, '_blank')
      }
    },
    
    handleCertClick(cert) {
      this.trackEvent('certification_click', { cert_id: cert.id, cert_name: cert.name })
      if (cert.link) {
        safeOpenWindow(cert.link, '_blank')
      }
    },
    
    handleAwardClick(award) {
      this.trackEvent('award_click', { award_id: award.id, award_name: award.name })
      if (award.link) {
        safeOpenWindow(award.link, '_blank')
      }
    },
    
    handleGridItemClick({ item, index }) {
      this.trackEvent('grid_item_click', { item_id: item.id, item_title: item.title, index })
      if (item.link) {
        safeOpenWindow(item.link, '_blank')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
/* 顶部粘性功能条 */
.top-sticky-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(6px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}

/* 左侧品牌信息 */
.brand-info {
  flex: 1;
  min-width: 0;
}

.brand-text {
  font-size: 13px;
  font-weight: 500;
  color: #8c8c8c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.1px;
  opacity: 0.8;
}

/* 右侧操作按钮 */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 28px;
  padding: 0 10px;
  border: 1px solid;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 11px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.75;
  
  &:hover {
    opacity: 1;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  i {
    font-size: 12px;
  }
  
  span {
    font-weight: 400;
  }
}

/* 电话按钮样式 */
.phone-btn {
  color: #69b1ff;
  border-color: #bae0ff;
  
  &:hover {
    color: #1677ff;
    background: rgba(240, 247, 255, 0.8);
    border-color: #69b1ff;
  }
}

/* 分享按钮样式 */
.share-btn {
  color: #b37feb;
  border-color: #efdbff;
  
  &:hover {
    color: #722ed1;
    background: rgba(249, 240, 255, 0.8);
    border-color: #b37feb;
  }
}

/* 动态图标效果 */
.icon-phone-animated {
  position: relative;
  display: inline-block;
  
  &::before {
    content: "📞";
    display: inline-block;
    animation: phoneRing 3s ease-in-out infinite;
  }
}

.icon-share-animated {
  position: relative;
  display: inline-block;
  
  &::before {
    content: "📤";
    display: inline-block;
    animation: shareFloat 2s ease-in-out infinite;
  }
}

/* 电话摇摆动画 */
@keyframes phoneRing {
  0%, 90%, 100% {
    transform: rotate(0deg);
  }
  2%, 8% {
    transform: rotate(-15deg);
  }
  4%, 6% {
    transform: rotate(15deg);
  }
}

/* 分享浮动动画 */
@keyframes shareFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-3px);
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .top-sticky-bar {
    padding: 6px 12px;
  }
  
  .brand-text {
    font-size: 12px;
  }
  
  .action-btn {
    height: 26px;
    padding: 0 8px;
    font-size: 10px;
    gap: 4px;
    
    span {
      display: none; /* 移动端隐藏文字，只显示图标 */
    }
    
    i {
      font-size: 11px;
    }
  }
}

/* 减少动画模式支持 */
@media (prefers-reduced-motion: reduce) {
  .icon-phone-animated::before,
  .icon-share-animated::before {
    animation: none;
  }
  
  .action-btn:hover {
    transform: none;
  }
}

/* 底部品牌横幅 */
.brand-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 20px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
    border-color: rgba(102, 126, 234, 0.15);
  }
}

.brand-icon {
  flex-shrink: 0;
  object-fit: contain;
  opacity: 0.9;
  transition: opacity 0.3s ease;
  
  .brand-banner:hover & {
    opacity: 1;
  }
}

.brand-slogan {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  line-height: 1.5;
  text-align: center;
  letter-spacing: 0.3px;
}

/* 页脚样式调整 */
.card-footer-simple {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  text-align: center;
  
  .powered-by {
    font-size: 12px;
    color: #999;
    opacity: 0.6;
  }
}

/* 隐藏旧的快速操作条（待确认新布局稳定后可删除旧模块） */
.qa-hidden { display: none; }
</style>
