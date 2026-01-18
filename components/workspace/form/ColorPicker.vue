<template>
  <div class="color-picker">
    <label v-if="label" class="picker-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <div class="picker-container">
      <!-- 颜色预览 -->
      <div 
        class="color-preview" 
        :style="{ backgroundColor: value }"
        @click="togglePicker"
      >
        <span class="color-value">{{ value || '选择颜色' }}</span>
      </div>
      
      <!-- 预设颜色 -->
      <div v-if="showPresets" class="preset-colors">
        <div
          v-for="color in presetColors"
          :key="color"
          class="preset-item"
          :class="{ active: value === color }"
          :style="{ backgroundColor: color }"
          @click="selectColor(color)"
        />
      </div>
      
      <!-- 原生颜色选择器 -->
      <input
        ref="colorInput"
        type="color"
        :value="value || '#00ffaa'"
        class="native-picker"
        @input="handleColorChange"
      />
    </div>
    
    <p v-if="hint" class="hint-message">{{ hint }}</p>
  </div>
</template>

<script>
export default {
  name: 'ColorPicker',
  
  props: {
    value: {
      type: String,
      default: ''
    },
    label: {
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
    },
    showPresets: {
      type: Boolean,
      default: true
    },
    presets: {
      type: Array,
      default: () => []
    }
  },
  
  computed: {
    presetColors() {
      if (this.presets.length > 0) {
        return this.presets
      }
      
      // 默认预设颜色（科幻风格）
      return [
        '#00ffaa', // 主色调
        '#ff1744', // 强调色
        '#00e5ff', // 辅助色1
        '#ffea00', // 辅助色2
        '#1a1a2e', // 深色
        '#16213e', // 深色2
        '#0f3460', // 蓝色
        '#533483', // 紫色
        '#f7f7f7', // 浅色
        '#e94560', // 红色
      ]
    }
  },
  
  methods: {
    togglePicker() {
      this.$refs.colorInput.click()
    },
    
    handleColorChange(event) {
      const color = event.target.value
      this.$emit('input', color)
      this.$emit('change', color)
    },
    
    selectColor(color) {
      this.$emit('input', color)
      this.$emit('change', color)
    }
  }
}
</script>

<style scoped>
.color-picker {
  width: 100%;
  margin-bottom: 16px;
}

.picker-label {
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

.picker-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.color-preview {
  height: 48px;
  border: 2px solid rgba(0, 255, 170, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.color-preview:hover {
  border-color: #00ffaa;
  box-shadow: 0 0 0 3px rgba(0, 255, 170, 0.1);
}

.color-value {
  font-size: 14px;
  font-weight: 500;
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.5);
  color: #fff;
  mix-blend-mode: difference;
}

.preset-colors {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 8px;
}

.preset-item {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.preset-item:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.preset-item.active {
  border-color: #fff;
  box-shadow: 0 0 0 2px #00ffaa;
}

.native-picker {
  display: none;
}

.hint-message {
  color: #666;
  font-size: 12px;
  margin-top: 4px;
}
</style>

