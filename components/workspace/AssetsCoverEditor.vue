<template>
  <div class="assets-cover-editor">
    <!-- 说明信息 -->
    <div class="editor-notice">
      <i class="icon-info">ℹ️</i>
      <div class="notice-content">
        <strong>分享封面生成</strong>
        <p>为每个素材生成分享封面和标题，用于推送到企业微信或生成独立分享链接</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载素材列表中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!assets.length" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>还没有素材</h3>
      <p>请先在"素材内容生成"标签页创建素材</p>
      <button class="btn-primary" @click="$emit('go-to-content')">
        <i class="icon-plus"></i>
        去创建素材
      </button>
    </div>

    <!-- 素材列表 -->
    <div v-else class="assets-list">
      <!-- 批量操作提示 -->
      <div v-if="selectedAssets.length > 0" class="batch-notice">
        <div class="batch-info">
          <i class="icon-check">✓</i>
          <span>已选择 {{ selectedAssets.length }} 个素材</span>
        </div>
        <div class="batch-actions">
          <button class="btn-batch" @click="batchGenerateCovers" :disabled="generating">
            {{ generating ? '生成中...' : '批量生成封面' }}
          </button>
          <button class="btn-text" @click="clearSelection">取消选择</button>
        </div>
      </div>

      <!-- 素材卡片 -->
      <div class="asset-cards">
        <div
          v-for="asset in assets"
          :key="asset.id"
          class="asset-card"
          :class="{ selected: isSelected(asset.id) }"
        >
          <!-- 选择框 -->
          <div class="card-checkbox">
            <input
              type="checkbox"
              :checked="isSelected(asset.id)"
              @change="toggleSelection(asset.id)"
            />
          </div>

          <!-- 卡片内容 -->
          <div class="card-body">
            <!-- 当前封面 -->
            <div class="cover-section">
              <div v-if="asset.cover" class="cover-preview">
                <img :src="asset.cover" :alt="asset.title" />
              </div>
              <div v-else class="cover-placeholder">
                <i class="icon-image">🖼</i>
                <span>暂无封面</span>
              </div>
            </div>

            <!-- 素材信息 -->
            <div class="asset-info">
              <h3 class="asset-title">{{ asset.title }}</h3>
              <p class="asset-summary">{{ asset.summary }}</p>
              
              <!-- 分享链接 -->
              <div class="share-link-section">
                <label class="link-label">分享链接</label>
                <div class="link-input-group">
                  <input
                    type="text"
                    :value="getShareUrl(asset.id)"
                    readonly
                    class="link-input"
                  />
                  <button class="btn-copy" @click="copyShareUrl(asset.id)">
                    <i class="icon-copy">📋</i>
                  </button>
                </div>
              </div>

              <!-- 分享标题 -->
              <div class="share-title-section">
                <label class="link-label">分享标题</label>
                <input
                  v-model="asset.shareTitle"
                  type="text"
                  class="title-input"
                  placeholder="自定义分享标题（留空则使用素材标题）"
                  maxlength="50"
                  @input="updateShareTitle(asset.id, asset.shareTitle)"
                />
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="card-actions">
            <button
              class="btn-action btn-upload"
              @click="openCoverUpload(asset.id)"
              title="上传新封面"
            >
              <i class="icon-upload">⬆️</i>
              上传封面
            </button>
            <button
              class="btn-action btn-generate"
              @click="generateCover(asset.id)"
              :disabled="generating"
              title="自动生成封面"
            >
              <i class="icon-magic">✨</i>
              生成封面
            </button>
            <button
              class="btn-action btn-preview"
              @click="previewAsset(asset.id)"
              title="预览分享效果"
            >
              <i class="icon-eye">👁️</i>
              预览
            </button>
          </div>

          <!-- 隐藏的文件输入 -->
          <input
            :ref="`coverInput-${asset.id}`"
            type="file"
            accept="image/*"
            class="hidden-input"
            @change="handleCoverUpload($event, asset.id)"
          />
        </div>
      </div>
    </div>

    <!-- 频率/配额提示对话框 -->
    <div v-if="showLimitWarning" class="modal-overlay" @click="showLimitWarning = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>⚠️ 操作限制提示</h3>
          <button class="modal-close" @click="showLimitWarning = false">×</button>
        </div>
        <div class="modal-body">
          <p>{{ limitWarningMessage }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showLimitWarning = false">我知道了</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import uploadSecurityMixin from '@/components/workspace/config/upload-security-mixin'

export default {
  name: 'AssetsCoverEditor',

  mixins: [uploadSecurityMixin],

  data() {
    return {
      assets: [],
      loading: false,
      generating: false,
      selectedAssets: [],
      showLimitWarning: false,
      limitWarningMessage: '',
      uploadThrottle: null,
      // 场景6: 批量操作防抖
      batchOperationLock: false,
      lastBatchTime: 0
    }
  },

  computed: {
    baseUrl() {
      return process.client ? window.location.origin : 'https://zjemail.cn'
    },
    
    tenantId() {
      // ✅ 从 workspace store 获取 tenantId
      return this.$store.state.workspace?.tenantInfo?.id || null
    }
  },

  mounted() {
    this.loadAssets()
  },

  methods: {
    async loadAssets() {
      this.loading = true
      try {
        const token = this.$wecomAuth?.getToken() || this.$store.state.auth?.token
        if (!token) {
          throw new Error('未登录')
        }

        const response = await this.$axios.get('/api/tenant/assets', {
          headers: { 'Authorization': `Bearer ${token}` },
          params: { status: 'all', limit: 100 }
        })

        if (response.data && response.data.success) {
          this.assets = (response.data.assets || []).map(asset => ({
            ...asset,
            shareTitle: asset.shareTitle || asset.title
          }))
        }
      } catch (error) {
        console.error('加载素材失败:', error)
        this.$toast?.error('加载素材失败')
      } finally {
        this.loading = false
      }
    },

    getShareUrl(assetId) {
      // ✅ 统一使用锚点方式：/assets/{tenantId}#asset-{assetId}
      if (!this.tenantId) {
        console.warn('⚠️ 无法获取 tenantId，使用默认格式')
        return `${this.baseUrl}/assets/${assetId}`
      }
      return `${this.baseUrl}/assets/${this.tenantId}#asset-${assetId}`
    },

    copyShareUrl(assetId) {
      const url = this.getShareUrl(assetId)
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url)
          .then(() => this.$toast?.success('链接已复制'))
          .catch(() => this.$toast?.error('复制失败'))
      }
    },

    async updateShareTitle(assetId, title) {
      // 节流保存
      if (this.saveThrottle) {
        clearTimeout(this.saveThrottle)
      }

      this.saveThrottle = setTimeout(async () => {
        try {
          const token = this.$wecomAuth?.getToken() || this.$store.state.auth?.token
          await this.$axios.patch(
            `/api/tenant/assets/${assetId}`,
            { shareTitle: title },
            { headers: { 'Authorization': `Bearer ${token}` } }
          )
        } catch (error) {
          console.error('保存分享标题失败:', error)
        }
      }, 1000)
    },

    // 选择管理
    isSelected(assetId) {
      return this.selectedAssets.includes(assetId)
    },

    toggleSelection(assetId) {
      const index = this.selectedAssets.indexOf(assetId)
      if (index > -1) {
        this.selectedAssets.splice(index, 1)
      } else {
        this.selectedAssets.push(assetId)
      }
    },

    clearSelection() {
      this.selectedAssets = []
    },

    // 封面上传
    openCoverUpload(assetId) {
      const input = this.$refs[`coverInput-${assetId}`]
      if (input && input[0]) {
        input[0].click()
      }
    },

    async handleCoverUpload(event, assetId) {
      const file = event.target.files?.[0]
      if (!file) return

      // 安全检查
      const securityCheck = this.quickSecurityCheck()
      if (!securityCheck.allowed) {
        if (securityCheck.reason === 'frequency') {
          this.showWarning(`上传过于频繁，请等待 ${securityCheck.waitTime} 秒后再试`)
        } else if (securityCheck.reason === 'quota') {
          this.showWarning(securityCheck.message || '已达图片上限')
        }
        event.target.value = ''
        return
      }

      try {
        // 压缩
        const compressedFile = await this.compressImage(file)
        
        // 上传
        const formData = new FormData()
        formData.append('file', compressedFile)

        const token = this.$wecomAuth?.getToken() || this.$store.state.auth?.token
        if (!token) {
          this.showWarning('登录已过期，请刷新页面重新登录')
          event.target.value = ''
          return
        }

        const response = await this.$axios.post('/api/v1/files/upload', formData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data && response.data.url) {
          // 更新封面
          await this.$axios.patch(
            `/api/tenant/assets/${assetId}`,
            { cover: response.data.url },
            { headers: { 'Authorization': `Bearer ${token}` } }
          )

          // 更新本地
          const asset = this.assets.find(a => a.id === assetId)
          if (asset) {
            asset.cover = response.data.url
          }

          this.$toast?.success('封面上传成功')
        }
      } catch (error) {
        console.error('上传失败:', error)
        let errorMsg = '上传失败'
        
        if (error.response?.status === 401) {
          errorMsg = 'Token已失效，请刷新页面'
        } else if (error.response?.status === 429) {
          errorMsg = '上传过于频繁，请稍后再试'
        } else if (error.response?.data?.error) {
          errorMsg = error.response.data.error
        }
        
        this.showWarning(errorMsg)
      }

      event.target.value = ''
    },

    async compressImage(file) {
      if (file.size <= 500 * 1024) return file

      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = new Image()
          img.onload = () => {
            const canvas = document.createElement('canvas')
            let width = img.width
            let height = img.height

            if (width > 1200) {
              height = (height * 1200) / width
              width = 1200
            }

            canvas.width = width
            canvas.height = height
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)

            canvas.toBlob(
              (blob) => blob ? resolve(new File([blob], file.name, { type: 'image/jpeg' })) : reject(new Error('压缩失败')),
              'image/jpeg',
              0.75
            )
          }
          img.onerror = () => reject(new Error('图片加载失败'))
          img.src = e.target.result
        }
        reader.onerror = () => reject(new Error('文件读取失败'))
        reader.readAsDataURL(file)
      })
    },

    // 生成封面
    async generateCover(assetId) {
      this.$toast?.info('自动生成封面功能开发中')
      // TODO: 实现自动生成封面逻辑
    },

    // 场景6: 批量生成封面（增强防抖和错误处理）
    async batchGenerateCovers() {
      if (this.selectedAssets.length === 0) return

      // 防抖检查 - 防止快速连续点击
      const now = Date.now()
      if (this.batchOperationLock) {
        this.showWarning('操作进行中，请稍候...')
        return
      }

      if (now - this.lastBatchTime < 5000) {
        const waitTime = Math.ceil((5000 - (now - this.lastBatchTime)) / 1000)
        this.showWarning(`批量操作过于频繁，请等待 ${waitTime} 秒后再试`)
        return
      }

      // 数量检查
      if (this.selectedAssets.length > 5) {
        this.showWarning('为避免触发频率限制，建议每次批量操作不超过5个素材')
        return
      }

      // 加锁
      this.batchOperationLock = true
      this.generating = true
      this.lastBatchTime = now
      
      let successCount = 0
      let failCount = 0
      const errors = []

      try {
        for (let i = 0; i < this.selectedAssets.length; i++) {
          const assetId = this.selectedAssets[i]
          
          try {
            await this.generateCover(assetId)
            successCount++
            
            // 延迟2秒避免频率限制（最后一个不需要延迟）
            if (i < this.selectedAssets.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 2000))
            }
          } catch (error) {
            failCount++
            errors.push({ assetId, error: error.message })
            console.error(`生成封面失败 (${assetId}):`, error)
            
            // 场景6: 429错误特殊处理
            if (error.response?.status === 429) {
              this.showWarning('触发频率限制，已停止批量操作')
              break // 立即停止
            }
          }
        }
      } finally {
        // 解锁
        this.batchOperationLock = false
        this.generating = false
        this.clearSelection()
      }

      // 结果提示
      if (failCount === 0) {
        this.$toast?.success(`✅ 成功生成 ${successCount} 个封面`)
      } else if (successCount === 0) {
        this.$toast?.error(`❌ 全部失败，请检查网络或稍后重试`)
      } else {
        this.$toast?.warning(`⚠️ 成功 ${successCount} 个，失败 ${failCount} 个`)
        // 详细错误日志
        if (errors.length > 0) {
          console.error('批量操作错误详情:', errors)
        }
      }
    },

    // 预览
    previewAsset(assetId) {
      this.$emit('preview-asset', assetId)
    },

    showWarning(message) {
      this.limitWarningMessage = message
      this.showLimitWarning = true
    },

    getImageCount() {
      return this.assets.filter(a => a.cover).length
    }
  }
}
</script>

<style lang="scss" scoped>
.assets-cover-editor {
  padding: 20px;
}

.editor-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #fff4e6 0%, #fffbe6 100%);
  border: 1px solid #ffc069;
  border-radius: 12px;
  color: #d46b08;

  .icon-info {
    font-size: 20px;
    flex-shrink: 0;
  }

  .notice-content {
    strong {
      display: block;
      margin-bottom: 4px;
      font-size: 14px;
    }

    p {
      margin: 0;
      font-size: 13px;
      line-height: 1.6;
    }
  }
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #262626;
}

.empty-state p {
  margin: 0 0 24px;
  font-size: 14px;
  color: #8c8c8c;
}

.batch-notice {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  margin-bottom: 20px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 12px;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #0050b3;
  font-weight: 600;
}

.batch-actions {
  display: flex;
  gap: 12px;
}

.btn-batch {
  padding: 8px 16px;
  background: #1890ff;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.asset-cards {
  display: grid;
  gap: 20px;
}

.asset-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 16px;
  padding: 20px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;

  &.selected {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  }
}

.card-checkbox {
  display: flex;
  align-items: center;

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
}

.card-body {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 20px;
}

.cover-section {
  .cover-preview img {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 8px;
  }

  .cover-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    aspect-ratio: 16 / 9;
    background: #f5f5f5;
    border: 2px dashed #d9d9d9;
    border-radius: 8px;
    color: #8c8c8c;
    font-size: 12px;

    .icon-image {
      font-size: 32px;
      margin-bottom: 8px;
    }
  }
}

.asset-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.asset-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.asset-summary {
  margin: 0;
  font-size: 13px;
  color: #595959;
  line-height: 1.6;
}

.share-link-section,
.share-title-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.link-label {
  font-size: 12px;
  font-weight: 600;
  color: #8c8c8c;
}

.link-input-group {
  display: flex;
  gap: 8px;
}

.link-input,
.title-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 13px;
  color: #262626;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
}

.btn-copy {
  padding: 8px 12px;
  background: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #e8e8e8;
  }
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  background: #ffffff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover:not(:disabled) {
    border-color: #667eea;
    color: #667eea;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-primary,
.btn-secondary,
.btn-text {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border: none;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.35);
  }
}

.btn-secondary {
  background: #f5f5ff;
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);

  &:hover {
    background: #ebebff;
  }
}

.btn-text {
  background: transparent;
  border: none;
  color: #595959;

  &:hover {
    color: #262626;
  }
}

.hidden-input {
  display: none;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  min-width: 400px;
  max-width: 500px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;

  h3 {
    margin: 0;
    font-size: 16px;
    color: #262626;
  }
}

.modal-close {
  padding: 0;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  font-size: 24px;
  color: #8c8c8c;
  cursor: pointer;

  &:hover {
    color: #262626;
  }
}

.modal-body {
  padding: 24px;

  p {
    margin: 0;
    line-height: 1.6;
    color: #595959;
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .card-body {
    grid-template-columns: 1fr;
  }

  .asset-card {
    grid-template-columns: auto 1fr;
  }

  .card-actions {
    grid-column: span 2;
  }
}
</style>

