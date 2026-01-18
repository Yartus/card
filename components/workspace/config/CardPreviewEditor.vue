<template>
  <div class="card-preview-editor">
    <div class="editor-header">
      <h3 class="editor-title">
        <span class="icon">🎨</span>
        卡片预览样式配置
      </h3>
      <p class="editor-desc">自定义卡片预览页面的样式，包括头像、背景、颜色等</p>
    </div>

    <div class="editor-body">
      <!-- 头像配置 -->
      <div class="config-section">
        <div class="section-header">
          <label class="section-label">头像设置</label>
          <span class="section-tip">默认使用公司统一图片，可选择使用员工照片</span>
        </div>
        <div class="avatar-config-row">
          <div class="avatar-preview-small">
            <img 
              v-if="displayAvatar" 
              :src="displayAvatar" 
              alt="头像预览"
              class="preview-avatar-img"
            />
            <div v-else class="avatar-placeholder-small">
              {{ avatarInitials }}
            </div>
          </div>
          <div class="avatar-options">
            <div class="avatar-mode-selector">
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="localConfig.avatarMode"
                  value="company"
                  @change="handleChange"
                />
                <span>公司统一图片</span>
              </label>
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="localConfig.avatarMode"
                  value="member"
                  @change="handleChange"
                />
                <span>员工照片</span>
              </label>
            </div>
            <div v-if="localConfig.avatarMode === 'company'" class="upload-custom-avatar">
              <input
                ref="companyAvatarFileInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleCompanyAvatarUpload"
              />
              <button 
                class="upload-btn-small"
                @click="$refs.companyAvatarFileInput.click()"
              >
                <span class="btn-icon">📤</span>
                上传公司统一图片（首图，高质量）
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 背景配置 -->
      <div class="config-section">
        <div class="section-header">
          <label class="section-label">背景样式</label>
          <span class="section-tip">选择背景类型和颜色</span>
        </div>
        <div class="bg-type-tabs">
          <button
            v-for="type in bgTypes"
            :key="type.value"
            :class="['bg-type-tab', { active: localConfig.backgroundType === type.value }]"
            @click="selectBgType(type.value)"
          >
            <span class="tab-icon">{{ type.icon }}</span>
            <span class="tab-label">{{ type.label }}</span>
          </button>
        </div>

        <!-- 图片背景配置 -->
        <div v-if="localConfig.backgroundType === 'image'" class="bg-settings">
          <ImageUpload
            v-model="localConfig.backgroundImage"
            label="背景图片（首图）"
            hint="建议尺寸：800×800px，高质量压缩，优先清晰度"
            :max-size="1024 * 1024"
            :high-quality="true"
            @change="handleChange"
          />
        </div>

        <!-- 纯色背景配置 -->
        <div v-if="localConfig.backgroundType === 'solid'" class="bg-settings">
          <div class="color-picker-item">
            <label>背景颜色</label>
            <div class="color-input-group">
              <input
                v-model="localConfig.backgroundColor"
                type="color"
                class="color-picker"
                @input="handleChange"
              />
              <input
                v-model="localConfig.backgroundColor"
                type="text"
                class="color-text"
                @input="handleChange"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 主题颜色配置 -->
      <div class="config-section">
        <div class="section-header">
          <label class="section-label">主题颜色</label>
          <span class="section-tip">统一设置底部区域、电话图标、头像边框的颜色</span>
        </div>
        <div class="color-picker-item">
          <div class="color-input-group">
            <input
              v-model="localConfig.themeColor"
              type="color"
              class="color-picker"
              @input="handleChange"
            />
            <input
              v-model="localConfig.themeColor"
              type="text"
              class="color-text"
              @input="handleChange"
            />
          </div>
        </div>
      </div>

      <!-- 个人介绍 -->
      <div class="config-section">
        <div class="section-header">
          <label class="section-label">个人介绍</label>
          <span class="section-tip">显示在卡片预览页面（建议20字以内）</span>
        </div>
        <textarea
          v-model="localConfig.personalIntro"
          class="form-textarea"
          placeholder="例如：专注于企业数字化转型，拥有10年行业经验"
          rows="2"
          maxlength="50"
          @input="handleChange"
        ></textarea>
        <div class="char-count">{{ localConfig.personalIntro?.length || 0 }} / 50</div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageUpload from '../form/ImageUpload.vue'

export default {
  name: 'CardPreviewEditor',
  
  components: {
    ImageUpload
  },
  
  props: {
    value: {
      type: Object,
      default: () => ({})
    },
    wecomAvatar: {
      type: String,
      default: ''
    }
  },
  
  data() {
    return {
      localConfig: {
        avatarMode: 'company', // 'company' 或 'member'
        companyAvatar: '', // 公司统一图片
        backgroundType: 'solid', // 默认纯色背景
        backgroundImage: '',
        backgroundColor: '#f5f5f5',
        themeColor: '#fbb9b6', // 统一主题颜色（底部区域、电话图标、头像边框）
        personalIntro: ''
      },
      bgTypes: [
        { value: 'image', label: '图片', icon: '🖼️' },
        { value: 'solid', label: '纯色', icon: '🎯' }
      ],
      uploading: false
    }
  },
  
  computed: {
    displayAvatar() {
      if (this.localConfig.avatarMode === 'company') {
        return this.localConfig.companyAvatar || ''
      } else {
        // 员工照片模式，使用企微头像
        return this.wecomAvatar || ''
      }
    },
    
    avatarInitials() {
      return '头像'
    }
  },
  
  watch: {
    value: {
      handler(newVal) {
        if (newVal) {
          this.localConfig = {
            avatarMode: newVal.avatarMode || 'company',
            companyAvatar: newVal.companyAvatar || '',
            backgroundType: newVal.backgroundType || 'solid',
            backgroundImage: newVal.backgroundImage || '',
            backgroundColor: newVal.backgroundColor || '#f5f5f5',
            themeColor: newVal.themeColor || '#fbb9b6',
            personalIntro: newVal.personalIntro || ''
          }
        }
      },
      immediate: true,
      deep: true
    }
  },
  
  methods: {
    handleChange() {
      this.$emit('input', { ...this.localConfig })
    },
    
    selectBgType(type) {
      this.localConfig.backgroundType = type
      this.handleChange()
    },
    
    async handleCompanyAvatarUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件
      if (!file.type.startsWith('image/')) {
        this.$toast?.error('请选择图片文件')
        return
      }
      
      // 首图允许更大文件，最大1MB（高质量优先）
      if (file.size > 1024 * 1024) {
        this.$toast?.error('图片大小不能超过1MB')
        return
      }
      
      this.uploading = true
      
      try {
        // 首图高质量压缩（优先清晰度）
        let processedFile = file
        if (file.size > 500 * 1024) {
          processedFile = await this.compressImageHighQuality(file)
        }
        
        // 使用统一的图片上传组件逻辑
        const formData = new FormData()
        formData.append('file', processedFile)
        
        const { data } = await this.$axios.post('/api/v1/files/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (data.success && data.url) {
          this.localConfig.companyAvatar = data.url
          this.localConfig.avatarMode = 'company'
          this.handleChange()
          this.$toast?.success('公司统一图片上传成功')
        } else {
          throw new Error(data.message || '上传失败')
        }
      } catch (error) {
        console.error('图片上传失败:', error)
        this.$toast?.error(error.response?.data?.message || '图片上传失败，请重试')
      } finally {
        this.uploading = false
        // 清空input，允许重复选择同一文件
        event.target.value = ''
      }
    },
    
    /**
     * 高质量压缩图片（用于首图，优先清晰度）
     * 策略：最大宽度2000px，质量0.9，确保清晰度
     */
    async compressImageHighQuality(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = new Image()
          img.onload = () => {
            // 计算压缩尺寸（首图允许更大尺寸）
            const MAX_WIDTH = 2000
            let width = img.width
            let height = img.height
            
            if (width > MAX_WIDTH) {
              height = Math.round((height * MAX_WIDTH) / width)
              width = MAX_WIDTH
            }
            
            // Canvas 压缩
            const canvas = document.createElement('canvas')
            canvas.width = width
            canvas.height = height
            const ctx = canvas.getContext('2d')
            
            // 使用高质量渲染
            ctx.imageSmoothingEnabled = true
            ctx.imageSmoothingQuality = 'high'
            ctx.drawImage(img, 0, 0, width, height)
            
            // 转为 Blob（质量 0.9，优先清晰度）
            canvas.toBlob((blob) => {
              if (blob) {
                const compressedFile = new File([blob], file.name, {
                  type: 'image/jpeg',
                  lastModified: Date.now()
                })
                resolve(compressedFile)
              } else {
                reject(new Error('压缩失败'))
              }
            }, 'image/jpeg', 0.9) // 高质量：0.9
          }
          img.onerror = () => reject(new Error('图片加载失败'))
          img.src = e.target.result
        }
        reader.onerror = () => reject(new Error('文件读取失败'))
        reader.readAsDataURL(file)
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.card-preview-editor {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.editor-header {
  margin-bottom: 24px;
}

.editor-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.editor-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.5;
}

.config-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
}

.section-header {
  margin-bottom: 16px;
}

.section-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.section-tip {
  font-size: 12px;
  color: #8c8c8c;
}

.avatar-config-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-preview-small {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid #f0f0f0;
  
  .preview-avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .avatar-placeholder-small {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    color: #8c8c8c;
    font-size: 20px;
  }
}

.avatar-options {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-label,
.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #262626;
  cursor: pointer;
  
  input[type="checkbox"],
  input[type="radio"] {
    width: 16px;
    height: 16px;
    cursor: pointer;
  }
}

.avatar-mode-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.upload-btn-small {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  color: #262626;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e8e8e8;
    border-color: #d0d0d0;
  }
  
  .btn-icon {
    font-size: 14px;
  }
}

.bg-type-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.bg-type-tab {
  flex: 1;
  padding: 10px 16px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  color: #262626;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e8e8e8;
  }
  
  &.active {
    background: #1890ff;
    border-color: #1890ff;
    color: white;
  }
  
  .tab-icon {
    font-size: 16px;
  }
}

.bg-settings {
  margin-top: 16px;
}

.pattern-selector {
  margin-bottom: 16px;
  
  label {
    display: block;
    font-size: 13px;
    color: #262626;
    margin-bottom: 8px;
  }
  
  .form-select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    background: white;
    cursor: pointer;
  }
}

.color-pickers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.color-picker-item {
  label {
    display: block;
    font-size: 13px;
    color: #262626;
    margin-bottom: 8px;
  }
}

.color-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.color-picker {
  width: 50px;
  height: 36px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
}

.color-text {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  font-family: monospace;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 60px;
  
  &:focus {
    outline: none;
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
  }
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}
</style>

