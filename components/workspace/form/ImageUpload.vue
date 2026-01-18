<template>
  <div class="image-upload">
    <label v-if="label" class="upload-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <div class="upload-area" @click="triggerUpload">
      <div v-if="previewUrl" class="preview-container">
        <img :src="previewUrl" :alt="label" class="preview-image" />
        <div class="preview-overlay">
          <button type="button" class="btn-change" @click.stop="triggerUpload">
            <i class="icon-edit"></i> 更换
          </button>
          <button type="button" class="btn-remove" @click.stop="handleRemove">
            <i class="icon-delete"></i> 删除
          </button>
        </div>
      </div>
      
      <div v-else class="upload-placeholder">
        <LottieIcon
          v-if="uploadAnimation"
          :animation-data="uploadAnimation"
          :width="48"
          :height="48"
          :autoplay="false"
          :loop="false"
        />
        <i v-else class="icon-upload"></i>
        <p class="upload-hint">点击上传图片</p>
        <p v-if="hint" class="upload-desc">{{ hint }}</p>
      </div>
    </div>
    
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
    
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import LottieIcon from '~/components/LottieIcon.vue'

export default {
  name: 'ImageUpload',
  
  components: {
    LottieIcon
  },
  
  props: {
    value: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    hint: {
      type: String,
      default: '支持 JPG/PNG，自动压缩到 500KB（保留清晰度）'
    },
    required: {
      type: Boolean,
      default: false
    },
    maxSize: {
      type: Number,
      default: 500 * 1024 // 500KB（避免 Base64 暴涨导致 JSON 深拷贝崩溃）
    },
    highQuality: {
      type: Boolean,
      default: false // 高质量模式（用于首图，优先清晰度）
    },
    aspectRatio: {
      type: String,
      default: '' // '16:9', '4:3', '1:1'
    }
  },
  
  data() {
    return {
      previewUrl: this.value,
      error: '',
      uploadAnimation: null
    }
  },
  
  watch: {
    value(newVal) {
      this.previewUrl = newVal
    }
  },
  
  methods: {
    triggerUpload() {
      this.$refs.fileInput.click()
    },
    
    async handleFileChange(event) {
      const file = event.target.files[0]
      if (!file) return
      
      this.error = ''
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        this.error = '只能上传图片文件'
        return
      }
      
      // ✅ 智能压缩：根据模式选择压缩策略
      let processedFile = file
      if (file.size > this.maxSize) {
        console.log(`📦 原图过大 (${(file.size / 1024).toFixed(0)}KB)，启动压缩...`)
        if (this.highQuality) {
          // 高质量模式（首图）：优先清晰度
          processedFile = await this.compressImageHighQuality(file)
          console.log(`✅ 高质量压缩完成 (${(processedFile.size / 1024).toFixed(0)}KB)`)
        } else {
          // 标准模式：平衡清晰度与体积
          processedFile = await this.compressImage(file)
          console.log(`✅ 压缩完成 (${(processedFile.size / 1024).toFixed(0)}KB)`)
        }
      }
      
      // 最终验证
      if (processedFile.size > this.maxSize) {
        const maxSizeKB = Math.round(this.maxSize / 1024)
        this.error = `压缩后仍超过 ${maxSizeKB}KB，请选择更小的图片`
        return
      }
      
      // 先创建本地预览
      const reader = new FileReader()
      reader.onload = (e) => {
        this.previewUrl = e.target.result
      }
      reader.readAsDataURL(processedFile)
      
      // 上传到服务器
      await this.uploadToServer(processedFile)
    },
    
    async uploadToServer(file) {
      try {
        console.log('📤 开始上传文件:', file.name, '大小:', (file.size / 1024).toFixed(2) + 'KB')
        
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
        
        console.log('✅ 文件上传成功:', response.data)
        
        if (response.data && response.data.success && response.data.url) {
          // 将相对路径转换为绝对URL（用于显示）
          const fileUrl = response.data.url.startsWith('http') 
            ? response.data.url 
            : window.location.origin + response.data.url
          
          // 更新预览URL
          this.previewUrl = fileUrl
          
          // 触发事件，传递服务器URL
          this.$emit('input', fileUrl)
          this.$emit('change', fileUrl)
          
          console.log('✅ URL已更新:', fileUrl)
        }
      } catch (error) {
        console.error('❌ 上传失败:', error)
        console.error('错误详情:', error.response?.data)
        
        const errorMsg = error.response?.data?.error || error.message || '上传失败，请重试'
        this.error = errorMsg
        this.previewUrl = ''
        
        alert(errorMsg)
      }
    },
    
    handleRemove() {
      this.previewUrl = ''
      this.error = ''
      this.$emit('input', '')
      this.$emit('remove')
      this.$refs.fileInput.value = ''
    },
    
    /**
     * ✅ 智能压缩图片（Canvas 原生实现，无需额外依赖）
     * 策略：宽度 1200px，质量 0.75，保留清晰度同时控制体积
     */
    async compressImage(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = new Image()
          img.onload = () => {
            // 计算压缩尺寸
            const MAX_WIDTH = 1200
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
            ctx.drawImage(img, 0, 0, width, height)
            
            // 转为 Blob（质量 0.75，平衡清晰度与体积）
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
            }, 'image/jpeg', 0.75)
          }
          img.onerror = () => reject(new Error('图片加载失败'))
          img.src = e.target.result
        }
        reader.onerror = () => reject(new Error('文件读取失败'))
        reader.readAsDataURL(file)
      })
    },
    
    /**
     * ✅ 高质量压缩图片（用于首图，优先清晰度）
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

<style scoped>
.image-upload {
  width: 100%;
}

.upload-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.required {
  color: #ff4757;
  margin-left: 4px;
}

.upload-area {
  width: 100%;
  min-height: 200px;
  border: 2px dashed rgba(0, 255, 170, 0.3);
  border-radius: 12px;
  background: rgba(0, 255, 170, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.upload-area:hover {
  border-color: rgba(0, 255, 170, 0.6);
  background: rgba(0, 255, 170, 0.1);
}

.preview-container {
  position: relative;
  width: 100%;
  min-height: 150px;
  max-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.preview-image {
  max-width: 150px;
  max-height: 150px;
  width: auto;
  height: auto;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.preview-container:hover .preview-overlay {
  opacity: 1;
}

.btn-change,
.btn-remove {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-change {
  background: rgba(0, 255, 170, 0.2);
  color: #00ffaa;
  border: 1px solid #00ffaa;
}

.btn-change:hover {
  background: rgba(0, 255, 170, 0.3);
}

.btn-remove {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
  border: 1px solid #ff4757;
}

.btn-remove:hover {
  background: rgba(255, 71, 87, 0.3);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 24px;
}

.icon-upload {
  font-size: 48px;
  color: rgba(0, 255, 170, 0.6);
  margin-bottom: 16px;
}

.upload-hint {
  font-size: 16px;
  font-weight: 500;
  color: #1a1a2e;
  margin: 8px 0;
}

.upload-desc {
  font-size: 12px;
  color: #666;
  margin: 0;
}

.error-message {
  color: #ff4757;
  font-size: 12px;
  margin-top: 8px;
}
</style>

