<template>
  <div class="asset-preview">
    <!-- 封面 -->
    <div v-if="cover" class="asset-cover">
      <div class="image-wrapper">
        <img :src="cover" alt="封面" class="module-image" />
      </div>
    </div>

    <!-- 标题和简介 -->
    <div v-if="title || summary" class="asset-header">
      <h1 v-if="title" class="asset-title">{{ title }}</h1>
      <p v-if="summary" class="asset-summary">{{ summary }}</p>
    </div>

    <!-- 内容块列表 -->
    <div class="asset-content">
      <template v-for="(block, index) in structuredBlocks">
        <!-- 网店直达块 - 独立模块，左右靠近外部框体 -->
        <div 
          v-if="block.type === 'shop-direct'" 
          :key="block.id || index"
          class="shop-direct-block-wrapper"
        >
          <ShopDirectBlock
            :title="block.data.title"
            :subtitle="block.data.subtitle"
            :shops="block.data.shops || []"
          />
        </div>
        
        <!-- 富文本内容块（文字、图片、亮点）- 组合成文章 -->
        <div
          v-else
          :key="block.id || index"
          :class="['content-block', block.typeClass]"
        >
          <!-- 文字块 -->
          <div v-if="block.type === 'text'" class="text-block">
            <p
              v-for="(para, pIdx) in splitParagraphs(block.data.content)"
              :key="pIdx"
              class="text-paragraph"
            >
              {{ para }}
            </p>
          </div>

          <!-- 图片块 -->
          <div v-else-if="block.type === 'image' && block.data.src" class="image-block">
            <div class="image-wrapper">
              <img :src="block.data.src" :alt="block.data.caption || '图片'" class="module-image" />
            </div>
            <p v-if="block.data.caption" class="image-caption">{{ block.data.caption }}</p>
          </div>

          <!-- 数据亮点组 -->
          <div v-else-if="block.type === 'highlight-group'" class="highlight-grid" :class="`columns-${highlightColumns}`">
            <div
              v-for="(item, hIdx) in block.items"
              :key="item.id || hIdx"
              class="highlight-card"
            >
              <div class="highlight-icon">
                <span v-if="!item.iconType || item.iconType === 'emoji'" class="icon-emoji">
                  {{ item.icon || '📊' }}
                </span>
                <img v-else-if="item.iconType === 'svg'" :src="item.icon" alt="icon" class="icon-svg" />
                <i v-else-if="item.iconType === 'css'" :class="item.icon" class="icon-css"></i>
              </div>
              <div class="highlight-content">
                <div class="highlight-label">{{ item.label }}</div>
                <div class="highlight-value">{{ item.value }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- 外部链接 -->
    <div v-if="externalLink" class="asset-footer">
      <a :href="externalLink" class="btn-external-link" target="_blank" rel="noopener noreferrer">
        <span>了解更多</span>
        <i class="icon-arrow">→</i>
      </a>
    </div>

    <!-- 空状态 -->
    <div v-if="!blocks || blocks.length === 0" class="empty-state">
      <div class="empty-icon">📄</div>
      <p class="empty-text">暂无内容</p>
    </div>
  </div>
</template>

<script>
import ShopDirectBlock from './ShopDirectBlock.vue'

export default {
  name: 'AssetPreview',
  
  components: {
    ShopDirectBlock
  },
  
  props: {
    title: {
      type: String,
      default: ''
    },
    summary: {
      type: String,
      default: ''
    },
    cover: {
      type: String,
      default: ''
    },
    blocks: {
      type: Array,
      default: () => []
    },
    highlightColumns: {
      type: Number,
      default: 3
    },
    externalLink: {
      type: String,
      default: ''
    }
  },
  
  methods: {
    splitParagraphs(text) {
      if (!text) return []
      return text.split('\n').filter(p => p.trim())
    }
  },

  computed: {
    structuredBlocks() {
      const result = []
      const highlightBuffer = []

      const flushHighlights = () => {
        if (highlightBuffer.length === 0) return
        result.push({
          type: 'highlight-group',
          typeClass: 'block-type-highlight-group',
          items: [...highlightBuffer],
          id: `highlight-group-${result.length}`
        })
        highlightBuffer.length = 0
      }

      this.blocks.forEach((block, index) => {
        if (block.type === 'highlight') {
          highlightBuffer.push(block)
        } else {
          flushHighlights()
          if (block.type === 'text') {
            result.push({
              type: 'text',
              data: block,
              typeClass: 'block-type-text',
              id: block.id || `text-${index}`
            })
          } else if (block.type === 'image') {
            result.push({
              type: 'image',
              data: block,
              typeClass: 'block-type-image',
              id: block.id || `image-${index}`
            })
          } else if (block.type === 'shop-direct') {
            result.push({
              type: 'shop-direct',
              data: block.data || { title: '', subtitle: '', shops: [] },
              typeClass: 'block-type-shop-direct',
              id: block.id || `shop-direct-${index}`
            })
          } else {
            result.push({
              type: block.type,
              data: block,
              typeClass: `block-type-${block.type}`,
              id: block.id || `block-${index}`
            })
          }
        }
      })

      flushHighlights()
      return result
    }
  }
}
</script>

<style lang="scss" scoped>
.asset-preview {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  background: white;
}

/* 头部 */
.asset-cover {
  margin-bottom: 24px;
  .image-wrapper {
    border-radius: 12px;
  }
}

.asset-header {
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

.asset-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 6px 0;
  line-height: 1.4;
}

.asset-summary {
  font-size: 14px;
  color: #8c8c8c;
  line-height: 1.6;
  margin: 0;
}

/* 内容块 */
.asset-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 富文本内容块（文字、图片、亮点）- 组合成文章，无框体 */
.content-block {
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 0;
}

/* 文字块 */
.text-block {
  .text-paragraph {
    font-size: 14px;
    color: #595959;
    line-height: 1.8;
    margin: 0 0 12px 0;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

/* 图片块 */
.image-block {
  background: #fafafa;
  border-radius: 12px;

  .image-wrapper {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }

  .image-caption {
    margin-top: 12px;
    font-size: 12px;
    color: #8c8c8c;
    text-align: center;
    line-height: 1.4;
  }
}

.image-wrapper {
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
}

.module-image:hover {
  transform: scale(1.04);
}

/* 网店直达块 - 独立模块，左右有间距，有圆角和边框 */
.shop-direct-block-wrapper {
  margin: 16px -24px; /* 上下间距16px，左右突破 asset-preview 的 padding */
  padding: 0 20px; /* 左右内边距20px，保持与边缘的距离 */
  background: transparent;
  border: none;
}

/* 数据亮点栅格 */
.highlight-grid {
  display: grid;
  gap: 12px;
}

.highlight-grid.columns-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.highlight-grid.columns-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.highlight-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 12px 8px;
  border-radius: 8px;
  background: rgba(0, 123, 255, 0.03);
  transition: all 0.3s;
}

.highlight-card:hover {
  background: rgba(0, 123, 255, 0.06);
  transform: translateY(-2px);
}

.highlight-icon {
  font-size: 32px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

.icon-emoji {
  font-size: 32px;
}

.icon-svg {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.icon-css {
  font-size: 32px;
  color: #1a1a2e;
}

.highlight-content {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.highlight-label {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 4px;
}

.highlight-value {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  line-height: 1.2;
}

/* 底部 */
.asset-footer {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 2px solid #f0f0f0;
  text-align: center;
}

.btn-external-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  }
  
  i {
    font-size: 18px;
    transition: transform 0.3s ease;
  }
  
  &:hover i {
    transform: translateX(4px);
  }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  
  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }
  
  .empty-text {
    font-size: 16px;
    color: #8c8c8c;
    margin: 0;
  }
}

/* 响应式 */
@media (max-width: 992px) {
  .highlight-grid.columns-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .asset-preview {
    padding: 16px;
  }

  .asset-title {
    font-size: 15px;
  }

  .asset-summary {
    font-size: 13px;
  }
  
  .text-block .text-paragraph {
    font-size: 13px;
  }
  
  .content-block {
    padding: 0;
  }
  
  .shop-direct-block-wrapper {
    margin: 12px -16px; /* 移动端上下间距12px，左右突破 padding */
    padding: 0 16px; /* 移动端左右内边距16px */
  }

  .highlight-card {
    padding: 12px 8px;
  }

  .highlight-value {
    font-size: 18px;
  }
  
  .highlight-label {
    font-size: 12px;
  }
}

@media (max-width: 540px) {
  .highlight-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
  
  .highlight-icon {
    font-size: 28px;
    height: 36px;
    
    .icon-emoji,
    .icon-css {
      font-size: 28px;
    }
    
    .icon-svg {
      width: 28px;
      height: 28px;
    }
  }
}
</style>

