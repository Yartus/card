<template>
  <section class="shop-direct-block">
    <!-- 标题区域（可选） -->
    <div v-if="title" class="section-header">
      <h3 class="section-title">{{ title }}</h3>
      <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
    </div>
    
    <!-- 网店列表 -->
    <div class="module-body">
      <div
        v-for="shop in enabledShops"
        :key="shop.id"
        class="shop-card"
        @click="handleShopClick(shop)"
      >
        <div class="shop-image-wrapper">
          <img :src="shop.image" :alt="shop.name" class="shop-image" />
          <div class="shop-overlay">
            <div class="shop-info">
              <h4 class="shop-name">{{ shop.name }}</h4>
              <span class="shop-platform">{{ getPlatformLabel(shop) }}</span>
            </div>
            <div class="shop-action">
              <i class="icon-arrow-right">→</i>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ShopDirectBlock',
  
  props: {
    title: {
      type: String,
      default: ''
    },
    subtitle: {
      type: String,
      default: ''
    },
    shops: {
      type: Array,
      default: () => []
    }
  },
  
  computed: {
    enabledShops() {
      return this.shops.filter(s => s.enabled !== false)
    }
  },
  
  methods: {
    async handleShopClick(shop) {
      try {
        // 动态导入 shop-handler（避免循环依赖）
        const shopHandler = await import('@/utils/shop-handler')
        await shopHandler.default.openShop(shop)
      } catch (error) {
        console.error('网店唤醒失败:', error)
        this.$toast?.error('无法打开网店，请稍后重试')
      }
    },
    
    getPlatformLabel(shop) {
      const labels = {
        tmall: '天猫',
        jd: '京东',
        pdd: '拼多多',
        '1688': '1688',
        taobao: '淘宝',
        miniprogram: '微信小程序',
        wechat_shop: '微信小店',
        custom: shop.platformName || '其他平台'
      }
      return labels[shop.platform] || shop.platformName || shop.platform
    }
  }
}
</script>

<style lang="scss" scoped>
// 素材库块样式规范：独立模块，有圆角和边框
.shop-direct-block {
  padding: 20px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  
  .section-header {
    padding: 0 0 16px 0;
    border-bottom: 1px solid #f0f2f5;
    margin-bottom: 16px;
  }
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #262626;
    margin: 0 0 6px 0;
    line-height: 1.4;
  }
  
  .section-subtitle {
    font-size: 14px;
    color: #8c8c8c;
    margin: 0;
    line-height: 1.6;
  }
  
  .module-body {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  // 网店卡片样式（复用 ShopDirect.vue）
  .shop-card {
    position: relative;
    width: 100%;
    height: 120px;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,.12);
    }
  }
  
  .shop-image-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
  }
  
  .shop-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 12px;
    display: block;
  }
  
  .shop-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 16px 20px;
    background: linear-gradient(to top, rgba(0,0,0,.7), transparent);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .shop-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .shop-name {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
    line-height: 1.4;
  }
  
  .shop-platform {
    font-size: 12px;
    color: rgba(255,255,255,.9);
    line-height: 1.4;
  }
  
  .shop-action {
    color: #ffffff;
    font-size: 18px;
    line-height: 1;
  }
  
  // 响应式
  @media (max-width: 768px) {
    .shop-card {
      height: 100px;
    }
    
    .shop-name {
      font-size: 15px;
    }
  }
}
</style>

