<template>
  <div class="config-section header-bg-config">
    <div class="section-header">
      <h3 class="section-title">
        <span class="icon">🎨</span>
        名片头部背景设置
      </h3>
      <p class="section-desc">
        自定义名片头部的背景样式，打造专属品牌形象
      </p>
    </div>

    <div class="section-body">
      <!-- 背景类型选择 -->
      <div class="bg-type-selector">
        <button
          v-for="type in bgTypes"
          :key="type.value"
          :class="['type-btn', { active: localConfig.backgroundType === type.value }]"
          @click="selectType(type.value)"
        >
          <span class="type-icon">{{ type.icon }}</span>
          <span class="type-label">{{ type.label }}</span>
        </button>
      </div>

      <!-- 渐变色配置 -->
      <div v-if="localConfig.backgroundType === 'gradient'" class="gradient-config">
        <div class="color-pickers">
          <div class="color-picker-group">
            <label class="picker-label">起始颜色</label>
            <div class="picker-wrapper">
              <input
                v-model="localConfig.gradientStart"
                type="color"
                class="color-input"
                @input="handleChange"
              />
              <input
                v-model="localConfig.gradientStart"
                type="text"
                class="color-text"
                placeholder="#667eea"
                @input="handleChange"
              />
            </div>
          </div>
          
          <div class="color-picker-group">
            <label class="picker-label">结束颜色</label>
            <div class="picker-wrapper">
              <input
                v-model="localConfig.gradientEnd"
                type="color"
                class="color-input"
                @input="handleChange"
              />
              <input
                v-model="localConfig.gradientEnd"
                type="text"
                class="color-text"
                placeholder="#764ba2"
                @input="handleChange"
              />
            </div>
          </div>
        </div>

        <!-- 渐变方向 -->
        <div class="gradient-angle">
          <label class="angle-label">渐变方向</label>
          <div class="angle-buttons">
            <button
              v-for="angle in gradientAngles"
              :key="angle.value"
              :class="['angle-btn', { active: localConfig.gradientAngle === angle.value }]"
              @click="selectAngle(angle.value)"
            >
              <span class="angle-icon">{{ angle.icon }}</span>
              <span class="angle-text">{{ angle.label }}</span>
            </button>
          </div>
        </div>

        <!-- 预设配色 -->
        <div class="preset-colors">
          <label class="preset-label">快速配色</label>
          <div class="preset-buttons">
            <button
              v-for="preset in colorPresets"
              :key="preset.name"
              class="preset-btn"
              :style="{ background: `linear-gradient(135deg, ${preset.start} 0%, ${preset.end} 100%)` }"
              @click="applyPreset(preset)"
            >
              <span class="preset-name">{{ preset.name }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 图片上传配置 -->
      <div v-else-if="localConfig.backgroundType === 'image'" class="image-config">
        <div class="image-upload-area">
          <div v-if="localConfig.backgroundImage" class="image-preview-large">
            <img :src="localConfig.backgroundImage" alt="背景图" />
            <button class="remove-image" @click="removeImage">
              <i class="icon-close"></i>
            </button>
          </div>
          
          <div v-else class="upload-placeholder">
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleImageUpload"
            />
            <button class="upload-btn" @click="$refs.fileInput.click()">
              <i class="icon-upload"></i>
              <span>点击上传背景图片</span>
            </button>
            <p class="upload-hint">建议尺寸：750x400px，支持JPG/PNG格式，文件小于2MB</p>
          </div>

          <div class="image-url-input">
            <label class="url-label">或输入图片URL</label>
            <input
              v-model="localConfig.backgroundImage"
              type="url"
              class="url-input"
              placeholder="https://example.com/background.jpg"
              @input="handleChange"
            />
          </div>
        </div>
      </div>

      <!-- 纯色配置 -->
      <div v-else-if="localConfig.backgroundType === 'solid'" class="solid-config">
        <div class="color-picker-group">
          <label class="picker-label">背景颜色</label>
          <div class="picker-wrapper">
            <input
              v-model="localConfig.solidColor"
              type="color"
              class="color-input"
              @input="handleChange"
            />
            <input
              v-model="localConfig.solidColor"
              type="text"
              class="color-text"
              placeholder="#667eea"
              @input="handleChange"
            />
          </div>
        </div>

        <!-- 纯色预设 -->
        <div class="preset-colors">
          <label class="preset-label">快速选色</label>
          <div class="solid-preset-buttons">
            <button
              v-for="color in solidPresets"
              :key="color.value"
              class="solid-preset-btn"
              :style="{ background: color.value }"
              @click="applySolidPreset(color.value)"
            >
              <span class="check-icon" v-if="localConfig.solidColor === color.value">✓</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 实时预览 -->
      <div class="preview-section">
        <label class="preview-label">实时预览</label>
        <div class="preview-card" :style="previewStyle">
          <div class="preview-content">
            <div class="preview-avatar"></div>
            <div class="preview-info">
              <div class="preview-name">张三</div>
              <div class="preview-title">产品经理</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HeaderBackgroundConfig',
  
  props: {
    value: {
      type: Object,
      default: () => ({
        backgroundType: 'gradient',
        gradientStart: '#667eea',
        gradientEnd: '#764ba2',
        gradientAngle: 135,
        backgroundImage: '',
        solidColor: '#667eea'
      })
    }
  },
  
  data() {
    return {
      localConfig: { ...this.value },
      bgTypes: [
        { value: 'gradient', icon: '🌈', label: '渐变色' },
        { value: 'image', icon: '🖼️', label: '上传图片' },
        { value: 'solid', icon: '🎨', label: '纯色' }
      ],
      gradientAngles: [
        { value: 135, icon: '↘', label: '左上到右下' },
        { value: 45, icon: '↗', label: '左下到右上' },
        { value: 90, icon: '→', label: '左到右' },
        { value: 180, icon: '↓', label: '上到下' }
      ],
      colorPresets: [
        { name: '紫色科技', start: '#667eea', end: '#764ba2' },
        { name: '蓝色海洋', start: '#2196F3', end: '#00BCD4' },
        { name: '绿色清新', start: '#4CAF50', end: '#8BC34A' },
        { name: '橙色活力', start: '#FF9800', end: '#FF5722' },
        { name: '粉色梦幻', start: '#E91E63', end: '#9C27B0' },
        { name: '红色激情', start: '#F44336', end: '#E91E63' },
        { name: '青色科技', start: '#00BCD4', end: '#3F51B5' },
        { name: '金色奢华', start: '#FFD700', end: '#FF8C00' }
      ],
      solidPresets: [
        { value: '#667eea', name: '紫色' },
        { value: '#2196F3', name: '蓝色' },
        { value: '#4CAF50', name: '绿色' },
        { value: '#FF9800', name: '橙色' },
        { value: '#E91E63', name: '粉色' },
        { value: '#9C27B0', name: '紫红' },
        { value: '#00BCD4', name: '青色' },
        { value: '#F44336', name: '红色' }
      ]
    }
  },
  
  computed: {
    previewStyle() {
      const { backgroundType, gradientStart, gradientEnd, gradientAngle, backgroundImage, solidColor } = this.localConfig
      
      if (backgroundType === 'gradient') {
        return {
          background: `linear-gradient(${gradientAngle}deg, ${gradientStart} 0%, ${gradientEnd} 100%)`
        }
      } else if (backgroundType === 'image' && backgroundImage) {
        return {
          backgroundImage: `url(${backgroundImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }
      } else if (backgroundType === 'solid') {
        return {
          background: solidColor
        }
      }
      
      return {}
    }
  },
  
  watch: {
    value: {
      handler(newVal) {
        this.localConfig = { ...newVal }
      },
      deep: true
    }
  },
  
  methods: {
    selectType(type) {
      this.localConfig.backgroundType = type
      this.handleChange()
    },
    
    selectAngle(angle) {
      this.localConfig.gradientAngle = angle
      this.handleChange()
    },
    
    applyPreset(preset) {
      this.localConfig.gradientStart = preset.start
      this.localConfig.gradientEnd = preset.end
      this.handleChange()
      this.$toast?.success(`已应用 ${preset.name}`)
    },
    
    applySolidPreset(color) {
      this.localConfig.solidColor = color
      this.handleChange()
    },
    
    handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件大小
      if (file.size > 2 * 1024 * 1024) {
        this.$toast?.error('图片大小不能超过2MB')
        return
      }
      
      // 这里应该上传到服务器，暂时使用本地预览
      const reader = new FileReader()
      reader.onload = (e) => {
        this.localConfig.backgroundImage = e.target.result
        this.handleChange()
        this.$toast?.success('图片上传成功')
      }
      reader.readAsDataURL(file)
    },
    
    removeImage() {
      this.localConfig.backgroundImage = ''
      this.handleChange()
    },
    
    handleChange() {
      this.$emit('input', { ...this.localConfig })
    }
  }
}
</script>

<style lang="scss" scoped>
.header-bg-config {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 8px 0;
}

.section-title .icon {
  font-size: 24px;
}

.section-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

/* 背景类型选择器 */
.bg-type-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.type-btn {
  padding: 16px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.type-btn:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.type-btn.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.type-icon {
  font-size: 32px;
}

.type-label {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

/* 渐变色配置 */
.gradient-config,
.solid-config {
  margin-bottom: 24px;
}

.color-pickers {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.color-picker-group {
  background: white;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.picker-label, .angle-label, .preset-label, .url-label, .preview-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  display: block;
  margin-bottom: 8px;
}

.picker-wrapper {
  display: flex;
  gap: 8px;
}

.color-input {
  width: 60px;
  height: 42px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
}

.color-text {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: monospace;
}

.color-text:focus {
  outline: none;
  border-color: #667eea;
}

/* 渐变方向 */
.gradient-angle {
  margin-bottom: 20px;
}

.angle-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.angle-btn {
  padding: 12px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.angle-btn:hover {
  border-color: #667eea;
}

.angle-btn.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.angle-icon {
  font-size: 20px;
}

.angle-text {
  font-size: 11px;
  color: #64748b;
}

/* 预设配色 */
.preset-colors {
  margin-bottom: 20px;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.preset-btn {
  height: 60px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-end;
  padding: 8px;
  position: relative;
  overflow: hidden;
}

.preset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.preset-name {
  font-size: 11px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

/* 纯色预设 */
.solid-preset-buttons {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
}

.solid-preset-btn {
  width: 100%;
  aspect-ratio: 1;
  border: 3px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.solid-preset-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.check-icon {
  color: white;
  font-size: 18px;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 图片上传 */
.image-config {
  margin-bottom: 24px;
}

.upload-placeholder {
  background: white;
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  margin-bottom: 16px;
}

.upload-btn {
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.icon-upload::before {
  content: '📤';
}

.upload-hint {
  font-size: 13px;
  color: #94a3b8;
  margin: 12px 0 0 0;
}

.image-preview-large {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
  
  img {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }
}

.remove-image {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.remove-image:hover {
  background: rgba(239, 68, 68, 0.9);
  transform: scale(1.1);
}

.icon-close::before {
  content: '✕';
  font-size: 18px;
}

.url-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
}

.url-input:focus {
  outline: none;
  border-color: #667eea;
}

/* 预览 */
.preview-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px dashed #e2e8f0;
}

.preview-card {
  height: 180px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  position: relative;
}

.preview-content {
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 1;
}

.preview-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.preview-info {
  color: white;
}

.preview-name {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.preview-title {
  font-size: 14px;
  opacity: 0.95;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
</style>

