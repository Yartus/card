<template>
  <div class="social-links">
    <div class="section-header">
      <h3 class="section-title">社交媒体</h3>
    </div>
    
    <div class="social-grid">
      <a
        v-for="social in filteredSocial"
        :key="social.platform"
        :href="social.url"
        target="_blank"
        rel="noopener noreferrer"
        class="social-item"
        @click="handleSocialClick(social)"
      >
        <div class="social-icon">
          <i :class="getSocialIcon(social.platform)"></i>
        </div>
        <span class="social-label">{{ social.platform }}</span>
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SocialLinks',
  
  props: {
    socialData: {
      type: Array,
      required: true,
      default: () => []
    },
    // 区域：cn（默认，仅展示国内常用平台）| global（全部展示）
    region: {
      type: String,
      default: 'cn'
    },
    // 允许额外展示的平台白名单
    allowPlatforms: {
      type: Array,
      default: () => []
    }
  },
  
  computed: {
    filteredSocial() {
      if (!Array.isArray(this.socialData)) return []
      if (this.region !== 'cn') return this.socialData
      const domestic = new Set(['WeChat', '微博', 'Weibo', '小红书', 'Xiaohongshu', '知乎', 'Zhihu', '抖音', 'Douyin'])
      return this.socialData.filter(s => domestic.has(s.platform) || this.allowPlatforms.includes(s.platform))
    }
  },
  
  methods: {
    handleSocialClick(social) {
      this.$emit('social-click', social)
    },
    
    getSocialIcon(platform) {
      const iconMap = {
        'LinkedIn': 'icon-linkedin',
        'WeChat': 'icon-wechat',
        'Weibo': 'icon-weibo',
        '微博': 'icon-weibo',
        'Dribbble': 'icon-dribbble',
        'Behance': 'icon-behance',
        'GitHub': 'icon-github',
        'Twitter': 'icon-twitter',
        'Facebook': 'icon-facebook',
        'Instagram': 'icon-instagram',
        'YouTube': 'icon-youtube',
        'TikTok': 'icon-tiktok',
        '抖音': 'icon-tiktok',
        '小红书': 'icon-xiaohongshu',
        'Xiaohongshu': 'icon-xiaohongshu',
        '知乎': 'icon-zhihu',
        'Zhihu': 'icon-zhihu'
      }
      
      return iconMap[platform] || 'icon-link'
    }
  }
}
</script>

<style lang="scss" scoped>
.social-links {
  padding: 0; /* ✅ 内容区域padding由内部元素控制 */
  background: #ffffff;
  margin: 12px 16px; /* ✅ 遵循设计规范：外边距12px 16px */
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,.08);
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}

.section-header {
  padding: 20px 20px 16px 20px; /* ✅ 遵循设计规范：统一内边距 */
  border-bottom: 1px solid #f0f2f5;
  margin-bottom: 0; /* padding已包含间距 */
}

.section-title {
  font-size: 16px; /* ✅ 遵循设计规范：标题16px */
  font-weight: 600;
  color: #262626;
  margin: 0 0 6px 0; /* ✅ 遵循设计规范：标题与副标题间距6px */
  line-height: 1.4;
}

.social-grid {
  padding: 20px; /* ✅ 遵循设计规范：内容区域统一内边距20px */
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
}

.social-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: var(--primary-color, #1890FF);
  }
}

.social-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--primary-color, #1890FF);
  color: white;
  
  i {
    font-size: 20px;
  }
}

.social-label {
  font-size: 12px;
  color: #595959;
  text-align: center;
  font-weight: 500;
}

// 特定平台的颜色
.social-item:nth-child(1) .social-icon { background: #0077B5; } // LinkedIn
.social-item:nth-child(2) .social-icon { background: #1AAD19; } // WeChat
.social-item:nth-child(3) .social-icon { background: #E6162D; } // Weibo
.social-item:nth-child(4) .social-icon { background: #EA4C89; } // Dribbble
.social-item:nth-child(5) .social-icon { background: #1769FF; } // Behance
.social-item:nth-child(6) .social-icon { background: #181717; } // GitHub

// 响应式设计
@media (max-width: 480px) {
  .social-links {
    padding: 16px;
  }
  
  .social-grid {
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 8px;
  }
  
  .social-item {
    padding: 12px 6px;
  }
  
  .social-icon {
    width: 32px;
    height: 32px;
    
    i {
      font-size: 16px;
    }
  }
  
  .social-label {
    font-size: 11px;
  }
}

// 图标字体（简化版本）
.icon-linkedin::before { content: "💼"; }
.icon-wechat::before { content: "💬"; }
.icon-weibo::before { content: "🐦"; }
.icon-dribbble::before { content: "🎨"; }
.icon-behance::before { content: "🎭"; }
.icon-github::before { content: "👨‍💻"; }
.icon-twitter::before { content: "🐦"; }
.icon-facebook::before { content: "📘"; }
.icon-instagram::before { content: "📷"; }
.icon-youtube::before { content: "📺"; }
.icon-tiktok::before { content: "🎵"; }
.icon-xiaohongshu::before { content: "📖"; }
.icon-zhihu::before { content: "🤔"; }
.icon-link::before { content: "🔗"; }
</style>
