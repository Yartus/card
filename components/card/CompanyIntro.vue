<template>
  <section class="company-intro">
    <div class="ci-card">
      <!-- 标题 -->
      <div v-if="config.title" class="ci-header">{{ config.title }}</div>
      
      <!-- 顶部图片 -->
      <div v-if="config.showImage && config.imagePosition === 'top' && config.image" class="ci-image-top">
        <img :src="config.image" :alt="config.title" />
      </div>
      
      <!-- 主体内容 -->
      <div class="ci-body">
        <!-- 文字内容 -->
        <div class="ci-content">
          <!-- 浮动图片（左上角/右上角） -->
          <div 
            v-if="config.showImage && (config.imagePosition === 'float-left' || config.imagePosition === 'float-right') && config.image" 
            class="ci-image-float"
            :class="{
              'float-left': config.imagePosition === 'float-left',
              'float-right': config.imagePosition === 'float-right'
            }"
          >
            <img :src="config.image" :alt="config.title" />
          </div>
          <!-- 简洁模式 -->
          <template v-if="config.mode === 'simple'">
            <div v-if="config.content" class="text-container">
              <p class="ci-text" :class="{ 'text-collapsed': !isContentExpanded && shouldShowExpandButton('content') }">
                {{ config.content }}
              </p>
              <button 
                v-if="shouldShowExpandButton('content')" 
                class="btn-expand" 
                @click="toggleContent"
              >
                {{ isContentExpanded ? '收起' : '展开全文' }}
                <span class="expand-icon">{{ isContentExpanded ? '▲' : '▼' }}</span>
              </button>
            </div>
          </template>
          
          <!-- 丰富模式 -->
          <template v-else>
            <h3 v-if="config.subtitle" class="ci-subtitle">{{ config.subtitle }}</h3>
            <div v-if="config.summary" class="text-container">
              <p class="ci-text" :class="{ 'text-collapsed': !isSummaryExpanded && shouldShowExpandButton('summary') }">
                {{ config.summary }}
              </p>
              <button 
                v-if="shouldShowExpandButton('summary')" 
                class="btn-expand" 
                @click="toggleSummary"
              >
                {{ isSummaryExpanded ? '收起' : '展开全文' }}
                <span class="expand-icon">{{ isSummaryExpanded ? '▲' : '▼' }}</span>
              </button>
            </div>
            <ul v-if="config.points && config.points.length > 0" class="ci-points">
              <li v-for="(point, idx) in config.points" :key="idx">{{ point }}</li>
            </ul>
          </template>
          
          <!-- 数据亮点 -->
          <div 
            v-if="config.showHighlights && config.highlights && config.highlights.length > 0" 
            class="ci-highlights"
            :class="{ 
              'highlights-2-cols': highlightsColumns === 2,
              'highlights-3-cols': highlightsColumns === 3
            }"
          >
            <div
              v-for="(highlight, idx) in config.highlights"
              :key="idx"
              class="highlight-item"
            >
              <!-- 图标渲染 -->
              <div class="highlight-icon">
                <!-- Emoji图标 -->
                <span v-if="!highlight.iconType || highlight.iconType === 'emoji'" class="icon-emoji">
                  {{ highlight.icon || '📊' }}
                </span>
                
                <!-- CSS图标 -->
                <i v-else-if="highlight.iconType === 'css'" :class="highlight.icon"></i>
                
                <!-- SVG图标 -->
                <img 
                  v-else-if="highlight.iconType === 'svg'" 
                  :src="highlight.icon" 
                  :alt="highlight.label"
                  class="icon-svg"
                />
                
                <!-- Lottie图标 -->
                <LottieIcon
                  v-else-if="highlight.iconType === 'lottie'"
                  :animation-key="highlight.icon"
                  :width="32"
                  :height="32"
                  :autoplay="true"
                  :loop="true"
                  class="icon-lottie"
                />
              </div>
              
              <div class="highlight-label">{{ highlight.label }}</div>
              <div class="highlight-value">{{ highlight.value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import LottieIcon from '../LottieIcon.vue'

export default {
  name: 'CompanyIntro',
  
  components: {
    LottieIcon
  },
  
  props: {
    // 向后兼容旧的intro prop
    intro: { 
      type: [String, Object], 
      default: null 
    },
    // 新的config prop（完整配置）
    config: {
      type: Object,
      default: () => ({})
    }
  },
  
  data() {
    return {
      isContentExpanded: false,  // 简洁模式的内容展开状态
      isSummaryExpanded: false,  // 丰富模式的summary展开状态
      contentLineCount: 0,       // 内容实际行数
      summaryLineCount: 0        // summary实际行数
    }
  },
  
  computed: {
    // 合并配置，优先使用新的config
    mergedConfig() {
      // 如果有新的config，使用它
      if (this.config && Object.keys(this.config).length > 0) {
        return this.config
      }
      
      // 否则尝试从旧的intro prop转换
      if (typeof this.intro === 'string') {
        return {
          mode: 'simple',
          content: this.intro
        }
      } else if (this.intro && typeof this.intro === 'object') {
        return {
          mode: 'rich',
          subtitle: this.intro.title,
          summary: this.intro.summary,
          points: this.intro.points || []
        }
      }
      
      return {}
    },
    
    // 获取数据亮点的列数
    highlightsColumns() {
      return this.config.highlightsColumns || 2
    }
  },
  
  methods: {
    // 判断是否需要显示展开按钮
    shouldShowExpandButton(type) {
      const text = type === 'content' ? this.config.content : this.config.summary
      if (!text) return false
      
      // 简单判断：超过150个字符就显示展开按钮
      // 或者可以在mounted中计算实际行数
      return text.length > 150
    },
    
    // 切换简洁模式内容的展开状态
    toggleContent() {
      this.isContentExpanded = !this.isContentExpanded
    },
    
    // 切换丰富模式summary的展开状态
    toggleSummary() {
      this.isSummaryExpanded = !this.isSummaryExpanded
    }
  },
  
  // 使用合并后的配置
  created() {
    // 将合并后的配置赋值给内部使用
    if (!this.config || Object.keys(this.config).length === 0) {
      this.$set(this, 'config', this.mergedConfig)
    }
  }
}
</script>

<style lang="scss" scoped>
.company-intro { 
  margin: 12px 16px; 
}

.ci-card { 
  background: #fff; 
  border: 1px solid rgba(0,0,0,.08); 
  border-radius: 12px; 
  box-shadow: 0 2px 8px rgba(0,0,0,.04); 
  overflow: hidden; 
}

.ci-header { 
  padding: 20px 20px 16px 20px; /* ✅ 遵循设计规范：统一内边距 */
  border-bottom: 1px solid #f0f2f5; 
  font-weight: 600; 
  font-size: 16px;
  color: #262626; 
}

/* 顶部图片 */
.ci-image-top {
  width: 100%;
  padding: 20px 20px 0 20px;  /* ✅ 呼吸感：左右上各20px，底部0（让ci-body承担） */
  
  img {
    width: 100%;
    height: 240px;
    object-fit: cover;
    display: block;
    border-radius: 12px;  /* ✅ 圆角12px，与多媒体模块一致 */
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);  /* ✅ 阴影增强，与多媒体模块一致 */
  }
}

/* 主体内容 */
.ci-body { 
  padding: 20px;  /* ✅ 统一为20px，与多媒体模块一致 */
}

/* 文字内容容器 */
.ci-content {
  position: relative;
  /* 为浮动图片预留空间 */
  overflow: auto; /* 清除浮动 */
}

/* 浮动图片 */
.ci-image-float {
  width: 140px;
  margin-bottom: 12px;
  
  img {
    width: 100%;
    height: 140px;
    object-fit: cover;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }
  }
}

/* 左浮动 */
.ci-image-float.float-left {
  float: left;
  margin-right: 16px;
}

/* 右浮动 */
.ci-image-float.float-right {
  float: right;
  margin-left: 16px;
}

.ci-subtitle { 
  margin: 0 0 12px 0; 
  font-size: 16px;
  font-weight: 600;
  color: #111; 
}

/* 文本容器 */
.text-container {
  position: relative;
}

.ci-text { 
  margin: 0; 
  color: rgba(0,0,0,.65); 
  line-height: 1.6; 
  font-size: 14px;
  transition: max-height 0.3s ease;
  
  &:last-child {
    margin-bottom: 0;
  }
}

/* 文本折叠状态（显示2行） */
.ci-text.text-collapsed {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 展开/收起按钮 */
.btn-expand {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid rgba(0, 123, 255, 0.3);
  border-radius: 16px;
  color: #007bff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(0, 123, 255, 0.05);
    border-color: #007bff;
  }
  
  &:active {
    transform: scale(0.98);
  }
}

.expand-icon {
  font-size: 10px;
  transition: transform 0.3s ease;
}

.ci-points { 
  margin: 12px 0 12px 18px; 
  padding: 0;
  color: rgba(0,0,0,.70); 
  
  li {
    margin-bottom: 6px;
    font-size: 14px;
    line-height: 1.5;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

/* 数据亮点 */
.ci-highlights {
  display: grid;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
  clear: both; /* 清除浮动，确保在浮动图片下方完整显示 */
}

/* 2列布局 */
.ci-highlights.highlights-2-cols {
  grid-template-columns: repeat(2, 1fr);
}

/* 3列布局 */
.ci-highlights.highlights-3-cols {
  grid-template-columns: repeat(3, 1fr);
}

.highlight-item {
  text-align: center;
  padding: 12px 8px;
  background: rgba(0, 123, 255, 0.03);
  border-radius: 8px;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(0, 123, 255, 0.06);
    transform: translateY(-2px);
  }
}

.highlight-icon {
  font-size: 32px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  
  .icon-emoji {
    font-size: 32px;
  }
  
  i {
    font-size: 32px;
  }
  
  .icon-svg {
    width: 32px;
    height: 32px;
    object-fit: contain;
  }
  
  .icon-lottie {
    display: inline-block;
  }
}

.highlight-label {
  font-size: 12px;
  color: rgba(0,0,0,.45);
  margin-bottom: 4px;
}

.highlight-value {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}

@media (max-width: 480px) {
  .company-intro {
    margin: 12px 12px;
  }
  
  .ci-header {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .ci-body {
    padding: 16px;  /* ✅ 移动端也保持呼吸感 */
  }
  
  .ci-image-top {
    padding: 16px 16px 0 16px;  /* ✅ 移动端呼吸感 */
    
    img {
      height: 180px;
    }
  }
  
  /* 移动端浮动图片缩小 */
  .ci-image-float {
    width: 110px;
    
    img {
      height: 110px;
    }
  }
  
  .ci-image-float.float-left {
    margin-right: 12px;
  }
  
  .ci-image-float.float-right {
    margin-left: 12px;
  }
  
  /* 移动端默认2列，但若配置为3列则保持3列 */
  .ci-highlights,
  .ci-highlights.highlights-2-cols {
    grid-template-columns: repeat(2, 1fr);
  }

  .ci-highlights.highlights-3-cols {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  
  .highlight-icon {
    font-size: 28px;
    height: 36px;
    
    .icon-emoji,
    i {
      font-size: 28px;
    }
    
    .icon-svg {
      width: 28px;
      height: 28px;
    }
  }
  
  .highlight-value {
    font-size: 16px;
  }
}
</style>
