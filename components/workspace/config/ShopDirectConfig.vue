<template>
  <div class="module-config shop-direct-config">
    <div class="config-section">
      <h4 class="section-title">基础设置</h4>
      
      <TextInput
        v-model="localData.title"
        label="模块标题"
        placeholder="网店直达"
        :required="true"
        hint="显示在模块顶部的标题"
        @input="emitChange"
      />
      
      <TextInput
        v-model="localData.subtitle"
        type="textarea"
        label="模块描述"
        placeholder="点击进入我们的官方店铺"
        :rows="2"
        hint="可选的模块描述文字"
        @input="emitChange"
      />
    </div>
    
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">网店列表</h4>
        <button 
          class="btn-add" 
          :disabled="!canAddShop"
          @click="addShop"
        >
          <i class="icon-plus">+</i> 添加网店
        </button>
      </div>
      
      <!-- 配额提示 -->
      <div class="quota-hint" :class="quotaClass">
        <i class="icon-info">ℹ️</i>
        <span>已添加 {{ shops.length }}/{{ maxShops }} 个网店</span>
        <span v-if="remainingSlots > 0" class="remaining">
          （还可添加{{ remainingSlots }}个）
        </span>
        <span v-else class="full-text">（已达上限）</span>
      </div>
      
      <draggable
        v-model="localData.shops"
        class="shops-list"
        handle=".drag-handle"
        @change="emitChange"
      >
        <div
          v-for="(shop, index) in localData.shops"
          :key="shop.id"
          class="shop-config-card"
        >
          <div class="shop-header">
            <i class="drag-handle icon-drag">☰</i>
            <span class="shop-index">网店 {{ index + 1 }}</span>
            <span class="shop-platform-badge">{{ getPlatformLabel(shop.platform) }}</span>
            <button class="btn-remove" @click="removeShop(index)">
              <i class="icon-delete">×</i>
            </button>
          </div>
          
          <div v-if="localData.shops[index]" class="shop-body">
            <!-- 网店名称 -->
            <TextInput
              v-model="localData.shops[index].name"
              label="网店名称"
              placeholder="天猫旗舰店 / 京东自营店"
              :required="true"
              @input="emitChange"
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
              @change="emitChange"
            />
            
            <!-- 自定义平台名称（仅custom平台显示） -->
            <TextInput
              v-if="shop.platform === 'custom'"
              v-model="localData.shops[index].platformName"
              label="平台名称"
              placeholder="例如：1688、唯品会、苏宁易购等"
              :required="true"
              hint="输入自定义平台名称"
              @input="emitChange"
            />
            
            <!-- 电商平台配置（所有APP唤醒平台，包括自定义平台） -->
            <template v-if="isAppPlatform(shop.platform)">
              <!-- APP Scheme -->
              <TextInput
                v-model="localData.shops[index].appScheme"
                type="url"
                label="APP唤醒链接"
                :placeholder="getAppSchemePlaceholder(shop.platform)"
                :hint="getAppSchemeHint(shop.platform)"
                @input="emitChange"
              />
              
              <!-- H5备用链接 -->
              <TextInput
                v-model="localData.shops[index].webUrl"
                type="url"
                label="H5备用链接"
                :placeholder="getWebUrlPlaceholder(shop.platform)"
                :required="true"
                hint="APP未安装时降级使用的网页链接（必填）"
                @input="emitChange"
              />
              
              <!-- 获取方法提示 -->
              <div class="help-box">
                <div class="help-title">
                  <i class="icon-help">💡</i>
                  <span>如何获取{{ getPlatformLabel(shop.platform) }}店铺唤醒链接？</span>
                </div>
                <div class="help-content">
                  <div v-if="shop.platform === 'tmall'">
                    <p><strong>情况1：数字ID格式URL</strong>（如 <code>https://shop12345678.taobao.com/</code>）</p>
                    <ol>
                      <li>从URL中直接提取店铺ID（数字部分）</li>
                    </ol>
                    <p><strong>情况2：店铺名格式URL</strong>（如 <code>https://baifenbaijj.tmall.com/</code>）</p>
                    <ol>
                      <li>打开店铺首页</li>
                      <li>查看网页源代码（按 <code>Ctrl+U</code>）</li>
                      <li>搜索 <code>shopId</code> 或 <code>shopid</code></li>
                      <li>找到类似 <code>shopId: "12345678"</code> 的内容，提取数字</li>
                    </ol>
                  </div>
                  <div v-else-if="shop.platform === 'jd'">
                    <p><strong>情况1：只有商品链接</strong>（如 <code>https://item.jd.com/100169957987.html</code>）</p>
                    <ol>
                      <li>打开商品页面</li>
                      <li>点击"进店"或"店铺"按钮，进入店铺首页</li>
                      <li>从店铺首页URL提取店铺ID（<code>shopId</code> 参数值）</li>
                    </ol>
                    <p><strong>情况2：已有店铺首页链接</strong>（如 <code>https://shop.m.jd.com/?shopId=123456</code>）</p>
                    <ol>
                      <li>从URL参数中提取 <code>shopId</code> 值</li>
                    </ol>
                    <p><strong>情况3：从商品页面源代码获取</strong></p>
                    <ol>
                      <li>打开商品页面，查看源代码（按 <code>Ctrl+U</code>）</li>
                      <li>搜索 <code>shopId</code> 或 <code>venderId</code></li>
                      <li>提取店铺ID数字</li>
                    </ol>
                  </div>
                  <div v-else>
                    <ol>
                      <li>在浏览器中打开店铺首页，复制URL</li>
                      <li>从URL中提取店铺ID（通常是数字）</li>
                      <li>使用以下格式构建唤醒链接：</li>
                    </ol>
                  </div>
                  <div class="help-example">
                    <strong>{{ getPlatformLabel(shop.platform) }}格式：</strong>
                    <code>{{ getAppSchemeExample(shop.platform) }}</code>
                  </div>
                  <div class="help-link">
                    <a href="/docs/网店APP唤醒链接获取指南.md" target="_blank">📖 查看详细获取指南</a>
                  </div>
                </div>
              </div>
            </template>
            
            <!-- 小程序/小店配置 -->
            <template v-if="['miniprogram', 'wechat_shop'].includes(shop.platform)">
              <!-- 小程序AppID -->
              <TextInput
                v-model="localData.shops[index].appId"
                label="小程序AppID"
                placeholder="wx1234567890abcdef"
                :required="true"
                hint="在微信公众平台获取，格式：wx开头"
                @input="emitChange"
              />
              
              <!-- 小程序页面路径 -->
              <TextInput
                v-model="localData.shops[index].path"
                label="页面路径（可选）"
                placeholder="pages/index/index?id=123"
                hint="不填则打开小程序首页，格式：pages/xxx/xxx?key=value"
                @input="emitChange"
              />
              
              <!-- URL Scheme（可选） -->
              <TextInput
                v-model="localData.shops[index].urlScheme"
                type="url"
                label="URL Scheme（可选）"
                placeholder="weixin://dl/business/?t=TOKEN"
                hint="用于外部环境唤醒，需在微信开放平台生成"
                @input="emitChange"
              />
              
              <!-- 小程序码（降级方案） -->
              <ImageUpload
                v-model="localData.shops[index].qrCode"
                label="小程序码（推荐）"
                hint="用于降级方案，当无法唤醒时显示。建议尺寸：430x430px"
                @change="emitChange"
              />
            </template>
            
            <!-- 启用开关 -->
            <div class="form-group">
              <label class="form-label">
                <input
                  v-model="localData.shops[index].enabled"
                  type="checkbox"
                  @change="emitChange"
                />
                启用此网店
              </label>
            </div>
          </div>
        </div>
      </draggable>
      
      <div v-if="localData.shops.length === 0" class="empty-state">
        <p>暂无网店，点击"添加网店"开始配置</p>
      </div>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import TextInput from '../form/TextInput.vue'
import ImageUpload from '../form/ImageUpload.vue'
import debounceMixin from './debounce-mixin'
import uploadSecurityMixin from './upload-security-mixin'

export default {
  name: 'ShopDirectConfig',
  
  mixins: [debounceMixin, uploadSecurityMixin],
  
  components: {
    draggable,
    TextInput,
    ImageUpload
  },
  
  props: {
    data: {
      type: Object,
      required: true
    }
  },
  
  data() {
    // 确保localData有所有必需的字段和默认值
    const baseData = this._smartClone ? this._smartClone(this.data) : { ...this.data }
    const localData = {
      title: '网店直达',
      subtitle: '',
      shops: [],
      ...baseData // 覆盖默认值
    }
    
    // 确保 shops 是数组
    if (!Array.isArray(localData.shops)) {
      localData.shops = []
    }
    
    // 确保每个 shop 都有必需的字段（防御性初始化）
    localData.shops = localData.shops.map(shop => {
      if (!shop || typeof shop !== 'object') {
        return {
          id: `shop-${Date.now()}-${Math.random()}`,
          name: '',
          platform: 'tmall',
          image: '',
          enabled: true
        }
      }
      // 确保每个 shop 至少有基础字段
      return {
        id: shop.id || `shop-${Date.now()}-${Math.random()}`,
        name: shop.name || '',
        platform: shop.platform || 'tmall',
        image: shop.image || '',
        enabled: shop.enabled !== undefined ? shop.enabled : true,
        ...shop // 保留其他字段
      }
    })
    
    return {
      localData,
      
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
      // 从套餐限制获取
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
    
    quotaClass() {
      return {
        'quota-warning': this.remainingSlots <= 1,
        'quota-full': this.remainingSlots === 0
      }
    }
  },
  
  methods: {
    // 实现 upload-security-mixin 要求的方法
    getImageCount() {
      // 计算所有网店的图片数量（横版图 + 小程序码）
      let count = 0
      this.shops.forEach(shop => {
        if (shop.image) count++
        if (shop.qrCode) count++
      })
      return count
    },
    
    // 添加网店
    addShop() {
      // 安全检查：数量限制
      if (!this.canAddShop) {
        this.$toast?.warning(`最多只能添加${this.maxShops}个网店`)
        return
      }
      
      // 安全检查：上传频率限制
      const frequencyCheck = this.checkUploadFrequency()
      if (!frequencyCheck.allowed) {
        this.$toast?.warning(`操作过于频繁，请${frequencyCheck.remaining}秒后再试`)
        return
      }
      
      // 确保 shops 数组存在
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
      
      this.localData.shops.unshift(newShop) // 添加到数组开头
      
      // 在下一个tick中确保响应式并触发更新
      this.$nextTick(() => {
        if (this.localData.shops[0]) {
          // 强制设置每个属性为响应式
          Object.keys(newShop).forEach(key => {
            this.$set(this.localData.shops[0], key, newShop[key])
          })
        }
        
        this.updateUploadTimestamp()
        this.emitChange()
        
        // 滚动到顶部
        const container = this.$el.querySelector('.shops-list')
        if (container) {
          container.parentElement.scrollTop = 0
        }
      })
    },
    
    // 删除网店
    removeShop(index) {
      // 防御性检查
      if (!this.localData.shops || index < 0 || index >= this.localData.shops.length) {
        console.warn('removeShop: 无效的索引', index)
        return
      }
      
      if (confirm('确定要删除这个网店吗？')) {
        this.localData.shops.splice(index, 1)
        
        // 在下一个tick中触发更新
        this.$nextTick(() => {
          this.emitChange()
        })
      }
    },
    
    // 选择平台
    selectPlatform(index, platform) {
      // 防御性检查
      if (!this.localData.shops || !this.localData.shops[index]) {
        console.warn('selectPlatform: 无效的索引', index)
        return
      }
      
      if (this.localData.shops[index].platform === platform) return
      
      this.$set(this.localData.shops[index], 'platform', platform)
      
      // 根据平台类型自动填充默认值
      const defaults = {
        tmall: {
          appScheme: 'tmall://shop?id=',
          webUrl: 'https://xxx.tmall.com'
        },
        jd: {
          appScheme: 'openapp.jdmobile://virtual?params=',
          webUrl: 'https://xxx.jd.com'
        },
        pdd: {
          appScheme: 'yangkeduo://com.xunmeng.pinduoduo/',
          webUrl: 'https://xxx.pinduoduo.com'
        },
        '1688': {
          appScheme: 'ali1688://shop?id=',
          webUrl: 'https://xxx.1688.com'
        },
        taobao: {
          appScheme: 'taobao://shop?id=',
          webUrl: 'https://xxx.taobao.com'
        },
        miniprogram: {
          appId: '',
          path: '',
          urlScheme: ''
        },
        wechat_shop: {
          appId: '',
          path: '',
          urlScheme: ''
        },
        custom: {
          platformName: '',
          appScheme: '',
          webUrl: ''
        }
      }
      
      // 如果对应字段为空，填充默认值
      const defaultValues = defaults[platform] || {}
      Object.keys(defaultValues).forEach(key => {
        if (!this.localData.shops[index][key]) {
          this.$set(this.localData.shops[index], key, defaultValues[key])
        }
      })
      
      // 微信小店提示
      if (platform === 'wechat_shop') {
        this.$toast?.info('微信小店也是小程序，请配置小程序AppID')
      }
      
      this.emitChange()
    },
    
    // 判断是否为APP唤醒平台（用于模板渲染）
    isAppPlatform(platform) {
      return !['miniprogram', 'wechat_shop'].includes(platform)
    },
    
    // 获取平台标签
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
    
    // 获取APP Scheme占位符
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
    
    // 获取APP Scheme提示
    getAppSchemeHint(platform) {
      const hints = {
        tmall: '格式：tmall://page.tm/shop?shopId=店铺ID（从店铺首页URL获取店铺ID）',
        jd: '格式：openapp.jdmobile://virtual?params={"category":"jump","des":"jshop","shopId":"店铺ID"}',
        pdd: '格式：yangkeduo://com.xunmeng.pinduoduo/duo_course_mall?mall_id=店铺ID',
        '1688': '格式：ali1688://shop?id=店铺ID',
        taobao: '格式：taobao://shop?id=店铺ID',
        custom: '输入自定义平台的APP唤醒链接（URL Scheme）'
      }
      return hints[platform] || '输入APP唤醒链接（URL Scheme）'
    },
    
    // 获取H5链接占位符
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
    },
    
    // 获取APP Scheme示例
    getAppSchemeExample(platform) {
      const examples = {
        tmall: 'tmall://page.tm/shop?shopId=12345678',
        jd: 'openapp.jdmobile://virtual?params={"category":"jump","des":"jshop","shopId":"123456"}',
        pdd: 'yangkeduo://com.xunmeng.pinduoduo/duo_course_mall?mall_id=123456',
        '1688': 'ali1688://shop?id=123456',
        taobao: 'taobao://shop?id=123456',
        custom: 'your-app://shop?id=xxx'
      }
      return examples[platform] || 'app://scheme?params=xxx'
    }
  }
}
</script>

<style scoped>
.module-config {
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
}

.config-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #e0e0e0;
}

.config-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 16px 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

/* 按钮样式 */
.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-add:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 配额提示 */
.quota-hint {
  padding: 10px 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-left: 3px solid #667eea;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.quota-hint.quota-warning {
  background: rgba(255, 152, 0, 0.1);
  border-left-color: #ff9800;
}

.quota-hint.quota-full {
  background: rgba(244, 67, 54, 0.1);
  border-left-color: #f44336;
}

.quota-hint .remaining {
  color: #667eea;
  font-weight: 500;
}

.quota-hint .full-text {
  color: #f44336;
  font-weight: 600;
}

/* 网店列表 */
.shops-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shop-config-card {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}

.shop-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e0e0e0;
}

.drag-handle {
  cursor: move;
  color: #8c8c8c;
  font-size: 18px;
  user-select: none;
}

.shop-index {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.shop-platform-badge {
  padding: 4px 8px;
  background: rgba(0, 255, 170, 0.2);
  color: #00aa7a;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
}

.btn-remove {
  padding: 6px;
  background: none;
  border: none;
  color: #ff4757;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 18px;
  line-height: 1;
}

.btn-remove:hover {
  background: rgba(255, 71, 87, 0.1);
}

.shop-body {
  padding: 20px;
}

/* 平台选择器 */
.platform-selector {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.platform-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.platform-option:hover {
  border-color: rgba(0, 255, 170, 0.5);
  background: rgba(0, 255, 170, 0.05);
}

.platform-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.1);
  box-shadow: 0 0 0 3px rgba(0, 255, 170, 0.1);
}

.platform-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.platform-name {
  font-size: 13px;
  font-weight: 500;
  color: #1a1a2e;
  text-align: center;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
  cursor: pointer;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #666;
  background: #fff;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 帮助提示框 */
.help-box {
  margin-top: 16px;
  padding: 16px;
  background: #f0f7ff;
  border: 1px solid #91d5ff;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.help-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #1890ff;
}

.icon-help {
  font-size: 18px;
}

.help-content {
  font-size: 13px;
  color: #595959;
  line-height: 1.8;
}

.help-content ol {
  margin: 0 0 12px 20px;
  padding: 0;
}

.help-content li {
  margin-bottom: 6px;
}

.help-example {
  margin: 12px 0;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
}

.help-example strong {
  display: block;
  margin-bottom: 8px;
  color: #262626;
  font-size: 13px;
}

.help-example code {
  display: block;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #d73027;
  word-break: break-all;
  line-height: 1.6;
}

.help-link {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #d9d9d9;
}

.help-link a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #1890ff;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s ease;
}

.help-link a:hover {
  color: #40a9ff;
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 1200px) {
  .platform-selector {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .platform-selector {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .shop-body {
    padding: 16px;
  }
  
  .help-box {
    padding: 12px;
  }
  
  .help-example code {
    font-size: 11px;
  }
}
</style>

