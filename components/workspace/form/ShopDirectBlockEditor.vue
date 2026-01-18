<template>
  <div class="shop-direct-block-editor">
    <!-- 标题（可选） -->
    <TextInput
      v-model="localData.title"
      label="模块标题（可选）"
      placeholder="网店直达"
      @input="emitUpdate"
    />
    
    <!-- 副标题（可选） -->
    <TextInput
      v-model="localData.subtitle"
      type="textarea"
      label="模块描述（可选）"
      placeholder="点击进入我们的官方店铺"
      :rows="2"
      @input="emitUpdate"
    />
    
    <!-- 网店列表 -->
    <div class="shops-section">
      <div class="section-header">
        <h4 class="section-title">网店列表</h4>
        <button 
          class="btn-add-shop" 
          :disabled="!canAddShop"
          @click="addShop"
        >
          <i class="icon-plus">+</i> 添加网店
        </button>
      </div>
      
      <!-- 配额提示 -->
      <div v-if="quotaInfo" class="quota-hint" :class="quotaClass">
        <i class="icon-info">ℹ️</i>
        <span>{{ quotaInfo }}</span>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!shops || shops.length === 0" class="empty-shops">
        <p>暂无网店，点击"添加网店"开始配置</p>
      </div>
      
      <!-- 网店列表 -->
      <draggable
        v-else
        v-model="localData.shops"
        class="shops-list"
        handle=".drag-handle"
        @change="emitUpdate"
      >
        <div
          v-for="(shop, index) in localData.shops"
          :key="shop.id"
          class="shop-config-item"
        >
          <div class="shop-header">
            <i class="drag-handle icon-drag">☰</i>
            <span class="shop-index">网店 {{ index + 1 }}</span>
            <span class="shop-platform-badge">{{ getPlatformLabel(shop.platform) }}</span>
            <button class="btn-remove-shop" @click="removeShop(index)">
              <i class="icon-delete">×</i>
            </button>
          </div>
          
          <div class="shop-body">
            <!-- 网店名称 -->
            <TextInput
              v-model="localData.shops[index].name"
              label="网店名称"
              placeholder="天猫旗舰店 / 京东自营店"
              :required="true"
              @input="emitUpdate"
            />
            
            <!-- 平台选择器 -->
            <div class="form-group">
              <label class="form-label">平台类型</label>
              <div class="platform-selector">
                <div
                  v-for="platform in platformOptions"
                  :key="platform.value"
                  class="platform-option"
                  :class="{ active: shop.platform === platform.value }"
                  @click="selectPlatform(index, platform.value)"
                >
                  <span class="platform-icon">{{ platform.icon }}</span>
                  <span class="platform-name">{{ platform.label }}</span>
                </div>
              </div>
            </div>
            
            <!-- 横版图片上传 -->
            <ImageUpload
              v-model="localData.shops[index].image"
              label="横版展示图"
              :required="true"
              hint="建议尺寸：800x200px，支持 JPG、PNG，自动压缩到500KB"
              @change="emitUpdate"
            />
            
            <!-- 自定义平台名称（仅custom平台显示） -->
            <TextInput
              v-if="shop.platform === 'custom'"
              v-model="localData.shops[index].platformName"
              label="平台名称"
              placeholder="例如：1688、唯品会、苏宁易购等"
              :required="true"
              hint="输入自定义平台名称"
              @input="emitUpdate"
            />
            
            <!-- 电商平台配置 -->
            <template v-if="isAppPlatform(shop.platform)">
              <TextInput
                v-model="localData.shops[index].appScheme"
                type="url"
                label="APP唤醒链接"
                :placeholder="getAppSchemePlaceholder(shop.platform)"
                :hint="getAppSchemeHint(shop.platform)"
                @input="emitUpdate"
              />
              
              <TextInput
                v-model="localData.shops[index].webUrl"
                type="url"
                label="H5备用链接"
                :placeholder="getWebUrlPlaceholder(shop.platform)"
                :required="true"
                hint="APP未安装时降级使用的网页链接（必填）"
                @input="emitUpdate"
              />
            </template>
            
            <!-- 小程序/小店配置 -->
            <template v-if="['miniprogram', 'wechat_shop'].includes(shop.platform)">
              <TextInput
                v-model="localData.shops[index].appId"
                label="小程序AppID"
                placeholder="wx1234567890abcdef"
                :required="true"
                hint="在微信公众平台获取，格式：wx开头"
                @input="emitUpdate"
              />
              
              <TextInput
                v-model="localData.shops[index].path"
                label="页面路径（可选）"
                placeholder="pages/index/index?id=123"
                hint="不填则打开小程序首页"
                @input="emitUpdate"
              />
              
              <TextInput
                v-model="localData.shops[index].urlScheme"
                type="url"
                label="URL Scheme（可选）"
                placeholder="weixin://dl/business/?t=TOKEN"
                hint="用于外部环境唤醒"
                @input="emitUpdate"
              />
              
              <ImageUpload
                v-model="localData.shops[index].qrCode"
                label="小程序码（推荐）"
                hint="用于降级方案，建议尺寸：430x430px"
                @change="emitUpdate"
              />
            </template>
          </div>
        </div>
      </draggable>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import TextInput from './TextInput.vue'
import ImageUpload from './ImageUpload.vue'
import uploadSecurityMixin from '../config/upload-security-mixin'

export default {
  name: 'ShopDirectBlockEditor',
  
  mixins: [uploadSecurityMixin],
  
  components: {
    draggable,
    TextInput,
    ImageUpload
  },
  
  props: {
    blockIndex: {
      type: Number,
      required: true
    },
    blockData: {
      type: Object,
      required: true
    }
  },
  
  data() {
    // 初始化数据
    const blockData = this.blockData || {}
    const data = blockData.data || {}
    
    return {
      localData: {
        title: data.title || '网店直达',
        subtitle: data.subtitle || '',
        shops: Array.isArray(data.shops) ? data.shops.map(shop => ({
          id: shop.id || `shop-${Date.now()}-${Math.random()}`,
          name: shop.name || '',
          platform: shop.platform || 'tmall',
          image: shop.image || '',
          enabled: shop.enabled !== undefined ? shop.enabled : true,
          ...shop
        })) : []
      },
      
      platformOptions: [
        { value: 'tmall', label: '天猫', icon: '🛍️' },
        { value: 'jd', label: '京东', icon: '📦' },
        { value: 'pdd', label: '拼多多', icon: '🎁' },
        { value: '1688', label: '1688', icon: '🏭' },
        { value: 'taobao', label: '淘宝', icon: '🛒' },
        { value: 'miniprogram', label: '微信小程序', icon: '📱' },
        { value: 'wechat_shop', label: '微信小店', icon: '🛒' },
        { value: 'custom', label: '其他平台', icon: '🔗' }
      ]
    }
  },
  
  computed: {
    shops() {
      return this.localData.shops || []
    },
    
    maxShops() {
      const plan = this.$store.state.workspace?.tenantInfo?.plan || 'free'
      const limits = {
        free: 2,
        trial: 2,
        pro: 3,
        enterprise: 3
      }
      return limits[plan] || 2
    },
    
    remainingSlots() {
      return Math.max(0, this.maxShops - this.shops.length)
    },
    
    canAddShop() {
      return this.shops.length < this.maxShops
    },
    
    quotaInfo() {
      if (this.remainingSlots === 0) {
        return `已添加 ${this.shops.length}/${this.maxShops} 个网店（已达上限）`
      }
      if (this.remainingSlots <= 1) {
        return `已添加 ${this.shops.length}/${this.maxShops} 个网店（还可添加${this.remainingSlots}个）`
      }
      return null
    },
    
    quotaClass() {
      return {
        'quota-warning': this.remainingSlots <= 1,
        'quota-full': this.remainingSlots === 0
      }
    }
  },
  
  watch: {
    blockData: {
      deep: true,
      handler(newData) {
        if (newData && newData.data) {
          this.localData = {
            title: newData.data.title || '网店直达',
            subtitle: newData.data.subtitle || '',
            shops: Array.isArray(newData.data.shops) ? newData.data.shops.map(shop => ({
              id: shop.id || `shop-${Date.now()}-${Math.random()}`,
              name: shop.name || '',
              platform: shop.platform || 'tmall',
              image: shop.image || '',
              enabled: shop.enabled !== undefined ? shop.enabled : true,
              ...shop
            })) : []
          }
        }
      }
    }
  },
  
  methods: {
    // 实现 upload-security-mixin 要求的方法
    getImageCount() {
      let count = 0
      this.shops.forEach(shop => {
        if (shop.image) count++
        if (shop.qrCode) count++
      })
      return count
    },
    
    emitUpdate() {
      this.$emit('update', this.localData)
    },
    
    addShop() {
      if (!this.canAddShop) {
        this.$toast?.warning(`最多只能添加${this.maxShops}个网店`)
        return
      }
      
      const frequencyCheck = this.checkUploadFrequency()
      if (!frequencyCheck.allowed) {
        this.$toast?.warning(`操作过于频繁，请${frequencyCheck.remaining}秒后再试`)
        return
      }
      
      if (!this.localData.shops) {
        this.$set(this.localData, 'shops', [])
      }
      
      const newShop = {
        id: `shop-${Date.now()}-${Math.random()}`,
        name: '',
        platform: 'tmall',
        image: '',
        enabled: true
      }
      
      this.localData.shops.push(newShop)
      this.updateUploadTimestamp()
      this.emitUpdate()
    },
    
    removeShop(index) {
      if (confirm('确定要删除这个网店吗？')) {
        this.localData.shops.splice(index, 1)
        this.emitUpdate()
      }
    },
    
    selectPlatform(index, platform) {
      if (!this.localData.shops || !this.localData.shops[index]) return
      if (this.localData.shops[index].platform === platform) return
      
      this.$set(this.localData.shops[index], 'platform', platform)
      
      // 根据平台填充默认值
      const defaults = {
        tmall: { appScheme: '', webUrl: '' },
        jd: { appScheme: '', webUrl: '' },
        pdd: { appScheme: '', webUrl: '' },
        '1688': { appScheme: '', webUrl: '' },
        taobao: { appScheme: '', webUrl: '' },
        miniprogram: { appId: '', path: '', urlScheme: '' },
        wechat_shop: { appId: '', path: '', urlScheme: '' },
        custom: { platformName: '', appScheme: '', webUrl: '' }
      }
      
      const defaultValues = defaults[platform] || {}
      Object.keys(defaultValues).forEach(key => {
        if (!this.localData.shops[index][key]) {
          this.$set(this.localData.shops[index], key, defaultValues[key])
        }
      })
      
      this.emitUpdate()
    },
    
    isAppPlatform(platform) {
      return !['miniprogram', 'wechat_shop'].includes(platform)
    },
    
    getPlatformLabel(platform) {
      const labels = {
        tmall: '天猫',
        jd: '京东',
        pdd: '拼多多',
        '1688': '1688',
        taobao: '淘宝',
        miniprogram: '微信小程序',
        wechat_shop: '微信小店',
        custom: '其他平台'
      }
      return labels[platform] || platform
    },
    
    getAppSchemePlaceholder(platform) {
      const placeholders = {
        tmall: 'tmall://page.tm/shop?shopId=12345678',
        jd: 'openapp.jdmobile://virtual?params={"category":"jump","des":"jshop","shopId":"123456"}',
        pdd: 'yangkeduo://com.xunmeng.pinduoduo/duo_course_mall?mall_id=123456',
        '1688': 'ali1688://shop?id=123456',
        taobao: 'taobao://shop?id=123456',
        custom: 'your-app://shop?id=xxx'
      }
      return placeholders[platform] || 'app://scheme?params=xxx'
    },
    
    getAppSchemeHint(platform) {
      const hints = {
        tmall: '格式：tmall://page.tm/shop?shopId=店铺ID',
        jd: '格式：openapp.jdmobile://virtual?params={"category":"jump","des":"jshop","shopId":"店铺ID"}',
        pdd: '格式：yangkeduo://com.xunmeng.pinduoduo/duo_course_mall?mall_id=店铺ID',
        '1688': '格式：ali1688://shop?id=店铺ID',
        taobao: '格式：taobao://shop?id=店铺ID',
        custom: '输入自定义平台的APP唤醒链接'
      }
      return hints[platform] || '输入APP唤醒链接'
    },
    
    getWebUrlPlaceholder(platform) {
      const placeholders = {
        tmall: 'https://shop12345678.taobao.com/',
        jd: 'https://shop.m.jd.com/?shopId=123456',
        pdd: 'https://mobile.yangkeduo.com/mall_page.html?mall_id=123456',
        '1688': 'https://shop123456.1688.com/',
        taobao: 'https://shop123456.taobao.com/',
        custom: 'https://your-shop.com/'
      }
      return placeholders[platform] || 'https://your-shop.com/'
    }
  }
}
</script>

<style lang="scss" scoped>
.shop-direct-block-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shops-section {
  margin-top: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.btn-add-shop {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.quota-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
  border-radius: 6px;
  font-size: 12px;
  
  &.quota-warning {
    background: #fffbe6;
    border: 1px solid #ffe58f;
    color: #d46b08;
  }
  
  &.quota-full {
    background: #fff1f0;
    border: 1px solid #ffccc7;
    color: #cf1322;
  }
}

.empty-shops {
  padding: 40px 20px;
  text-align: center;
  background: #fafafa;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  color: #8c8c8c;
  font-size: 13px;
}

.shops-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shop-config-item {
  background: #f8f9ff;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  padding: 16px;
}

.shop-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.drag-handle {
  font-size: 16px;
  color: #bfbfbf;
  cursor: move;
  
  &:hover {
    color: #667eea;
  }
}

.shop-index {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #262626;
}

.shop-platform-badge {
  padding: 4px 8px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 4px;
  font-size: 12px;
  color: #667eea;
  font-weight: 500;
}

.btn-remove-shop {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff1f0;
  border: none;
  border-radius: 4px;
  color: #ff4d4f;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #ff4d4f;
    color: white;
  }
}

.shop-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.platform-selector {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 8px;
}

.platform-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba(102, 126, 234, 0.5);
    background: rgba(102, 126, 234, 0.05);
  }
  
  &.active {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.1);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
}

.platform-icon {
  font-size: 24px;
}

.platform-name {
  font-size: 12px;
  font-weight: 500;
  color: #262626;
  text-align: center;
}

.form-group {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .platform-selector {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

