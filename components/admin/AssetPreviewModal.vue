<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>素材预览</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body">
        <div v-if="asset" class="asset-preview">
          <!-- 图片预览 -->
          <div v-if="isImage" class="image-preview">
            <img :src="asset.content_url" :alt="asset.name" class="preview-image">
          </div>
          
          <!-- 视频预览 -->
          <div v-else-if="isVideo" class="video-preview">
            <video :src="asset.content_url" controls class="preview-video">
              您的浏览器不支持视频播放
            </video>
          </div>
          
          <!-- 文档预览 -->
          <div v-else-if="isDocument" class="document-preview">
            <div class="document-icon">
              <i class="file-icon">📄</i>
            </div>
            <p class="document-name">{{ asset.name }}</p>
            <p class="document-type">{{ getFileType(asset.content_url) }}</p>
            <a :href="asset.content_url" target="_blank" class="download-btn">
              下载文件
            </a>
          </div>
          
          <!-- 其他文件预览 -->
          <div v-else class="other-preview">
            <div class="file-icon">
              <i class="icon">📁</i>
            </div>
            <p class="file-name">{{ asset.name }}</p>
            <p class="file-type">{{ getFileType(asset.content_url) }}</p>
            <a :href="asset.content_url" target="_blank" class="download-btn">
              下载文件
            </a>
          </div>
          
          <!-- 素材信息 -->
          <div class="asset-info">
            <h4>素材信息</h4>
            <div class="info-grid">
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
        <button class="btn btn-primary" @click="editAsset">编辑</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetPreviewModal',
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
    },
    
    isDocument() {
      if (!this.asset.content_url) return false
      const docExts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
      return docExts.some(ext => this.asset.content_url.toLowerCase().includes(ext))
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    
    editAsset() {
      this.$emit('edit', this.asset)
    },
    
    getFileType(url) {
      if (!url) return '未知'
      const ext = url.split('.').pop()?.toLowerCase()
      const typeMap = {
        'jpg': 'JPEG图片',
        'jpeg': 'JPEG图片',
        'png': 'PNG图片',
        'gif': 'GIF图片',
        'webp': 'WebP图片',
        'svg': 'SVG图片',
        'mp4': 'MP4视频',
        'avi': 'AVI视频',
        'mov': 'MOV视频',
        'wmv': 'WMV视频',
        'flv': 'FLV视频',
        'webm': 'WebM视频',
        'pdf': 'PDF文档',
        'doc': 'Word文档',
        'docx': 'Word文档',
        'xls': 'Excel表格',
        'xlsx': 'Excel表格',
        'ppt': 'PowerPoint演示',
        'pptx': 'PowerPoint演示'
      }
      return typeMap[ext] || ext?.toUpperCase() + '文件'
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

.asset-preview {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-preview {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.video-preview {
  text-align: center;
}

.preview-video {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.document-preview,
.other-preview {
  text-align: center;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
}

.document-icon,
.file-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.document-name,
.file-name {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.document-type,
.file-type {
  color: #666;
  margin-bottom: 16px;
}

.download-btn {
  display: inline-block;
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
}

.asset-info h4 {
  margin: 0 0 16px 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
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

.tag {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
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
</style>
