<template>
  <div class="module-config media-showcase-config">
    <div class="config-section">
      <h4 class="section-title">基础设置</h4>
      
      <TextInput
        v-model="localData.title"
        label="模块标题"
        placeholder="多媒体展示 / 工厂环境 / 产品图册"
        :required="true"
        hint="根据内容类型自定义标题"
        @input="emitChange"
      />
      
      <TextInput
        v-model="localData.subtitle"
        type="textarea"
        label="模块描述"
        placeholder="可选的模块描述文字"
        :rows="2"
        @input="emitChange"
      />
    </div>
    
    <div class="config-section">
      <h4 class="section-title">展示模式</h4>
      
      <div class="mode-selector">
        <div
          v-for="mode in modeOptions"
          :key="mode.value"
          class="mode-option"
          :class="{ active: localData.mode === mode.value }"
          @click="selectMode(mode.value)"
        >
          <div class="mode-icon">{{ mode.icon }}</div>
          <div class="mode-info">
            <span class="mode-name">{{ mode.label }}</span>
            <span class="mode-desc">{{ mode.description }}</span>
          </div>
        </div>
      </div>
      
      <div class="mode-hint">
        <i class="icon-info"></i>
        <span>{{ getModeHint(localData.mode) }}</span>
      </div>
      
      <!-- 🔒 免费版视频限制提示 -->
      <div 
        v-if="localData.mode === 'video' && maxVideos === 0" 
        class="plan-restriction-notice"
      >
        <i class="icon-lock">🔒</i>
        <div class="notice-content">
          <strong>免费版不支持视频模式</strong>
          <p>请切换到"图文交替"或"图片网格"模式，或升级套餐以使用视频功能。</p>
        </div>
      </div>
    </div>
    
    <!-- 视频模式 -->
    <template v-if="localData.mode === 'video'">
      <div class="config-section">
        <h4 class="section-title">网格设置</h4>
        
        <div class="form-group">
          <label class="form-label">网格列数</label>
          <div class="columns-selector">
            <button
              v-for="col in [1, 2, 3]"
              :key="col"
              class="column-option"
              :class="{ active: localData.grid_columns === col }"
              @click="localData.grid_columns = col; emitChange()"
            >
              {{ col }}列
            </button>
          </div>
        </div>
      </div>
      
      <div class="config-section">
        <div class="section-header">
          <h4 class="section-title">视频列表</h4>
          <button 
            class="btn-add" 
            @click="addVideo"
            :disabled="!canAddMoreVideos"
          >
            <i class="icon-plus"></i> 添加视频
          </button>
        </div>
        
        <!-- 🎯 视频配额提示 -->
        <div v-if="videoQuotaInfo" class="quota-info" :class="quotaClass">
          <i class="icon-info">ℹ️</i>
          <span>{{ videoQuotaInfo }}</span>
        </div>
        
        <div v-if="!localData.videos || localData.videos.length === 0" class="empty-state">
          <p>暂无视频，点击"添加视频"开始配置</p>
        </div>
        
        <draggable
          v-else
          v-model="localData.videos"
          class="items-list"
          handle=".drag-handle"
          @change="emitChange"
        >
          <div
            v-for="(video, index) in localData.videos"
            :key="video.id"
            class="item-card"
          >
            <div class="item-header">
              <i class="drag-handle icon-drag"></i>
              <span class="item-index">视频 {{ index + 1 }}</span>
              <button class="btn-remove" @click="removeVideo(index)">
                <i class="icon-delete"></i>
              </button>
            </div>
            
            <div v-if="localData.videos[index]" class="item-body">
              <!-- 视频来源选择 -->
              <div class="form-group">
                <label class="form-label">视频来源</label>
                <div class="video-source-selector">
                  <button
                    class="source-option"
                    :class="{ active: localData.videos[index].type === 'external' }"
                    @click="localData.videos[index].type = 'external'; emitChange()"
                  >
                    外部链接
                  </button>
                  <button
                    class="source-option"
                    :class="{ 
                      active: localData.videos[index].type === 'local',
                      disabled: !allowLocalUpload
                    }"
                    :disabled="!allowLocalUpload"
                    @click="selectLocalUpload(index)"
                  >
                    本地上传
                    <span v-if="!allowLocalUpload" class="upgrade-hint">（付费版功能）</span>
                  </button>
                </div>
              </div>
              
              <!-- 外部链接 -->
              <TextInput
                v-if="localData.videos[index].type === 'external'"
                v-model="localData.videos[index].url"
                label="视频链接"
                placeholder="优酷/腾讯/B站链接"
                :required="true"
                hint="粘贴视频分享链接，支持优酷、腾讯、B站"
                @input="handleUrlChange(index)"
              />
              
              <!-- 本地上传 -->
              <div v-if="localData.videos[index].type === 'local'" class="upload-section">
                <label class="form-label">
                  上传视频文件
                  <span class="label-hint">（最大 {{ maxVideoSizeMB }}MB）</span>
                </label>
                <input
                  :ref="`videoUpload-${index}`"
                  type="file"
                  accept="video/mp4,video/webm,video/ogg,video/quicktime"
                  style="display: none"
                  @change="handleVideoUpload($event, index)"
                />
                <div v-if="!localData.videos[index].url" class="upload-placeholder">
                  <button class="btn-upload" @click="$refs[`videoUpload-${index}`][0].click()">
                    <i class="icon-upload">📤</i>
                    <span>选择视频文件</span>
                  </button>
                  <p class="upload-hint">支持 MP4、WebM、OGG 格式</p>
                </div>
                <div v-else class="upload-success">
                  <i class="icon-check">✓</i>
                  <span>{{ localData.videos[index].fileName || '已上传' }}</span>
                  <button class="btn-reupload" @click="$refs[`videoUpload-${index}`][0].click()">
                    重新上传
                  </button>
                </div>
                <!-- 上传进度 -->
                <div v-if="localData.videos[index].uploading" class="upload-progress">
                  <div class="progress-bar">
                    <div
                      class="progress-fill"
                      :style="{ width: (localData.videos[index].uploadProgress || 0) + '%' }"
                    ></div>
                  </div>
                  <span class="progress-text">{{ localData.videos[index].uploadProgress || 0 }}%</span>
                </div>
              </div>
              
              <TextInput
                v-model="localData.videos[index].title"
                label="视频标题"
                placeholder="视频标题"
                :required="true"
                @input="emitChange"
              />
              
              <TextInput
                v-model="localData.videos[index].description"
                type="textarea"
                label="视频描述"
                placeholder="简短描述视频内容..."
                :rows="2"
                @input="emitChange"
              />
              
              <ImageUpload
                v-model="localData.videos[index].thumbnail"
                label="封面图"
                hint="推荐比例 16:9"
                @change="emitChange"
              />
            </div>
          </div>
        </draggable>
      </div>
    </template>
    
    <!-- 图文交替模式（新版：内容块列表） -->
    <template v-if="localData.mode === 'text-image-alt'">
      <div class="config-section">
        <div class="section-header">
          <h4 class="section-title">内容块列表</h4>
          <div class="btn-group">
            <button class="btn-add-block" @click="addTextBlock">
              <i class="icon-plus"></i> 添加文字
            </button>
            <button class="btn-add-block" @click="addImageBlock" :disabled="!canAddMoreImages">
              <i class="icon-plus"></i> 添加图片
            </button>
          </div>
        </div>
        
        <!-- 配额提示 -->
        <div class="quota-info" :class="{ warning: getImageCount() >= MAX_IMAGES * 0.8 }">
          <span>已添加 {{ getImageCount() }} 张图片 / {{ MAX_IMAGES }} 张</span>
          <span v-if="getImageCount() >= MAX_IMAGES" class="quota-full">图片已达上限</span>
        </div>
        
        <div class="info-hint">
          <i class="icon-info"></i>
          <span>文字和图片将按顺序交替显示。可拖拽 ☰ 图标调整顺序</span>
        </div>
        
        <div v-if="!localData.content.blocks || localData.content.blocks.length === 0" class="empty-state">
          <p>暂无内容，点击"添加文字"或"添加图片"开始配置</p>
        </div>
        
        <draggable
          v-else
          v-model="localData.content.blocks"
          class="blocks-list"
          handle=".drag-handle"
          @change="emitChange"
        >
          <div
            v-for="(block, index) in localData.content.blocks"
            :key="block.id"
            :class="['block-card', `block-type-${block.type}`]"
          >
            <i class="drag-handle icon-drag">☰</i>
            <div class="block-type-badge">{{ block.type === 'text' ? '📝 文字' : '🖼 图片' }}</div>
            
            <!-- 文字块 -->
            <div v-if="block.type === 'text'" class="text-block-content">
              <TextInput
                v-model="localData.content.blocks[index].text"
                type="textarea"
                label=""
                placeholder="输入文字内容..."
                :rows="4"
                :required="true"
                @input="emitChange"
              />
            </div>
            
            <!-- 图片块 -->
            <div v-if="block.type === 'image'" class="image-block-content">
              <div class="image-preview">
                <img v-if="localData.content.blocks[index].src" :src="localData.content.blocks[index].src" alt="preview" />
                <div v-else class="placeholder">图片 {{ getImageIndex(index) + 1 }}</div>
              </div>
              <div class="image-upload-area">
                <ImageUpload
                  v-model="localData.content.blocks[index].src"
                  label=""
                  :required="true"
                  hint="推荐横图，比例 16:9 或 4:3"
                  @change="emitChange"
                />
                <TextInput
                  v-model="localData.content.blocks[index].caption"
                  label="图片说明（可选）"
                  placeholder="添加图片说明文字"
                  @input="emitChange"
                />
              </div>
            </div>
            
            <button class="btn-remove-simple" @click="removeBlock(index)">
              <i class="icon-delete">✕</i>
            </button>
          </div>
        </draggable>
      </div>
    </template>
    
    <!-- 图片网格模式 -->
    <template v-if="localData.mode === 'image-grid'">
      <div class="config-section">
        <h4 class="section-title">顶部文字内容（可选）</h4>
        
        <TextInput
          v-model="localData.content.topText"
          type="textarea"
          label="介绍文字"
          placeholder="输入工厂介绍、产品说明等文字内容..."
          :rows="6"
          hint="支持换行，将在图片网格上方显示"
          @input="emitChange"
        />
      </div>
      
      <div class="config-section">
        <h4 class="section-title">网格设置</h4>
        
        <div class="form-group">
          <label class="form-label">网格列数</label>
          <div class="columns-selector">
            <button
              v-for="col in [2, 3]"
              :key="col"
              class="column-option"
              :class="{ active: localData.grid_columns === col }"
              @click="localData.grid_columns = col; emitChange()"
            >
              {{ col }}列
            </button>
          </div>
        </div>
      </div>
      
      <div class="config-section">
        <div class="section-header">
          <h4 class="section-title">图片列表</h4>
          <button class="btn-add" @click="addImage" :disabled="!canAddMoreImages">
            <i class="icon-plus"></i> 添加图片
          </button>
        </div>
        
        <!-- 配额提示 -->
        <div class="quota-info" :class="{ warning: getImageCount() >= MAX_IMAGES * 0.8 }">
          <span>已添加 {{ getImageCount() }} / {{ MAX_IMAGES }} 张图片</span>
          <span v-if="getImageCount() >= MAX_IMAGES" class="quota-full">已达上限</span>
        </div>
        
        <div class="info-hint">
          <i class="icon-info"></i>
          <span>图片将以网格形式排列，适合展示产品细节、多角度照片。可拖拽 ☰ 图标调整顺序</span>
        </div>
        
        <div v-if="!localData.content.images || localData.content.images.length === 0" class="empty-state">
          <p>暂无图片，点击"添加图片"开始配置</p>
        </div>
        
        <draggable
          v-else
          v-model="localData.content.images"
          class="images-list"
          handle=".drag-handle"
          @change="emitChange"
        >
          <div
            v-for="(image, index) in localData.content.images"
            :key="image.id"
            class="image-card"
          >
            <i class="drag-handle icon-drag">☰</i>
            <div v-if="localData.content.images[index]" class="image-preview">
              <img v-if="localData.content.images[index].src" :src="localData.content.images[index].src" alt="preview" />
              <div v-else class="placeholder">图片 {{ index + 1 }}</div>
            </div>
            <div v-if="localData.content.images[index]" class="image-upload-area">
              <ImageUpload
                v-model="localData.content.images[index].src"
                label=""
                :required="true"
                hint="推荐方图或横图，比例 1:1 或 4:3"
                @change="emitChange"
              />
              <TextInput
                v-model="localData.content.images[index].caption"
                label="图片说明（可选）"
                placeholder="添加图片说明文字"
                @input="emitChange"
              />
            </div>
            <button class="btn-remove-simple" @click="removeImage(index)">
              <i class="icon-delete">✕</i>
            </button>
          </div>
        </draggable>
      </div>
    </template>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import TextInput from '../form/TextInput.vue'
import ImageUpload from '../form/ImageUpload.vue'
import debounceMixin from './debounce-mixin'
import uploadSecurityMixin from './upload-security-mixin'

export default {
  name: 'VideoShowcaseConfig',
  
  mixins: [debounceMixin, uploadSecurityMixin],
  
  components: {
    draggable,
    TextInput,
    ImageUpload
  },
  
  props: {
    data: {
      type: Object,
      required: true
    }
  },
  
  data() {
    const localData = this._smartClone ? this._smartClone(this.data) : { ...this.data }
    
    // 确保所有必需字段存在
    if (!localData.mode) localData.mode = 'video'
    if (!localData.grid_columns) localData.grid_columns = 2
    if (!localData.videos) localData.videos = []
    if (!localData.content) {
      localData.content = { text: '', images: [] }
    }
    if (!localData.content.images) {
      localData.content.images = []
    }
    
    // 确保每个视频都有完整字段
    if (localData.videos && localData.videos.length > 0) {
      localData.videos = localData.videos.map(v => ({
        id: v.id || `video-${Date.now()}`,
        url: v.url || '',
        title: v.title || '',
        description: v.description || '',
        thumbnail: v.thumbnail || ''
      }))
    }
    
    // 确保每个图片都有完整字段
    if (localData.content.images && localData.content.images.length > 0) {
      localData.content.images = localData.content.images.map(img => ({
        id: img.id || `img-${Date.now()}`,
        src: img.src || '',
        caption: img.caption || ''
      }))
    }
    
    return {
      localData,
      
      modeOptions: [
        {
          value: 'video',
          label: '视频展示',
          icon: '🎬',
          description: '网格展示视频，支持外部链接'
        },
        {
          value: 'text-image-alt',
          label: '图文交替',
          icon: '📄',
          description: '文字+图片纵向排列，适合工厂介绍'
        },
        {
          value: 'image-grid',
          label: '图片网格',
          icon: '🖼️',
          description: '文字+图片网格，适合产品展示'
        }
      ],
      
      // 视频上传配置（从框架定义或租户配置获取）
      allowLocalUpload: true,  // 默认允许，实际应从套餐配置读取
      maxVideoSizeMB: this.getVideoSizeLimit()  // 根据套餐动态获取
    }
  },
  
  computed: {
    // 支持的视频平台域名白名单
    supportedDomains() {
      return [
        'youku.com',
        'v.youku.com',
        'qq.com',
        'v.qq.com',
        'bilibili.com',
        'b23.tv'
      ]
    },
    
    // 🎯 获取当前套餐的视频数量限制
    maxVideos() {
      const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
      const limits = {
        free: 0,       // 不支持视频
        trial: 1,      // 1个视频
        pro: 1,        // 1个视频
        enterprise: 2  // 2个视频
      }
      return limits[plan] || 0
    },
    
    // 🎯 当前视频数量
    currentVideoCount() {
      return this.localData.videos ? this.localData.videos.length : 0
    },
    
    // 🎯 是否可以添加更多视频
    canAddMoreVideos() {
      if (this.maxVideos === 0) return false  // free套餐不支持
      return this.currentVideoCount < this.maxVideos
    },
    
    // 🎯 视频配额信息
    videoQuotaInfo() {
      const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
      
      if (plan === 'free') {
        return '免费版不支持视频模式，请使用图文模式或升级套餐'
      }
      
      if (this.currentVideoCount >= this.maxVideos) {
        return `已达到视频数量上限（${this.maxVideos}个），升级套餐可添加更多`
      }
      
      return `当前：${this.currentVideoCount} / ${this.maxVideos} 个视频`
    },
    
    // 🎯 配额提示样式
    quotaClass() {
      const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
      if (plan === 'free') return 'quota-error'
      if (this.currentVideoCount >= this.maxVideos) return 'quota-warning'
      return 'quota-normal'
    }
  },
  
  methods: {
    // upload-security-mixin 需要的方法
    getImageCount() {
      if (this.localData.mode === 'video') {
        // 视频模式：统计缩略图数量
        return this.localData.videos ? this.localData.videos.filter(v => v.thumbnail).length : 0
      } else if (this.localData.mode === 'text-image-alt') {
        // 图文交替模式：统计 blocks 中的图片块数量
        return this.localData.content && this.localData.content.blocks
          ? this.localData.content.blocks.filter(b => b.type === 'image').length
          : 0
      } else {
        // 图片网格模式：统计图片列表
        return this.localData.content && this.localData.content.images 
          ? this.localData.content.images.length 
          : 0
      }
    },
    
    selectMode(mode) {
      if (this.localData.mode === mode) return
      
      // 切换模式时确认
      if ((this.localData.videos && this.localData.videos.length > 0) || 
          (this.localData.content.images && this.localData.content.images.length > 0)) {
        if (!confirm('切换模式将清空当前内容，是否继续？')) {
          return
        }
      }
      
      this.localData.mode = mode
      
      // 重置内容
      if (mode === 'video') {
        this.localData.videos = []
        this.localData.content = { text: '', images: [] }
      } else {
        this.localData.videos = []
        this.localData.content = { text: '', images: [] }
      }
      
      this.$nextTick(() => {
        this.emitChange()
      })
    },
    
    getModeHint(mode) {
      const hints = {
        'video': '支持优酷、腾讯、B站等外部视频链接，适合产品演示、公司宣传',
        'text-image-alt': '文字段落+图片交替显示，图片全宽排列，适合工厂环境、生产线展示',
        'image-grid': '文字段落+图片网格展示，适合产品细节、多角度照片展示'
      }
      return hints[mode] || ''
    },
    
    getVideoSizeLimit() {
      // 根据租户套餐返回视频大小限制（MB）
      const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
      const limits = {
        free: 10,
        trial: 20,
        pro: 30,
        enterprise: 50
      }
      return limits[plan] || 10
    },
    
    selectLocalUpload(index) {
      if (!this.allowLocalUpload) {
        alert('本地视频上传功能仅限付费版租户使用，请联系客服升级套餐')
        return
      }
      this.$set(this.localData.videos[index], 'type', 'local')
      this.emitChange()
    },
    
    handleUrlChange(index) {
      const url = this.localData.videos[index].url
      if (!url) {
        this.emitChange()
        return
      }
      
      // 检查是否是支持的域名
      const isSupported = this.supportedDomains.some(domain => url.includes(domain))
      
      if (!isSupported) {
        // 不支持的域名，给出警告
        this.$nextTick(() => {
          alert('⚠️ 提示：该视频链接可能无法正常播放。\n\n支持的平台：优酷、腾讯视频、B站\n\n如果视频来自其他平台或私有CDN，可能会因为跨域限制（X-Frame-Options）导致无法显示。')
        })
      }
      
      this.emitChange()
    },
    
    async handleVideoUpload(event, index) {
      const file = event.target.files[0]
      if (!file) return
      
      // 检查文件类型
      const validTypes = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime']
      if (!validTypes.includes(file.type)) {
        alert('不支持的视频格式，请上传 MP4、WebM 或 OGG 格式的视频')
        return
      }
      
      // 检查文件大小
      const maxSize = this.maxVideoSizeMB * 1024 * 1024
      if (file.size > maxSize) {
        alert(`视频文件过大，最大支持 ${this.maxVideoSizeMB}MB`)
        return
      }
      
      // 设置上传状态
      this.$set(this.localData.videos[index], 'uploading', true)
      this.$set(this.localData.videos[index], 'uploadProgress', 0)
      this.$set(this.localData.videos[index], 'fileName', file.name)
      
      try {
        // 创建FormData上传
        const formData = new FormData()
        formData.append('file', file)  // ✅ 改为 'file' 字段名
        formData.append('file_type', 'video')  // ✅ 改为 'file_type'
        
        // 获取JWT token
        const token = localStorage.getItem('workspace_token')
        if (!token) {
          throw new Error('未登录，请重新登录')
        }
        
        // 上传到正确的路由
        const uploadPromise = this.$axios.post('/api/v1/files/upload', formData, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            this.$set(this.localData.videos[index], 'uploadProgress', progress)
          }
        })
        
        const response = await uploadPromise
        
        if (response.data && response.data.success && response.data.url) {
          this.$set(this.localData.videos[index], 'url', response.data.url)
          this.$set(this.localData.videos[index], 'uploading', false)
          this.emitChange()
          console.log('✅ 视频上传成功:', response.data.file_name)
        } else {
          throw new Error(response.data?.error || '上传失败')
        }
      } catch (error) {
        console.error('视频上传失败:', error)
        const errorMsg = error.response?.data?.error || error.message || '视频上传失败，请重试'
        const limitMB = error.response?.data?.limit_mb
        if (limitMB) {
          alert(`${errorMsg}\n您的套餐限制：${limitMB}MB`)
        } else {
          alert(errorMsg)
        }
        this.$set(this.localData.videos[index], 'uploading', false)
        this.$set(this.localData.videos[index], 'url', '')
      }
      
      // 清空input
      event.target.value = ''
    },
    
    addVideo() {
      // 🎯 检查视频数量限制
      if (!this.canAddMoreVideos) {
        const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
        if (plan === 'free') {
          alert('❌ 免费版不支持视频模式\n\n请使用图文交替或图片网格模式，或联系客服升级套餐。')
        } else {
          alert(`❌ 已达到视频数量上限\n\n您的套餐限制：${this.maxVideos}个视频\n升级到企业版可添加2个视频。`)
        }
        return
      }
      
      if (!this.localData.videos) {
        this.$set(this.localData, 'videos', [])
      }
      
      const newVideo = {
        id: `video-${Date.now()}`,
        type: 'external',  // 默认外部链接
        url: '',
        title: '',
        description: '',
        thumbnail: '',
        fileName: '',
        uploading: false,
        uploadProgress: 0
      }
      
      this.localData.videos.unshift(newVideo)
      
      this.$nextTick(() => {
        if (this.localData.videos[0]) {
          this.$set(this.localData.videos[0], 'id', newVideo.id)
          this.$set(this.localData.videos[0], 'type', newVideo.type)
          this.$set(this.localData.videos[0], 'url', newVideo.url)
          this.$set(this.localData.videos[0], 'title', newVideo.title)
          this.$set(this.localData.videos[0], 'description', newVideo.description)
          this.$set(this.localData.videos[0], 'thumbnail', newVideo.thumbnail)
        }
        this.emitChange()
      })
    },
    
    removeVideo(index) {
      if (!this.localData.videos || index < 0 || index >= this.localData.videos.length) {
        return
      }
      
      if (confirm('确定要删除这个视频吗？')) {
        this.localData.videos.splice(index, 1)
        this.$nextTick(() => {
          this.emitChange()
        })
      }
    },
    
    addImage() {
      // 检查是否可以添加更多图片（使用 upload-security-mixin）
      if (!this.canAddMoreImages) {
        this.$message?.warning(`最多只能添加 ${this.MAX_IMAGES} 张图片`)
        alert(`最多只能添加 ${this.MAX_IMAGES} 张图片`)
        return
      }
      
      if (!this.localData.content) {
        this.$set(this.localData, 'content', { text: '', images: [] })
      }
      if (!this.localData.content.images) {
        this.$set(this.localData.content, 'images', [])
      }
      
      const newImage = {
        id: `img-${Date.now()}`,
        src: '',
        caption: ''
      }
      
      // ✅ 使用 unshift 将新图片添加到列表顶部
      this.localData.content.images.unshift(newImage)
      
      this.$nextTick(() => {
        // ✅ 新图片在索引 0 的位置
        if (this.localData.content.images[0]) {
          this.$set(this.localData.content.images[0], 'id', newImage.id)
          this.$set(this.localData.content.images[0], 'src', newImage.src)
          this.$set(this.localData.content.images[0], 'caption', newImage.caption)
        }
        this.emitChange()
      })
    },
    
    removeImage(index) {
      if (!this.localData.content.images || index < 0 || index >= this.localData.content.images.length) {
        return
      }
      
      if (confirm('确定要删除这张图片吗？')) {
        this.localData.content.images.splice(index, 1)
        this.$nextTick(() => {
          this.emitChange()
        })
      }
    },
    
    // ===== 图文交替模式（blocks）相关方法 =====
    
    addTextBlock() {
      if (!this.localData.content) {
        this.$set(this.localData, 'content', { blocks: [] })
      }
      if (!this.localData.content.blocks) {
        this.$set(this.localData.content, 'blocks', [])
      }
      
      const newBlock = {
        id: `text-${Date.now()}`,
        type: 'text',
        text: ''
      }
      
      // 添加到顶部
      this.localData.content.blocks.unshift(newBlock)
      
      this.$nextTick(() => {
        if (this.localData.content.blocks[0]) {
          this.$set(this.localData.content.blocks[0], 'id', newBlock.id)
          this.$set(this.localData.content.blocks[0], 'type', newBlock.type)
          this.$set(this.localData.content.blocks[0], 'text', newBlock.text)
        }
        this.emitChange()
      })
    },
    
    addImageBlock() {
      // 检查是否可以添加更多图片
      if (!this.canAddMoreImages) {
        this.$message?.warning(`最多只能添加 ${this.MAX_IMAGES} 张图片`)
        alert(`最多只能添加 ${this.MAX_IMAGES} 张图片`)
        return
      }
      
      if (!this.localData.content) {
        this.$set(this.localData, 'content', { blocks: [] })
      }
      if (!this.localData.content.blocks) {
        this.$set(this.localData.content, 'blocks', [])
      }
      
      const newBlock = {
        id: `img-${Date.now()}`,
        type: 'image',
        src: '',
        caption: ''
      }
      
      // 添加到顶部
      this.localData.content.blocks.unshift(newBlock)
      
      this.$nextTick(() => {
        if (this.localData.content.blocks[0]) {
          this.$set(this.localData.content.blocks[0], 'id', newBlock.id)
          this.$set(this.localData.content.blocks[0], 'type', newBlock.type)
          this.$set(this.localData.content.blocks[0], 'src', newBlock.src)
          this.$set(this.localData.content.blocks[0], 'caption', newBlock.caption)
        }
        this.emitChange()
      })
    },
    
    removeBlock(index) {
      if (!this.localData.content.blocks || index < 0 || index >= this.localData.content.blocks.length) {
        return
      }
      
      const blockType = this.localData.content.blocks[index].type
      const message = blockType === 'text' ? '确定要删除这段文字吗？' : '确定要删除这张图片吗？'
      
      if (confirm(message)) {
        this.localData.content.blocks.splice(index, 1)
        this.$nextTick(() => {
          this.emitChange()
        })
      }
    },
    
    getImageIndex(blockIndex) {
      // 计算某个图片块在所有图片中的序号
      if (!this.localData.content.blocks) return 0
      
      let imageCount = 0
      for (let i = 0; i < blockIndex; i++) {
        if (this.localData.content.blocks[i].type === 'image') {
          imageCount++
        }
      }
      return imageCount
    }
  }
}
</script>

<style scoped>
/* 参考 StandardGridConfig 的样式规范 */
.module-config {
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
}

.config-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #e0e0e0;
}

.config-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 16px 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

/* 模式选择器 */
.mode-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.mode-option {
  padding: 16px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
}

.mode-option:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.mode-option.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.mode-icon {
  font-size: 32px;
  line-height: 1;
}

.mode-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mode-name {
  font-weight: 600;
  font-size: 15px;
  color: #1a1a2e;
}

.mode-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.mode-hint {
  padding: 12px 16px;
  background: rgba(0, 123, 255, 0.1);
  border-left: 3px solid #007bff;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.info-hint {
  padding: 12px 16px;
  background: rgba(102, 126, 234, 0.1);
  border-left: 3px solid #667eea;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

/* 列数选择器 */
.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.columns-selector {
  display: flex;
  gap: 8px;
}

.column-option {
  flex: 1;
  padding: 10px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.column-option:hover {
  border-color: #00ffaa;
}

.column-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.1);
  color: #00aa7a;
}

/* 按钮 */
.btn-add {
  padding: 8px 16px;
  background: #00ffaa;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-add:hover {
  background: #00e69a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 170, 0.3);
}

.btn-add:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 配额提示 */
.quota-info {
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.quota-info.quota-normal {
  background: rgba(0, 123, 255, 0.1);
  border-left: 3px solid #007bff;
  color: #1a1a2e;
}

.quota-info.quota-warning {
  background: rgba(255, 193, 7, 0.15);
  border-left: 3px solid #ffc107;
  color: #856404;
}

.quota-info.quota-error {
  background: rgba(220, 53, 69, 0.1);
  border-left: 3px solid #dc3545;
  color: #721c24;
}

.quota-full {
  padding: 2px 8px;
  background: #ff4757;
  color: #fff;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

/* 套餐限制提示 */
.plan-restriction-notice {
  margin-top: 12px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(255, 59, 48, 0.1) 0%, rgba(255, 149, 0, 0.1) 100%);
  border-left: 4px solid #ff3b30;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.plan-restriction-notice .icon-lock {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.plan-restriction-notice .notice-content {
  flex: 1;
}

.plan-restriction-notice strong {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #721c24;
  margin-bottom: 4px;
}

.plan-restriction-notice p {
  font-size: 13px;
  color: #856404;
  margin: 0;
  line-height: 1.5;
}

/* 空状态 */
.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #666;
  background: #fff;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
}

/* 项目列表 */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.item-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.drag-handle {
  cursor: move;
  color: #999;
  font-size: 18px;
}

.item-index {
  flex: 1;
  font-weight: 600;
  font-size: 14px;
  color: #1a1a2e;
}

.btn-remove {
  padding: 6px 10px;
  background: none;
  border: none;
  color: #ff4757;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-remove:hover {
  background: rgba(255, 71, 87, 0.1);
}

.item-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 图片列表 */
.images-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.image-card:hover {
  border-color: #00ffaa;
  box-shadow: 0 2px 8px rgba(0, 255, 170, 0.1);
}

.image-preview {
  width: 80px;
  height: 80px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.image-preview .placeholder {
  font-size: 11px;
  color: #999;
  text-align: center;
}

.image-upload-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-remove-simple {
  padding: 6px 10px;
  background: none;
  border: none;
  color: #ff4757;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 18px;
  flex-shrink: 0;
}

.btn-remove-simple:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 视频来源选择器 */
.video-source-selector {
  display: flex;
  gap: 8px;
}

.source-option {
  flex: 1;
  padding: 10px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  position: relative;
}

.source-option:hover:not(:disabled) {
  border-color: #667eea;
}

.source-option.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.source-option.disabled,
.source-option:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.upgrade-hint {
  display: block;
  font-size: 11px;
  color: #ff9800;
  margin-top: 2px;
}

/* 上传区域 */
.upload-section {
  margin-top: 16px;
}

.upload-placeholder {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-upload:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.upload-hint {
  font-size: 12px;
  color: #999;
  margin: 8px 0 0 0;
}

.upload-success {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid #4caf50;
  border-radius: 8px;
}

.upload-success .icon-check {
  color: #4caf50;
  font-size: 18px;
  font-weight: bold;
}

.btn-reupload {
  margin-left: auto;
  padding: 4px 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reupload:hover {
  border-color: #667eea;
  color: #667eea;
}

.upload-progress {
  margin-top: 12px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

/* ========== 图文交替模式（blocks）样式 ========== */

.btn-group {
  display: flex;
  gap: 8px;
}

.btn-add-block {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-add-block:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-1px);
}

.btn-add-block:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.blocks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.block-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.block-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.block-type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.block-type-text .block-type-badge {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.block-type-image .block-type-badge {
  background: rgba(33, 150, 243, 0.1);
  color: #2196f3;
}

.text-block-content {
  margin-top: 12px;
}

.image-block-content {
  margin-top: 12px;
  display: flex;
  gap: 16px;
}

.image-block-content .image-preview {
  flex-shrink: 0;
  width: 120px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-block-content .image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-block-content .image-preview .placeholder {
  color: #999;
  font-size: 12px;
}

.image-block-content .image-upload-area {
  flex: 1;
}

/* 响应式 */
@media (max-width: 768px) {
  .mode-selector {
    grid-template-columns: 1fr;
  }
  
  .image-card {
    flex-direction: column;
    align-items: stretch;
  }
  
  .image-preview {
    width: 100%;
    height: 120px;
  }
  
  .btn-group {
    flex-direction: column;
  }
  
  .image-block-content {
    flex-direction: column;
  }
  
  .image-block-content .image-preview {
    width: 100%;
    height: 150px;
  }
}
</style>
