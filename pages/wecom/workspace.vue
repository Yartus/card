<template>
  <div class="workspace-page">
    <!-- 加载中 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>正在加载工作台...</p>
    </div>

    <!-- 主内容 -->
    <div v-else class="workspace-container">
      <!-- 顶部操作栏 -->
      <div class="workspace-header">
        <div class="header-left">
          <h1 class="workspace-title">
            <span class="icon">🎨</span>
            名片配置工作台
          </h1>
          <p v-if="tenantInfo" class="tenant-name">{{ tenantInfo.name }}</p>
        </div>
        
        <div class="header-actions">
          <button
            class="btn btn-secondary"
            @click="handleReset"
            :disabled="!isDirty"
          >
            <span class="icon">↺</span>
            重置
          </button>
          
          <button
            class="btn btn-preview"
            @click="showFullPreview = true"
          >
            <span class="icon">👁</span>
            全屏预览
          </button>
          
          <button
            class="btn btn-primary"
            @click="handleSave"
            :disabled="isSaving || !isDirty"
            :class="{ loading: isSaving }"
          >
            <span v-if="!isSaving" class="icon">💾</span>
            <span v-else class="spinner-small"></span>
            {{ isSaving ? '保存中...' : (activeTab === 'assets' && assetsSubTab === 'content' ? '保存素材' : '保存配置') }}
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-banner">
        <span class="icon">⚠️</span>
        {{ error }}
        <button class="close-btn" @click="clearError">×</button>
      </div>

      <!-- 未保存提示 -->
      <div v-if="isDirty" class="warning-banner">
        <span class="icon">ℹ️</span>
        您有未保存的更改
      </div>

      <!-- 标签页导航 -->
      <div class="tabs-navigation">
        <button
          :class="['tab-btn', { active: activeTab === 'modules' }]"
          @click="activeTab = 'modules'"
        >
          <span class="tab-icon">🎨</span>
          <span class="tab-text">名片模块配置</span>
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'assets' }]"
          @click="activeTab = 'assets'"
        >
          <span class="tab-icon">📚</span>
          <span class="tab-text">素材库配置</span>
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'members' }]"
          @click="activeTab = 'members'"
        >
          <span class="tab-icon">👥</span>
          <span class="tab-text">成员管理</span>
        </button>
      </div>

      <!-- 名片模块配置（左右分栏布局） -->
      <div v-show="activeTab === 'modules'" class="modules-container">
        <!-- 左侧：配置区 -->
        <div class="config-section">
          <!-- 子导航 -->
          <div class="sub-navigation">
            <button
              :class="['sub-tab', { active: subTab === 'basic' }]"
              @click="subTab = 'basic'"
            >
              <span class="sub-tab-icon">📦</span>
              <span class="sub-tab-text">基础模块</span>
            </button>
            <button
              :class="['sub-tab', { active: subTab === 'contact' }]"
              @click="subTab = 'contact'"
            >
              <span class="sub-tab-icon">👁️</span>
              <span class="sub-tab-text">联系方式</span>
            </button>
            <button
              :class="['sub-tab', { active: subTab === 'background' }]"
              @click="subTab = 'background'"
            >
              <span class="sub-tab-icon">🎨</span>
              <span class="sub-tab-text">背景设置</span>
            </button>
            <button
              :class="['sub-tab', { active: subTab === 'avatar' }]"
              @click="subTab = 'avatar'"
            >
              <span class="sub-tab-icon">👤</span>
              <span class="sub-tab-text">头像设置</span>
            </button>
            <button
              :class="['sub-tab', { active: subTab === 'logo' }]"
              @click="subTab = 'logo'"
            >
              <span class="sub-tab-icon">🏢</span>
              <span class="sub-tab-text">公司Logo</span>
            </button>
            <button
              :class="['sub-tab', { active: subTab === 'push' }]"
              @click="subTab = 'push'"
            >
              <span class="sub-tab-icon">📨</span>
              <span class="sub-tab-text">推送设置</span>
            </button>
          </div>

          <!-- 子配置内容区 -->
          <div class="sub-config-content">
            <!-- 基础模块配置 -->
            <div v-show="subTab === 'basic'" class="basic-config">
              <div class="basic-config-layout">
                <!-- 左侧：模块库 -->
                <div class="module-library-section">
                  <ModuleLibrary />
                </div>
                
                <!-- 右侧：配置区 -->
                <div class="config-area-section">
                  <ConfigArea />
                </div>
              </div>
            </div>

            <!-- 联系方式配置 -->
            <div v-show="subTab === 'contact'" class="contact-config">
              <ContactVisibilityConfig
                v-model="contactVisibility"
                :company-info="companyInfo"
                :last-sync-time="lastMemberSync"
                @input="handleContactVisibilityChange"
                @company-info-change="handleCompanyInfoChange"
                @sync-complete="handleSyncComplete"
              />
            </div>

            <!-- 头部背景配置 -->
            <div v-show="subTab === 'background'" class="background-config">
              <BackgroundEditor
                v-model="headerBackground"
                @input="handleHeaderBackgroundChange"
              />
            </div>

            <!-- 头像配置 -->
            <div v-show="subTab === 'avatar'" class="avatar-config">
              <AvatarEditor
                v-model="avatarConfig"
                :basic-info="basicInfoForAvatar"
                @input="handleAvatarConfigChange"
              />
            </div>

            <!-- Logo配置 -->
            <div v-show="subTab === 'logo'" class="logo-config">
              <LogoConfig
                v-model="logoConfig"
                :header-background="headerBackground"
                @input="handleLogoConfigChange"
              />
            </div>

            <!-- 推送设置 -->
            <div v-show="subTab === 'push'" class="push-config">
              <PushConfigSection
                v-model="pushConfig"
                :wecom-avatar="avatarConfig.wecomAvatar || basicInfoForAvatar.avatar"
                :member-info="basicInfoForAvatar"
                @input="handlePushConfigChange"
              />
            </div>
          </div>
        </div>

        <!-- 右侧：实时预览 -->
        <div class="preview-section">
          <div class="preview-sticky">
            <PreviewPanel
              :preview-card-data="previewCardData"
              :contact-visibility="contactVisibility"
              :header-background="headerBackground"
              :avatar-config="avatarConfig"
              :logo-config="logoConfig"
              :company-info="companyInfo"
            />
          </div>
        </div>
      </div>

      <!-- 素材库配置区域 -->
      <div v-show="activeTab === 'assets'" class="assets-container">
        <!-- 左侧：配置区 -->
        <div class="config-section">
          <!-- 子导航 -->
          <div class="sub-navigation">
            <button
              :class="['sub-tab', { active: assetsSubTab === 'content' }]"
              @click="assetsSubTab = 'content'"
            >
              <span class="sub-tab-icon">📝</span>
              <span class="sub-tab-text">素材内容生成</span>
            </button>
            <button
              :class="['sub-tab', { active: assetsSubTab === 'push' }]"
              @click="assetsSubTab = 'push'"
            >
              <span class="sub-tab-icon">📨</span>
              <span class="sub-tab-text">推送设置</span>
            </button>
            <button
              :class="['sub-tab', { active: assetsSubTab === 'list' }]"
              @click="assetsSubTab = 'list'"
            >
              <span class="sub-tab-icon">📋</span>
              <span class="sub-tab-text">素材列表</span>
            </button>
          </div>

          <!-- 子配置内容区 -->
          <div class="sub-config-content">
            <!-- 素材内容生成 -->
            <div v-show="assetsSubTab === 'content'" class="assets-content-config">
              <AssetsContentEditor
                v-if="authReady && assetsSubTab === 'content'"
                ref="assetContentEditor"
                @saved="handleAssetSaved"
              />
            </div>

            <!-- 推送设置 -->
            <div v-show="assetsSubTab === 'push'" class="assets-push-config">
              <AssetsCoverEditor
                v-if="authReady && assetsSubTab === 'push'"
                @go-to-content="assetsSubTab = 'content'"
                @preview-asset="handlePreviewAsset"
              />
            </div>

            <!-- 素材列表 -->
            <div v-show="assetsSubTab === 'list'" class="assets-list-config">
              <AssetsLibrary
                v-if="authReady && assetsSubTab === 'list'"
                @go-to-content="assetsSubTab = 'content'"
              />
            </div>
          </div>
        </div>

        <!-- 右侧：统一预览 -->
        <div class="preview-section">
          <AssetsPreviewPanel
            :active-tab="assetsSubTab"
            :selected-asset="selectedAssetForPreview"
            :asset-stats="assetStats"
          />
        </div>
      </div>

      <!-- 成员管理区域 -->
      <div v-show="activeTab === 'members'" class="members-container">
        <div class="members-header">
          <h2 class="section-title">
            <span class="icon">👥</span>
            成员信息管理
          </h2>
          <p class="section-description">
            手动编辑成员的对外显示名称、手机号码、职位信息（优先级：手动编辑 > OAuth授权 > 企微同步）
          </p>
        </div>

        <!-- 成员列表 -->
        <div v-if="membersLoading" class="members-loading">
          <div class="spinner"></div>
          <p>加载成员列表...</p>
        </div>

        <div v-else-if="membersError" class="members-error">
          <span class="icon">❌</span>
          {{ membersError }}
          <button class="btn btn-secondary" @click="loadMembers">重试</button>
        </div>

        <div v-else class="members-table-wrapper">
          <table class="members-table">
            <thead>
              <tr>
                <th style="width: 70px;">头像</th>
                <th style="width: 80px;">推送照片</th>
                <th style="width: 160px;">员工姓名</th>
                <th style="width: 130px;">手机号码</th>
                <th style="width: 110px;">职位</th>
                <th style="width: 80px;">角色</th>
                <th style="width: 90px;">数据来源</th>
                <th style="width: 90px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in membersList" :key="member.id">
                <td class="member-avatar-cell">
                  <template v-if="editingMemberId === member.id">
                    <div class="member-avatar-editor">
                      <ImageUpload
                        v-model="editForm.customAvatarUrl"
                        label="成员头像"
                        hint="建议400×400px，支持 JPG/PNG，未设置将使用企微头像"
                        :max-size="600 * 1024"
                        class="member-image-upload"
                      />
                      <p class="upload-tip">管理员上传后会覆盖企微头像，仅作用于该成员</p>
                    </div>
                  </template>
                  <template v-else>
                    <div class="member-avatar-display">
                      <img 
                        v-if="memberDisplayAvatar(member)" 
                        :src="memberDisplayAvatar(member)" 
                        class="member-avatar"
                        :alt="member.name"
                      />
                      <div v-else class="member-avatar-placeholder">👤</div>
                      <span v-if="member.custom_avatar_url" class="custom-badge">自定义</span>
                    </div>
                  </template>
                </td>
                <td class="member-push-photo-cell">
                  <template v-if="editingMemberId === member.id">
                    <div class="member-avatar-editor">
                      <ImageUpload
                        v-model="editForm.customPushPhotoUrl"
                        label="推送照片"
                        hint="推送卡片展示图，建议800×600px，未设置将使用全局配置"
                        :max-size="800 * 1024"
                        class="member-image-upload"
                      />
                      <p class="upload-tip">用于欢迎语第二条卡片展示的照片</p>
                    </div>
                  </template>
                  <template v-else>
                    <div class="member-push-display" :class="{ empty: !member.custom_push_photo_url }">
                      <img 
                        v-if="member.custom_push_photo_url" 
                        :src="member.custom_push_photo_url" 
                        alt="推送照片"
                        class="push-photo"
                      />
                      <div v-else class="member-avatar-placeholder push-placeholder">🖼️</div>
                    </div>
                  </template>
                </td>
                <td class="member-name-cell">
                  <div v-if="editingMemberId === member.id">
                    <input
                      v-model="editForm.displayName"
                      type="text"
                      class="edit-input"
                      placeholder="请输入姓名（如：张三）"
                    />
                    <p class="edit-hint">真实姓名，用于名片显示</p>
                  </div>
                  <div v-else class="member-name-display">
                    <div class="name-main">
                      <span v-if="member.display_name" class="display-name">
                        {{ member.display_name }}
                      </span>
                      <span v-else-if="member.name && member.name !== member.userid && member.name !== member.open_userid" class="display-name oauth-name">
                        {{ member.name }}
                      </span>
                      <span v-else class="no-name">未设置</span>
                    </div>
                    <div class="name-meta">
                      <span class="userid-short" :title="'完整ID: ' + (member.open_userid || member.userid || '无')">
                        {{ (member.open_userid || member.userid || '-').slice(-6) }}
                      </span>
                      <span v-if="member.open_userid" class="sync-badge oauth">OAuth</span>
                      <span v-else class="sync-badge local">本地</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div v-if="editingMemberId === member.id">
                    <input
                      v-model="editForm.mobile"
                      type="tel"
                      class="edit-input"
                      placeholder="手机号码"
                    />
                  </div>
                  <div v-else>{{ member.mobile || '-' }}</div>
                </td>
                <td>
                  <div v-if="editingMemberId === member.id">
                    <input
                      v-model="editForm.position"
                      type="text"
                      class="edit-input"
                      placeholder="职位"
                    />
                  </div>
                  <div v-else>{{ member.position || '-' }}</div>
                </td>
                <td>
                  <span :class="['role-badge', member.is_admin ? 'admin' : 'member']">
                    {{ member.is_admin ? '管理员' : '员工' }}
                  </span>
                </td>
                <td>
                  <div class="data-source-cell">
                    <span v-if="member.oauth_authorized" class="source-badge oauth-authorized">
                      <span class="badge-icon">✓</span>
                      <span class="badge-text">OAuth授权</span>
                    </span>
                    <span v-else class="source-badge local-sync">
                      <span class="badge-icon">📋</span>
                      <span class="badge-text">通讯录</span>
                    </span>
                  </div>
                </td>
                <td>
                  <div class="action-buttons">
                    <button
                      v-if="editingMemberId !== member.id"
                      class="btn-icon btn-edit"
                      @click="startEdit(member)"
                      title="编辑"
                    >
                      ✏️
                    </button>
                    <template v-else>
                      <button
                        class="btn-icon btn-save"
                        @click="saveEdit(member.id)"
                        :disabled="savingMemberId === member.id"
                        title="保存"
                      >
                        {{ savingMemberId === member.id ? '⏳' : '✓' }}
                      </button>
                      <button
                        class="btn-icon btn-cancel"
                        @click="cancelEdit"
                        title="取消"
                      >
                        ✕
                      </button>
                    </template>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="membersList.length === 0" class="empty-state">
            <span class="icon">📭</span>
            <p>暂无成员数据</p>
            <p class="hint">请先在企业微信中添加成员，然后同步到系统</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 全屏预览弹窗 -->
    <div v-if="showFullPreview" class="modal-overlay" @click="showFullPreview = false">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h2>名片预览</h2>
          <button class="modal-close" @click="showFullPreview = false">×</button>
        </div>
        <div class="modal-body">
          <PreviewPanel
            :fullscreen="true"
            :preview-card-data="previewCardData"
            :contact-visibility="contactVisibility"
            :header-background="headerBackground"
            :avatar-config="avatarConfig"
            :logo-config="logoConfig"
            :company-info="companyInfo"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import ModuleLibrary from '@/components/workspace/ModuleLibrary.vue'
import ConfigArea from '@/components/workspace/ConfigArea.vue'
import PreviewPanel from '@/components/workspace/PreviewPanel.vue'
import PushConfigSection from '@/components/workspace/config/PushConfigSection.vue'
import AssetsLibrary from '@/components/workspace/AssetsLibrary.vue'
import AssetsContentEditor from '@/components/workspace/AssetsContentEditor.vue'
import AssetsCoverEditor from '@/components/workspace/AssetsCoverEditor.vue'
import AssetsPreviewPanel from '@/components/workspace/AssetsPreviewPanel.vue'
import ImageUpload from '@/components/workspace/form/ImageUpload.vue'

export default {
  name: 'WorkspacePage',
  
  components: {
    ModuleLibrary,
    ConfigArea,
    PreviewPanel,
    PushConfigSection,
    AssetsLibrary,
    AssetsContentEditor,
    AssetsCoverEditor,
    AssetsPreviewPanel,
    ImageUpload,
    ContactVisibilityConfig: () => import('@/components/workspace/config/ContactVisibilityConfig.vue'),
    BackgroundEditor: () => import('@/components/workspace/config/BackgroundEditor.vue'),
    AvatarEditor: () => import('@/components/workspace/config/AvatarEditor.vue'),
    LogoConfig: () => import('@/components/workspace/config/LogoConfig.vue')
  },
  
  head() {
    return {
      meta: [
        { 'http-equiv': 'Cache-Control', content: 'no-cache, no-store, must-revalidate' },
        { 'http-equiv': 'Pragma', content: 'no-cache' },
        { 'http-equiv': 'Expires', content: '0' }
      ]
    }
  },
  
  data() {
    return {
      showFullPreview: false,
      activeTab: 'modules', // 'modules', 'assets', 'members'
      subTab: 'basic', // 'basic', 'contact', 'background', 'avatar', 'logo', 'push' (子导航，仅在modules tab下使用)
      assetsSubTab: 'content', // 'content', 'push', 'list' (子导航，仅在assets tab下使用)
      
      // 成员管理
      membersList: [],
      membersLoading: false,
      membersError: null,
      editingMemberId: null,
      savingMemberId: null,
      editForm: {
        displayName: '',
        mobile: '',
        position: '',
        customAvatarUrl: '',
        customPushPhotoUrl: ''
      },
      
      
      // 素材库预览数据
      selectedAssetForPreview: null,
      assetStats: {
        total: 0,
        published: 0,
        draft: 0
      },
      
      // 推送配置
      pushConfig: {
        cardTitle: '',
        cardDesc: '',
        cardImage: '',
        personalIntro: '',
        cardPreviewConfig: {
          avatarMode: 'company',
          companyAvatar: '',
          backgroundType: 'svg',
          svgPattern: 'geometric',
          svgGradientStart: '#ffffff',
          svgGradientEnd: '#FC726E',
          backgroundImage: '',
          backgroundColor: '#f5f5f5',
          themeColor: '#fbb9b6',
          personalIntro: ''
        }
      },
      pushConfigDirty: false,
      
      // 联系方式配置
      contactVisibility: {
        mobile: true,
        email: true,
        wechat: true,
        phone: false,
        address: true,
        website: true
      },
      contactVisibilityDirty: false,
      
      // 企业联系信息
      companyInfo: {
        phone: '',
        address: '',
        website: ''
      },
      companyInfoDirty: false,
      lastMemberSync: null,
      
      // 头部背景配置
      headerBackground: {
        backgroundType: 'svg',
        svgPattern: 'geometric',
        svgGradientStart: '#ffffff',
        svgGradientEnd: '#FC726E',
        svgDensity: 300,
        svgOpacity: 0.5,
        backgroundImage: '',
        imageOpacity: 0.8,
        imageBlur: 0,
        imageSaturation: 1.2,
        solidColor: '#667eea'
      },
      headerBackgroundDirty: false,
      
      // 头像配置
      avatarConfig: {
        useWecomAvatar: true,
        customAvatar: '',
        wecomAvatar: ''
      },
      avatarConfigDirty: false,
      
      // Logo配置
      logoConfig: {
        logo: '',
        showInHeader: true,
        showInMiddle: false,
        showInFooter: true,
        logoSize: 80
      },
      logoConfigDirty: false,
      // ✅ 认证与配置加载完成后再挂载依赖接口的子组件
      authReady: false,

      // 实时预览所使用的真实名片数据
      previewCardData: null
    }
  },
  
  computed: {
    ...mapState('workspace', [
      'tenantInfo',
      'isSaving',
      'isLoading',
      'error'
    ]),
    
    ...mapGetters('workspace', [
      'moduleCount',
      'enabledModuleCount',
      'isConfigValid'
    ]),
    
    // 合并所有配置的dirty状态
    isDirty() {
      // 名片模块的dirty状态
      const modulesDirty = this.$store.state.workspace.isDirty || 
                           this.pushConfigDirty || 
                           this.contactVisibilityDirty || 
                           this.companyInfoDirty ||
                           this.headerBackgroundDirty || 
                           this.avatarConfigDirty ||
                           this.logoConfigDirty
      
      // 素材库的dirty状态（仅在素材库tab时检查，安全访问）
      let assetsDirty = false
      try {
        if (this.activeTab === 'assets' && 
            this.assetsSubTab === 'content' &&
            this.$store.state.assetEditor) {
          assetsDirty = this.$store.state.assetEditor.isDirty || false
        }
      } catch (e) {
        // assetEditor store 未注册时，忽略错误
        console.warn('⚠️ assetEditor store 未注册，跳过素材库 dirty 状态检查')
      }
      
      return modulesDirty || assetsDirty
    },
    
    // 素材库链接
    assetLibraryUrl() {
      if (!this.tenantInfo || !this.tenantInfo.id) return ''
      const baseUrl = process.client ? window.location.origin : 'https://zjemail.cn'
      return `${baseUrl}/assets/${this.tenantInfo.id}`
    },
    
    // 头像编辑器需要的基础信息
    basicInfoForAvatar() {
      const userInfo = this.$wecomAuth?.getUserInfo() || {}
      return {
        name: userInfo.name || this.tenantInfo?.name || '管理员',
        avatar: userInfo.avatar || this.tenantInfo?.avatar || '',
        title: userInfo.title || '管理员'
      }
    }
  },
  
  async mounted() {
    console.log('🚀 Workspace页面加载')
    console.log('📍 当前URL:', window.location.href)
    console.log('📍 Query参数:', JSON.stringify(this.$route.query))
    
    const isMobile = /Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    
    // ✅ 官方推荐的企微OAuth认证流程
    // 使用getuserinfo3rd接口，自动识别企业
    const code = this.$route.query.code
    
    // 步骤1：检查是否有企微回调code参数
    if (code) {
      console.log('📱 检测到OAuth code参数，开始验证用户身份...')
      try {
        // 调用后端验证接口（只需要code，后端会自动识别企业）
        const { data } = await this.$axios.get('/api/v1/wecom/auth/verify_user', {
          params: {
            code,
            target: isMobile ? 'card' : 'workspace',
            allow_non_admin: isMobile
          }
        })
        
        if (data.success) {
          // 保存token和用户信息
          this.$wecomAuth.setToken(data.token)
          this.$wecomAuth.setUserInfo(data.user)
          
          console.log('✅ 认证成功:', {
            userid: data.user.userid,
            corp_id: data.user.corp_id,
            tenant_name: data.user.tenant_name
          })
          
          // ✅ 移动端检测：认证成功后，如果是移动端，直接跳转到名片页面
          if (isMobile) {
            console.log('📱 移动端认证成功，跳转到名片页面（显示当前用户的名片）')
            this.$router.replace('/wecom/card')
            return
          }
          
          // ✅ 使用 window.history.replaceState 清除URL参数，避免页面刷新
          const url = new URL(window.location.href)
          url.search = ''
          window.history.replaceState({}, '', url.toString())
          console.log('✅ URL参数已清除，不会触发页面刷新')
        } else {
          throw new Error(data.message || '认证失败')
        }
      } catch (error) {
        console.error('❌ 认证失败:', error)
        const errorMsg = error.response?.data?.message || error.message || '认证失败'
        alert('认证失败：' + errorMsg)
        
        // 如果是权限不足，跳转到安装页面
        if (error.response?.status === 403) {
          this.$router.push('/wecom/install')
        }
        return
      }
    }
    
    // 步骤2：检查是否已经有token
    if (!this.$wecomAuth.isAuthenticated()) {
      console.log('⚠️ 未检测到认证token，需要进行OAuth授权')
      console.log('📍 当前URL:', window.location.href)
      console.log('📍 Query参数:', this.$route.query)
      
      // 🔑 关键修改：主动发起OAuth授权
      // 没有token且没有code，说明需要跳转到企微授权页面
      if (!code) {
        console.log('🔄 正在跳转到企微授权页面...')
        await this.redirectToAuth()
        return
      }
      
      // 如果有code但认证失败（不应该走到这里）
      alert('认证异常，请重新打开应用')
      this.$router.push('/wecom/install')
      return
    }
    
    console.log('✅ 已有认证token，跳过验证直接加载配置')
    
    // 步骤4：检查用户权限和设备类型，自动分流
    const userInfo = this.$wecomAuth.getUserInfo()
    console.log('👤 用户信息:', userInfo)
    console.log('📱 设备类型:', isMobile ? '移动端' : '电脑端')
    
    // ✅ 普通用户：任何设备都跳转到名片页面
    if (!userInfo?.is_admin) {
      console.log('⚠️ 普通用户，跳转到名片页面')
      this.$router.replace('/wecom/card')
      return
    }
    
    // ✅ 管理员在移动端：跳转到名片页面
    if (userInfo?.is_admin && isMobile) {
      console.log('📱 管理员在移动端，跳转到名片页面')
      this.$router.replace('/wecom/card')
      return
    }
    
    // ✅ 管理员在电脑端：留在工作台
    console.log('💻 管理员在电脑端，显示工作台')
    
    // 步骤5：加载配置（只有管理员才能执行）
    try {
      await this.loadConfig()
      console.log('✅ 配置加载成功')
      
      // 🔧 同步store中的header配置到本地data
      if (this.$store.state.workspace.header) {
        // 同步联系方式配置
        if (this.$store.state.workspace.header.contact_visibility) {
          this.contactVisibility = { 
            ...this.contactVisibility, 
            ...this.$store.state.workspace.header.contact_visibility 
          }
          console.log('✅ 联系方式配置已同步:', this.contactVisibility)
        }
        
        // 同步企业联系信息
        if (this.$store.state.workspace.header.company_info) {
          this.companyInfo = {
            ...this.companyInfo,
            ...this.$store.state.workspace.header.company_info
          }
          console.log('✅ 企业联系信息已同步:', this.companyInfo)
        }
        
        // 同步头部背景配置
        if (this.$store.state.workspace.header && this.$store.state.workspace.header.background) {
          this.headerBackground = {
            ...this.headerBackground,
            ...this.$store.state.workspace.header.background
          }
          console.log('✅ 头部背景配置已同步:', this.headerBackground)
        }
        
        // 同步头像配置
        if (this.$store.state.workspace.header && this.$store.state.workspace.header.avatar) {
          this.avatarConfig = {
            ...this.avatarConfig,
            ...this.$store.state.workspace.header.avatar
          }
          // 如果使用企业微信头像，从basicInfo获取
          if (this.avatarConfig.useWecomAvatar && this.tenantInfo) {
            this.avatarConfig.wecomAvatar = this.tenantInfo.avatar || ''
          }
          console.log('✅ 头像配置已同步:', this.avatarConfig)
        }
        
        // 同步Logo配置
        if (this.$store.state.workspace.header.company_logo) {
          this.logoConfig = {
            ...this.logoConfig,
            enabled: this.$store.state.workspace.header.show_company_logo !== false,
            logoUrl: this.$store.state.workspace.header.company_logo || '',
            logoSize: this.$store.state.workspace.header.logo_size || 'medium',
            logoPosition: this.$store.state.workspace.header.logo_position || 'left'
          }
          console.log('✅ Logo配置已同步:', this.logoConfig)
        }
      }
      
      // 加载推送配置
      await this.loadPushConfig()

      // 加载当前成员真实名片数据用于预览
      await this.loadPreviewCardData()
      
      // ✅ 所有初始化流程完成，允许依赖鉴权的子组件挂载
      this.authReady = true
      console.log('✅ Workspace 鉴权初始化完成，子组件已解锁')
    } catch (error) {
      console.error('❌ 加载配置失败:', error)
      if (error.response?.status === 403) {
        alert('您没有管理员权限，将跳转到名片查看页面')
        this.$router.replace('/wecom/card')
      } else if (error.response?.status === 401) {
        console.log('⚠️ Token已失效（401），重新认证')
        this.$wecomAuth.clearAuth()
        await this.redirectToAuth()
      } else {
        alert('加载配置失败：' + (error.response?.data?.message || error.message || '未知错误'))
      }
    }
  },
  
  beforeRouteLeave(to, from, next) {
    // 离开页面前检查未保存的更改
    if (this.isDirty) {
      const confirmed = confirm('您有未保存的更改，确定要离开吗？')
      if (!confirmed) {
        next(false)
        return
      }
    }
    next()
  },
  
  watch: {
    activeTab(newTab) {
      if (newTab === 'members' && this.membersList.length === 0) {
        this.loadMembers()
      }
    }
  },
  
  methods: {
    ...mapActions('workspace', [
      'loadConfig',
      'saveConfig',
      'resetConfig'
    ]),
    
    // 加载推送配置
    async loadPushConfig() {
      try {
        if (this.tenantInfo && this.tenantInfo.config) {
          const pushConfig = this.tenantInfo.config.push_config || {}
          this.pushConfig = {
            cardTitle: pushConfig.cardTitle || '',
            cardPreviewConfig: pushConfig.cardPreviewConfig || {
              avatarMode: 'company',
              companyAvatar: '',
              backgroundType: 'svg',
              svgPattern: 'geometric',
              svgGradientStart: '#ffffff',
              svgGradientEnd: '#FC726E',
              backgroundImage: '',
              backgroundColor: '#f5f5f5',
              bottomColor: '#fbb9b6',
              phoneIconColor: '#fbb9b6',
              personalIntro: ''
            }
          }
          console.log('✅ 推送配置已加载:', this.pushConfig)
        }
      } catch (error) {
        console.error('❌ 加载推送配置失败:', error)
      }
    },

    async loadPreviewCardData() {
      try {
        const { data } = await this.$axios.get('/api/v1/wecom/card/my')
        if (data && data.card_data) {
          this.previewCardData = data.card_data
          console.log('✅ 预览名片数据已加载')
        }
      } catch (error) {
        console.error('❌ 加载预览名片数据失败:', error)
      }
    },
    
    // 推送配置变更
    handlePushConfigChange(config) {
      this.pushConfig = { ...config }
      this.pushConfigDirty = true
      console.log('📝 推送配置已变更:', config)
    },
    
    handleContactVisibilityChange(config) {
      this.contactVisibility = { ...config }
      this.contactVisibilityDirty = true
      console.log('📝 联系方式配置已变更:', config)
    },
    
    handleCompanyInfoChange(info) {
      this.companyInfo = { ...info }
      this.companyInfoDirty = true
      console.log('📝 企业联系信息已变更:', info)
    },
    
    handleHeaderBackgroundChange(config) {
      // 深拷贝确保响应式
      this.headerBackground = JSON.parse(JSON.stringify(config))
      this.headerBackgroundDirty = true
      console.log('📝 头部背景配置已变更:', config)
    },

    handleAvatarConfigChange(config) {
      // 深拷贝确保响应式
      this.avatarConfig = JSON.parse(JSON.stringify(config))
      this.avatarConfigDirty = true
      console.log('📝 头像配置已变更:', config)
    },

    handleLogoConfigChange(config) {
      // 深拷贝确保响应式
      this.logoConfig = JSON.parse(JSON.stringify(config))
      this.logoConfigDirty = true
      console.log('📝 Logo配置已变更:', config)
    },
    
    handleSyncComplete(data) {
      this.lastMemberSync = data.synced_at
      this.$toast.success(data.message || '同步成功')
      console.log('✅ 成员同步完成:', data)
    },
    
    async redirectToAuth() {
      // 获取当前页面URL作为回调地址
      const redirectUri = window.location.origin + this.$route.path
      try {
        const authUrl = await this.$wecomAuth.getAuthUrl(redirectUri)
        // 重定向到企微授权页面
        window.location.href = authUrl
      } catch (error) {
        console.error('Failed to get auth URL:', error)
        alert('获取授权链接失败')
        this.$router.push('/wecom/install')
      }
    },
    
    async handleSave() {
      let hasChanges = false
      
      try {
        // 名片模块配置tab：保存所有子配置
        if (this.activeTab === 'modules') {
          // 基础模块配置验证
          if (!this.isConfigValid) {
            alert('配置验证失败，请检查配置项')
            return
          }
          
          // 保存基础模块配置
          if (this.$store.state.workspace.isDirty) {
            await this.saveConfig()
            hasChanges = true
          }
          
          // 保存联系方式配置
          if (this.contactVisibilityDirty) {
            await this.saveContactVisibility()
            this.contactVisibilityDirty = false
            hasChanges = true
          }
          
          // 保存企业联系信息
          if (this.companyInfoDirty) {
            await this.saveCompanyInfo()
            this.companyInfoDirty = false
            hasChanges = true
          }
          
          // 保存头部背景配置
          if (this.headerBackgroundDirty) {
            await this.saveHeaderBackground()
            this.headerBackgroundDirty = false
            hasChanges = true
          }
          
          // 保存头像配置
          if (this.avatarConfigDirty) {
            await this.saveAvatarConfig()
            this.avatarConfigDirty = false
            hasChanges = true
          }
          
          // 保存Logo配置
          if (this.logoConfigDirty) {
            await this.saveLogoConfig()
            this.logoConfigDirty = false
            hasChanges = true
          }
        }
        
        // 推送消息配置（在modules tab的push子标签中）
        if (this.pushConfigDirty) {
          await this.savePushConfig()
          this.pushConfigDirty = false
          hasChanges = true
        }
        
        // ✅ 素材库配置tab：保存素材内容
        if (this.activeTab === 'assets' && this.assetsSubTab === 'content') {
          // 调用 AssetsContentEditor 的保存方法
          if (this.$refs.assetContentEditor) {
            try {
              await this.$refs.assetContentEditor.saveAsset()
              hasChanges = true
            } catch (error) {
              console.error('保存素材失败:', error)
              // 错误已在 AssetsContentEditor 中处理，这里不重复提示
              throw error // 重新抛出错误，让外层 catch 处理
            }
          } else {
            this.$toast?.warning('素材编辑器未加载，请稍后重试')
          }
        }
        
        if (hasChanges) {
          this.$toast?.success('配置已保存')
        } else {
          this.$toast?.info('当前没有需要保存的更改')
        }
      } catch (error) {
        console.error('❌ 保存失败:', error)
        const errorMsg = error.response?.data?.message || error.response?.data?.error || error.message || '保存失败，请重试'
        this.$toast?.error(errorMsg)
        
        // 如果是认证错误，提示用户重新登录
        if (error.response?.status === 401) {
          console.error('认证失败，可能需要重新登录')
        }
        // 如果是权限错误
        if (error.response?.status === 403) {
          console.error('权限不足，需要管理员权限')
        }
      }
    },
    
    // 保存推送配置
    async savePushConfig() {
      try {
        // 验证配置数据
        if (!this.pushConfig || typeof this.pushConfig !== 'object') {
          throw new Error('推送配置数据无效')
        }
        
        console.log('💾 开始保存推送配置:', JSON.stringify(this.pushConfig, null, 2))
        
        // 确保发送正确的数据格式
        const payload = {
          push_config: {
            cardTitle: this.pushConfig.cardTitle || '',
            cardPreviewConfig: this.pushConfig.cardPreviewConfig || {}
          }
        }
        
        console.log('📤 发送请求数据:', JSON.stringify(payload, null, 2))
        
        const response = await this.$axios.put('/api/v1/wecom/tenant/workspace', payload, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        console.log('📥 服务器响应:', response.status, response.data)
        
        if (response.data && response.data.success) {
          console.log('✅ 推送配置保存成功')
          // 更新tenantInfo
          if (this.tenantInfo) {
            this.tenantInfo.config = this.tenantInfo.config || {}
            this.tenantInfo.config.push_config = { ...this.pushConfig }
          }
          return true
        } else {
          const errorMsg = response.data?.error || response.data?.message || '保存失败'
          console.error('❌ 保存失败:', errorMsg)
          throw new Error(errorMsg)
        }
      } catch (error) {
        console.error('❌ 保存推送配置失败:', error)
        console.error('错误状态:', error.response?.status)
        console.error('错误详情:', error.response?.data)
        console.error('错误堆栈:', error.stack)
        
        let errorMsg = '保存失败，请重试'
        
        if (error.response) {
          // 服务器返回了错误响应
          errorMsg = error.response.data?.message || error.response.data?.error || error.message
          
          // 根据状态码提供更具体的错误信息
          if (error.response.status === 401) {
            errorMsg = '认证失败，请重新登录'
          } else if (error.response.status === 403) {
            errorMsg = '权限不足，需要管理员权限'
          } else if (error.response.status === 400) {
            errorMsg = error.response.data?.error || '请求数据格式错误'
          } else if (error.response.status === 500) {
            errorMsg = error.response.data?.message || '服务器内部错误'
          }
        } else if (error.request) {
          // 请求已发送但没有收到响应
          errorMsg = '网络错误，请检查网络连接'
        } else {
          // 其他错误
          errorMsg = error.message || '未知错误'
        }
        
        throw new Error(errorMsg)
      }
    },
    
    // 保存联系方式配置
    async saveContactVisibility() {
      try {
        console.log('💾 开始保存联系方式配置:', this.contactVisibility)
        
        // 从 store 构建完整配置
        const config = {
          version: this.$store.state.workspace.version || '1.0',
          modules: this.$store.state.workspace.modules || [],
          theme: this.$store.state.workspace.theme || 'tech',
          header: {
            ...this.$store.state.workspace.header,
            contact_visibility: this.contactVisibility
          }
        }
        
        console.log('📦 完整配置:', config)
        
        const response = await this.$axios.put('/api/v1/wecom/tenant/workspace', {
          config
        })
        
        console.log('📥 服务器响应:', response.data)
        if (response.data.success) {
          console.log('✅ 联系方式配置保存成功')
          // 更新 store
          this.$store.commit('workspace/SET_CONFIG', config)
        }
      } catch (error) {
        console.error('❌ 保存联系方式配置失败:', error)
        console.error('错误详情:', error.response?.data)
        throw error
      }
    },
    
    async saveCompanyInfo() {
      try {
        console.log('💾 开始保存企业联系信息:', this.companyInfo)
        
        // 从 store 构建完整配置
        const config = {
          version: this.$store.state.workspace.version || '1.0',
          modules: this.$store.state.workspace.modules || [],
          theme: this.$store.state.workspace.theme || 'tech',
          header: {
            ...this.$store.state.workspace.header,
            company_info: this.companyInfo
          }
        }
        
        console.log('📦 完整配置:', config)
        
        const response = await this.$axios.put('/api/v1/wecom/tenant/workspace', {
          config
        })
        
        console.log('📥 服务器响应:', response.data)
        if (response.data.success) {
          console.log('✅ 企业联系信息保存成功')
          // 更新 store
          this.$store.commit('workspace/SET_CONFIG', config)
        }
      } catch (error) {
        console.error('❌ 保存企业联系信息失败:', error)
        console.error('错误详情:', error.response?.data)
        throw error
      }
    },
    
    // 保存头部背景配置
    async saveHeaderBackground() {
      try {
        console.log('💾 开始保存头部背景配置:', this.headerBackground)
        
        // 从 store 构建完整配置
        const config = {
          version: this.$store.state.workspace.version || '1.0',
          modules: this.$store.state.workspace.modules || [],
          theme: this.$store.state.workspace.theme || 'tech',
          header: {
            ...this.$store.state.workspace.header,
            background: this.headerBackground
          }
        }
        
        console.log('📦 完整配置:', config)
        
        const response = await this.$axios.put('/api/v1/wecom/tenant/workspace', {
          config
        })
        
        console.log('📥 服务器响应:', response.data)
        if (response.data.success) {
          console.log('✅ 头部背景配置保存成功')
          // 更新 store
          this.$store.commit('workspace/SET_CONFIG', config)
        }
      } catch (error) {
        console.error('❌ 保存头部背景配置失败:', error)
        console.error('错误详情:', error.response?.data)
        throw error
      }
    },
    
    // 保存头像配置
    async saveAvatarConfig() {
      try {
        console.log('💾 开始保存头像配置:', this.avatarConfig)
        
        // 从 store 构建完整配置
        const config = {
          version: this.$store.state.workspace.version || '1.0',
          modules: this.$store.state.workspace.modules || [],
          theme: this.$store.state.workspace.theme || 'tech',
          header: {
            ...this.$store.state.workspace.header,
            avatar: this.avatarConfig
          }
        }
        
        console.log('📦 完整配置:', config)
        
        const response = await this.$axios.put('/api/v1/wecom/tenant/workspace', {
          config
        })
        
        console.log('📥 服务器响应:', response.data)
        if (response.data.success) {
          console.log('✅ 头像配置保存成功')
          // 更新 store
          this.$store.commit('workspace/SET_CONFIG', config)
        }
      } catch (error) {
        console.error('❌ 保存头像配置失败:', error)
        console.error('错误详情:', error.response?.data)
        throw error
      }
    },
    
    // 保存Logo配置
    async saveLogoConfig() {
      try {
        console.log('💾 开始保存Logo配置:', this.logoConfig)
        
        // 从 store 构建完整配置
        const config = {
          version: this.$store.state.workspace.version || '1.0',
          modules: this.$store.state.workspace.modules || [],
          theme: this.$store.state.workspace.theme || 'tech',
          header: {
            ...this.$store.state.workspace.header,
            logo: this.logoConfig
          }
        }
        
        console.log('📦 完整配置:', config)
        
        const response = await this.$axios.put('/api/v1/wecom/tenant/workspace', {
          config
        })
        
        console.log('📥 服务器响应:', response.data)
        if (response.data.success) {
          console.log('✅ Logo配置保存成功')
          // 更新 store
          this.$store.commit('workspace/SET_CONFIG', config)
        }
      } catch (error) {
        console.error('❌ 保存Logo配置失败:', error)
        console.error('错误详情:', error.response?.data)
        throw error
      }
    },
    
    handleReset() {
      this.resetConfig()
    },
    
    clearError() {
      this.$store.commit('workspace/CLEAR_ERROR')
    },
    
    // 复制素材库链接
    copyAssetLink() {
      if (!this.assetLibraryUrl) {
        this.$toast?.error('素材库链接不可用')
        return
      }
      
      if (navigator.clipboard) {
        navigator.clipboard.writeText(this.assetLibraryUrl)
          .then(() => {
            this.$toast?.success('素材库链接已复制')
          })
          .catch(() => {
            this.$toast?.error('复制失败，请手动复制')
          })
      } else {
        // 降级方案
        const textArea = document.createElement('textarea')
        textArea.value = this.assetLibraryUrl
        document.body.appendChild(textArea)
        textArea.select()
        try {
          document.execCommand('copy')
          this.$toast?.success('素材库链接已复制')
        } catch (err) {
          this.$toast?.error('复制失败，请手动复制')
        }
        document.body.removeChild(textArea)
      }
    },
    
    // 查看素材库规划文档
    handleAssetManagement() {
      this.$toast?.info('素材库功能规划中，敬请期待')
      // 可以在这里打开文档链接或显示详细说明
    },
    
    // 素材保存后回调
    handleAssetSaved(asset) {
      this.$toast?.success('素材保存成功')
      // 刷新素材统计
      this.refreshAssetStats()
    },
    
    // 预览素材
    handlePreviewAsset(assetId) {
      // TODO: 加载素材详情
      this.selectedAssetForPreview = { id: assetId }
    },
    
    // 刷新素材统计
    async refreshAssetStats() {
      try {
        const token = this.$wecomAuth?.getToken()
        if (!token) return
        
        const response = await this.$axios.get('/api/tenant/assets/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.data && response.data.success) {
          this.assetStats = response.data.stats || this.assetStats
        }
      } catch (error) {
        // 静默处理错误，避免影响页面加载
        if (error.response?.status !== 404) {
          console.warn('⚠️ 获取素材统计失败:', error.message)
        }
        // 404 表示 API 未注册，使用默认值即可，不抛出错误
      }
    },
    
    // 成员管理方法
    async loadMembers() {
      this.membersLoading = true
      this.membersError = null
      
      try {
        const token = this.$wecomAuth.getToken()
        if (!token) {
          throw new Error('未登录，请刷新页面')
        }
        
        const response = await this.$axios.get('/api/v1/wecom/members', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.data && response.data.members) {
          this.membersList = response.data.members
          console.log('✅ 成员列表加载成功:', this.membersList.length)
        }
      } catch (error) {
        console.error('❌ 加载成员列表失败:', error)
        this.membersError = error.response?.data?.error || error.message || '加载失败'
      } finally {
        this.membersLoading = false
      }
    },
    
    startEdit(member) {
      this.editingMemberId = member.id
      this.editForm = {
        displayName: member.display_name || '',
        mobile: member.mobile || '',
        position: member.position || '',
        customAvatarUrl: member.custom_avatar_url || '',
        customPushPhotoUrl: member.custom_push_photo_url || ''
      }
    },
    
    cancelEdit() {
      this.editingMemberId = null
      this.editForm = {
        displayName: '',
        mobile: '',
        position: '',
        customAvatarUrl: '',
        customPushPhotoUrl: ''
      }
    },
    
    async saveEdit(memberId) {
      if (!this.editForm.displayName || !this.editForm.displayName.trim()) {
        alert('姓名不能为空')
        return
      }
      
      this.savingMemberId = memberId
      
      try {
        const token = this.$wecomAuth.getToken()
        if (!token) {
          throw new Error('未登录，请刷新页面')
        }
        
        const response = await this.$axios.put(
          `/api/v1/wecom/members/${memberId}`,
          {
            display_name: this.editForm.displayName.trim(),
            mobile: this.editForm.mobile.trim() || null,
            position: this.editForm.position.trim() || null,
            custom_avatar_url: this.normalizeUrl(this.editForm.customAvatarUrl),
            custom_push_photo_url: this.normalizeUrl(this.editForm.customPushPhotoUrl)
          },
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )
        
        if (response.data && response.data.success) {
          // 更新本地列表
          const index = this.membersList.findIndex(m => m.id === memberId)
          if (index !== -1) {
            this.membersList[index] = {
              ...this.membersList[index],
              ...response.data.member
            }
          }
          
          alert('✅ 保存成功！成员信息已更新')
          this.cancelEdit()
        }
      } catch (error) {
        console.error('❌ 保存成员信息失败:', error)
        const errorMsg = error.response?.data?.error || error.message || '保存失败'
        alert(`保存失败: ${errorMsg}`)
      } finally {
        this.savingMemberId = null
      }
    },

    normalizeUrl(url) {
      if (!url || typeof url !== 'string') {
        return null
      }
      const trimmed = url.trim()
      return trimmed || null
    },

    memberDisplayAvatar(member) {
      if (!member) return ''
      return member.custom_avatar_url || member.avatar_url || ''
    }
  }
}
</script>

<style scoped>
.workspace-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
}

.workspace-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

/* 加载中 */
.loading-overlay {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e8e8e8;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 主容器 */
.workspace-container {
  padding: 24px;
  max-width: 1920px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

/* 顶部操作栏 */
.workspace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.workspace-title {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  letter-spacing: -0.5px;
}

.workspace-title::before {
  content: '✨';
  font-size: 32px;
  filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
}

.tenant-name {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 按钮样式 */
.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn .icon {
  font-size: 16px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-primary:hover:not(:disabled)::before {
  left: 100%;
}

.btn-secondary {
  background: white;
  color: #595959;
  border: 1px solid #d9d9d9;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-preview {
  background: #52c41a;
  color: white;
}

.btn-preview:hover {
  background: #389e0d;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.loading {
  position: relative;
}

.spinner-small {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* 提示横幅 */
.error-banner,
.warning-banner {
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.error-banner {
  background: #fff2e8;
  border: 1px solid #ffbb96;
  color: #d4380d;
}

.warning-banner {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #0050b3;
}

.close-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: inherit;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.06);
}

/* 标签页导航 */
.tabs-navigation {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 8px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.tab-btn {
  flex: 1;
  padding: 14px 28px;
  background: transparent;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
}

.tab-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.tab-btn:hover:not(.active) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  transform: translateY(-2px);
}

.tab-btn.active {
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.tab-btn.active::before {
  opacity: 1;
}

.tab-btn .tab-icon,
.tab-btn .tab-text {
  position: relative;
  z-index: 1;
}

.tab-icon {
  font-size: 22px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  flex-shrink: 0;
}

.tab-text {
  white-space: nowrap;
}

/* 推送配置容器 */
.push-config-container {
  max-width: 900px;
  margin: 0 auto;
  animation: fadeInUp 0.6s ease-out;
}

/* 素材库配置容器 */
.assets-config-container {
  animation: fadeInUp 0.6s ease-out;
  max-width: 1200px;
  margin: 0 auto;
}

.assets-management {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.8);
  padding: 40px;
}

.assets-header {
  text-align: center;
  margin-bottom: 32px;
}

.assets-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.assets-subtitle {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
}

.assets-quick-info {
  margin-bottom: 32px;
}

.info-card {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 20px 24px;
  border: 1px solid #e8e8e8;
}

.info-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-bottom: 8px;
  font-weight: 500;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-value code {
  flex: 1;
  background: white;
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  color: #262626;
  word-break: break-all;
}

.copy-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.copy-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.assets-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.placeholder-content {
  text-align: center;
  max-width: 600px;
  padding: 40px;
}

.placeholder-icon {
  font-size: 80px;
  display: block;
  margin-bottom: 24px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.placeholder-title {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 16px 0;
}

.placeholder-desc {
  font-size: 16px;
  color: #595959;
  line-height: 1.8;
  margin: 0 0 20px 0;
  text-align: left;
}

.placeholder-tip {
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 0 0 24px 0;
  font-size: 14px;
  color: #874d00;
  text-align: left;
}

.placeholder-tip strong {
  font-weight: 600;
}

.placeholder-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.placeholder-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 名片模块配置 - 左右分栏布局 */
.modules-container {
  display: grid;
  grid-template-columns: 1fr 405px; /* 右侧固定405px，匹配375px手机+边框 */
  gap: 24px;
  min-height: calc(100vh - 200px);
  align-items: start; /* 确保左右两列从顶部对齐 */
  animation: fadeInUp 0.6s ease-out;
}

/* 左侧配置区 */
.config-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 子导航 */
.sub-navigation {
  display: flex;
  gap: 12px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.sub-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  font-weight: 500;
  color: #666;
  position: relative;
}

.sub-tab:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  transform: translateY(-2px);
}

.sub-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.sub-tab-icon {
  font-size: 20px;
  position: relative;
  z-index: 1;
}

.sub-tab-text {
  position: relative;
  z-index: 1;
  white-space: nowrap;
}

/* 子配置内容区 */
.sub-config-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.8);
  padding: 32px;
  min-height: 600px;
}

/* 基础模块配置布局 */
.basic-config-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  min-height: 600px;
}

/* 右侧预览区 */
.preview-section {
  position: relative;
  display: flex;
  justify-content: center;
  margin-top: 14px; /* 向上调整，与左侧子导航对齐 */
}

.preview-sticky {
  position: sticky;
  top: 0;
  background: #f8f9fa;
  backdrop-filter: blur(20px);
  border-radius: 32px; /* 更大的圆角，像手机 */
  box-shadow: 
    0 0 0 12px rgba(102, 126, 234, 0.1), /* 内层淡紫色边框 */
    0 0 0 14px rgba(255, 255, 255, 0.8), /* 中层白色边框 */
    0 4px 24px rgba(0, 0, 0, 0.12); /* 外层阴影 - 减少垂直偏移 */
  /* 标准手机竖屏比例 375:667 (iPhone 6/7/8) */
  width: 375px;
  height: 667px;
  overflow: hidden;
  border: 2px solid rgba(102, 126, 234, 0.2); /* 淡紫色细边框 */
}

/* 全屏预览弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-large {
  width: 90%;
  max-width: 1200px;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
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
  flex: 1;
}

/* 素材库容器 */
.assets-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  padding: 24px;
  min-height: calc(100vh - 280px);
}

.assets-preview-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.assets-preview-panel h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.preview-placeholder {
  color: #8c8c8c;
  text-align: center;
  padding: 40px 20px;
  line-height: 1.6;
}

.config-placeholder {
  color: #8c8c8c;
  text-align: center;
  padding: 60px 20px;
  font-size: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 响应式 */
@media (max-width: 1600px) {
  .workspace-layout {
    grid-template-columns: 260px 1fr 360px;
  }
}

@media (max-width: 1400px) {
  .workspace-layout {
    grid-template-columns: 240px 1fr 340px;
  }
}

@media (max-width: 1200px) {
  .workspace-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .panel-right {
    position: relative;
    top: 0;
    max-height: none;
  }
  
  .assets-container {
    grid-template-columns: 1fr;
  }
}

/* 成员管理样式 */
.members-container {
  padding: 24px;
  background: white;
  border-radius: 12px;
  max-width: 1400px;
  margin: 0 auto;
}

.members-header {
  margin-bottom: 24px;
}

.members-header .section-title {
  font-size: 24px;
  font-weight: 700;
  color: #262626;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.members-header .section-description {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

.members-loading,
.members-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
}

.members-error {
  color: #ff4d4f;
}

.members-table-wrapper {
  overflow-x: auto;
}

.members-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.members-table thead {
  background: #fafafa;
}

.members-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #595959;
  border-bottom: 2px solid #f0f0f0;
  white-space: nowrap;
}

.members-table td {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  color: #262626;
  vertical-align: middle;
}

.members-table tbody tr:hover {
  background: #fafafa;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.member-avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.member-avatar-cell {
  width: 70px;
  text-align: center;
}

.member-push-photo-cell {
  width: 80px;
  text-align: center;
}

.member-name-cell {
  width: 160px;
  max-width: 200px;
}

.member-avatar-editor,
.member-push-photo-cell .member-avatar-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-image-upload .upload-area {
  min-height: 140px;
}

.member-image-upload .preview-image {
  max-width: 120px;
  max-height: 120px;
}

.upload-tip {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0;
}

.member-avatar-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.custom-badge {
  display: inline-flex;
  align-items: center;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 999px;
  background: #e6f7ff;
  color: #096dd9;
  border: 1px solid #91d5ff;
  width: fit-content;
}

.member-push-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.push-photo {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #f0f0f0;
}

.push-placeholder {
  width: 60px;
  height: 60px;
  background: #fafafa;
  border: 1px dashed #d9d9d9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.push-label {
  font-size: 10px;
  color: #8c8c8c;
  text-align: center;
  line-height: 1.2;
}

.userid-code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  margin-right: 4px;
  
  &.primary-id {
    background: #e6f7ff;
    color: #0066cc;
    border: 1px solid #91d5ff;
  }
  
  &.secondary-id {
    background: #fff7e6;
    color: #d46b08;
    border: 1px solid #ffd591;
    font-size: 11px;
  }
  color: #595959;
}

.member-name-display {
  display: flex;
  flex-direction: column;
  gap: 4px;
  
  .name-main {
    font-size: 14px;
    line-height: 1.4;
    
    .display-name {
      font-weight: 500;
      color: #262626;
      
      &.oauth-name {
        color: #0066cc;
      }
    }
    
    .no-name {
      color: #bfbfbf;
      font-size: 12px;
    }
  }
  
  .name-meta {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .userid-short {
      font-size: 10px;
      color: #8c8c8c;
      font-family: 'Monaco', 'Menlo', monospace;
      cursor: help;
      background: #f5f5f5;
      padding: 1px 4px;
      border-radius: 2px;
    }
    
    .sync-badge {
      display: inline-block;
      padding: 1px 4px;
      border-radius: 2px;
      font-size: 9px;
      font-weight: 500;
      line-height: 1.2;
      
      &.oauth {
        background: #e6f7ff;
        color: #0066cc;
      }
      
      &.local {
        background: #f0f0f0;
        color: #8c8c8c;
      }
    }
  }
}

.member-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-hint {
  font-size: 11px;
  color: #8c8c8c;
  margin-top: 4px;
  margin-bottom: 0;
}

.warning-badge {
  font-size: 11px;
  padding: 2px 6px;
  background: #fff7e6;
  color: #d46b08;
  border-radius: 4px;
  border: 1px solid #ffd591;
}

.info-badge {
  font-size: 10px;
  padding: 2px 5px;
  background: #e6f7ff;
  color: #0066cc;
  border-radius: 3px;
  border: 1px solid #91d5ff;
  margin-left: 4px;
  white-space: nowrap;
}

.muted-text {
  color: #bfbfbf;
  font-style: italic;
}

.role-badge {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 500;
  display: inline-block;
}

.role-badge.admin {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.role-badge.member {
  background: #f6f6f6;
  color: #8c8c8c;
  border: 1px solid #d9d9d9;
}

.data-source-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.source-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 10px;
  font-weight: 500;
  white-space: nowrap;
  
  .badge-icon {
    font-size: 12px;
    line-height: 1;
  }
  
  .badge-text {
    line-height: 1;
  }
}

.source-badge.oauth-authorized {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.source-badge.local-sync {
  background: #f0f5ff;
  color: #597ef7;
  border: 1px solid #adc6ff;
}

.edit-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.edit-input:focus {
  border-color: #667eea;
  outline: none;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-icon:hover {
  background: #f5f5f5;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon.btn-edit:hover {
  background: #e6f7ff;
}

.btn-icon.btn-save {
  color: #52c41a;
}

.btn-icon.btn-save:hover {
  background: #f6ffed;
}

.btn-icon.btn-cancel {
  color: #ff4d4f;
}

.btn-icon.btn-cancel:hover {
  background: #fff1f0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #8c8c8c;
}

.empty-state .icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 8px 0;
  font-size: 14px;
}

.empty-state .hint {
  font-size: 12px;
  color: #bfbfbf;
}
</style>
