<template>
  <div class="card-preview-display">
    <div class="preview-header">
      <h4 class="preview-title">
        <span class="icon">👁️</span>
        卡片预览效果
      </h4>
      <p class="preview-desc">实时预览卡片样式，调整配置后立即生效</p>
    </div>
    
    <div class="preview-container">
      <div 
        class="card" 
        :class="{ 'card-hover': isHovered }" 
        @mouseenter="isHovered = true" 
        @mouseleave="isHovered = false"
        @touchstart="isHovered = true"
        @touchend="isHovered = false"
      >
        <!-- 拨打电话按钮（右上角） -->
        <button class="phone-btn" :style="phoneIconStyle" v-if="previewData.mobile">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
          </svg>
        </button>

        <!-- 头像区域 -->
        <div class="profile-pic" :style="{ ...profilePicStyle, ...avatarBorderStyle }">
          <img
            v-if="displayAvatar"
            :src="displayAvatar"
            :alt="previewData.name"
          />
          <!-- 不显示占位符，保持空白 -->
        </div>

        <!-- 底部信息区 -->
        <div class="bottom" :style="bottomStyle">
          <!-- 文字内容（只在hover时显示） -->
          <div class="content" v-if="isHovered">
            <span class="name">{{ previewData.name || '未设置' }}</span>
            <span v-if="displayIntro" class="about-me">{{ displayIntro }}</span>
          </div>
          <!-- 按钮区域（始终显示） -->
          <div class="bottom-bottom">
            <div class="social-links-container">
              <!-- 分享名片 -->
              <button class="social-btn" title="分享名片">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="18" cy="5" r="3"></circle>
                  <circle cx="6" cy="12" r="3"></circle>
                  <circle cx="18" cy="19" r="3"></circle>
                  <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                  <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                </svg>
              </button>
              <!-- WhatsApp -->
              <a class="social-btn" v-if="previewData.mobile" title="WhatsApp">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.375a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .96 4.534.96 10.09c0 1.76.413 3.421 1.15 4.888L.03 23.876l9.135-2.389a11.714 11.714 0 005.885 1.577h.005c5.554 0 10.09-4.535 10.09-10.09 0-2.902-1.19-5.515-3.122-7.405"/>
                </svg>
              </a>
            </div>
            <button class="button">查看详情</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardPreviewDisplay',
  
  props: {
    previewData: {
      type: Object,
      default: () => ({
        name: '张三',
        title: '产品经理',
        personalIntro: '专注于企业数字化转型',
        mobile: '13800138000',
        avatar: ''
      })
    },
    cardConfig: {
      type: Object,
      default: () => ({
        avatarMode: 'company',
        companyAvatar: '',
        backgroundType: 'svg',
        svgPattern: 'geometric',
        svgGradientStart: '#ffffff',
        svgGradientEnd: '#FC726E',
        backgroundImage: '',
        backgroundColor: '#f5f5f5',
        themeColor: '#fbb9b6'
      })
    },
    wecomAvatar: {
      type: String,
      default: ''
    }
  },
  
  data() {
    return {
      isHovered: false
    }
  },
  
  computed: {
    displayAvatar() {
      // 根据avatarMode判断
      if (this.cardConfig.avatarMode === 'company' && this.cardConfig.companyAvatar) {
        return this.cardConfig.companyAvatar
      }
      return this.wecomAvatar || this.previewData.avatar || ''
    },
    
    avatarInitials() {
      const name = this.previewData.name || '未设置'
      return name.length > 2 ? name.substring(0, 2) : name
    },
    
    // 是否有背景图片
    hasBackgroundImage() {
      const bgType = this.cardConfig.backgroundType || 'image'
      if (bgType === 'image') {
        return !!this.cardConfig.backgroundImage
      }
      return false
    },
    
    profilePicStyle() {
      let background = ''
      
      if (this.cardConfig.backgroundType === 'image' && this.cardConfig.backgroundImage) {
        // 图片背景
        background = `url(${this.cardConfig.backgroundImage}) center/cover`
      } else if (this.cardConfig.backgroundType === 'solid') {
        // 纯色背景
        background = this.cardConfig.backgroundColor
      } else {
        // 默认渐变
        background = 'linear-gradient(135deg, #fff8f6 0%, #fef0ef 50%, #fde4e1 100%)'
      }
      
      return {
        background
      }
    },
    
    themeColor() {
      return this.cardConfig.themeColor || '#fbb9b6'
    },
    
    bottomStyle() {
      return {
        backgroundColor: this.themeColor
      }
    },
    
    phoneIconStyle() {
      return {
        '--phone-icon-color': this.themeColor
      }
    },
    
    avatarBorderStyle() {
      return {
        '--avatar-border-color': this.themeColor
      }
    },
    
    // 显示介绍（优先使用个人介绍，其次公司介绍）
    displayIntro() {
      // 优先使用个人介绍
      if (this.previewData.personalIntro) {
        return this.previewData.personalIntro
      }
      // 其次使用公司介绍
      return this.previewData.companyIntro || ''
    }
  },
  
  methods: {
    // 几何图案SVG
    generateGeometricSVGString(start, end, opacity) {
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
    
    // 圆点网格SVG
    generateDotsSVGString(start, end, opacity) {
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
    
    // 线条SVG
    generateLinesSVGString(start, end, opacity) {
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
    
    // 波浪SVG
    generateWavesSVGString(start, end, opacity) {
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
    
    // 网格SVG
    generateGridSVGString(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="gridPattern" patternUnits="userSpaceOnUse" width="20" height="20">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,${opacity})" stroke-width="1"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#gridPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 圆圈SVG
    generateCirclesSVGString(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="circlesPattern" patternUnits="userSpaceOnUse" width="40" height="40">
            <circle cx="20" cy="20" r="8" fill="none" stroke="rgba(255,255,255,${opacity})" stroke-width="1.5"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#circlesPattern)" width="100%" height="100%"></rect>
      </svg>`
    }
  }
}
</script>

<style lang="scss" scoped>
.card-preview-display {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-top: 24px;
}

.preview-header {
  margin-bottom: 20px;
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 6px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-desc {
  font-size: 13px;
  color: #8c8c8c;
  margin: 0;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  min-height: 400px;
}

.card {
  width: 280px;
  height: 280px;
  background: white;
  border-radius: 32px;
  padding: 3px;
  position: relative;
  box-shadow: rgba(96, 75, 74, 0.3) 0px 70px 30px -50px;
  transition: all 0.5s ease-in-out;
  overflow: hidden;
}

.card-hover {
  border-top-left-radius: 55px;
}

.phone-btn {
  position: absolute;
  right: 2rem;
  top: 1.4rem;
  background: transparent;
  border: none;
  cursor: pointer;
  z-index: 10;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.phone-btn svg {
  stroke: var(--phone-icon-color, #fbb9b6);
  stroke-width: 3px;
  width: 24px;
  height: 24px;
  transition: all 0.3s ease;
}

.phone-btn:hover svg {
  stroke: #f55d56;
  transform: scale(1.1);
}

.profile-pic {
  position: absolute;
  width: calc(100% - 6px);
  height: calc(100% - 6px);
  top: 3px;
  left: 3px;
  border-radius: 29px;
  z-index: 1;
  border: 0px solid #fbb9b6;
  overflow: hidden;
  transition: all 0.5s ease-in-out 0.2s, z-index 0.5s ease-in-out 0.2s;
}

.profile-pic img {
  object-fit: cover;
  width: 100%;
  height: 100%;
  object-position: center;
  transition: all 0.5s ease-in-out 0s;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.3);
  color: rgba(0, 0, 0, 0.5);
  font-size: 48px;
  font-weight: 600;
}

.card-hover .profile-pic {
  width: 100px;
  height: 100px;
  aspect-ratio: 1;
  top: 10px;
  left: 10px;
  border-radius: 50%;
  z-index: 3;
  border: 7px solid var(--avatar-border-color, #fbb9b6);
  box-shadow: rgba(96, 75, 74, 0.1882352941) 0px 5px 5px 0px;
  transition: all 0.5s ease-in-out, z-index 0.5s ease-in-out 0.1s;
}

.card-hover .profile-pic:hover {
  transform: scale(1.3);
  border-radius: 0px;
}

.card-hover .profile-pic img {
  transform: scale(2.5);
  object-position: 0px 25px;
  transition: all 0.5s ease-in-out 0.5s;
}

.bottom {
  position: absolute;
  bottom: 3px;
  left: 3px;
  right: 3px;
  top: 80%;
  border-radius: 29px;
  z-index: 2;
  box-shadow: rgba(96, 75, 74, 0.1882352941) 0px 5px 5px 0px inset;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.645, 0.045, 0.355, 1) 0s;
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card-hover .bottom {
  top: 20%;
  border-radius: 80px 29px 29px 29px;
  transition: all 0.5s cubic-bezier(0.645, 0.045, 0.355, 1) 0.2s;
}

.content {
  position: absolute;
  bottom: 0;
  left: 1.5rem;
  right: 1.5rem;
  height: 160px;
}

.name {
  display: block;
  font-size: 1.2rem;
  color: white;
  font-weight: bold;
}

.about-me {
  display: block;
  font-size: 0.9rem;
  color: white;
  margin-top: 1rem;
}

.bottom-bottom {
  position: absolute;
  bottom: 1rem;
  left: 1.5rem;
  right: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.social-links-container {
  display: flex;
  gap: 0.5rem;
}

.social-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: white;
}

.social-btn svg {
  height: 20px;
  width: 20px;
  fill: white;
  filter: drop-shadow(0 5px 5px rgba(165, 132, 130, 0.1333333333));
  transition: all 0.3s ease;
}

.social-btn:hover svg {
  fill: #f55d56;
  transform: scale(1.2);
}

.button {
  background: white;
  color: #fbb9b6;
  border: none;
  border-radius: 20px;
  font-size: 0.6rem;
  padding: 0.4rem 0.6rem;
  box-shadow: rgba(165, 132, 130, 0.1333333333) 0px 5px 5px 0px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.button:hover {
  background: #f55d56;
  color: white;
}
</style>

