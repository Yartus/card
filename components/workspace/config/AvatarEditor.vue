<template>
  <div class="avatar-editor">
    <div class="editor-header">
      <h3 class="editor-title">
        <span class="icon">👤</span>
        头像设置
      </h3>
      <p class="editor-desc">默认使用企业微信头像，可上传高清头像替换</p>
    </div>

    <div class="editor-body">
      <!-- 当前头像预览 -->
      <div class="avatar-preview-section">
        <label class="section-label">当前头像</label>
        <div class="avatar-preview-container">
          <div class="avatar-preview-large">
            <img 
              v-if="currentAvatar" 
              :src="currentAvatar" 
              alt="头像预览"
              class="preview-image"
            />
            <div v-else class="avatar-placeholder-large">
              {{ avatarInitials }}
            </div>
            <div class="avatar-badge" v-if="isWecomAvatar">
              <span class="badge-text">企微</span>
            </div>
          </div>
          <div class="avatar-info">
            <p class="avatar-source">
              <span v-if="isWecomAvatar">来源：企业微信</span>
              <span v-else>来源：自定义上传</span>
            </p>
            <p class="avatar-size" v-if="avatarSize">
              尺寸：{{ avatarSize.width }} × {{ avatarSize.height }}px
            </p>
          </div>
        </div>
      </div>

      <!-- 头像上传 -->
      <div class="avatar-upload-section">
        <label class="section-label">上传新头像</label>
        <div class="upload-options">
          <!-- 使用企业微信头像 -->
          <button 
            class="option-btn"
            :class="{ active: useWecomAvatar }"
            @click="useWecomAvatar = true; handleChange()"
          >
            <span class="option-icon">🔄</span>
            <span class="option-text">使用企业微信头像</span>
          </button>

          <!-- 上传自定义头像 -->
          <div class="upload-custom">
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleFileChange"
            />
            <button 
              class="option-btn"
              :class="{ active: !useWecomAvatar && customAvatar }"
              @click="$refs.fileInput.click()"
            >
              <span class="option-icon">📤</span>
              <span class="option-text">上传高清头像</span>
            </button>
            <p class="upload-hint">
              支持 JPG、PNG 格式，建议尺寸：400×400px，文件小于 2MB
            </p>
          </div>
        </div>

        <!-- 上传进度 -->
        <div v-if="uploading" class="upload-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <span class="progress-text">{{ uploadProgress }}%</span>
        </div>

        <!-- 错误提示 -->
        <div v-if="uploadError" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ uploadError }}</span>
        </div>
      </div>

      <!-- 头像裁剪（可选，高级功能） -->
      <div v-if="showCrop && cropImage" class="avatar-crop-section">
        <label class="section-label">裁剪头像</label>
        <div class="crop-container">
          <div class="crop-preview" ref="cropPreview">
            <!-- 这里可以集成 cropperjs 等裁剪库 -->
            <img :src="cropImage" alt="裁剪预览" />
          </div>
          <div class="crop-actions">
            <button class="crop-btn cancel" @click="cancelCrop">取消</button>
            <button class="crop-btn confirm" @click="confirmCrop">确认</button>
          </div>
        </div>
      </div>

      <!-- 实时预览 -->
      <div class="preview-section">
        <label class="section-label">名片预览</label>
        <div class="card-preview" :style="previewCardStyle">
          <div class="preview-avatar-wrapper">
            <img 
              v-if="displayAvatar" 
              :src="displayAvatar" 
              alt="预览头像"
              class="preview-avatar-img"
            />
            <div v-else class="preview-avatar-placeholder">
              {{ avatarInitials }}
            </div>
          </div>
          <div class="preview-info">
            <div class="preview-name">{{ userName || '张三' }}</div>
            <div class="preview-title">{{ userTitle || '产品经理' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AvatarEditor',
  
  props: {
    value: {
      type: Object,
      default: () => ({
        useWecomAvatar: true,  // 是否使用企业微信头像
        customAvatar: '',      // 自定义头像URL
        wecomAvatar: ''        // 企业微信头像URL（从basicInfo同步）
      })
    },
    basicInfo: {
      type: Object,
      default: () => ({
        name: '',
        avatar: ''
      })
    }
  },
  
  data() {
    return {
      localConfig: { ...this.value },
      uploading: false,
      uploadProgress: 0,
      uploadError: '',
      cropImage: '',
      showCrop: false,
      avatarSize: null
    }
  },
  
  computed: {
    useWecomAvatar: {
      get() {
        return this.localConfig.useWecomAvatar !== false
      },
      set(val) {
        this.localConfig.useWecomAvatar = val
      }
    },
    
    currentAvatar() {
      if (this.useWecomAvatar) {
        return this.localConfig.wecomAvatar || this.basicInfo.avatar || ''
      }
      return this.localConfig.customAvatar || ''
    },
    
    displayAvatar() {
      return this.currentAvatar
    },
    
    avatarInitials() {
      if (!this.basicInfo.name) return '?'
      const names = this.basicInfo.name.split(' ')
      if (names.length >= 2) {
        return names[0].charAt(0) + names[1].charAt(0)
      }
      return this.basicInfo.name.charAt(0)
    },
    
    userName() {
      return this.basicInfo.name || ''
    },
    
    userTitle() {
      return this.basicInfo.title || ''
    },
    
    isWecomAvatar() {
      return this.useWecomAvatar && (this.localConfig.wecomAvatar || this.basicInfo.avatar)
    },
    
    previewCardStyle() {
      // 可以添加背景样式预览
      return {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }
    }
  },
  
  watch: {
    value: {
      handler(newVal) {
        this.localConfig = { ...newVal }
      },
      deep: true
    },
    
    'basicInfo.avatar'(newVal) {
      if (newVal && this.useWecomAvatar) {
        this.localConfig.wecomAvatar = newVal
        this.handleChange()
      }
    }
  },
  
  mounted() {
    // 初始化企业微信头像
    if (this.basicInfo.avatar && !this.localConfig.wecomAvatar) {
      this.localConfig.wecomAvatar = this.basicInfo.avatar
    }
  },
  
  methods: {
    async handleFileChange(event) {
      const file = event.target.files[0]
      if (!file) return
      
      this.uploadError = ''
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        this.uploadError = '只能上传图片文件'
        return
      }
      
      // 验证文件大小（2MB）
      if (file.size > 2 * 1024 * 1024) {
        this.uploadError = '图片大小不能超过2MB'
        return
      }
      
      // 读取图片尺寸
      await this.readImageSize(file)
      
      // 压缩图片（如果太大）
      let processedFile = file
      if (file.size > 500 * 1024) {
        processedFile = await this.compressImage(file)
      }
      
      // 上传到服务器
      await this.uploadAvatar(processedFile)
    },
    
    readImageSize(file) {
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = new Image()
          img.onload = () => {
            this.avatarSize = {
              width: img.width,
              height: img.height
            }
            resolve()
          }
          img.src = e.target.result
        }
        reader.readAsDataURL(file)
      })
    },
    
    compressImage(file) {
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = new Image()
          img.onload = () => {
            const canvas = document.createElement('canvas')
            const ctx = canvas.getContext('2d')
            
            // 限制最大尺寸为 800x800
            let width = img.width
            let height = img.height
            const maxSize = 800
            
            if (width > maxSize || height > maxSize) {
              if (width > height) {
                height = (height * maxSize) / width
                width = maxSize
              } else {
                width = (width * maxSize) / height
                height = maxSize
              }
            }
            
            canvas.width = width
            canvas.height = height
            ctx.drawImage(img, 0, 0, width, height)
            
            canvas.toBlob((blob) => {
              const compressedFile = new File([blob], file.name, {
                type: 'image/jpeg',
                lastModified: Date.now()
              })
              resolve(compressedFile)
            }, 'image/jpeg', 0.85)
          }
          img.src = e.target.result
        }
        reader.readAsDataURL(file)
      })
    },
    
    async uploadAvatar(file) {
      this.uploading = true
      this.uploadProgress = 0
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('file_type', 'avatar')
        
        // 获取JWT token
        const token = this.$wecomAuth?.getToken()
        if (!token) {
          throw new Error('未找到认证token，请重新登录')
        }
        
        // 模拟上传进度
        const progressInterval = setInterval(() => {
          if (this.uploadProgress < 90) {
            this.uploadProgress += 10
          }
        }, 100)
        
        const response = await this.$axios.post('/api/v1/files/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              this.uploadProgress = Math.round((progressEvent.loaded * 90) / progressEvent.total)
            }
          }
        })
        
        clearInterval(progressInterval)
        this.uploadProgress = 100
        
        if (response.data && response.data.success && response.data.url) {
          const fileUrl = response.data.url.startsWith('http') 
            ? response.data.url 
            : window.location.origin + response.data.url
          
          this.localConfig.customAvatar = fileUrl
          this.localConfig.useWecomAvatar = false
          this.handleChange()
          
          this.$toast?.success('头像上传成功')
        }
      } catch (error) {
        console.error('上传失败:', error)
        this.uploadError = error.response?.data?.error || error.message || '上传失败，请重试'
        this.$toast?.error(this.uploadError)
      } finally {
        this.uploading = false
        this.uploadProgress = 0
        setTimeout(() => {
          this.uploadError = ''
        }, 3000)
      }
    },
    
    cancelCrop() {
      this.showCrop = false
      this.cropImage = ''
    },
    
    confirmCrop() {
      // 实现裁剪确认逻辑
      this.showCrop = false
      this.cropImage = ''
    },
    
    handleChange() {
      this.$emit('input', { ...this.localConfig })
    }
  }
}
</script>

<style lang="scss" scoped>
.avatar-editor {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.editor-header {
  margin-bottom: 24px;
}

.editor-title {
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

.editor-title .icon {
  font-size: 24px;
}

.editor-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

.section-label {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 12px;
}

/* 头像预览 */
.avatar-preview-section {
  margin-bottom: 24px;
}

.avatar-preview-container {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-preview-large {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder-large {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.avatar-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(102, 126, 234, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.avatar-info {
  flex: 1;
}

.avatar-source {
  font-size: 14px;
  color: #475569;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.avatar-size {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
}

/* 上传选项 */
.avatar-upload-section {
  margin-bottom: 24px;
}

.upload-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.option-btn:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.option-btn.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
  color: #667eea;
}

.option-icon {
  font-size: 20px;
}

.upload-custom {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
  padding-left: 32px;
}

/* 上传进度 */
.upload-progress {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
  min-width: 40px;
}

/* 错误提示 */
.error-message {
  margin-top: 12px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  font-size: 16px;
}

/* 裁剪区域 */
.avatar-crop-section {
  margin-bottom: 24px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.crop-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.crop-preview {
  width: 100%;
  height: 300px;
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.crop-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.crop-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.crop-btn {
  padding: 10px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.crop-btn.cancel {
  background: white;
  color: #64748b;
}

.crop-btn.cancel:hover {
  border-color: #cbd5e1;
}

.crop-btn.confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.crop-btn.confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 预览区域 */
.preview-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px dashed #e2e8f0;
}

.card-preview {
  height: 180px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  position: relative;
  padding: 24px;
}

.preview-avatar-wrapper {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 3px solid white;
  flex-shrink: 0;
}

.preview-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 100%);
}

.preview-info {
  margin-left: 16px;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.preview-name {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.preview-title {
  font-size: 14px;
  opacity: 0.95;
}

/* 响应式 */
@media (max-width: 768px) {
  .avatar-preview-container {
    flex-direction: column;
    text-align: center;
  }
  
  .card-preview {
    flex-direction: column;
    height: auto;
    min-height: 200px;
  }
  
  .preview-info {
    margin-left: 0;
    margin-top: 12px;
    text-align: center;
  }
}
</style>

