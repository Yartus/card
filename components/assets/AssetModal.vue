<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ isEdit ? '编辑素材' : '素材详情' }}</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body">
        <div v-if="asset" class="asset-detail">
          <!-- 素材预览区域 -->
          <div class="asset-preview-section">
            <div v-if="isImage" class="preview-image">
              <img :src="asset.content_url" :alt="asset.name" class="preview-img">
            </div>
            
            <div v-else-if="isVideo" class="preview-video">
              <video :src="asset.content_url" controls class="preview-vid">
                您的浏览器不支持视频播放
              </video>
            </div>
            
            <div v-else class="preview-file">
              <div class="file-icon">
                <i class="icon">📄</i>
              </div>
              <p class="file-name">{{ asset.name }}</p>
              <a :href="asset.content_url" target="_blank" class="download-link">
                下载文件
              </a>
            </div>
          </div>
          
          <!-- 素材信息 -->
          <div class="asset-info-section">
            <div v-if="isEdit" class="edit-form">
              <div class="form-group">
                <label>素材名称</label>
                <input 
                  v-model="editData.name" 
                  type="text" 
                  class="form-input"
                  placeholder="请输入素材名称"
                >
              </div>
              
              <div class="form-group">
                <label>素材描述</label>
                <textarea 
                  v-model="editData.description" 
                  class="form-textarea"
                  placeholder="请输入素材描述"
                  rows="3"
                ></textarea>
              </div>
              
              <div class="form-group">
                <label>标签</label>
                <div class="tags-input">
                  <input
                    v-model="newTag"
                    type="text"
                    class="form-input"
                    placeholder="输入标签后按回车添加"
                    @keyup.enter="addTag"
                  >
                  <div v-if="editData.tags.length > 0" class="tags-list">
                    <span 
                      v-for="(tag, index) in editData.tags" 
                      :key="index" 
                      class="tag"
                    >
                      {{ tag }}
                      <button type="button" @click="removeTag(index)" class="tag-remove">&times;</button>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="form-group">
                <label>分类</label>
                <select v-model="editData.category" class="form-select">
                  <option value="">请选择分类</option>
                  <option value="image">图片</option>
                  <option value="video">视频</option>
                  <option value="document">文档</option>
                  <option value="other">其他</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>可见性</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input 
                      v-model="editData.isPublic" 
                      type="radio" 
                      :value="true"
                    >
                    公开
                  </label>
                  <label class="radio-item">
                    <input 
                      v-model="editData.isPublic" 
                      type="radio" 
                      :value="false"
                    >
                    私有
                  </label>
                </div>
              </div>
            </div>
            
            <div v-else class="info-display">
              <div class="info-item">
                <label>名称：</label>
                <span>{{ asset.name }}</span>
              </div>
              <div class="info-item">
                <label>描述：</label>
                <span>{{ asset.description || '无描述' }}</span>
              </div>
              <div class="info-item">
                <label>分类：</label>
                <span>{{ getCategoryName(asset.category) }}</span>
              </div>
              <div class="info-item">
                <label>标签：</label>
                <div v-if="asset.tags && asset.tags.length > 0" class="tags">
                  <span v-for="tag in asset.tags" :key="tag" class="tag">{{ tag }}</span>
                </div>
                <span v-else>无标签</span>
              </div>
              <div class="info-item">
                <label>可见性：</label>
                <span :class="asset.isPublic ? 'public' : 'private'">
                  {{ asset.isPublic ? '公开' : '私有' }}
                </span>
              </div>
              <div class="info-item">
                <label>上传时间：</label>
                <span>{{ formatDate(asset.created_at) }}</span>
              </div>
              <div class="info-item">
                <label>文件大小：</label>
                <span>{{ formatFileSize(asset.file_size) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">关闭</button>
        <button v-if="isEdit" class="btn btn-primary" @click="saveChanges" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button v-else class="btn btn-primary" @click="startEdit">编辑</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    asset: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      isEdit: false,
      editData: {
        name: '',
        description: '',
        tags: [],
        category: '',
        isPublic: true
      },
      newTag: '',
      saving: false
    }
  },
  computed: {
    isImage() {
      if (!this.asset.content_url) return false
      const imageExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
      return imageExts.some(ext => this.asset.content_url.toLowerCase().includes(ext))
    },
    
    isVideo() {
      if (!this.asset.content_url) return false
      const videoExts = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
      return videoExts.some(ext => this.asset.content_url.toLowerCase().includes(ext))
    }
  },
  watch: {
    asset: {
      handler(newAsset) {
        if (newAsset && Object.keys(newAsset).length > 0) {
          this.editData = {
            name: newAsset.name || '',
            description: newAsset.description || '',
            tags: [...(newAsset.tags || [])],
            category: newAsset.category || '',
            isPublic: newAsset.isPublic !== false
          }
        }
      },
      immediate: true
    }
  },
  methods: {
    close() {
      this.$emit('close')
      this.isEdit = false
      this.resetEditData()
    },
    
    startEdit() {
      this.isEdit = true
    },
    
    resetEditData() {
      this.editData = {
        name: '',
        description: '',
        tags: [],
        category: '',
        isPublic: true
      }
      this.newTag = ''
    },
    
    addTag() {
      const tag = this.newTag.trim()
      if (tag && !this.editData.tags.includes(tag)) {
        this.editData.tags.push(tag)
        this.newTag = ''
      }
    },
    
    removeTag(index) {
      this.editData.tags.splice(index, 1)
    },
    
    async saveChanges() {
      if (!this.editData.name.trim()) {
        this.$toast.error('请输入素材名称')
        return
      }
      
      this.saving = true
      try {
        const response = await this.$axios.put(`/api/assets/${this.asset.id}`, this.editData)
        this.$emit('updated', response.data)
        this.isEdit = false
        this.$toast.success('素材更新成功')
      } catch (error) {
        console.error('保存失败:', error)
        this.$toast.error('保存失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.saving = false
      }
    },
    
    getCategoryName(category) {
      const categoryMap = {
        'image': '图片',
        'video': '视频',
        'document': '文档',
        'other': '其他'
      }
      return categoryMap[category] || '未分类'
    },
    
    formatDate(dateString) {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    
    formatFileSize(bytes) {
      if (!bytes) return '未知'
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
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
  max-height: 60vh;
  overflow-y: auto;
}

.asset-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.asset-preview-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.preview-image,
.preview-video {
  width: 100%;
  text-align: center;
}

.preview-img,
.preview-vid {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.preview-file {
  text-align: center;
}

.file-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.file-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.download-link {
  display: inline-block;
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
}

.asset-info-section {
  display: flex;
  flex-direction: column;
}

.edit-form .form-group {
  margin-bottom: 16px;
}

.edit-form label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.tags-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  display: inline-flex;
  align-items: center;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.tag-remove {
  background: none;
  border: none;
  margin-left: 4px;
  cursor: pointer;
  color: #999;
  font-size: 14px;
  line-height: 1;
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-item input {
  margin-right: 6px;
}

.info-display {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: flex-start;
}

.info-item label {
  min-width: 80px;
  color: #666;
  font-weight: 500;
}

.info-item span {
  color: #333;
  flex: 1;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.public {
  color: #52c41a;
}

.private {
  color: #ff4d4f;
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

@media (max-width: 768px) {
  .asset-detail {
    grid-template-columns: 1fr;
  }
  
  .asset-preview-section {
    min-height: 200px;
  }
}
</style>
