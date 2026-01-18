<template>
  <div class="module-config logo-wall-config">
    <div class="config-section">
      <h4 class="section-title">基础设置</h4>
      
      <TextInput
        v-model="localData.title"
        label="模块标题"
        placeholder="合作客户 / 合作伙伴"
        :required="true"
        hint="显示在Logo墙顶部的标题"
        @input="emitChange"
      />
      
      <div class="info-note">
        <i class="icon-info"></i>
        <span>Logo墙适合展示10个以上的合作伙伴Logo，通过横向滚动动画展示</span>
      </div>
    </div>
    
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">Logo列表</h4>
        <div class="header-actions">
          <button class="btn-batch-upload" @click="triggerBatchUpload">
            <i class="icon-upload"></i> 批量上传
          </button>
          <button class="btn-add" @click="addLogo">
            <i class="icon-plus"></i> 单个添加
          </button>
        </div>
      </div>
      
      <!-- 批量上传隐藏input -->
      <input
        ref="batchUploadInput"
        type="file"
        accept="image/*"
        multiple
        style="display: none"
        @change="handleBatchUpload"
      />
      
      <div class="info-hints">
        <div v-if="localData.logos.length < 10" class="warning-hint">
          <i class="icon-warning"></i>
          <span>建议至少添加10个Logo以获得更好的滚动效果</span>
        </div>
        
        <div class="quota-hint" :class="{ 'quota-warning': remainingSlots <= 5, 'quota-full': remainingSlots === 0 }">
          <i class="icon-info"></i>
          <span>已添加 {{ localData.logos.length }}/{{ MAX_LOGOS }} 个Logo</span>
          <span v-if="remainingSlots > 0" class="remaining">（还可添加{{ remainingSlots }}个）</span>
          <span v-else class="full-text">（已达上限）</span>
        </div>
      </div>
      
      <draggable
        v-model="localData.logos"
        class="logos-list"
        handle=".drag-handle"
        @change="emitChange"
      >
        <div
          v-for="(logo, index) in localData.logos"
          :key="logo.id"
          class="logo-card-simple"
        >
          <i class="drag-handle icon-drag">☰</i>
          <div v-if="localData.logos[index]" class="logo-preview">
            <img v-if="localData.logos[index].src" :src="localData.logos[index].src" alt="logo" />
            <div v-else class="logo-placeholder">Logo {{ index + 1 }}</div>
          </div>
          <div v-if="localData.logos[index]" class="logo-upload-area">
            <ImageUpload
              v-model="localData.logos[index].src"
              label=""
              :required="true"
              hint="建议尺寸：400x200px，支持透明背景PNG"
              @change="emitChange"
            />
          </div>
          <button class="btn-remove-simple" @click="removeLogo(index)">
            <i class="icon-delete">✕</i>
          </button>
        </div>
      </draggable>
      
      <div v-if="localData.logos.length === 0" class="empty-state">
        <p>暂无Logo，点击"批量上传"或"单个添加"开始配置</p>
        <p class="tip">💡 建议添加10个以上Logo以获得连续滚动效果</p>
      </div>
    </div>
    
    <div class="config-section">
      <h4 class="section-title">动画设置</h4>
      
      <div class="form-group">
        <label class="form-label">滚动速度</label>
        <div class="speed-control">
          <input
            v-model.number="localData.scrollSpeed"
            type="range"
            min="1.5"
            max="5"
            step="0.5"
            class="speed-slider"
            @input="emitChange"
          />
          <div class="speed-value">
            <span class="value">{{ getSpeedLabel(localData.scrollSpeed) }}</span>
            <span class="desc">{{ localData.scrollSpeed }}秒/个Logo</span>
          </div>
        </div>
        <p class="hint-text">
          调整Logo滚动速度，数值越小滚动越快
          <span v-if="localData.logos && localData.logos.length > 0" class="auto-calc">
            （当前{{ localData.logos.length }}个Logo，预计滚动一圈约 {{ calculatedDuration }}秒）
          </span>
        </p>
      </div>
      
      <div class="form-group">
        <label class="form-label">
          <input
            v-model="localData.pauseOnHover"
            type="checkbox"
            @change="emitChange"
          />
          鼠标悬停时暂停滚动
        </label>
        <p class="hint-text">启用后，用户将鼠标移到Logo上时滚动会暂停</p>
      </div>
      
      <div class="form-group">
        <label class="form-label">Logo间距</label>
        <div class="gap-selector">
          <button
            v-for="gap in gapOptions"
            :key="gap.value"
            class="gap-option"
            :class="{ active: localData.gap === gap.value }"
            @click="selectGap(gap.value)"
          >
            {{ gap.label }}
          </button>
        </div>
      </div>
    </div>
    
    <div class="config-section">
      <h4 class="section-title">视觉效果</h4>
      
      <div class="form-group">
        <label class="form-label">默认样式</label>
        <div class="style-options">
          <label class="radio-option">
            <input
              v-model="localData.defaultStyle"
              type="radio"
              value="grayscale"
              @change="emitChange"
            />
            <span>灰度（悬停彩色）</span>
          </label>
          <label class="radio-option">
            <input
              v-model="localData.defaultStyle"
              type="radio"
              value="color"
              @change="emitChange"
            />
            <span>彩色</span>
          </label>
          <label class="radio-option">
            <input
              v-model="localData.defaultStyle"
              type="radio"
              value="dim"
              @change="emitChange"
            />
            <span>半透明（悬停不透明）</span>
          </label>
        </div>
      </div>
      
      <div class="preview-box">
        <div class="preview-title">效果预览</div>
        <div class="preview-content">
          <div class="mini-logo-track" :style="previewStyle">
            <div
              v-for="(logo, index) in previewLogos"
              :key="logo.id || `preview-logo-${index}`"
              class="mini-logo"
              :class="`style-${localData.defaultStyle || 'grayscale'}`"
            >
              <img v-if="logo && logo.src" :src="logo.src" :alt="logo.name || 'Logo'" />
              <div v-else class="logo-placeholder">{{ (logo && logo.name) || 'Logo' }}</div>
            </div>
          </div>
          <p v-if="localData.logos && localData.logos.length > 0" class="preview-hint">
            {{ localData.logos.length }}个Logo，{{ calculatedDuration }}秒滚动一圈
          </p>
          <p v-else class="preview-hint">暂无Logo，请先添加</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import TextInput from '../form/TextInput.vue'
import ImageUpload from '../form/ImageUpload.vue'
import debounceMixin from './debounce-mixin'

export default {
  name: 'LogoWallConfig',
  
  mixins: [debounceMixin],
  
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
    // 确保localData有所有必需的字段和默认值
    const baseData = this._smartClone ? this._smartClone(this.data) : { ...this.data }
    const localData = {
      title: '合作客户',
      logos: [],
      scrollSpeed: 2.5, // 新配置：滚动速度系数（2.5秒/个Logo）
      pauseOnHover: true,
      gap: 28,
      defaultStyle: 'grayscale',
      ...baseData // 覆盖默认值
    }
    
    // 安全限制配置（动态获取套餐限制）
    const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
    const logoLimits = {
      free: 8,
      trial: 20,
      paid: 20,
      pro: 20,
      enterprise: 30
    }
    const MAX_LOGOS = logoLimits[plan] || 8  // 根据套餐动态设置
    const MAX_BATCH_UPLOAD = 10  // 单次批量上传最大数量
    const UPLOAD_COOLDOWN = 2000  // 上传冷却时间（毫秒）
    const MAX_FILE_SIZE = 500 * 1024  // 单个文件最大500KB
    
    // 数据迁移：兼容旧字段
    if (baseData.perLogoDisplay && !baseData.scrollSpeed) {
      // 旧的 perLogoDisplay 直接映射为 scrollSpeed
      localData.scrollSpeed = baseData.perLogoDisplay
    } else if (baseData.duration && !baseData.scrollSpeed) {
      // 最旧的 duration 转换为 scrollSpeed
      const logoCount = (baseData.logos || []).length || 10
      localData.scrollSpeed = Math.max(1.5, Math.min(5, baseData.duration / logoCount))
    }
    
    // 确保logos是数组
    if (!Array.isArray(localData.logos)) {
      localData.logos = []
    }
    
    return {
      localData,
      
      // 安全限制常量
      MAX_LOGOS,
      MAX_BATCH_UPLOAD,
      UPLOAD_COOLDOWN,
      MAX_FILE_SIZE,
      
      // 上传控制状态
      lastUploadTime: 0,
      isUploading: false,
      uploadCount: 0,
      
      gapOptions: [
        { value: 20, label: '紧凑' },
        { value: 28, label: '适中' },
        { value: 36, label: '宽松' }
      ]
    }
  },
  
  computed: {
    previewStyle() {
      return {
        gap: `${this.localData.gap || 28}px`
      }
    },
    
    // 安全获取预览Logo列表（前5个）
    previewLogos() {
      if (!this.localData.logos || !Array.isArray(this.localData.logos)) {
        return []
      }
      return this.localData.logos.slice(0, 5).filter(logo => logo && typeof logo === 'object')
    },
    
    // 计算总滚动时长
    calculatedDuration() {
      const logoCount = (this.localData.logos || []).length
      if (logoCount === 0) return 0
      
      const totalDuration = logoCount * (this.localData.scrollSpeed || 2.5)
      const safeDuration = Math.max(20, totalDuration)
      return Math.round(safeDuration)
    },
    
    // 安全检查：是否可以添加更多Logo
    canAddMoreLogos() {
      return (this.localData.logos || []).length < this.MAX_LOGOS
    },
    
    // 安全检查：还能添加多少个Logo
    remainingSlots() {
      return this.MAX_LOGOS - (this.localData.logos || []).length
    }
  },
  
  // watch 已由 debounce-mixin 提供
  
  watch: {
    // 监听 defaultStyle 变化，确保安全更新
    'localData.defaultStyle'(newVal, oldVal) {
      if (newVal !== oldVal && newVal) {
        // 防御性检查：确保 defaultStyle 是有效值
        const validStyles = ['grayscale', 'color', 'dim']
        if (!validStyles.includes(newVal)) {
          console.warn(`Invalid defaultStyle: ${newVal}, resetting to 'grayscale'`)
          this.$set(this.localData, 'defaultStyle', 'grayscale')
          return
        }
        
        // 使用 $nextTick 确保 DOM 更新完成后再触发
        this.$nextTick(() => {
          this.emitChange()
        })
      }
    }
  },
  
  methods: {
    // emitChange 方法现在由 debounce-mixin 提供
    
    addLogo() {
      // 安全检查：数量限制
      if (!this.canAddMoreLogos) {
        alert(`最多只能添加${this.MAX_LOGOS}个Logo`)
        return
      }
      
      // 安全检查：上传频率限制
      const now = Date.now()
      if (now - this.lastUploadTime < this.UPLOAD_COOLDOWN) {
        const remaining = Math.ceil((this.UPLOAD_COOLDOWN - (now - this.lastUploadTime)) / 1000)
        alert(`操作过于频繁，请${remaining}秒后再试`)
        return
      }
      
      // 确保 logos 数组存在
      if (!this.localData.logos) {
        this.$set(this.localData, 'logos', [])
      }
      
      // 创建新Logo对象
      const newLogo = {
        id: `logo-${Date.now()}`,
        src: '',
        name: `Logo ${this.localData.logos.length + 1}`
      }
      
      this.localData.logos.push(newLogo)
      
      // 在下一个tick中确保响应式并触发更新
      this.$nextTick(() => {
        const index = this.localData.logos.length - 1
        if (this.localData.logos[index]) {
          // 强制设置每个属性为响应式
          this.$set(this.localData.logos[index], 'id', newLogo.id)
          this.$set(this.localData.logos[index], 'src', newLogo.src)
          this.$set(this.localData.logos[index], 'name', newLogo.name)
        }
        
        this.lastUploadTime = now
        this.emitChangeImmediate()
      })
    },
    
    triggerBatchUpload() {
      this.$refs.batchUploadInput.click()
    },
    
    /**
     * ✅ 上传单个 Logo 到服务器（复用 ImageUpload 逻辑）
     */
    async uploadLogoToServer(file) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', 'image')
      
      // 获取JWT token
      const token = this.$wecomAuth?.getToken()
      if (!token) {
        throw new Error('未找到认证token，请重新登录')
      }
      
      const response = await this.$axios.post('/api/v1/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.data && response.data.success && response.data.url) {
        // 返回完整 URL
        const fileUrl = response.data.url.startsWith('http') 
          ? response.data.url 
          : window.location.origin + response.data.url
        return fileUrl
      } else {
        throw new Error('上传响应格式错误')
      }
    },
    
    async handleBatchUpload(event) {
      const files = Array.from(event.target.files)
      if (files.length === 0) return
      
      // 安全检查1：上传频率限制
      const now = Date.now()
      if (now - this.lastUploadTime < this.UPLOAD_COOLDOWN) {
        const remaining = Math.ceil((this.UPLOAD_COOLDOWN - (now - this.lastUploadTime)) / 1000)
        alert(`操作过于频繁，请${remaining}秒后再试`)
        event.target.value = ''
        return
      }
      
      // 安全检查2：批量上传数量限制
      if (files.length > this.MAX_BATCH_UPLOAD) {
        alert(`单次最多上传${this.MAX_BATCH_UPLOAD}个文件，您选择了${files.length}个`)
        event.target.value = ''
        return
      }
      
      // 安全检查3：总数量限制
      const currentCount = this.localData.logos.length
      const availableSlots = this.MAX_LOGOS - currentCount
      if (files.length > availableSlots) {
        alert(`最多只能添加${this.MAX_LOGOS}个Logo，当前已有${currentCount}个，还能添加${availableSlots}个`)
        event.target.value = ''
        return
      }
      
      // 安全检查4：文件类型和大小验证
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp']
      const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']
      const invalidFiles = []
      
      for (const file of files) {
        // MIME类型检查
        if (!allowedTypes.includes(file.type)) {
          invalidFiles.push(`${file.name} (不支持的文件类型)`)
          continue
        }
        
        // 文件扩展名检查
        const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
        if (!allowedExtensions.includes(extension)) {
          invalidFiles.push(`${file.name} (不支持的文件扩展名)`)
          continue
        }
        
        // 文件大小检查
        if (file.size > this.MAX_FILE_SIZE) {
          invalidFiles.push(`${file.name} (超过${this.MAX_FILE_SIZE / 1024}KB限制)`)
          continue
        }
      }
      
      if (invalidFiles.length > 0) {
        alert(`以下文件不符合要求：\n${invalidFiles.join('\n')}\n\n只支持JPG、PNG、GIF、SVG、WebP格式，单个文件最大${this.MAX_FILE_SIZE / 1024}KB`)
        event.target.value = ''
        return
      }
      
      this.isUploading = true
      
      try {
        // ✅ 改为服务器上传，避免 Base64 拖垮 WebView
        const uploadedLogos = await Promise.all(
          files.map(async (file, index) => {
            try {
              // 上传到服务器
              const url = await this.uploadLogoToServer(file)
              return {
                id: `logo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                src: url, // ✅ 存储 URL，不是 Base64
                name: file.name.replace(/\.[^/.]+$/, '') || `Logo ${this.localData.logos.length + index + 1}`
              }
            } catch (error) {
              console.error(`上传失败: ${file.name}`, error)
              return null
            }
          })
        )
        
        // 过滤失败的上传
        const successLogos = uploadedLogos.filter(logo => logo !== null)
        
        if (successLogos.length === 0) {
          throw new Error('所有图片上传失败')
        }
        
        // 批量添加所有logo
        this.localData.logos.push(...successLogos)
        
        // 更新上传时间和计数
        this.lastUploadTime = now
        this.uploadCount += successLogos.length
        
        // 触发更新
        this.$nextTick(() => {
          this.emitChangeImmediate()
        })
        
        console.log(`✅ 成功上传 ${successLogos.length} 个Logo (总计: ${this.uploadCount})`)
      } catch (error) {
        console.error('❌ 批量上传失败:', error)
        alert('部分图片上传失败，请重试')
      } finally {
        this.isUploading = false
        // 清空input，允许重复上传相同文件
        event.target.value = ''
      }
    },
    
    removeLogo(index) {
      // 防御性检查
      if (!this.localData.logos || index < 0 || index >= this.localData.logos.length) {
        console.warn('removeLogo: 无效的索引', index)
        return
      }
      
      if (confirm('确定要删除这个Logo吗？')) {
        this.localData.logos.splice(index, 1)
        
        // 在下一个tick中触发更新
        this.$nextTick(() => {
          this.emitChangeImmediate()
        })
      }
    },
    
    selectGap(gap) {
      this.localData.gap = gap
      this.emitChangeImmediate()
    },
    
    getSpeedLabel(scrollSpeed) {
      // 防御性检查
      if (typeof scrollSpeed !== 'number' || isNaN(scrollSpeed)) {
        return '适中'
      }
      
      // 基于滚动速度系数返回文字描述
      if (scrollSpeed <= 2) return '快速'
      if (scrollSpeed <= 3) return '适中'
      if (scrollSpeed <= 4) return '慢速'
      return '很慢'
    }
  },
  
  errorCaptured(err, vm, info) {
    console.error('LogoWallConfig: Error captured:', err, info)
    console.error('Current localData:', this.localData)
    // 防止错误传播导致整个应用崩溃
    return false
  }
}
</script>

<style scoped>
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

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-batch-upload {
  padding: 8px 16px;
  background: #1890ff;
  color: white;
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

.btn-batch-upload:hover {
  background: #40a9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.info-note {
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

.info-hints {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.warning-hint {
  padding: 12px 16px;
  background: rgba(255, 193, 7, 0.1);
  border-left: 3px solid #ffc107;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 8px;
}

.quota-hint {
  padding: 10px 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-left: 3px solid #667eea;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.quota-hint.quota-warning {
  background: rgba(255, 152, 0, 0.1);
  border-left-color: #ff9800;
}

.quota-hint.quota-full {
  background: rgba(244, 67, 54, 0.1);
  border-left-color: #f44336;
}

.quota-hint .remaining {
  color: #667eea;
  font-weight: 500;
}

.quota-hint .full-text {
  color: #f44336;
  font-weight: 600;
}

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

.logos-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.logo-card-simple {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.logo-card-simple:hover {
  border-color: #00ffaa;
  box-shadow: 0 2px 8px rgba(0, 255, 170, 0.1);
}

.drag-handle {
  cursor: move;
  color: #999;
  font-size: 18px;
  padding: 4px;
  flex-shrink: 0;
}

.logo-preview {
  width: 80px;
  height: 50px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.logo-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.logo-placeholder {
  font-size: 11px;
  color: #999;
  text-align: center;
}

.logo-upload-area {
  flex: 1;
  min-width: 0;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #666;
  background: #fff;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
}

.empty-state .tip {
  color: #fa8c16;
  margin-top: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.hint-text {
  font-size: 12px;
  color: #666;
  margin: 4px 0 0 0;
  line-height: 1.6;
}

.auto-calc {
  display: inline-block;
  margin-top: 4px;
  padding: 4px 8px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 6px;
  color: #667eea;
  font-weight: 500;
  font-size: 11px;
}

/* 速度控制 */
.speed-control {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.speed-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(to right, #00ffaa, #00aa7a);
  outline: none;
  -webkit-appearance: none;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #00ffaa;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 255, 170, 0.4);
}

.speed-value {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 60px;
}

.speed-value .value {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.speed-value .desc {
  font-size: 11px;
  color: #666;
}

/* 间距选择器 */
.gap-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 8px;
}

.gap-option {
  padding: 10px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.gap-option:hover {
  border-color: #00ffaa;
}

.gap-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.1);
  font-weight: 600;
}

/* 样式选项 */
.style-options {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  margin: 0;
}

/* 预览框 */
.preview-box {
  margin-top: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
}

.preview-title {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.preview-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  overflow: hidden;
}

.mini-logo-track {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
}

.mini-logo {
  height: 32px;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
}

.mini-logo img {
  height: 100%;
  width: auto;
  object-fit: contain;
}

.mini-logo.style-grayscale img {
  filter: grayscale(100%);
  opacity: 0.7;
}

.mini-logo.style-color img {
  filter: none;
  opacity: 1;
}

.mini-logo.style-dim img {
  opacity: 0.5;
}

.logo-placeholder {
  font-size: 10px;
  color: #999;
  padding: 4px 8px;
}

.preview-hint {
  font-size: 12px;
  color: #666;
  text-align: center;
  margin: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .speed-control {
    flex-direction: column;
    align-items: stretch;
  }
  
  .speed-value {
    align-items: center;
  }
  
  .style-options {
    flex-direction: column;
  }
}
</style>

