<template>
  <section class="logo-wall-section">
    <div class="lw-card">
      <div class="lw-header">{{ title || '合作客户' }}</div>
      <div class="lw-body">
        <!-- 横向滚动模式 -->
        <div v-if="layout === 'scroll'" class="logo-wall" :class="{ 'paused': pauseOnHover }">
          <div class="logo-track" :style="trackStyle">
            <img
              v-for="(logo, idx) in doubled"
              :key="idx"
              class="logo scroll-logo"
              :class="`style-${defaultStyle}`"
              :src="logo.src || logo.logo"
              :alt="logo.name || logo.alt || 'logo'"
              loading="lazy"
            />
          </div>
        </div>

        <!-- 网格布局模式 -->
        <div v-else class="logo-grid" :class="`grid-cols-${gridColumns}`">
          <div
            v-for="(logo, idx) in logos"
            :key="idx"
            class="logo-item"
            :class="{ clickable: logo.url }"
            @click="handleLogoClick(logo)"
          >
            <img
              :src="logo.src || logo.logo"
              :alt="logo.name || logo.alt || 'logo'"
              class="logo grid-logo"
              loading="lazy"
            />
            <div v-if="showName && logo.name" class="logo-name">{{ logo.name }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'LogoWall',
  props: {
    // 标题
    title: {
      type: String,
      default: '合作客户'
    },
    // Logo列表
    logos: {
      type: Array,
      default: () => []
    },
    // 布局模式：scroll(横向滚动) 或 grid(网格)
    layout: {
      type: String,
      default: 'scroll',
      validator: value => ['scroll', 'grid'].includes(value)
    },
    // 网格列数（仅在grid模式下生效）
    gridColumns: {
      type: Number,
      default: 3,
      validator: value => [2, 3, 4].includes(value)
    },
    // 是否显示名称（仅在grid模式下生效）
    showName: {
      type: Boolean,
      default: false
    },
    // 滚动动画时长（秒，仅在scroll模式下生效）- 兼容旧配置
    duration: {
      type: Number,
      default: null
    },
    // 滚动速度系数（数值越小越快）- 新配置方式
    scrollSpeed: {
      type: Number,
      default: 2.5  // 适中速度
    },
    // 兼容旧字段
    perLogoDisplay: {
      type: Number,
      default: null
    },
    // 悬停时暂停（仅在scroll模式下生效）
    pauseOnHover: {
      type: Boolean,
      default: true
    },
    // Logo间距（仅在scroll模式下生效）
    gap: {
      type: Number,
      default: 24
    },
    // 默认样式（仅在scroll模式下生效）
    defaultStyle: {
      type: String,
      default: 'grayscale',
      validator: value => ['grayscale', 'color', 'dim'].includes(value)
    }
  },
  computed: {
    doubled() {
      return [...this.logos, ...this.logos]
    },
    trackStyle() {
      // 新的计算逻辑：基于滚动速度系数
      let calculatedDuration
      
      const logoCount = this.logos.length || 10
      
      if (this.scrollSpeed !== null && this.scrollSpeed !== undefined) {
        // 新方式：总时长 = Logo数量 × 滚动速度系数
        // scrollSpeed: 1.5(快) / 2.5(适中) / 3.5(慢) / 5(很慢)
        calculatedDuration = logoCount * this.scrollSpeed
      } else if (this.perLogoDisplay) {
        // 兼容旧perLogoDisplay字段
        calculatedDuration = logoCount * this.perLogoDisplay
      } else if (this.duration) {
        // 兼容最旧的duration字段
        calculatedDuration = this.duration
      } else {
        // 默认：适中速度 (2.5秒/个)
        calculatedDuration = logoCount * 2.5
      }
      
      // 确保最小20秒，避免动画太快导致性能问题
      const safeDuration = Math.max(20, calculatedDuration)
      
      return {
        animationDuration: `${safeDuration}s`,
        gap: `${this.gap || 28}px`
      }
    }
  },
  methods: {
    handleLogoClick(logo) {
      // Logo墙不再支持跳转功能
      return
    }
  }
}
</script>

<style lang="scss" scoped>
.logo-wall-section { 
  margin: 12px 16px; /* ✅ 与其他模块保持一致 */
}

.lw-card { 
  background: #fff; 
  border: 1px solid rgba(0,0,0,.08); 
  border-radius: 12px; 
  box-shadow: 0 2px 8px rgba(0,0,0,.04); 
  overflow: hidden; 
}

.lw-header { 
  padding: 20px 20px 16px 20px; /* ✅ 遵循设计规范：统一内边距20px */
  border-bottom: 1px solid #f0f2f5; 
  font-weight: 600; 
  font-size: 16px;
  color: #262626; 
}

.lw-body { 
  padding: 20px; /* ✅ 遵循设计规范：统一内边距20px */
}

/* 统一容器样式 - 与其他模块保持一致 */
.logo-wall { 
  margin: 12px 16px;  /* 左右16px边距，营造呼吸感 */
  padding: 16px 0;     /* 上下留白 */
  overflow: hidden; 
}

.logo-track { 
  display: flex; 
  /* gap由内联样式控制 */
  align-items: center; 
  animation: marquee 30s linear infinite; 
}

/* 横向滚动模式的Logo */
.scroll-logo { 
  height: 42px; 
  width: auto; 
  transition: all 0.3s ease;
}

.logo-wall:hover .logo-track { 
  animation-play-state: paused; 
}

.scroll-logo:hover {
  transform: scale(1.05);
}

/* 样式变体 */
.scroll-logo.style-grayscale {
  filter: grayscale(100%);
  opacity: 0.7;
}

.scroll-logo.style-grayscale:hover {
  filter: grayscale(0);
  opacity: 1;
}

.scroll-logo.style-dim {
  opacity: 0.5;
}

.scroll-logo.style-dim:hover {
  opacity: 1;
}

.scroll-logo.style-color {
  filter: none;
  opacity: 1;
}

/* 网格布局模式 */
.logo-grid {
  display: grid;
  gap: 20px;
  
  &.grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  &.grid-cols-3 {
    grid-template-columns: repeat(3, 1fr);
  }
  
  &.grid-cols-4 {
    grid-template-columns: repeat(4, 1fr);
  }
}

.logo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100px;
  
  &.clickable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      border-color: rgba(102, 126, 234, 0.3);
    }
    
    &:active {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
}

.grid-logo {
  max-width: 100%;
  max-height: 60px;
  width: auto;
  height: auto;
  object-fit: contain;
  filter: grayscale(80%) opacity(0.8);
  transition: all 0.3s ease;
}

.logo-item:hover .grid-logo {
  filter: grayscale(0%) opacity(1);
  transform: scale(1.05);
}

.logo-name {
  margin-top: 12px;
  font-size: 13px;
  font-weight: 500;
  color: #595959;
  text-align: center;
  line-height: 1.4;
}

@keyframes marquee { 
  0% { transform: translateX(0);} 
  100% { transform: translateX(-50%);} 
}

@media (max-width: 768px) {
  .logo-grid {
    &.grid-cols-3,
    &.grid-cols-4 {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

@media (max-width: 480px) {
  .logo-wall-section {
    margin: 12px 12px;
  }
  
  .lw-header {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .lw-body {
    padding: 14px 16px;
  }
  
  .scroll-logo {
    height: 36px;
  }
  
  .logo-track {
    gap: 24px;
  }
  
  .logo-grid {
    gap: 12px;
    
    &.grid-cols-2,
    &.grid-cols-3,
    &.grid-cols-4 {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  .logo-item {
    padding: 16px;
    min-height: 80px;
  }
  
  .grid-logo {
    max-height: 50px;
  }
  
  .logo-name {
    font-size: 12px;
    margin-top: 8px;
  }
}

/* 减少动画模式支持 */
@media (prefers-reduced-motion: reduce) {
  .logo-track {
    animation: none;
  }
}
</style>


