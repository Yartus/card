<template>
  <div class="card-header" :style="headerStyle">
    <!-- 背景层 -->
    <div class="header-background" :style="backgroundStyle"></div>

    <!-- 头像（居中重叠） -->
    <div class="card-avatar" @click="$emit('avatar-click')">
      <img 
        v-if="displayAvatar" 
        :src="displayAvatar" 
        :alt="basicInfo.name"
        class="avatar-image"
        @error="handleAvatarError"
      />
      <div v-else class="avatar-placeholder">
        {{ avatarText }}
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="card-content">
      <!-- 姓名 -->
      <div class="card-title">{{ basicInfo.name || '未设置' }}</div>
      
      <!-- 公司简称 - 职务 -->
      <div class="card-subtitle">
        <span v-if="companyShort">{{ companyShort }}</span>
        <span v-if="companyShort && basicInfo.title" class="company-separator"> - </span>
        <span v-if="basicInfo.title">{{ basicInfo.title || '员工' }}</span>
        <span v-if="!companyShort && !basicInfo.title">员工</span>
      </div>
      
      <!-- Slogan（单独一行） -->
      <div v-if="slogan" class="card-slogan">{{ slogan }}</div>

      <!-- 按钮组 -->
      <div class="card-actions">
        <button class="card-btn" @click="handleSaveContact">
          保存到通讯录
        </button>
        <button class="card-btn card-btn-solid" @click="handleShare">
          分享
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardHeader',
  
  props: {
    basicInfo: {
      type: Object,
      required: true,
      default: () => ({})
    },
    companyShort: {
      type: String,
      default: ''
    },
    slogan: {
      type: String,
      default: ''
    },
    headerBackground: {
      type: Object,
      default: () => ({
        backgroundType: 'svg',
        svgPattern: 'geometric',
        svgGradientStart: '#ffffff',
        svgGradientEnd: '#FC726E',
        svgDensity: 300,
        svgOpacity: 0.5,
        backgroundImage: '',
        imageOpacity: 0.8,
        imageBlur: 0,
        imageSaturation: 1.2,
        solidColor: '#667eea'
      })
    },
    avatarConfig: {
      type: Object,
      default: () => ({
        useWecomAvatar: true,
        customAvatar: '',
        wecomAvatar: ''
      })
    }
  },
  
  computed: {
    avatarText() {
      if (!this.basicInfo.name) return '?'
      const names = this.basicInfo.name.split(' ')
      if (names.length >= 2) {
        return names[0].charAt(0) + names[1].charAt(0)
      }
      return this.basicInfo.name.charAt(0)
    },
    
    displayAvatar() {
      const config = this.avatarConfig || {}
      // 默认使用企业微信头像
      if (config.useWecomAvatar !== false) {
        return config.wecomAvatar || this.basicInfo.avatar || ''
      }
      return config.customAvatar || ''
    },
    
    // 计算背景样式
    backgroundStyle() {
      const config = this.headerBackground || {}
      
      if (config.backgroundType === 'svg') {
        // 生成SVG背景
        const svg = this.generateSVG({
          svgPattern: config.svgPattern || 'geometric',
          svgGradientStart: config.svgGradientStart || '#ffffff',
          svgGradientEnd: config.svgGradientEnd || '#FC726E',
          svgOpacity: config.svgOpacity !== undefined ? config.svgOpacity : 0.5
        })
        return {
          backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(svg)}")`,
          backgroundSize: `${config.svgDensity || 300}px ${config.svgDensity || 300}px`,
          backgroundRepeat: 'repeat'
        }
      } else if (config.backgroundType === 'image' && config.backgroundImage) {
        return {
          backgroundImage: `url(${config.backgroundImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: config.imageOpacity !== undefined ? config.imageOpacity : 0.8,
          filter: `blur(${config.imageBlur || 0}px) saturate(${config.imageSaturation || 1.2})`
        }
      } else if (config.backgroundType === 'solid') {
        return {
          background: config.solidColor || '#667eea'
        }
      }
      
      // 默认SVG背景
      return {
        backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(this.generateDefaultSVG())}")`,
        backgroundSize: '300px 300px',
        backgroundRepeat: 'repeat'
      }
    },
    
    headerStyle() {
      return {
        position: 'relative',
        overflow: 'hidden'
      }
    }
  },
  
  methods: {
    handleAvatarError(event) {
      event.target.style.display = 'none'
    },
    
    handleSaveContact() {
      this.$emit('save-contact')
    },
    
    handleShare() {
      this.$emit('share')
    },
    
    // 生成SVG背景
    generateSVG(config) {
      const { svgPattern, svgGradientStart, svgGradientEnd, svgOpacity } = config
      
      switch (svgPattern) {
        case 'geometric':
          return this.generateGeometricSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'dots':
          return this.generateDotsSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'lines':
          return this.generateLinesSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'waves':
          return this.generateWavesSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'grid':
          return this.generateGridSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'circles':
          return this.generateCirclesSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        default:
          return this.generateGeometricSVG(svgGradientStart, svgGradientEnd, svgOpacity)
      }
    },
    
    generateDefaultSVG() {
      return this.generateGeometricSVG('#ffffff', '#FC726E', 0.5)
    },
    
    // 几何图案SVG - 改进版：六边形蜂窝图案
    generateGeometricSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="hexPattern" patternUnits="userSpaceOnUse" width="60" height="52" patternTransform="rotate(0)">
            <g fill="none" stroke="rgba(255,255,255,${opacity})" stroke-width="1.5">
              <path d="M30,0 L50,13 L50,39 L30,52 L10,39 L10,13 Z"/>
            </g>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#hexPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 圆点网格SVG - 改进版：密集圆点阵列
    generateDotsSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="dotsPattern" patternUnits="userSpaceOnUse" width="20" height="20">
            <circle cx="10" cy="10" r="2.5" fill="rgba(255,255,255,${opacity})"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#dotsPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 线条SVG - 改进版：斜线纹理
    generateLinesSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="linesPattern" patternUnits="userSpaceOnUse" width="40" height="40" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="40" stroke="rgba(255,255,255,${opacity})" stroke-width="1.5"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#linesPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 波浪SVG - 改进版：多层波浪
    generateWavesSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <path d="M0,100 Q100,60 200,100 T400,100" stroke="rgba(255,255,255,${opacity})" stroke-width="2.5" fill="none"/>
        <path d="M0,120 Q100,80 200,120 T400,120" stroke="rgba(255,255,255,${opacity * 0.7})" stroke-width="2" fill="none"/>
        <path d="M0,80 Q100,40 200,80 T400,80" stroke="rgba(255,255,255,${opacity * 0.7})" stroke-width="2" fill="none"/>
      </svg>`
    },
    
    // 网格SVG - 改进版：精细网格
    generateGridSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="gridPattern" patternUnits="userSpaceOnUse" width="20" height="20">
            <line x1="0" y1="0" x2="0" y2="20" stroke="rgba(255,255,255,${opacity})" stroke-width="1"/>
            <line x1="0" y1="0" x2="20" y2="0" stroke="rgba(255,255,255,${opacity})" stroke-width="1"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#gridPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 圆形SVG - 改进版：同心圆
    generateCirclesSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <circle cx="100" cy="100" r="30" fill="none" stroke="rgba(255,255,255,${opacity})" stroke-width="2"/>
        <circle cx="100" cy="100" r="50" fill="none" stroke="rgba(255,255,255,${opacity * 0.7})" stroke-width="1.5"/>
        <circle cx="100" cy="100" r="70" fill="none" stroke="rgba(255,255,255,${opacity * 0.5})" stroke-width="1"/>
      </svg>`
    }
  }
}
</script>

<style lang="scss" scoped>
/* ✅ 头部背景撑满到边框，与其他模块区隔，底部圆角和阴影增强层次感 */
.card-header {
  position: relative;
  width: 100%;
  height: auto;
  min-height: 384px; /* ✅ 整个头部高度384px，中心在192px */
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #ffffff;
  margin: 0; /* ✅ 无外边距，撑满 */
  margin-bottom: 12px; /* ✅ 仅底部间距，与其他模块区隔 */
  border-radius: 0 0 20px 20px; /* ✅ 底部圆角，增强层次感 */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); /* ✅ 增强底部阴影，营造层次感 */
  overflow: hidden;
}

/* 背景层 - 撑满整个头部区域 */
.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 192px;
  pointer-events: none;
  width: 100%; /* ✅ 确保撑满 */
}

/* 头像（圆心在整个名片头部中心，跨越背景区和文字信息区） */
.card-avatar {
  position: absolute;
  width: 110px; /* ✅ 调整大小：110px，半径55px */
  height: 110px;
  background: #ffffff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  top: 137px; /* ✅ 整个头部中心(192px) - 头像半径(55px) = 137px，圆心在背景区和文字信息区分界处 */
  left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 4px solid #ffffff;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
  z-index: 2;
}

.card-avatar:hover {
  transform: translateX(-50%) scale(1.00); /* ✅ 保持居中，同时放大 */
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 700;
  color: #262626;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
}

/* 内容区域 */
.card-content {
  position: relative;
  width: 100%;
  padding: 0 20px 20px 20px; /* ✅ 左右和底部内边距20px */
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0; /* ✅ 使用margin控制间距 */
  z-index: 1;
  margin-top: 192px; /* ✅ 背景层高度192px（正好是头部中心） */
  padding-top: 80px; /* ✅ 头像与名字之间的间隔拉大到80px */
}

/* 姓名 */
.card-title {
  font-size: 18px; /* ✅ 参考代码：18px */
  font-weight: 500; /* ✅ 参考代码：500 */
  color: #262626; /* ✅ 遵循设计规范：主文字颜色 */
  margin: 0;
  margin-top: 0; /* ✅ 头像和姓名之间的间隔由padding-top提供 */
  margin-bottom: 6px; /* ✅ 姓名和职位之间的间隔 */
  line-height: 1.4; /* ✅ 遵循设计规范：行高1.4 */
  text-align: center;
}

/* 公司简称 - 职务 */
.card-subtitle {
  font-size: 15px; /* ✅ 参考代码：15px */
  font-weight: 400; /* ✅ 参考代码：400 */
  color: #78858F; /* ✅ 参考代码：副色 */
  margin: 0;
  margin-bottom: 12px; /* ✅ 简称-职务和slogan之间的间隔 */
  line-height: 1.4; /* ✅ 遵循设计规范：行高1.4 */
  text-align: center;
  
  /* 单行显示，超出省略 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.company-separator {
  margin: 0 4px;
  color: #78858F;
  opacity: 0.6;
}

/* Slogan（单独一行） */
.card-slogan {
  font-size: 13px; /* ✅ 遵循设计规范：说明文字13px */
  font-weight: 400;
  color: #8c8c8c; /* ✅ 遵循设计规范：辅助文字颜色 */
  text-align: center;
  width: 100%;
  padding: 0;
  box-sizing: border-box;
  margin: 0;
  margin-bottom: 20px; /* ✅ slogan和按钮之间的间隔 */
  line-height: 1.4; /* ✅ 遵循设计规范：行高1.4 */
  
  /* 单行显示，超出省略 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 按钮组 */
.card-actions {
  margin-top: 0; /* ✅ 间隔由card-company的margin-bottom提供 */
  display: none; /* ✅ 暂时隐藏按钮 */
  gap: 12px; /* ✅ 遵循设计规范：内容块间距12px */
  width: 100%;
  justify-content: center;
  padding: 0;
  box-sizing: border-box;
}

.card-btn {
  width: 100px; /* ✅ 参考代码：100px */
  height: 36px; /* ✅ 参考代码：31px，调整为36px更易点击 */
  border: 2px solid #000000; /* ✅ 参考代码：2px solid var(--main-color) */
  border-radius: 4px; /* ✅ 参考代码：4px */
  font-weight: 700; /* ✅ 参考代码：700 */
  font-size: 11px; /* ✅ 参考代码：11px */
  color: #000000; /* ✅ 参考代码：var(--main-color) */
  background: #ffffff; /* ✅ 参考代码：var(--bg-color) */
  text-transform: uppercase; /* ✅ 参考代码：uppercase */
  transition: all 0.3s ease; /* ✅ 遵循设计规范：过渡动画 */
  cursor: pointer;
  line-height: 1;
  padding: 0;
}

.card-btn:hover {
  background: #000000;
  color: #ffffff;
}

.card-btn-solid {
  background: #000000;
  color: #ffffff;
}

.card-btn-solid:hover {
  background: #ffffff;
  color: #000000;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .card-header {
    max-width: 100%;
    margin: 0; /* ✅ 移动端也撑满 */
    margin-bottom: 12px; /* ✅ 仅底部间距 */
    border-radius: 0 0 16px 16px; /* ✅ 移动端底部圆角 */
    min-height: 360px;
  }
  
  .header-background {
    height: 160px;
  }
  
  .card-avatar {
    width: 100px;
    height: 100px;
    top: 130px; /* ✅ 移动端：整个头部中心(180px，min-height:360px) - 头像半径(50px) = 130px，圆心在背景区和文字信息区分界处 */
    border-width: 3px;
  }
  
  .avatar-placeholder {
    font-size: 40px;
  }
  
  .card-content {
    padding: 0 16px 16px 16px; /* ✅ 移动端内边距16px */
    margin-top: 160px; /* ✅ 背景层高度160px */
    padding-top: 80px; /* ✅ 移动端头像与名字之间的间隔也拉大到80px */
  }
  
  .card-title {
    font-size: 16px; /* ✅ 移动端字号调整 */
    margin-bottom: 10px; /* ✅ 移动端间距稍小 */
  }
  
  .card-subtitle {
    font-size: 14px; /* ✅ 移动端字号调整 */
    margin-bottom: 10px; /* ✅ 移动端间距稍小 */
  }
  
  .card-slogan {
    font-size: 12px; /* ✅ 移动端字号调整 */
    margin-bottom: 16px; /* ✅ 移动端间距稍小 */
    padding: 0; /* ✅ 移动端不需要额外padding */
  }
  
  .card-actions {
    margin-top: 0; /* ✅ 间隔由card-slogan的margin-bottom提供 */
    gap: 10px;
    padding: 0; /* ✅ 移动端不需要额外padding */
  }
  
  .card-btn {
    width: 90px;
    height: 32px;
    font-size: 10px;
  }
}

/* 减少动画模式支持 */
@media (prefers-reduced-motion: reduce) {
  .card-avatar {
    transition: none;
  }
  
  .card-btn {
    transition: none;
  }
}
</style>
