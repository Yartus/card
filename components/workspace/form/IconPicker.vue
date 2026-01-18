<template>
  <div class="icon-picker">
    <label v-if="label" class="form-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>

    <!-- 当前选中的图标预览 -->
    <div class="icon-preview-container" @click="togglePicker">
      <div v-if="selectedIcon" class="icon-preview">
        <!-- Emoji -->
        <span v-if="iconType === 'emoji'" class="icon-emoji">
          {{ selectedIcon }}
        </span>
        
        <!-- CSS Icon -->
        <i v-else-if="iconType === 'css'" :class="selectedIcon" class="icon-css"></i>
        
        <!-- SVG Icon -->
        <img
          v-else-if="iconType === 'svg'"
          :src="selectedIcon"
          alt="icon"
          class="icon-svg"
          @error="handleSvgError"
        />
        
        <!-- Lottie Icon -->
        <LottieIcon
          v-else-if="iconType === 'lottie'"
          :animation-data="lottieData"
          :width="32"
          :height="32"
          :autoplay="true"
          :loop="true"
          class="icon-lottie"
        />
      </div>
      
      <div v-else class="icon-placeholder">
        <i class="icon-add"></i>
        <span>{{ placeholder || '选择图标' }}</span>
      </div>
      
      <button type="button" class="btn-change">
        {{ selectedIcon ? '更换' : '选择' }}
      </button>
    </div>

    <!-- 图标选择器弹窗 -->
    <div v-if="showPicker" class="icon-picker-modal" @click.self="closePicker">
      <div class="picker-content">
        <div class="picker-header">
          <h3>选择图标</h3>
          <button class="btn-close" @click="closePicker">
            <i class="icon-close"></i>
          </button>
        </div>

        <!-- 标签切换 -->
        <div class="picker-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.type"
            class="tab-btn"
            :class="{ active: activeTab === tab.type }"
            @click="activeTab = tab.type"
          >
            {{ tab.label }}
            <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
          </button>
        </div>

        <!-- 搜索框（CSS和SVG标签页） -->
        <div v-if="activeTab === 'css' || activeTab === 'svg'" class="picker-search">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索图标名称..."
            class="search-input"
          />
        </div>

        <!-- Emoji类别选择 -->
        <div v-if="activeTab === 'emoji'" class="emoji-categories">
          <button
            v-for="(category, key) in emojiCategories"
            :key="key"
            class="category-btn"
            :class="{ active: activeEmojiCategory === key }"
            @click="activeEmojiCategory = key"
          >
            {{ category.name }}
          </button>
        </div>
        
        <!-- SVG图标类别选择 -->
        <div v-if="activeTab === 'svg'" class="svg-categories">
          <button
            v-for="category in svgCategoryOptions"
            :key="category.key"
            class="category-btn"
            :class="{ active: activeSvgCategory === category.key }"
            @click="activeSvgCategory = category.key"
          >
            {{ category.name }}
            <span class="category-count">({{ category.count }})</span>
          </button>
        </div>

        <!-- 图标列表 -->
        <div class="picker-body">
          <!-- Emoji列表 -->
          <div v-if="activeTab === 'emoji'" class="emoji-grid">
            <button
              v-for="emoji in currentEmojiList"
              :key="emoji"
              class="emoji-item"
              :class="{ selected: selectedIcon === emoji && iconType === 'emoji' }"
              @click="selectIcon('emoji', emoji)"
            >
              {{ emoji }}
            </button>
          </div>

          <!-- CSS图标列表 -->
          <div v-if="activeTab === 'css'" class="css-icon-grid">
            <button
              v-for="icon in filteredCssIcons"
              :key="icon.class"
              class="css-icon-item"
              :class="{ selected: selectedIcon === icon.class && iconType === 'css' }"
              @click="selectIcon('css', icon.class)"
              :title="icon.name"
            >
              <i :class="icon.class"></i>
              <span class="icon-name">{{ icon.name }}</span>
            </button>
          </div>

          <!-- SVG图标列表 -->
          <div v-if="activeTab === 'svg'" class="svg-icon-grid">
            <button
              v-for="icon in filteredSvgIcons"
              :key="icon.file"
              class="svg-icon-item"
              :class="{ selected: selectedIcon === `/icons/${icon.file}` && iconType === 'svg' }"
              @click="selectIcon('svg', `/icons/${icon.file}`)"
              :title="icon.name"
            >
              <img :src="`/icons/${icon.file}`" :alt="icon.name" />
              <span class="icon-name">{{ icon.name }}</span>
            </button>
          </div>

          <!-- Lottie动画列表 -->
          <div v-if="activeTab === 'lottie'" class="lottie-grid">
            <button
              v-for="anim in lottieAnimations"
              :key="anim.key"
              class="lottie-item"
              :class="{ selected: selectedIcon === anim.key && iconType === 'lottie' }"
              @click="selectIcon('lottie', anim.key)"
              :title="anim.name"
            >
              <LottieIcon
                v-if="anim.data"
                :animation-data="anim.data"
                :width="48"
                :height="48"
                :autoplay="true"
                :loop="true"
              />
              <span class="icon-name">{{ anim.name }}</span>
            </button>
          </div>

          <!-- 空状态 -->
          <div v-if="isEmptyState" class="empty-state">
            <p>{{ emptyMessage }}</p>
          </div>
        </div>

        <!-- 底部操作 -->
        <div class="picker-footer">
          <button class="btn-cancel" @click="closePicker">取消</button>
          <button class="btn-confirm" @click="confirmSelection">确定</button>
        </div>
      </div>
    </div>

    <p v-if="hint" class="form-hint">{{ hint }}</p>
  </div>
</template>

<script>
import LottieIcon from '@/components/LottieIcon.vue'
import { 
  SVG_ICONS, 
  CSS_ICONS, 
  EMOJI_CATEGORIES, 
  LOTTIE_ANIMATIONS,
  searchIcons
} from '@/config/icon-library'

export default {
  name: 'IconPicker',
  
  components: {
    LottieIcon
  },
  
  props: {
    value: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: '' // 'emoji', 'css', 'svg', 'lottie'
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    hint: {
      type: String,
      default: ''
    },
    required: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      showPicker: false,
      activeTab: 'emoji',
      searchQuery: '',
      selectedIcon: this.value || '📊',
      iconType: this.type || 'emoji',
      lottieData: null,
      scrollPosition: 0, // 保存滚动位置
      
      // 从配置加载
      emojiCategories: EMOJI_CATEGORIES || {},
      cssIconList: CSS_ICONS || [],
      svgIconList: SVG_ICONS || [],
      lottieAnimations: [],
      
      // 当前选中的emoji类别
      activeEmojiCategory: 'smileys',
      
      // SVG图标分类
      activeSvgCategory: 'all'
    }
  },
  
  computed: {
    tabs() {
      const emojiCount = Object.values(this.emojiCategories).reduce(
        (sum, cat) => sum + cat.emojis.length, 0
      )
      return [
        { type: 'emoji', label: 'Emoji', count: emojiCount },
        { type: 'css', label: 'CSS图标', count: this.cssIconList.length },
        { type: 'svg', label: 'SVG图标', count: this.svgIconList.length },
        { type: 'lottie', label: 'Lottie动画', count: this.lottieAnimations.length }
      ]
    },
    
    currentEmojiList() {
      const category = this.emojiCategories[this.activeEmojiCategory]
      return category ? category.emojis : []
    },
    
    // SVG图标分类列表
    svgCategories() {
      const categories = {}
      this.svgIconList.forEach(icon => {
        const cat = icon.category || 'other'
        if (!categories[cat]) {
          categories[cat] = []
        }
        categories[cat].push(icon)
      })
      return categories
    },
    
    // SVG分类选项（用于显示分类按钮）
    svgCategoryOptions() {
      const categoryNames = {
        'all': '全部',
        'contact': '联系方式',
        'social': '社交媒体',
        'professional': '专业平台',
        'community': '社区论坛',
        'media': '媒体娱乐',
        'payment': '支付商务',
        'delivery': '外卖配送',
        'shopping': '电商购物',
        'other': '其他'
      }
      
      const options = [{ key: 'all', name: '全部', count: this.svgIconList.length }]
      const cats = this.svgCategories
      Object.keys(cats).forEach(key => {
        if (cats[key].length > 0) {
          options.push({
            key,
            name: categoryNames[key] || key,
            count: cats[key].length
          })
        }
      })
      return options
    },
    
    filteredSvgIcons() {
      let icons = this.svgIconList
      
      // 按分类筛选
      if (this.activeSvgCategory !== 'all') {
        icons = icons.filter(icon => icon.category === this.activeSvgCategory)
      }
      
      // 按搜索词筛选
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        icons = icons.filter(icon => 
          icon.name.toLowerCase().includes(query) ||
          icon.file.toLowerCase().includes(query)
        )
      }
      
      return icons
    },
    
    filteredCssIcons() {
      if (!this.searchQuery) {
        return this.cssIconList
      }
      const query = this.searchQuery.toLowerCase()
      return this.cssIconList.filter(icon =>
        icon.name.toLowerCase().includes(query) ||
        icon.class.toLowerCase().includes(query)
      )
    },
    
    isEmptyState() {
      if (this.activeTab === 'emoji') return this.currentEmojiList.length === 0
      if (this.activeTab === 'css') return this.filteredCssIcons.length === 0
      if (this.activeTab === 'svg') return this.filteredSvgIcons.length === 0
      if (this.activeTab === 'lottie') return this.lottieAnimations.length === 0
      return false
    },
    
    emptyMessage() {
      if (this.searchQuery) {
        return '未找到匹配的图标'
      }
      return '暂无可用图标'
    }
  },
  
  watch: {
    value(newVal) {
      this.selectedIcon = newVal || '📊'
    },
    type(newVal) {
      this.iconType = newVal || 'emoji'
    },
    
    async selectedIcon(newVal) {
      // 如果选择的是Lottie动画，加载动画数据
      if (this.iconType === 'lottie' && newVal) {
        await this.loadLottieData(newVal)
      }
    }
  },
  
  async mounted() {
    try {
      // 确保有默认值
      if (!this.selectedIcon) {
        this.selectedIcon = '📊'
      }
      if (!this.iconType) {
        this.iconType = 'emoji'
      }
      
      await this.loadLottieAnimations()
      
      // 如果已有选中的Lottie图标，加载其数据
      if (this.iconType === 'lottie' && this.selectedIcon) {
        await this.loadLottieData(this.selectedIcon)
      }
    } catch (error) {
      console.error('⚠️ IconPicker 初始化失败:', error)
    }
  },
  
  beforeDestroy() {
    // 不需要恢复滚动，因为没有锁定
  },
  
  methods: {
    togglePicker() {
      this.showPicker = !this.showPicker
      
      // 不锁定背景滚动，让Modal容器自己处理滚动
      // 移除了所有body的position:fixed设置
    },
    
    handleSvgError(e) {
      console.warn('SVG图标加载失败:', e.target.src)
      // 可以设置一个默认图标
      e.target.style.display = 'none'
    },
    
    closePicker() {
      this.showPicker = false
      this.searchQuery = ''
      // 不需要恢复滚动，因为没有锁定
    },
    
    selectIcon(type, value) {
      this.iconType = type
      this.selectedIcon = value
    },
    
    confirmSelection() {
      // 防御性检查
      if (!this.selectedIcon) {
        this.$toast?.warning('请先选择一个图标')
        return
      }
      
      try {
        this.$emit('input', this.selectedIcon)
        this.$emit('update:type', this.iconType) // 支持 .sync 修饰符
        this.$emit('change', this.selectedIcon, this.iconType)
        this.closePicker()
      } catch (error) {
        console.error('⚠️ 图标选择确认失败:', error)
        this.$toast?.error('图标选择失败，请重试')
      }
    },
    
    async loadLottieAnimations() {
      try {
        // 从配置加载Lottie动画列表
        this.lottieAnimations = LOTTIE_ANIMATIONS.map(anim => ({ ...anim, data: null }))
        
        // 预加载动画数据
        for (const anim of this.lottieAnimations) {
          try {
            const response = await fetch(`/assets/animations/${anim.path}`)
            if (response.ok) {
              anim.data = await response.json()
            }
          } catch (e) {
            console.warn(`Failed to load animation: ${anim.key}`, e)
          }
        }
      } catch (error) {
        console.warn('Failed to load Lottie animations:', error)
      }
    },
    
    async loadLottieData(key) {
      try {
        const animation = this.lottieAnimations.find(a => a.key === key)
        if (animation && animation.data) {
          this.lottieData = animation.data
        } else {
          // 尝试从LOTTIE_ANIMATIONS配置中查找
          const config = LOTTIE_ANIMATIONS.find(a => a.key === key)
          if (config) {
            const response = await fetch(`/assets/animations/${config.path}`)
            if (response.ok) {
              this.lottieData = await response.json()
            }
          }
        }
      } catch (error) {
        console.warn('Failed to load Lottie data:', error)
        this.lottieData = null
      }
    }
  }
}
</script>

<style scoped>
.icon-picker {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.required {
  color: #ff4444;
  margin-left: 4px;
}

/* 预览容器 */
.icon-preview-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.icon-preview-container:hover {
  border-color: #00ffaa;
}

.icon-preview,
.icon-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-emoji {
  font-size: 32px;
  line-height: 1;
}

.icon-css {
  font-size: 32px;
  color: #1a1a2e;
}

.icon-svg {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.icon-lottie {
  width: 32px;
  height: 32px;
}

.icon-placeholder {
  color: #999;
}

.icon-placeholder .icon-add {
  font-size: 24px;
}

.btn-change {
  padding: 8px 16px;
  background: #00ffaa;
  color: #1a1a2e;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-change:hover {
  background: #00dd99;
}

/* 弹窗 - 优化：始终在当前屏幕居中显示 */
.icon-picker-modal {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99999 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 20px;
  overflow: hidden !important; /* 防止背景滚动 */
  margin: 0 !important;
  transform: none !important;
}

.picker-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh; /* 最高不超过屏幕85% */
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden; /* 内容溢出时由picker-body处理滚动 */
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.picker-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 20px;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: background 0.2s;
}

.btn-close:hover {
  background: #f5f5f5;
}

/* 标签页 */
.picker-tabs {
  display: flex;
  padding: 16px 24px 0;
  gap: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-btn:hover {
  color: #1a1a2e;
}

.tab-btn.active {
  color: #00ffaa;
  border-bottom-color: #00ffaa;
}

.tab-count {
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.tab-btn.active .tab-count {
  background: #00ffaa;
  color: #1a1a2e;
}

/* 搜索框 */
.picker-search {
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #00ffaa;
}

/* Emoji类别选择 */
.emoji-categories,
.svg-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  max-height: 120px;
  overflow-y: auto;
}

.category-btn {
  padding: 6px 12px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.category-btn:hover {
  background: #e8f9f5;
  border-color: #00ffaa;
}

.category-btn.active {
  background: #00ffaa;
  border-color: #00ffaa;
  color: #1a1a2e;
  font-weight: 500;
}

.category-count {
  font-size: 12px;
  opacity: 0.7;
  margin-left: 4px;
}

/* 图标网格 */
.picker-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.emoji-grid,
.css-icon-grid,
.svg-icon-grid,
.lottie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.emoji-item,
.css-icon-item,
.svg-icon-item,
.lottie-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 90px;
}

/* SVG和CSS图标使用深色棋盘格背景，便于查看透明和白色图标 */
.css-icon-item,
.svg-icon-item {
  position: relative;
  background: 
    linear-gradient(45deg, #d8d8d8 25%, transparent 25%),
    linear-gradient(-45deg, #d8d8d8 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #d8d8d8 75%),
    linear-gradient(-45deg, transparent 75%, #d8d8d8 75%);
  background-size: 16px 16px;
  background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
  background-color: #ebebeb;
  border: 2px solid #c0c0c0; /* 加粗边框，让白色图标更清晰 */
}

.emoji-item:hover,
.css-icon-item:hover,
.svg-icon-item:hover,
.lottie-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* hover时为SVG和CSS图标添加浅色覆盖和边框高亮 */
.css-icon-item:hover,
.svg-icon-item:hover {
  background-color: rgba(0, 255, 170, 0.1);
  border-color: #00ffaa;
}

.emoji-item.selected,
.lottie-item.selected {
  background: #00ffaa;
  border-color: #00dd99;
}

/* 选中的SVG和CSS图标使用实色背景，更清晰 */
.css-icon-item.selected,
.svg-icon-item.selected {
  background: #00ffaa !important;
  border-color: #00dd99;
  box-shadow: 0 0 0 3px rgba(0, 255, 170, 0.2);
}

.emoji-item {
  font-size: 32px;
  height: 80px;
}

.css-icon-item i,
.svg-icon-item img {
  font-size: 32px;
  width: 32px;
  height: 32px;
  object-fit: contain;
  /* 为白色/浅色图标添加细微阴影轮廓 */
  filter: drop-shadow(0 0 1px rgba(0, 0, 0, 0.2)) 
          drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.icon-name {
  font-size: 11px;
  color: #666;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 空状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

/* 底部操作 */
.picker-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f0f0f0;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-confirm {
  background: #00ffaa;
  color: #1a1a2e;
}

.btn-confirm:hover {
  background: #00dd99;
}

.form-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #999;
}
</style>

