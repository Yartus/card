<template>
  <div class="icon-selector">
    <label v-if="label" class="selector-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <div class="selector-container">
      <!-- 当前选中的图标 -->
      <div class="current-icon" @click="showModal = true">
        <div v-if="selectedIcon" class="icon-display">
          <LottieIcon
            v-if="selectedIcon.type === 'lottie' && selectedIcon.animation"
            :animation-data="selectedIcon.animation"
            :width="32"
            :height="32"
            :autoplay="true"
            :loop="true"
          />
          <i v-else-if="selectedIcon.type === 'emoji'" class="emoji-icon">
            {{ selectedIcon.value }}
          </i>
          <i v-else :class="selectedIcon.value" class="css-icon"></i>
        </div>
        <span v-else class="placeholder">选择图标</span>
        <i class="icon-chevron-down"></i>
      </div>
    </div>
    
    <!-- 图标选择弹窗 -->
    <transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>选择图标</h3>
            <button class="btn-close" @click="showModal = false">×</button>
          </div>
          
          <div class="modal-body">
            <!-- 图标类型选择 -->
            <div class="icon-types">
              <button
                v-for="type in iconTypes"
                :key="type.value"
                class="type-btn"
                :class="{ active: currentType === type.value }"
                @click="currentType = type.value"
              >
                {{ type.label }}
              </button>
            </div>
            
            <!-- Emoji 图标 -->
            <div v-if="currentType === 'emoji'" class="emoji-grid">
              <div
                v-for="emoji in emojiList"
                :key="emoji"
                class="emoji-item"
                :class="{ selected: value === emoji }"
                @click="selectIcon({ type: 'emoji', value: emoji })"
              >
                {{ emoji }}
              </div>
            </div>
            
            <!-- CSS 图标 -->
            <div v-if="currentType === 'css'" class="icon-grid">
              <div
                v-for="icon in cssIcons"
                :key="icon"
                class="icon-item"
                :class="{ selected: value === icon }"
                @click="selectIcon({ type: 'css', value: icon })"
              >
                <i :class="icon"></i>
              </div>
            </div>
            
            <!-- Lottie 动画 -->
            <div v-if="currentType === 'lottie'" class="lottie-grid">
              <div
                v-for="lottie in lottieList"
                :key="lottie.name"
                class="lottie-item"
                :class="{ selected: value === lottie.name }"
                @click="selectLottie(lottie)"
              >
                <LottieIcon
                  v-if="lottie.animation"
                  :animation-data="lottie.animation"
                  :width="48"
                  :height="48"
                  :autoplay="true"
                  :loop="true"
                />
                <span class="lottie-name">{{ lottie.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import LottieIcon from '~/components/LottieIcon.vue'

export default {
  name: 'IconSelector',
  
  components: {
    LottieIcon
  },
  
  props: {
    value: {
      type: String,
      default: ''
    },
    label: {
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
      showModal: false,
      currentType: 'emoji',
      selectedIcon: null,
      
      iconTypes: [
        { label: 'Emoji', value: 'emoji' },
        { label: 'CSS图标', value: 'css' },
        { label: 'Lottie动画', value: 'lottie' }
      ],
      
      // Emoji 列表
      emojiList: [
        '📱', '💼', '🏢', '📧', '🌐', '📞', '📍', '🔗',
        '⭐', '🎯', '🚀', '💡', '🔥', '✨', '🎨', '📊',
        '👥', '💬', '📸', '🎬', '🎵', '📚', '🏆', '🎁',
        '💰', '📈', '🔒', '⚙️', '🌟', '💎', '🎪', '🌈'
      ],
      
      // CSS 图标类名列表（根据实际项目调整）
      cssIcons: [
        'icon-phone', 'icon-email', 'icon-location', 'icon-user',
        'icon-company', 'icon-star', 'icon-heart', 'icon-share',
        'icon-link', 'icon-globe', 'icon-message', 'icon-camera',
        'icon-video', 'icon-music', 'icon-file', 'icon-folder'
      ],
      
      // Lottie 动画列表
      lottieList: []
    }
  },
  
  async mounted() {
    // 加载 Lottie 动画列表
    await this.loadLottieAnimations()
    
    // 初始化选中的图标
    if (this.value) {
      this.initializeIcon()
    }
  },
  
  methods: {
    async loadLottieAnimations() {
      // 这里可以从配置文件或API加载动画列表
      this.lottieList = [
        { name: 'phone-ring', label: '电话动画', animation: null },
        { name: 'share-float', label: '分享动画', animation: null }
      ]
    },
    
    initializeIcon() {
      // 根据 value 判断图标类型
      if (this.emojiList.includes(this.value)) {
        this.selectedIcon = { type: 'emoji', value: this.value }
      } else if (this.cssIcons.includes(this.value)) {
        this.selectedIcon = { type: 'css', value: this.value }
      } else {
        // 假设是 Lottie
        this.selectedIcon = { type: 'lottie', value: this.value }
      }
    },
    
    selectIcon(icon) {
      this.selectedIcon = icon
      this.$emit('input', icon.value)
      this.$emit('change', icon)
      this.showModal = false
    },
    
    async selectLottie(lottie) {
      // 这里可以加载 Lottie 动画数据
      this.selectedIcon = {
        type: 'lottie',
        value: lottie.name,
        animation: lottie.animation
      }
      this.$emit('input', lottie.name)
      this.$emit('change', this.selectedIcon)
      this.showModal = false
    }
  }
}
</script>

<style scoped>
.icon-selector {
  width: 100%;
  margin-bottom: 16px;
}

.selector-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.required {
  color: #ff4757;
  margin-left: 4px;
}

.current-icon {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 170, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.current-icon:hover {
  border-color: #00ffaa;
  background: rgba(255, 255, 255, 0.08);
}

.icon-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.emoji-icon {
  font-size: 24px;
}

.css-icon {
  font-size: 24px;
  color: #00ffaa;
}

.placeholder {
  color: #666;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1a1a2e;
}

.btn-close {
  background: none;
  border: none;
  font-size: 32px;
  color: #666;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.icon-types {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.type-btn {
  padding: 8px 16px;
  background: rgba(0, 255, 170, 0.1);
  border: 1px solid rgba(0, 255, 170, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-btn.active {
  background: #00ffaa;
  color: #fff;
}

.emoji-grid,
.icon-grid,
.lottie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 12px;
}

.emoji-item,
.icon-item,
.lottie-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(0, 255, 170, 0.05);
}

.emoji-item:hover,
.icon-item:hover,
.lottie-item:hover {
  background: rgba(0, 255, 170, 0.1);
  transform: scale(1.05);
}

.emoji-item.selected,
.icon-item.selected,
.lottie-item.selected {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.2);
}

.lottie-item {
  flex-direction: column;
  padding: 8px;
}

.lottie-name {
  font-size: 10px;
  margin-top: 4px;
  text-align: center;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter,
.modal-leave-to {
  opacity: 0;
}
</style>

