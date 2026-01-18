<template>
  <div class="asset-editor-modal" @click="handleBackdropClick">
    <div class="modal-container" @click.stop>
      <!-- 头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          {{ isNew ? '创建素材' : '编辑素材' }}
        </h2>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>

      <!-- 内容 -->
      <div class="modal-body">
        <!-- 基础信息 -->
        <div class="form-section">
          <h3 class="section-title">基础信息</h3>
          
          <div class="form-group">
            <label class="form-label required">素材标题</label>
            <input
              v-model="localAsset.title"
              type="text"
              class="form-input"
              placeholder="请输入素材标题（将显示在卡片上）"
              maxlength="100"
            />
            <div class="form-hint">{{ localAsset.title.length }}/100</div>
          </div>

          <div class="form-group">
            <label class="form-label required">简介</label>
            <textarea
              v-model="localAsset.summary"
              class="form-textarea"
              placeholder="请输入素材简介（将显示在卡片预览中）"
              rows="3"
              maxlength="200"
            ></textarea>
            <div class="form-hint">{{ localAsset.summary.length }}/200</div>
          </div>

          <div class="form-group">
            <label class="form-label required">封面图</label>
            <div class="cover-upload">
              <div v-if="localAsset.cover" class="cover-preview">
                <img :src="localAsset.cover" alt="封面图" />
                <div class="cover-actions">
                  <button class="btn-cover-action" @click="triggerCoverUpload">
                    <i class="icon-camera"></i>
                    更换
                  </button>
                  <button class="btn-cover-action danger" @click="localAsset.cover = ''">
                    <i class="icon-delete"></i>
                    删除
                  </button>
                </div>
              </div>
              <button v-else class="btn-upload-cover" @click="triggerCoverUpload">
                <i class="icon-image"></i>
                <span>上传封面图</span>
                <div class="upload-hint">建议尺寸：16:9，支持JPG/PNG</div>
              </button>
              <input
                ref="coverInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleCoverUpload"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">标签</label>
            <div class="tags-input">
              <div class="tags-list">
                <span
                  v-for="(tag, index) in localAsset.tags"
                  :key="index"
                  class="tag-item"
                >
                  {{ tag }}
                  <i class="icon-close" @click="removeTag(index)"></i>
                </span>
                <input
                  v-model="newTag"
                  type="text"
                  class="tag-input"
                  placeholder="输入标签后按回车"
                  @keydown.enter.prevent="addTag"
                />
              </div>
            </div>
            <div class="form-hint">最多添加5个标签，用于分类和搜索</div>
          </div>
        </div>

        <!-- 详细内容 -->
        <div class="form-section">
          <h3 class="section-title">详细内容</h3>
          
          <div class="form-group">
            <label class="form-label required">富文本内容</label>
            <BlockEditor
              v-model="localAsset.blocks"
              :max-blocks="maxBlocks"
              :max-images="maxImages"
              @change="handleBlocksChange"
            />
            <div class="form-hint">支持文字、图片、数据亮点自由混排，可拖拽排序</div>
          </div>

          <div class="form-group">
            <label class="form-label">外部链接</label>
            <input
              v-model="localAsset.externalLink"
              type="url"
              class="form-input"
              placeholder="https://example.com（可选）"
            />
            <div class="form-hint">用户可点击"了解更多"跳转到此链接</div>
          </div>
        </div>

        <!-- 高级设置 -->
        <div class="form-section">
          <h3 class="section-title">高级设置</h3>
          
          <div class="form-group">
            <label class="form-label">亮点列数</label>
            <div class="columns-toggle">
              <button
                v-for="option in [2, 3]"
                :key="option"
                type="button"
                class="btn-column"
                :class="{ active: highlightColumns === option }"
                @click="setHighlightColumns(option)"
              >
                {{ option }} 列
              </button>
            </div>
            <div class="form-hint">桌面端默认 3 列，小屏会自动降级；保存后预览与分享同步生效。</div>
          </div>

          <div class="form-group">
            <label class="form-label">状态</label>
            <div class="radio-group">
              <label class="radio-item">
                <input
                  v-model="localAsset.status"
                  type="radio"
                  value="draft"
                  class="radio-input"
                />
                <span class="radio-label">
                  <i class="icon-draft"></i>
                  草稿
                </span>
                <span class="radio-desc">保存为草稿，不会在素材库中显示</span>
              </label>
              <label class="radio-item">
                <input
                  v-model="localAsset.status"
                  type="radio"
                  value="published"
                  class="radio-input"
                />
                <span class="radio-label">
                  <i class="icon-publish"></i>
                  发布
                </span>
                <span class="radio-desc">立即发布到素材库，员工可访问</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="checkbox-item">
              <input
                v-model="localAsset.allowShare"
                type="checkbox"
                class="checkbox-input"
              />
              <span class="checkbox-label">允许员工分享此素材</span>
            </label>
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">
          取消
        </button>
        <button class="btn-primary" @click="handleSave" :disabled="!isValid">
          {{ isNew ? '创建' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import BlockEditor from './form/BlockEditor.vue'
import uploadSecurityMixin from './config/upload-security-mixin'

export default {
  name: 'AssetEditorModal',
  
  components: {
    BlockEditor
  },
  
  mixins: [uploadSecurityMixin],
  
  props: {
    asset: {
      type: Object,
      default: null
    },
    isModal: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    const asset = this.asset || {}
    
    // ✅ 数据兼容层：旧数据转新格式
    let blocks = []
    if (asset.blocks && Array.isArray(asset.blocks)) {
      // 新格式：直接使用
      blocks = asset.blocks
    } else if (asset.metadata && asset.metadata.blocks) {
      // 从 metadata 中加载
      blocks = asset.metadata.blocks
    } else {
      // 旧格式转换
      blocks = this.convertLegacyData(asset)
    }
    
    // 获取套餐限制
    const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
    const limits = this.getPlanLimits(plan)
    
    return {
      localAsset: {
        id: asset.id || null,
        title: asset.title || '',
        summary: asset.summary || '',
        cover: asset.cover || '',
        blocks: blocks, // ✅ 新：使用 blocks 数组
        tags: asset.tags || [],
        externalLink: asset.externalLink || asset.metadata?.externalLink || '',
        status: asset.status || 'draft',
        allowShare: asset.allowShare !== false,
        // 保留旧字段用于向后兼容（保存时会同步）
        content: asset.content || '',
        detailImages: asset.detailImages || [],
        metadata: {
          ...(asset.metadata || {}),
          version: '2.0',
          highlightColumns: asset.metadata?.highlightColumns || 3
        }
      },
      newTag: '',
      scrollPosition: 0,
      maxBlocks: limits.maxBlocks,
      maxImages: limits.maxImages,
      highlightColumns: asset.metadata?.highlightColumns || 3
    }
  },
  
  computed: {
    isNew() {
      return !this.localAsset.id
    },
    
    isValid() {
      return (
        this.localAsset.title.trim() &&
        this.localAsset.summary.trim() &&
        this.localAsset.cover &&
        this.localAsset.blocks.length > 0
      )
    }
  },
  
  mounted() {
    // 只在作为弹窗模式时才锁定背景滚动
    // 如果有 isModal prop 且为 true，才锁定滚动
    if (this.isModal) {
      this.scrollPosition = window.pageYOffset
      document.body.style.overflow = 'hidden'
      document.body.style.position = 'fixed'
      document.body.style.top = `-${this.scrollPosition}px`
      document.body.style.width = '100%'
    }
  },
  
  beforeDestroy() {
    // 只在作为弹窗模式时才恢复滚动
    if (this.isModal) {
      document.body.style.removeProperty('overflow')
      document.body.style.removeProperty('position')
      document.body.style.removeProperty('top')
      document.body.style.removeProperty('width')
      window.scrollTo(0, this.scrollPosition || 0)
    }
  },
  
  methods: {
    // 实现 upload-security-mixin 要求的方法
    getImageCount() {
      return this.localAsset.blocks.filter(b => b.type === 'image').length
    },
    
    // 套餐限制配置（与名片系统保持一致）
    getPlanLimits(plan) {
      const limits = {
        free: { 
          maxBlocks: 10,      // 内容块总数
          maxImages: 5,       // 图片数量（对齐多媒体模块）
          maxHighlights: 3    // 数据亮点数量（对齐企业简介）
        },
        trial: { 
          maxBlocks: 15, 
          maxImages: 8,       // 对齐多媒体模块
          maxHighlights: 8 
        },
        pro: { 
          maxBlocks: 20, 
          maxImages: 10,      // 对齐多媒体模块
          maxHighlights: 10 
        },
        enterprise: { 
          maxBlocks: 30, 
          maxImages: 20,      // 对齐多媒体模块（20张）
          maxHighlights: 15   // 对齐企业简介
        }
      }
      return limits[plan] || limits.free
    },
    
    // 旧数据转新格式
    convertLegacyData(asset) {
      const blocks = []
      
      // 转换旧的 content 字段（文字）
      if (asset.content && asset.content.trim()) {
        blocks.push({
          id: `block-text-${Date.now()}`,
          type: 'text',
          content: asset.content
        })
      }
      
      // 转换旧的 detailImages 数组
      if (asset.detailImages && Array.isArray(asset.detailImages)) {
        asset.detailImages.forEach((img, index) => {
          blocks.push({
            id: `block-image-${Date.now()}-${index}`,
            type: 'image',
            src: img,
            caption: ''
          })
        })
      }
      
      return blocks
    },
    
    handleBackdropClick() {
      if (confirm('确定要关闭吗？未保存的更改将丢失。')) {
        this.$emit('close')
      }
    },
    
    handleBlocksChange() {
      // blocks 更新时，同步更新旧格式字段（向后兼容）
      this.syncLegacyFields()
    },
    
    syncLegacyFields() {
      // 同步 content 字段（仅包含文字块）
      const textBlocks = this.localAsset.blocks.filter(b => b.type === 'text')
      this.localAsset.content = textBlocks.map(b => b.content).join('\n\n')
      
      // 同步 detailImages 字段（仅包含图片块）
      const imageBlocks = this.localAsset.blocks.filter(b => b.type === 'image' && b.src)
      this.localAsset.detailImages = imageBlocks.map(b => b.src)
      if (this.localAsset.metadata) {
        this.localAsset.metadata.highlightColumns = this.highlightColumns
      }
    },
    
    setHighlightColumns(value) {
      this.highlightColumns = value
      if (!this.localAsset.metadata) {
        this.$set(this.localAsset, 'metadata', {})
      }
      this.$set(this.localAsset.metadata, 'highlightColumns', value)
    },
    
    handleSave() {
      if (!this.isValid) {
        this.$toast?.warning('请填写所有必填项')
        return
      }
      
      // 最后同步一次旧字段
      this.syncLegacyFields()
      
      // 构建 metadata
      const metadata = {
        ...(this.localAsset.metadata || {}),
        blocks: this.localAsset.blocks,
        externalLink: this.localAsset.externalLink,
        highlightColumns: this.highlightColumns,
        version: '2.0' // 标记为新版格式
      }
      
      this.$emit('save', {
        ...this.localAsset,
        metadata: metadata,
        updated_at: new Date().toISOString()
      })
    },
    
    triggerCoverUpload() {
      // ✅ 上传前安全检查
      if (!this.checkUploadLimit()) {
        return
      }
      this.$refs.coverInput.click()
    },
    
    async handleCoverUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 文件类型验证
      if (!file.type.startsWith('image/')) {
        this.$toast?.error('请上传图片文件')
        event.target.value = ''
        return
      }
      
      try {
        // ✅ 使用 ImageUpload 的压缩逻辑
        const compressedFile = await this.compressImage(file)
        
        // ✅ 上传到服务器
        const formData = new FormData()
        formData.append('file', compressedFile)
        formData.append('file_type', 'image')
        
        const token = await this.getAuthToken()
        const response = await this.$axios.post('/api/v1/files/upload', formData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (response.data.success) {
          this.localAsset.cover = response.data.url
          this.$toast?.success('封面上传成功')
        } else {
          throw new Error(response.data.error || '上传失败')
        }
      } catch (error) {
        console.error('封面上传失败:', error)
        this.$toast?.error(error.response?.data?.error || '封面上传失败')
      } finally {
        event.target.value = ''
      }
    },
    
    // ✅ 封装上传限制检查（调用mixin方法）
    checkUploadLimit() {
      const check = this.quickSecurityCheck()  // ✅ 修复：调用无参数版本
      
      if (!check.allowed) {
        if (check.reason === 'frequency') {
          this.$toast?.error(`上传过于频繁，请${check.waitTime}秒后再试`)
        } else if (check.reason === 'quota') {
          this.$toast?.error(check.message)
        } else {
          this.$toast?.error(check.message || '暂时无法上传')
        }
        return false
      }
      
      return true
    },
    
    // ✅ 复用 ImageUpload 的压缩逻辑
    async compressImage(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = new Image()
          img.onload = () => {
            const MAX_WIDTH = 1200
            let width = img.width
            let height = img.height
            
            if (width > MAX_WIDTH) {
              height = Math.round((height * MAX_WIDTH) / width)
              width = MAX_WIDTH
            }
            
            const canvas = document.createElement('canvas')
            canvas.width = width
            canvas.height = height
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)
            
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
    
    addTag() {
      const tag = this.newTag.trim()
      if (!tag) return
      
      if (this.localAsset.tags.length >= 5) {
        this.$toast?.warning('最多添加5个标签')
        return
      }
      
      if (this.localAsset.tags.includes(tag)) {
        this.$toast?.warning('标签已存在')
        return
      }
      
      this.localAsset.tags.push(tag)
      this.newTag = ''
    },
    
    removeTag(index) {
      this.localAsset.tags.splice(index, 1)
    },

    async getAuthToken() {
      if (this.$wecomAuth?.getToken) {
        const token = this.$wecomAuth.getToken()
        if (token) return token
      }

      const storeToken = this.$store?.state?.auth?.token
      if (storeToken) {
        return storeToken
      }

      throw new Error('未找到认证token')
    }
  }
}
</script>

<style lang="scss" scoped>
.asset-editor-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.modal-container {
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  background: white;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #262626;
  margin: 0;
}

.btn-close {
  width: 36px;
  height: 36px;
  background: #f5f5f5;
  border: none;
  border-radius: 50%;
  font-size: 24px;
  color: #8c8c8c;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e8e8e8;
    color: #262626;
    transform: rotate(90deg);
  }
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #595959;
  margin-bottom: 8px;
  
  &.required::after {
    content: '*';
    color: #ff4d4f;
    margin-left: 4px;
  }
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.6;
  
  &.large {
    min-height: 200px;
  }
}

.form-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #8c8c8c;
}

.columns-toggle {
  display: inline-flex;
  gap: 8px;
}

.btn-column {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #d9d9d9;
  background: #ffffff;
  color: #595959;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-column.active {
  border-color: transparent;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
}

.btn-column:not(.active):hover {
  border-color: #667eea;
  color: #667eea;
}

/* 封面上传 */
.cover-upload {
  margin-top: 8px;
}

.cover-preview {
  position: relative;
  width: 100%;
  max-width: 400px;
  aspect-ratio: 16/9;
  border-radius: 12px;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .cover-actions {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 12px;
    background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
    display: flex;
    gap: 8px;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover .cover-actions {
    opacity: 1;
  }
}

.btn-cover-action {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
  }
  
  &.danger {
    background: #ff4d4f;
    color: white;
  }
}

.btn-upload-cover {
  width: 100%;
  max-width: 400px;
  aspect-ratio: 16/9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #f8f9ff;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f0f4ff;
  }
  
  i {
    font-size: 32px;
    color: #667eea;
  }
  
  span {
    font-size: 14px;
    font-weight: 600;
    color: #595959;
  }
  
  .upload-hint {
    font-size: 12px;
    color: #8c8c8c;
  }
}

/* 标签输入 */
.tags-input {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 8px;
  transition: all 0.3s ease;
  
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #f0f2ff 0%, #e6f0ff 100%);
  color: #667eea;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  
  i {
    cursor: pointer;
    transition: transform 0.2s ease;
    
    &:hover {
      transform: scale(1.2);
    }
  }
}

.tag-input {
  flex: 1;
  min-width: 120px;
  border: none;
  outline: none;
  font-size: 14px;
  padding: 4px;
}

/* BlockEditor 集成后，这些样式已移除 */

/* 单选框组 */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f8f9ff;
  }
  
  .radio-input {
    margin-top: 2px;
    cursor: pointer;
  }
  
  .radio-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #262626;
  }
  
  .radio-desc {
    flex: 1;
    font-size: 13px;
    color: #8c8c8c;
    margin-left: 32px;
  }
}

.radio-input:checked + .radio-label {
  color: #667eea;
}

/* 复选框 */
.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  
  .checkbox-input {
    cursor: pointer;
  }
  
  .checkbox-label {
    font-size: 14px;
    color: #595959;
  }
}

/* 底部操作 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #f0f0f0;
}

.btn-secondary,
.btn-primary {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: white;
  border: 1px solid #d9d9d9;
  color: #595959;
  
  &:hover {
    border-color: #667eea;
    color: #667eea;
  }
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .modal-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>

