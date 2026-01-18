<template>
  <div class="timeline-section">
    <!-- 标题（左对齐，与其他模块一致） -->
    <div v-if="title" class="section-header">
      <h3 class="section-title">{{ title }}</h3>
      <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
    </div>
    
    <!-- 时间线内容 -->
    <div class="timeline-container">
      <div 
        v-for="(event, index) in events"
        :key="event.id"
        class="timeline-item"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <!-- 左侧：时间标签 -->
        <div class="event-date">{{ event.date }}</div>
        
        <!-- 中间：圆点和连线 -->
        <div class="event-axis">
          <div class="axis-line" :style="lineStyles"></div>
          <div class="axis-dot" :style="dotStyles">
            <!-- Emoji 图标 -->
            <span v-if="event.icon && (!event.iconType || event.iconType === 'emoji')" class="dot-icon dot-icon-emoji">
              {{ event.icon }}
            </span>
            
            <!-- SVG 图标 -->
            <img
              v-else-if="event.icon && event.iconType === 'svg'"
              :src="event.icon"
              class="dot-icon dot-icon-svg"
              alt="icon"
            />
            
            <!-- CSS 图标 (Font Awesome) -->
            <i
              v-else-if="event.icon && event.iconType === 'css'"
              :class="event.icon"
              class="dot-icon dot-icon-css"
            ></i>
            
            <!-- Lottie 动画图标（暂不支持，降级为 Emoji） -->
            <span v-else-if="event.icon && event.iconType === 'lottie'" class="dot-icon dot-icon-emoji">
              {{ event.icon }}
            </span>
          </div>
        </div>
        
        <!-- 右侧：内容（无边框，简洁） -->
        <div class="event-content">
          <div class="content-line" :style="lineStyles"></div>
          <div class="content-main">
            <h4 class="event-title">{{ event.title }}</h4>
            <p v-if="event.description" class="event-description">{{ event.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Timeline',
  
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    },
    events: {
      type: Array,
      default: () => []
    },
    layout: {
      type: String,
      default: 'vertical',
      validator: value => ['vertical'].includes(value)
    },
    lineStyle: {
      type: String,
      default: 'solid',
      validator: value => ['solid', 'dashed'].includes(value)
    },
    accentColor: {
      type: String,
      default: '#1890FF'
    }
  },
  
  computed: {
    lineStyles() {
      return {
        borderLeftStyle: this.lineStyle,
        borderColor: this.accentColor
      }
    },
    
    dotStyles() {
      return {
        background: this.accentColor,
        boxShadow: `0 0 0 3px ${this.hexToRgba(this.accentColor, 0.15)}`
      }
    }
  },
  
  methods: {
    hexToRgba(hex, alpha) {
      if (!hex) return `rgba(24, 144, 255, ${alpha})`
      const r = parseInt(hex.slice(1, 3), 16)
      const g = parseInt(hex.slice(3, 5), 16)
      const b = parseInt(hex.slice(5, 7), 16)
      return `rgba(${r}, ${g}, ${b}, ${alpha})`
    }
  }
}
</script>

<style lang="scss" scoped>
/* 模块容器 - 统一卡片样式 */
.timeline-section {
  padding: 16px 20px;
  background: #ffffff;
  margin: 12px 16px;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,.08);
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}

/* 标题区域 */
.section-header {
  padding: 20px 20px 16px 20px; /* ✅ 遵循设计规范：统一内边距 */
  border-bottom: 1px solid #f0f2f5;
  margin-bottom: 0; /* padding已包含间距 */
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
}

.section-subtitle {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
  line-height: 1.6;
}

/* 时间线容器 */
.timeline-container {
  position: relative;
  padding: 0;
}

/* 单个时间线项 */
.timeline-item {
  display: grid;
  grid-template-columns: 70px 40px 1fr;
  gap: 0;
  margin-bottom: 28px;
  position: relative;
  opacity: 0;
  animation: fadeIn 0.5s ease-out forwards;
  
  &:last-child {
    margin-bottom: 0;
    
    .axis-line {
      display: none;
    }
  }
}

/* 左侧：时间 */
.event-date {
  padding-right: 16px;
  padding-top: 2px;
  font-size: 13px;
  font-weight: 600;
  color: #1890FF;
  text-align: right;
  line-height: 1.4;
}

/* 中间：轴线和圆点 */
.event-axis {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 2px;
}

.axis-line {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: calc(100% + 28px);
  border-left: 2px solid #e8e8e8;
  border-left-style: inherit;
}

.axis-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #1890FF;
  position: relative;
  z-index: 2;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.2);
  }
}

.dot-icon {
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dot-icon-emoji {
  font-size: 8px;
}

.dot-icon-svg {
  width: 10px;
  height: 10px;
  object-fit: contain;
  filter: brightness(0) invert(1); /* 将 SVG 转为白色 */
}

.dot-icon-css {
  font-size: 8px;
  color: white;
}

.dot-icon-lottie {
  width: 10px;
  height: 10px;
}

/* 右侧：内容区 */
.event-content {
  padding-left: 16px;
  padding-top: 0;
  position: relative;
}

.content-line {
  position: absolute;
  left: 0;
  top: 8px;
  width: 20px;
  height: 1px;
  border-top: 1px solid #e8e8e8;
  border-top-style: inherit;
}

.content-main {
  padding-left: 8px;
  padding-bottom: 4px;
}

.event-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 6px 0;
  line-height: 1.4;
}

.event-description {
  font-size: 13px;
  color: #595959;
  line-height: 1.4;
  margin: 0;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .timeline-section {
    padding: 16px;
    margin: 12px;
  }
  
  .timeline-item {
    grid-template-columns: 60px 32px 1fr;
    margin-bottom: 24px;
  }
  
  .event-date {
    font-size: 12px;
    padding-right: 12px;
  }
  
  .axis-dot {
    width: 10px;
    height: 10px;
  }
  
  .dot-icon-emoji {
    font-size: 7px;
  }
  
  .dot-icon-svg {
    width: 8px;
    height: 8px;
  }
  
  .dot-icon-css {
    font-size: 7px;
  }
  
  .dot-icon-lottie {
    width: 8px;
    height: 8px;
  }
  
  .event-content {
    padding-left: 12px;
  }
  
  .content-line {
    width: 16px;
  }
  
  .event-title {
    font-size: 14px;
  }
  
  .event-description {
    font-size: 13px;
  }
  
  .section-subtitle {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .timeline-item {
    grid-template-columns: 55px 28px 1fr;
    margin-bottom: 20px;
  }
  
  .event-date {
    font-size: 11px;
    padding-right: 10px;
  }
  
  .axis-dot {
    width: 9px;
    height: 9px;
  }
  
  .dot-icon-emoji {
    font-size: 6px;
  }
  
  .dot-icon-svg {
    width: 7px;
    height: 7px;
  }
  
  .dot-icon-css {
    font-size: 6px;
  }
  
  .dot-icon-lottie {
    width: 7px;
    height: 7px;
  }
  
  .event-content {
    padding-left: 10px;
  }
  
  .content-line {
    width: 14px;
  }
  
  .section-title {
    font-size: 16px;
  }
  
  .section-subtitle {
    font-size: 13px;
  }
}
</style>
