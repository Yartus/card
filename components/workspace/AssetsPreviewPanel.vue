<template>
  <div class="assets-preview-panel">
    <div class="preview-sticky">
      <!-- 预览头部 -->
      <div class="preview-header">
        <h3 class="preview-title">
          <i class="icon-eye">👁️</i>
          {{ previewTitle }}
        </h3>
        <p class="preview-desc">{{ previewDesc }}</p>
      </div>

      <!-- 预览内容区 -->
      <div class="preview-body">
        <!-- Tab1: 素材详情预览 -->
        <div v-if="activeTab === 'content'" class="preview-content">
          <div v-if="!draftAsset" class="preview-empty">
            <div class="empty-icon">📝</div>
            <p>开始编辑素材，这里会实时显示预览效果</p>
          </div>
          
          <div v-else class="content-preview">
            <!-- 封面 -->
            <div v-if="draftAsset.cover" class="preview-cover">
              <img :src="draftAsset.cover" :alt="draftAsset.title" />
            </div>
            <div v-else class="preview-cover-placeholder">
              <i class="icon-image">🖼</i>
              <span>等待上传封面</span>
            </div>

            <!-- 标题简介 -->
            <div class="preview-header-info">
              <h2 class="preview-asset-title">{{ draftAsset.title || '未命名素材' }}</h2>
              <p class="preview-asset-summary">{{ draftAsset.summary || '暂无简介' }}</p>
            </div>

            <!-- 使用AssetPreview组件渲染内容 -->
            <AssetPreview
              v-if="hasBlocks"
              :blocks="safeBlocks"
              :highlight-columns="safeHighlightColumns"
            />
            
            <div v-else class="preview-empty-blocks">
              <i class="icon-blocks">📦</i>
              <p>在左侧添加图文内容后，这里会显示排版效果</p>
            </div>
          </div>
        </div>

        <!-- Tab2: 分享封面预览 -->
        <div v-else-if="activeTab === 'push'" class="preview-share">
          <div v-if="!selectedAsset" class="preview-empty">
            <div class="empty-icon">📨</div>
            <p>选择素材后，这里会显示分享卡片效果</p>
          </div>
          
          <div v-else class="share-card-preview">
            <div class="share-card">
              <!-- 封面 -->
              <div v-if="selectedAsset.cover" class="share-cover">
                <img :src="selectedAsset.cover" :alt="selectedAsset.title" />
              </div>
              <div v-else class="share-cover-placeholder">
                <i class="icon-image">🖼</i>
                <span>暂无封面</span>
              </div>

              <!-- 卡片内容 -->
              <div class="share-content">
                <h3 class="share-title">{{ selectedAsset.shareTitle || selectedAsset.title }}</h3>
                <p class="share-summary">{{ selectedAsset.summary }}</p>
                
                <!-- 标签 -->
                <div v-if="selectedAsset.tags && selectedAsset.tags.length" class="share-tags">
                  <span v-for="tag in selectedAsset.tags.slice(0, 3)" :key="tag" class="share-tag">
                    #{{ tag }}
                  </span>
                </div>

                <!-- 分享信息 -->
                <div class="share-info">
                  <span class="share-source">来自 {{ tenantName }}</span>
                  <span class="share-action">点击查看详情 →</span>
                </div>
              </div>
            </div>

            <!-- 模拟企微分享效果 -->
            <div class="wecom-share-tip">
              <i class="icon-info">ℹ️</i>
              <span>在企业微信中分享时，将显示为上方卡片样式</span>
            </div>
          </div>
        </div>

        <!-- Tab3: 素材列表预览 -->
        <div v-else-if="activeTab === 'list'" class="preview-list">
          <div class="list-summary">
            <div class="summary-card">
              <div class="summary-icon">📊</div>
              <div class="summary-content">
                <div class="summary-label">素材总数</div>
                <div class="summary-value">{{ assetStats.total }}</div>
              </div>
            </div>

            <div class="summary-card">
              <div class="summary-icon success">✓</div>
              <div class="summary-content">
                <div class="summary-label">已发布</div>
                <div class="summary-value">{{ assetStats.published }}</div>
              </div>
            </div>

            <div class="summary-card">
              <div class="summary-icon draft">📝</div>
              <div class="summary-content">
                <div class="summary-label">草稿</div>
                <div class="summary-value">{{ assetStats.draft }}</div>
              </div>
            </div>
          </div>

          <!-- 素材库链接 -->
          <div class="library-link-card">
            <div class="link-label">
              <i class="icon-link">🔗</i>
              素材库总链接
            </div>
            <div class="link-value">
              <code>{{ libraryUrl }}</code>
              <button class="btn-copy-small" @click="copyLibraryUrl" title="复制链接">
                <i class="icon-copy">📋</i>
              </button>
            </div>
            <div class="link-tip">
              可配置到企业微信聊天侧边栏，员工快速访问全部素材
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import AssetPreview from '@/components/card/AssetPreview.vue'

export default {
  name: 'AssetsPreviewPanel',

  components: {
    AssetPreview
  },

  props: {
    activeTab: {
      type: String,
      required: true,
      validator: (value) => ['content', 'push', 'list'].includes(value)
    },
    selectedAsset: {
      type: Object,
      default: null
    },
    assetStats: {
      type: Object,
      default: () => ({
        total: 0,
        published: 0,
        draft: 0
      })
    }
  },

  computed: {
    ...mapState('assetEditor', ['draftAsset']),
    ...mapGetters('assetEditor', ['hasDraft']),

    previewTitle() {
      const titles = {
        content: '素材详情预览',
        push: '分享封面预览',
        list: '素材库概览'
      }
      return titles[this.activeTab] || '预览'
    },

    previewDesc() {
      const descs = {
        content: '左侧编辑会实时更新，保存后即可发布',
        push: '显示素材在企业微信中的分享效果',
        list: '素材库整体统计和访问链接'
      }
      return descs[this.activeTab] || ''
    },

    hasBlocks() {
      // 防御性检查 - 防止空数据崩溃
      if (!this.draftAsset) return false
      
      // 安全获取blocks
      let blocks = []
      try {
        blocks = this.draftAsset.blocks || this.draftAsset.metadata?.blocks || []
      } catch (e) {
        console.warn('⚠️ 获取blocks失败:', e)
        return false
      }
      
      // 确保是数组且有内容
      return Array.isArray(blocks) && blocks.length > 0
    },

    tenantName() {
      return this.$store.state.workspace?.tenantInfo?.name || '企业名称'
    },

    libraryUrl() {
      const tenantId = this.$store.state.workspace?.tenantInfo?.id || 'tenant-id'
      const baseUrl = process.client ? window.location.origin : 'https://zjemail.cn'
      return `${baseUrl}/assets/${tenantId}`
    },

    // 安全获取blocks - 防止空数据崩溃
    safeBlocks() {
      if (!this.draftAsset) return []
      try {
        const blocks = this.draftAsset.blocks || this.draftAsset.metadata?.blocks || []
        return Array.isArray(blocks) ? blocks : []
      } catch (e) {
        console.error('⚠️ 获取blocks出错:', e)
        return []
      }
    },

    // 安全获取highlightColumns
    safeHighlightColumns() {
      try {
        return this.draftAsset?.metadata?.highlightColumns || 3
      } catch (e) {
        return 3
      }
    }
  },

  methods: {
    copyLibraryUrl() {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(this.libraryUrl)
          .then(() => this.$toast?.success('链接已复制'))
          .catch(() => this.$toast?.error('复制失败'))
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.assets-preview-panel {
  height: 100%;
  background: #f5f5f5;
  border-left: 1px solid #e8e8e8;
}

.preview-sticky {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 20px;
}

.preview-header {
  margin-bottom: 20px;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #262626;

  .icon-eye {
    font-size: 20px;
  }
}

.preview-desc {
  margin: 0;
  font-size: 13px;
  color: #8c8c8c;
  line-height: 1.6;
}

.preview-body {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #8c8c8c;

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  p {
    margin: 0;
    font-size: 14px;
    line-height: 1.6;
  }
}

/* 素材详情预览 */
.content-preview {
  padding: 0;
}

.preview-cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.preview-cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  aspect-ratio: 16 / 9;
  background: #f5f5f5;
  color: #8c8c8c;

  .icon-image {
    font-size: 48px;
    margin-bottom: 8px;
  }

  span {
    font-size: 13px;
  }
}

.preview-header-info {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.preview-asset-title {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 700;
  color: #262626;
  line-height: 1.4;
}

.preview-asset-summary {
  margin: 0;
  font-size: 14px;
  color: #595959;
  line-height: 1.8;
}

.preview-empty-blocks {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #8c8c8c;

  .icon-blocks {
    font-size: 40px;
    margin-bottom: 12px;
  }

  p {
    margin: 0;
    font-size: 13px;
  }
}

/* 分享封面预览 */
.preview-share {
  padding: 24px;
}

.share-card-preview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-card {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.share-cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.share-cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  aspect-ratio: 16 / 9;
  background: #f5f5f5;
  color: #8c8c8c;

  .icon-image {
    font-size: 40px;
    margin-bottom: 8px;
  }
}

.share-content {
  padding: 16px 20px;
}

.share-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  line-height: 1.4;
}

.share-summary {
  margin: 0 0 12px;
  font-size: 13px;
  color: #595959;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.share-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.share-tag {
  padding: 4px 10px;
  background: #f0f0f0;
  color: #595959;
  border-radius: 12px;
  font-size: 12px;
}

.share-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
}

.share-source {
  color: #8c8c8c;
}

.share-action {
  color: #1890ff;
  font-weight: 600;
}

.wecom-share-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 8px;
  color: #0050b3;
  font-size: 12px;

  .icon-info {
    flex-shrink: 0;
  }
}

/* 素材列表预览 */
.preview-list {
  padding: 24px;
}

.list-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fafafa;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
}

.summary-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-radius: 8px;
  font-size: 20px;

  &.success {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  }

  &.draft {
    background: linear-gradient(135deg, #faad14 0%, #d48806 100%);
  }
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: #262626;
}

.library-link-card {
  padding: 16px;
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
}

.link-label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #262626;
}

.link-value {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;

  code {
    flex: 1;
    padding: 8px 12px;
    background: #f5f5f5;
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    font-size: 12px;
    color: #262626;
    word-break: break-all;
  }
}

.btn-copy-small {
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #667eea;
    color: #667eea;
  }
}

.link-tip {
  font-size: 12px;
  color: #8c8c8c;
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .list-summary {
    grid-template-columns: 1fr;
  }
}
</style>

