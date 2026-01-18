<template>
  <div class="assets-content-editor">
    <!-- 全屏编辑器布局（无右侧预览） -->
    <div class="editor-container">
      <!-- 提示信息 -->
      <div class="editor-notice">
        <i class="icon-info">ℹ️</i>
        <span>编辑后的内容会实时同步到右侧预览区，保存后才会永久生效</span>
      </div>

      <!-- 基础信息 -->
      <section class="module-container">
        <div class="section-header">
          <h2 class="section-title">基础信息</h2>
          <p class="section-subtitle">标题、简介与封面决定首屏点击效果</p>
        </div>
        <div class="module-body">
          <div class="form-grid form-grid-two">
            <div class="form-group">
              <label class="form-label required">素材标题</label>
              <input
                v-model="localAsset.title"
                type="text"
                class="form-input"
                placeholder="请输入素材标题"
                maxlength="100"
                @input="syncToStore"
              />
              <span class="form-hint">{{ localAsset.title.length }}/100</span>
            </div>
            <div class="form-group">
              <label class="form-label required">简介</label>
              <textarea
                v-model="localAsset.summary"
                class="form-textarea"
                rows="4"
                maxlength="200"
                placeholder="简要说明素材核心价值"
                @input="syncToStore"
              ></textarea>
              <span class="form-hint">{{ localAsset.summary.length }}/200</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">标签</label>
            <div class="tags-input">
              <div class="tags-list">
                <span
                  v-for="(tag, index) in localAsset.tags"
                  :key="`${tag}-${index}`"
                  class="tag-chip"
                >
                  {{ tag }}
                  <button type="button" class="tag-remove" @click="removeTag(index)">×</button>
                </span>
              </div>
              <div class="tag-input-wrapper">
                <input
                  v-model="newTag"
                  type="text"
                  class="tag-input"
                  placeholder="输入标签后按回车添加"
                  maxlength="20"
                  @keydown.enter.prevent="addTag"
                />
                <span class="form-hint">{{ localAsset.tags.length }}/10 个标签</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label required">封面图</label>
            <div class="cover-upload">
              <div v-if="!localAsset.cover" class="cover-placeholder" @click="$refs.coverInput.click()">
                <span class="placeholder-icon">🖼</span>
                <span class="placeholder-title">上传封面图</span>
                <span class="placeholder-desc">支持 JPG/PNG，自动压缩至 500KB</span>
              </div>
              <div v-else class="cover-preview">
                <div class="image-wrapper">
                  <img :src="localAsset.cover" alt="封面" class="module-image" />
                </div>
                <div class="cover-actions">
                  <button type="button" class="btn-secondary" @click="$refs.coverInput.click()">
                    更换封面
                  </button>
                  <button type="button" class="btn-text danger" @click="removeCover">
                    删除封面
                  </button>
                </div>
              </div>
              <input ref="coverInput" type="file" accept="image/*" class="hidden-input" @change="handleCoverUpload" />
            </div>
            <ul class="cover-tips">
              <li>推荐尺寸 1600 × 900，保持关键信息居中</li>
              <li>会同步用于右侧预览与分享卡片</li>
              <li>上传过于频繁会触发安全限制</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 内容块 -->
      <section class="module-container">
        <div class="section-header">
          <h2 class="section-title">图文内容</h2>
          <p class="section-subtitle">文字与图片可自由组合，自动遵循模块排版规范</p>
        </div>
        <div class="module-body">
          <BlockEditor
            v-model="localAsset.blocks"
            :max-blocks="maxBlocks"
            :max-images="maxImages"
            @change="handleBlocksChange"
          />
        </div>
      </section>

      <!-- 企业亮点 -->
      <section class="module-container">
        <div class="section-header">
          <h2 class="section-title">企业亮点</h2>
          <p class="section-subtitle">图标 + 文案排布，参考名片资质模块</p>
        </div>
        <div class="module-body">
          <div class="form-group">
            <label class="form-label">列数</label>
            <div class="columns-toggle">
              <button
                v-for="option in columnOptions"
                :key="option"
                type="button"
                class="btn-column"
                :class="{ active: highlightColumns === option }"
                @click="setHighlightColumns(option)"
              >
                {{ option }} 列
              </button>
            </div>
            <span class="form-hint">桌面端默认 3 列，小屏会自适应降级</span>
          </div>
          <p class="form-note">亮点内容在上方图文编辑器中以"亮点块"形式维护，预览自动匹配列数</p>
        </div>
      </section>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="resetDraft" :disabled="saving">
          重置内容
        </button>
        <button type="button" class="btn-primary" @click="saveAsset" :disabled="!isValid || saving">
          {{ saving ? '保存中...' : isNew ? '创建素材' : '保存修改' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import BlockEditor from '@/components/workspace/form/BlockEditor.vue'
import uploadSecurityMixin from '@/components/workspace/config/upload-security-mixin'

const DEFAULT_ASSET = () => ({
  id: null,
  title: '',
  summary: '',
  cover: '',
  blocks: [],
  tags: [],
  externalLink: '',
  status: 'draft',
  allowShare: true,
  metadata: {
    version: '2.0',
    highlightColumns: 3
  }
})

export default {
  name: 'AssetsContentEditor',

  components: {
    BlockEditor
  },

  mixins: [uploadSecurityMixin],

  data() {
    const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
    const limits = this.getPlanLimits(plan)
    
    // 从Vuex获取草稿或初始化（安全访问）
    let draft = null
    try {
      draft = this.$store.state.assetEditor?.draftAsset
    } catch (e) {
      console.warn('⚠️ assetEditor模块未注册，使用本地状态')
    }
    const initial = draft ? this.normalizeAsset(draft) : DEFAULT_ASSET()

    return {
      localAsset: initial,
      newTag: '',
      maxBlocks: limits.maxBlocks,
      maxImages: limits.maxImages,
      highlightColumns: initial.metadata?.highlightColumns || 3,
      saving: false,
      columnOptions: [2, 3],
      uploadError: null
    }
  },

  computed: {
    // 安全地访问Vuex - 防止模块未注册
    draftAsset() {
      return this.$store.state.assetEditor?.draftAsset || null
    },
    editMode() {
      return this.$store.state.assetEditor?.editMode || 'create'
    },
    isCreating() {
      return this.editMode === 'create'
    },
    isEditing() {
      return this.editMode === 'edit'
    },

    isNew() {
      return !this.localAsset.id || this.isCreating
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

  watch: {
    // 监听Vuex中的草稿变化
    draftAsset: {
      deep: true,
      handler(newValue) {
        if (newValue && JSON.stringify(newValue) !== JSON.stringify(this.localAsset)) {
          this.localAsset = this.normalizeAsset(newValue)
          this.highlightColumns = this.localAsset.metadata?.highlightColumns || 3
        }
      }
    }
  },

  mounted() {
    // ✅ 安全初始化：只在组件可见且 store 可用时才创建草稿
    this.$nextTick(() => {
      try {
        // 检查组件是否可见
        if (this.$el && this.$el.offsetParent !== null) {
          // 检查 store 是否可用
          if (this.$store.state.assetEditor) {
            if (!this.draftAsset) {
              this.startCreate()
            }
          } else {
            console.warn('⚠️ assetEditor store 未注册，使用本地状态')
          }
        }
      } catch (e) {
        console.warn('⚠️ 素材编辑器初始化失败:', e.message)
      }
    })
  },

  methods: {
    // 安全地调用Vuex actions
    startCreate() {
      try {
        this.$store.dispatch('assetEditor/startCreate')
      } catch (e) {
        console.warn('⚠️ Vuex action调用失败，使用本地状态')
      }
    },
    startEdit(asset) {
      try {
        this.$store.dispatch('assetEditor/startEdit', asset)
      } catch (e) {
        console.warn('⚠️ Vuex action调用失败')
      }
    },
    updateDraft(asset) {
      try {
        this.$store.dispatch('assetEditor/updateDraft', asset)
      } catch (e) {
        console.warn('⚠️ Vuex更新失败，仅本地保存')
      }
    },
    markSaved() {
      try {
        this.$store.dispatch('assetEditor/markSaved')
      } catch (e) {
        console.warn('⚠️ Vuex标记失败')
      }
    },
    cancelEdit() {
      try {
        this.$store.dispatch('assetEditor/cancelEdit')
      } catch (e) {
        console.warn('⚠️ Vuex取消失败')
      }
    },

    // 同步到Vuex store（实时同步到右侧预览）
    syncToStore() {
      this.updateDraft(this.localAsset)
    },

    normalizeAsset(asset) {
      // 防御性深拷贝
      let normalized
      try {
        normalized = JSON.parse(JSON.stringify({ ...DEFAULT_ASSET(), ...asset }))
      } catch (e) {
        console.error('⚠️ 资产数据解析失败:', e)
        normalized = { ...DEFAULT_ASSET() }
      }

      // 场景5: metadata vs meta_data 字段冲突处理
      // API可能返回meta_data，前端统一转为metadata
      if (!normalized.metadata && normalized.meta_data) {
        normalized.metadata = normalized.meta_data
      }

      // 确保metadata存在
      if (!normalized.metadata || typeof normalized.metadata !== 'object') {
        normalized.metadata = {
          version: '2.0',
          highlightColumns: 3
        }
      }

      // 场景4: 旧数据兼容 - legacy字段转换
      // 优先级：blocks > metadata.blocks > legacy转换
      if (!normalized.blocks || !Array.isArray(normalized.blocks) || normalized.blocks.length === 0) {
        // 尝试从metadata.blocks获取
        if (normalized.metadata?.blocks && Array.isArray(normalized.metadata.blocks) && normalized.metadata.blocks.length > 0) {
          normalized.blocks = normalized.metadata.blocks
        }
        // 如果还是空，尝试从legacy字段转换
        else if (normalized.content || (normalized.detailImages && normalized.detailImages.length > 0)) {
          console.log('⚠️ 检测到旧数据格式，自动转换...')
          normalized.blocks = this.convertLegacyData(normalized)
        }
        // 最后确保至少是空数组
        else {
          normalized.blocks = []
        }
      }

      // 确保highlightColumns存在且合法
      if (!normalized.metadata.highlightColumns || ![2, 3].includes(normalized.metadata.highlightColumns)) {
        normalized.metadata.highlightColumns = 3
      }

      // 确保version存在
      if (!normalized.metadata.version) {
        normalized.metadata.version = '2.0'
      }

      return normalized
    },

    // 场景4: 增强的legacy数据转换
    convertLegacyData(asset) {
      const blocks = []
      
      try {
        // 转换content字段为text块
        if (asset.content && typeof asset.content === 'string' && asset.content.trim()) {
          blocks.push({
            id: `block-text-${Date.now()}`,
            type: 'text',
            content: asset.content.trim()
          })
        }

        // 转换detailImages数组为image块
        if (Array.isArray(asset.detailImages) && asset.detailImages.length > 0) {
          asset.detailImages.forEach((img, index) => {
            if (img && typeof img === 'string') {
              blocks.push({
                id: `block-image-${Date.now()}-${index}`,
                type: 'image',
                src: img,
                caption: ''
              })
            }
          })
        }

        console.log(`✅ 成功转换 ${blocks.length} 个legacy块`)
      } catch (e) {
        console.error('⚠️ Legacy数据转换失败:', e)
      }

      return blocks
    },

    setHighlightColumns(value) {
      this.highlightColumns = value
      this.localAsset.metadata = {
        ...(this.localAsset.metadata || {}),
        highlightColumns: value
      }
      this.syncToStore()
    },

    handleBlocksChange(blocks) {
      // BlockEditor会更新localAsset.blocks
      // 确保 blocks 数组正确更新到 localAsset
      if (Array.isArray(blocks)) {
        this.localAsset.blocks = blocks
      }
      this.syncToStore()
    },

    getPlanLimits(plan) {
      const limits = {
        free: { maxBlocks: 10, maxImages: 5 },
        trial: { maxBlocks: 15, maxImages: 8 },
        pro: { maxBlocks: 20, maxImages: 10 },
        enterprise: { maxBlocks: 30, maxImages: 20 }
      }
      return limits[plan] || limits.free
    },

    // 标签管理
    addTag() {
      const tag = this.newTag.trim()
      if (!tag) return
      if (this.localAsset.tags.length >= 10) {
        this.$toast?.warning('最多添加10个标签')
        return
      }
      if (this.localAsset.tags.includes(tag)) {
        this.$toast?.warning('标签已存在')
        return
      }
      this.localAsset.tags.push(tag)
      this.newTag = ''
      this.syncToStore()
    },

    removeTag(index) {
      this.localAsset.tags.splice(index, 1)
      this.syncToStore()
    },

    // 封面上传
    async handleCoverUpload(event) {
      const file = event.target.files?.[0]
      if (!file) return

      // 安全检查
      const securityCheck = this.quickSecurityCheck()
      if (!securityCheck.allowed) {
        if (securityCheck.reason === 'frequency') {
          this.$toast?.error(`上传过于频繁，请等待 ${securityCheck.waitTime} 秒后再试`)
        } else if (securityCheck.reason === 'quota') {
          this.$toast?.error(securityCheck.message || '已达图片上限')
        }
        event.target.value = ''
        return
      }

      try {
        // 压缩图片
        const compressedFile = await this.compressImage(file)
        
        // 上传到服务器
        const formData = new FormData()
        formData.append('file', compressedFile)

        const token = this.$wecomAuth?.getToken() || this.$store.state.auth?.token
        if (!token) {
          this.$toast?.error('登录已过期，请刷新页面重新登录')
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
          this.localAsset.cover = response.data.url
          this.syncToStore()
          this.$toast?.success('封面上传成功')
        } else {
          throw new Error('上传返回数据格式错误')
        }
      } catch (error) {
        console.error('封面上传失败:', error)
        let errorMsg = '封面上传失败'
        
        if (error.response?.status === 401) {
          errorMsg = 'Token已失效，请刷新页面重新登录'
        } else if (error.response?.status === 429) {
          errorMsg = '上传过于频繁，请稍后再试'
        } else if (error.response?.status === 413) {
          errorMsg = '图片过大，请选择更小的图片'
        } else if (error.response?.data?.error) {
          errorMsg = error.response.data.error
        }
        
        this.$toast?.error(errorMsg)
      }

      event.target.value = ''
    },

    async compressImage(file) {
      if (file.size <= 500 * 1024) {
        return file
      }

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
              (blob) => {
                if (blob) {
                  resolve(new File([blob], file.name, { type: 'image/jpeg' }))
                } else {
                  reject(new Error('压缩失败'))
                }
              },
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

    removeCover() {
      this.localAsset.cover = ''
      this.syncToStore()
    },

    // 重置草稿
    resetDraft() {
      if (!confirm('确定重置？未保存的内容将丢失')) {
        return
      }
      this.localAsset = DEFAULT_ASSET()
      this.highlightColumns = 3
      this.startCreate()
      this.$toast?.info('已重置')
    },

    // 保存素材
    async saveAsset() {
      if (!this.isValid) {
        this.$toast?.warning('请填写完整信息')
        return
      }

      this.saving = true

      try {
        const token = this.$wecomAuth?.getToken() || this.$store.state.auth?.token
        if (!token) {
          throw new Error('登录已过期，请刷新页面')
        }

        // 准备保存数据
        const assetData = {
          ...this.localAsset,
          metadata: {
            ...this.localAsset.metadata,
            blocks: this.localAsset.blocks,
            highlightColumns: this.highlightColumns
          }
        }

        // 调试：检查数据格式
        console.log('📦 保存素材数据:', {
          title: assetData.title,
          summary: assetData.summary,
          cover: assetData.cover ? '有封面' : '无封面',
          blocksCount: assetData.metadata.blocks?.length || 0,
          blocks: assetData.metadata.blocks?.map(b => ({
            type: b.type,
            hasData: !!b.data,
            dataKeys: b.data ? Object.keys(b.data) : []
          }))
        })

        let response
        if (this.isNew) {
          // 创建新素材
          response = await this.$axios.post('/api/tenant/assets', assetData, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          this.$toast?.success('素材创建成功')
        } else {
          // 更新已有素材
          response = await this.$axios.put(`/api/tenant/assets/${this.localAsset.id}`, assetData, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          this.$toast?.success('素材保存成功')
        }

        // 标记为已保存
        this.markSaved()

        // 如果是新建，更新ID
        if (this.isNew && response.data.asset) {
          this.localAsset.id = response.data.asset.id
          this.startEdit(response.data.asset)
        }

        // 通知父组件刷新列表
        this.$emit('saved', response.data.asset)

      } catch (error) {
        console.error('保存素材失败:', error)
        console.error('错误详情:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message
        })
        
        let errorMsg = '保存失败'
        
        if (error.response?.status === 401) {
          errorMsg = '登录已过期，请刷新页面'
        } else if (error.response?.data?.error) {
          errorMsg = error.response.data.error
        } else if (error.message) {
          errorMsg = error.message
        }
        
        this.$toast?.error(errorMsg)
      } finally {
        this.saving = false
      }
    },

    // 获取图片数量（用于upload-security-mixin）
    getImageCount() {
      const coverCount = this.localAsset.cover ? 1 : 0
      const blockImageCount = this.localAsset.blocks.filter(b => b.type === 'image').length
      return coverCount + blockImageCount
    }
  }
}
</script>

<style lang="scss" scoped>
.assets-content-editor {
  padding: 0;
}

.editor-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.editor-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #e8f4fd 0%, #f0f9ff 100%);
  border: 1px solid #91d5ff;
  border-radius: 12px;
  color: #0050b3;
  font-size: 14px;

  .icon-info {
    font-size: 20px;
  }
}

.module-container {
  margin-bottom: 24px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.section-header {
  padding: 20px 20px 16px 20px;
  border-bottom: 1px solid #f0f2f5;
}

.section-title {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.section-subtitle {
  margin: 0;
  font-size: 13px;
  color: #8c8c8c;
  line-height: 1.6;
}

.module-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  gap: 20px;

  &.form-grid-two {
    grid-template-columns: repeat(2, 1fr);
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #262626;

  &.required::after {
    content: ' *';
    color: #ff4d4f;
  }
}

.form-input,
.form-textarea {
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  color: #262626;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }
}

.form-textarea {
  resize: vertical;
  line-height: 1.6;
}

.form-hint {
  font-size: 12px;
  color: #8c8c8c;
}

.form-note {
  margin: 12px 0 0;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 13px;
  color: #595959;
  line-height: 1.6;
}

/* 标签输入 */
.tags-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.tag-remove {
  padding: 0;
  width: 16px;
  height: 16px;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.5);
  }
}

.tag-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tag-input {
  padding: 10px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 13px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }
}

/* 封面上传 */
.cover-upload {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #f8f9ff;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  color: #595959;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: #667eea;
    background: #f0f4ff;
  }
}

.placeholder-icon {
  font-size: 42px;
}

.placeholder-title {
  font-size: 15px;
  font-weight: 600;
}

.placeholder-desc {
  font-size: 12px;
  color: #8c8c8c;
}

.cover-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-wrapper {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.module-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;

  &:hover {
    transform: scale(1.05);
  }
}

.cover-actions {
  display: flex;
  gap: 12px;
}

.cover-tips {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  color: #8c8c8c;
  line-height: 1.8;
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
  cursor: pointer;
  transition: all 0.3s ease;

  &.active {
    border-color: transparent;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
  }

  &:not(.active):hover {
    border-color: #667eea;
    color: #667eea;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

.btn-primary,
.btn-secondary,
.btn-text {
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.35);

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.45);
  }
}

.btn-secondary {
  background: #f5f5ff;
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.3);

  &:hover:not(:disabled) {
    background: #ebebff;
    border-color: #667eea;
  }
}

.btn-text {
  padding: 8px 16px;
  background: transparent;
  color: #595959;

  &.danger {
    color: #ff4d4f;

    &:hover {
      background: #fff1f0;
    }
  }
}

.hidden-input {
  display: none;
}

@media (max-width: 768px) {
  .editor-container {
    padding: 16px;
  }

  .form-grid.form-grid-two {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
