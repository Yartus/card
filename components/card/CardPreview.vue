<template>
  <div class="card-preview-container">
    <div 
      class="card" 
      :class="{ 'card-hover': isHovered }" 
      @mouseenter="isHovered = true" 
      @mouseleave="isHovered = false"
      @touchstart="isHovered = true"
      @touchend="isHovered = false"
    >
      <!-- 拨打电话按钮（右上角） -->
      <button class="phone-btn" :style="phoneIconStyle" @click="handlePhoneClick" v-if="contactInfo.mobile">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
        </svg>
      </button>

      <!-- 头像区域 -->
      <div class="profile-pic" :style="{ ...profilePicStyle, ...avatarBorderStyle }">
        <img
          v-if="displayAvatar"
          :src="displayAvatar"
          :alt="basicInfo.name"
          @error="handleAvatarError"
        />
        <!-- 不显示占位符，保持空白 -->
      </div>

        <!-- 底部信息区 -->
        <div class="bottom" :style="bottomStyle">
          <!-- 文字内容（只在hover时显示） -->
          <div class="content" v-if="isHovered">
            <span class="name">{{ basicInfo.name || '未设置' }}</span>
            <span class="about-me">{{ displayIntro }}</span>
          </div>
          <!-- 按钮区域（始终显示） -->
          <div class="bottom-bottom">
            <div class="social-links-container">
              <!-- 分享名片 -->
              <button class="social-btn" @click="handleShare" title="分享名片">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="18" cy="5" r="3"></circle>
                  <circle cx="6" cy="12" r="3"></circle>
                  <circle cx="18" cy="19" r="3"></circle>
                  <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                  <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                </svg>
              </button>
              <!-- WhatsApp -->
              <a class="social-btn" :href="whatsappUrl" target="_blank" title="WhatsApp" v-if="contactInfo.mobile">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.375a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .96 4.534.96 10.09c0 1.76.413 3.421 1.15 4.888L.03 23.876l9.135-2.389a11.714 11.714 0 005.885 1.577h.005c5.554 0 10.09-4.535 10.09-10.09 0-2.902-1.19-5.515-3.122-7.405"/>
                </svg>
              </a>
            </div>
            <button class="button" @click="handleContactMe">查看详情</button>
          </div>
        </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardPreview',
  
  props: {
    cardData: {
      type: Object,
      required: true,
      default: () => ({})
    },
    cardUrl: {
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
    basicInfo() {
      return this.cardData.basic_info || {}
    },
    
    contactInfo() {
      return this.cardData.contact_info || {}
    },
    
    avatarConfig() {
      return this.cardData.avatar_config || {}
    },
    
    // 显示的头像（根据avatarMode：公司统一图片或员工照片）
    displayAvatar() {
      const cardPreviewConfig = this.cardData.card_preview_config || {}
      const avatarMode = cardPreviewConfig.avatarMode || this.avatarConfig.avatarMode || 'company'
      
      if (avatarMode === 'company') {
        // 公司统一图片模式
        return cardPreviewConfig.companyAvatar || this.avatarConfig.companyAvatar || ''
      } else {
        // 员工照片模式，使用企微头像
        return this.avatarConfig.wecomAvatar || this.basicInfo.avatar || ''
      }
    },
    
    // 头像占位符文字
    avatarText() {
      const name = this.basicInfo.name || '未设置'
      return name.length > 2 ? name.substring(0, 2) : name
    },
    
    // 是否有背景图片
    hasBackgroundImage() {
      const cardPreviewConfig = this.cardData.card_preview_config || {}
      const headerBackground = this.cardData.header_background || {}
      const bgType = cardPreviewConfig.backgroundType || headerBackground.backgroundType || 'image'
      if (bgType === 'image') {
        return !!(cardPreviewConfig.backgroundImage || headerBackground.backgroundImage)
      }
      return false
    },
    
    // 个人介绍（优先使用个人介绍，其次公司介绍）
    displayIntro() {
      // 优先使用个人介绍
      if (this.cardData.personal_intro) {
        return this.cardData.personal_intro
      }
      // 其次使用公司介绍
      return this.cardData.company_intro || this.basicInfo.slogan || '欢迎了解我的更多信息'
    },
    
    // WhatsApp链接
    whatsappUrl() {
      const mobile = this.contactInfo.mobile
      if (!mobile) return ''
      // 移除所有非数字字符
      const cleanMobile = mobile.replace(/\D/g, '')
      // WhatsApp链接格式：https://wa.me/国家代码+号码
      // 如果是中国号码（11位），需要添加86
      if (cleanMobile.length === 11 && cleanMobile.startsWith('1')) {
        return `https://wa.me/86${cleanMobile}`
      }
      return `https://wa.me/${cleanMobile}`
    },
    
    // 主题颜色（统一用于底部、电话图标、头像边框）
    themeColor() {
      const cardPreviewConfig = this.cardData.card_preview_config || {}
      return cardPreviewConfig.themeColor || '#fbb9b6'
    },
    
    // 底部样式（使用主题颜色）
    bottomStyle() {
      return {
        backgroundColor: this.themeColor
      }
    },
    
    // 电话图标样式（使用主题颜色）
    phoneIconStyle() {
      return {
        '--phone-icon-color': this.themeColor
      }
    },
    
    // 头像边框样式（使用主题颜色）
    avatarBorderStyle() {
      return {
        '--avatar-border-color': this.themeColor
      }
    },
    
    // 头像区域背景样式（使用卡片预览配置）
    profilePicStyle() {
      const cardPreviewConfig = this.cardData.card_preview_config || {}
      const headerBackground = this.cardData.header_background || {}
      
      // 优先使用卡片预览配置（推送卡片不支持SVG，只支持图片和纯色）
      const bgType = cardPreviewConfig.backgroundType || headerBackground.backgroundType || 'image'
      
      let background = ''
      
      if (bgType === 'image') {
        // 图片背景
        const bgImage = cardPreviewConfig.backgroundImage || headerBackground.backgroundImage || ''
        if (bgImage) {
          background = `url(${bgImage}) center/cover`
        } else {
          background = 'linear-gradient(135deg, #fff8f6 0%, #fef0ef 50%, #fde4e1 100%)'
        }
      } else if (bgType === 'solid') {
        // 纯色背景
        background = cardPreviewConfig.backgroundColor || headerBackground.backgroundColor || '#f5f5f5'
      } else {
        // 默认渐变
        background = 'linear-gradient(135deg, #fff8f6 0%, #fef0ef 50%, #fde4e1 100%)'
      }
      
      return {
        background
      }
    }
  },
  
  methods: {
    handleAvatarError(e) {
      e.target.style.display = 'none'
      const placeholder = e.target.nextElementSibling
      if (placeholder) {
        placeholder.style.display = 'flex'
      }
    },
    
    handlePhoneClick() {
      const mobile = this.contactInfo.mobile
      if (!mobile) return
      
      // 在企业微信环境中使用企微API
      if (this.isWecomEnv && window.wx) {
        try {
          window.wx.invoke('makePhoneCall', {
            number: mobile
          })
        } catch (e) {
          console.error('调用企微拨号失败:', e)
          this.fallbackPhoneCall(mobile)
        }
      } else {
        this.fallbackPhoneCall(mobile)
      }
    },
    
    fallbackPhoneCall(mobile) {
      // 移动端直接拨号
      if (/Mobile|Android|iPhone|iPad/i.test(navigator.userAgent)) {
        window.location.href = `tel:${mobile}`
      } else {
        // PC端复制到剪贴板
        this.copyToClipboard(mobile)
        this.showToast('电话号码已复制到剪贴板')
      }
    },
    
    handleShare() {
      this.$emit('share', {
        cardUrl: this.cardUrl,
        name: this.basicInfo.name,
        title: this.basicInfo.title
      })
    },
    
    handleContactMe() {
      // 跳转到完整名片页面（查看详情）
      // 从当前URL中提取tenantId和memberId
      const pathParts = window.location.pathname.split('/')
      const previewIndex = pathParts.indexOf('card-preview')
      if (previewIndex !== -1 && pathParts.length > previewIndex + 2) {
        const tenantId = pathParts[previewIndex + 1]
        const memberId = pathParts[previewIndex + 2]
        window.location.href = `/card/${tenantId}/${memberId}`
      } else if (this.cardUrl) {
        window.location.href = this.cardUrl
      } else {
        this.$emit('contact-me')
      }
    },
    
    copyToClipboard(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(err => {
          console.error('复制失败:', err)
        })
      } else {
        // 降级方案
        const textarea = document.createElement('textarea')
        textarea.value = text
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        try {
          document.execCommand('copy')
        } catch (err) {
          console.error('复制失败:', err)
        }
        document.body.removeChild(textarea)
      }
    },
    
    showToast(message) {
      // 简单的提示，可以替换为更完善的toast组件
      if (this.$toast) {
        this.$toast.success(message)
      } else {
        alert(message)
      }
    },
    
    get isWecomEnv() {
      return /wxwork/i.test(navigator.userAgent)
    }
  }
}
</script>

<style lang="scss" scoped>
.card-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
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
  background: linear-gradient(135deg, #fff8f6 0%, #fef0ef 50%, #fde4e1 100%);
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
  font-size: 48px;
  font-weight: bold;
  color: #fbb9b6;
  background: linear-gradient(135deg, #fff8f6 0%, #fef0ef 50%, #fde4e1 100%);
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
  background: #fbb9b6;
  top: 80%;
  border-radius: 29px;
  z-index: 2;
  box-shadow: rgba(96, 75, 74, 0.1882352941) 0px 5px 5px 0px inset;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.645, 0.045, 0.355, 1) 0s;
}

.card-hover .bottom {
  top: 20%;
  border-radius: 80px 29px 29px 29px;
  transition: all 0.5s cubic-bezier(0.645, 0.045, 0.355, 1) 0.2s;
}

.bottom .content {
  position: absolute;
  bottom: 0;
  left: 1.5rem;
  right: 1.5rem;
  height: 160px;
}

.bottom .content .name {
  display: block;
  font-size: 1.2rem;
  color: white;
  font-weight: bold;
}

.bottom .content .about-me {
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
  gap: 1rem;
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
  text-transform: uppercase;
}

.button:hover {
  background: #f55d56;
  color: white;
  transform: translateY(-2px);
  box-shadow: rgba(165, 132, 130, 0.3) 0px 8px 12px 0px;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .card {
    width: 320px;
    height: 320px;
  }
  
  .phone-btn {
    right: 1.5rem;
    top: 1.2rem;
  }
  
  .bottom .content {
    padding-bottom: 70px;
  }
  
  .bottom .content .name {
    font-size: 1.3rem;
  }
  
  .bottom .content .title {
    font-size: 1rem;
  }
  
  .bottom .content .about-me {
    font-size: 0.9rem;
  }
}
</style>

