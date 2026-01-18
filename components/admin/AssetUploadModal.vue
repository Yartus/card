<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>上传素材</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body">
        <!-- 配额提示 -->
        <div class="quota-hint" :class="{ 
          'quota-warning': remainingImageSlots <= 5,
          'quota-full': remainingImageSlots === 0 
        }">
          <i class="icon-info">ℹ️</i>
          <span>已选择 {{ getImageCount() }}/{{ MAX_IMAGES }} 个文件</span>
          <span v-if="remainingImageSlots > 0" class="remaining">
            （还可添加{{ remainingImageSlots }}个）
          </span>
          <span v-else class="full-text">（已达上限）</span>
        </div>
        
        <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
          <input
            ref="fileInput"
            type="file"
            multiple
            accept="image/*,video/*,.pdf,.doc,.docx"
            @change="handleFileSelect"
            style="display: none"
          >
          <div class="upload-placeholder">
            <i class="upload-icon">📁</i>
            <p>点击或拖拽文件到此处上传</p>
            <p class="upload-hint">支持图片、视频、PDF、Word文档（单次最多{{ MAX_BATCH_UPLOAD }}个，单个最大{{ MAX_FILE_SIZE / 1024 }}KB）</p>
          </div>
        </div>
        
        <div v-if="selectedFiles.length > 0" class="file-list">
          <h4>选择的文件：</h4>
          <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
            <button @click="removeFile(index)" class="remove-btn">删除</button>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">取消</button>
        <button 
          class="btn btn-primary" 
          @click="uploadFiles"
          :disabled="selectedFiles.length === 0 || uploading"
        >
          {{ uploading ? '上传中...' : '上传' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import uploadSecurityMixin from '../workspace/config/upload-security-mixin'

export default {
  name: 'AssetUploadModal',
  
  mixins: [uploadSecurityMixin],
  
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selectedFiles: [],
      uploading: false
    }
  },
  methods: {
    // 实现 upload-security-mixin 要求的方法
    getImageCount() {
      return this.selectedFiles.length
    },
    
    close() {
      this.$emit('close')
      this.selectedFiles = []
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      this.addFiles(files)
      // 清空input以允许重复选择
      event.target.value = ''
    },
    
    handleDrop(event) {
      const files = Array.from(event.dataTransfer.files)
      this.addFiles(files)
    },
    
    addFiles(files) {
      // 安全检查
      const securityCheck = this.securityCheckBeforeUpload(files)
      if (!securityCheck.allowed) {
        alert(securityCheck.message)
        return
      }
      
      // 添加通过检查的文件
      const validFiles = securityCheck.validFiles
      validFiles.forEach(file => {
        if (!this.selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
          this.selectedFiles.push(file)
        }
      })
      
      // 更新时间戳和计数
      this.updateUploadTimestamp()
      this.incrementUploadCount(validFiles.length)
    },
    
    removeFile(index) {
      this.selectedFiles.splice(index, 1)
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    async uploadFiles() {
      if (this.selectedFiles.length === 0) return
      
      this.uploading = true
      try {
        const formData = new FormData()
        this.selectedFiles.forEach(file => {
          formData.append('files', file)
        })
        
        const response = await this.$axios.post('/api/admin/assets/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        this.$emit('uploaded', response.data)
        this.close()
        this.$toast.success('素材上传成功')
      } catch (error) {
        console.error('上传失败:', error)
        this.$toast.error('上传失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.uploading = false
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 配额提示 */
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
  margin-bottom: 16px;
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

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #1890ff;
}

.upload-placeholder {
  color: #666;
}

.upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.upload-hint {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

.file-list {
  margin-top: 20px;
}

.file-list h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.file-name {
  flex: 1;
  color: #333;
}

.file-size {
  color: #999;
  margin: 0 12px;
  font-size: 14px;
}

.remove-btn {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
