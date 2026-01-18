<template>
  <div class="config-section logo-config">
    <div class="section-header">
      <h3 class="section-title">
        <span class="icon">🏢</span>
        公司Logo设置
      </h3>
      <p class="section-desc">
        上传公司Logo，将显示在员工名片中，增强品牌识别度
      </p>
    </div>

    <div class="section-body">
      <!-- Logo上传区域 -->
      <div class="logo-upload-section">
        <h4 class="settings-title">头部Logo</h4>
        
        <ImageUpload
          v-model="localConfig.logoUrl"
          label=""
          hint="建议尺寸：200x60px，支持PNG、SVG透明背景"
          :max-size="1 * 1024 * 1024"
          @change="handleChange"
        />
        
        <div class="logo-type-hint">
          <i class="icon-info">ℹ️</i>
          <span>支持JPG、PNG、SVG格式，建议使用透明背景PNG或SVG以获得最佳效果</span>
        </div>
      </div>

      <!-- Logo显示设置 -->
      <div class="display-settings">
        <h4 class="settings-title">头部Logo设置</h4>
        
        <div class="toggle-list">
          <div class="toggle-item">
            <div class="toggle-info">
              <div class="toggle-label">
                <i class="icon-header"></i>
                在名片头部显示Logo
              </div>
              <div class="toggle-hint">显示在公司名称旁边</div>
            </div>
            <label class="switch">
              <input
                v-model="localConfig.showInHeader"
                type="checkbox"
                @change="handleChange"
              />
              <span class="slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- 底部品牌横幅配置 -->
      <div class="footer-logo-settings">
        <h4 class="settings-title">底部品牌横幅</h4>
        
        <!-- 开关 -->
        <div class="toggle-item">
          <div class="toggle-info">
            <div class="toggle-label">
              <i class="icon-footer"></i>
              显示底部品牌横幅
            </div>
            <div class="toggle-hint">Logo图标 + Slogan组合展示</div>
          </div>
          <label class="switch">
            <input
              v-model="localConfig.showInFooter"
              type="checkbox"
              @change="handleChange"
            />
            <span class="slider"></span>
          </label>
        </div>

        <!-- 品牌横幅配置 -->
        <div v-if="localConfig.showInFooter" class="footer-logo-config">
          <!-- Logo图标 -->
          <div class="config-group">
            <label class="url-label">
              <i class="icon-image"></i>
              品牌图标
            </label>
            <p class="config-hint">留空则使用头部Logo</p>
            
            <ImageUpload
              v-model="localConfig.footerLogoUrl"
              label=""
              hint="建议尺寸：64x64px，支持PNG、SVG透明背景"
              :max-size="500 * 1024"
              @change="handleChange"
            />
          </div>

          <!-- Slogan文字 -->
          <div class="config-group">
            <label class="url-label">
              <i class="icon-text"></i>
              品牌口号 (Slogan)
            </label>
            <input
              v-model="localConfig.footerSlogan"
              type="text"
              class="text-input"
              placeholder="例如：创新引领未来 · 品质成就卓越"
              maxlength="50"
              @input="handleChange"
            />
            <div class="char-count">{{ (localConfig.footerSlogan || '').length }}/50</div>
          </div>

          <!-- Logo尺寸 -->
          <div class="footer-size-settings">
            <label class="size-label">图标高度</label>
            <div class="size-slider">
              <input
                v-model.number="localConfig.footerLogoSize"
                type="range"
                min="20"
                max="48"
                step="2"
                class="slider-input"
                @input="handleChange"
              />
              <div class="size-value">{{ localConfig.footerLogoSize }}px</div>
            </div>
          </div>

          <!-- 预览效果 -->
          <div class="footer-preview">
            <div class="footer-preview-banner">
              <!-- Lottie动画 -->
              <LottieIcon
                v-if="(localConfig.footerLogoType === 'lottie' || localConfig.logoType === 'lottie') && (localConfig.footerLogoUrl || localConfig.logoUrl)"
                :animation-data="localConfig.footerLogoUrl || localConfig.logoUrl"
                :width="localConfig.footerLogoSize"
                :height="localConfig.footerLogoSize"
                :autoplay="true"
                :loop="true"
                class="footer-preview-icon"
              />
              <!-- 图片 -->
              <img 
                v-else-if="localConfig.footerLogoUrl || localConfig.logoUrl"
                :src="localConfig.footerLogoUrl || localConfig.logoUrl" 
                alt="品牌图标"
                :style="{ height: localConfig.footerLogoSize + 'px' }"
                class="footer-preview-icon"
              />
              <span class="footer-preview-text">
                {{ localConfig.footerSlogan || '在此输入品牌口号' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Logo尺寸设置 -->
      <div class="size-settings">
        <h4 class="settings-title">头部Logo尺寸</h4>
        
        <div class="size-slider">
          <input
            v-model.number="localConfig.logoSize"
            type="range"
            min="30"
            max="100"
            step="5"
            class="slider-input"
            @input="handleChange"
          />
          <div class="size-value">{{ localConfig.logoSize }}px</div>
        </div>

        <div class="size-presets">
          <button
            v-for="size in headerSizePresets"
            :key="size.value"
            :class="['size-btn', { active: localConfig.logoSize === size.value }]"
            @click="selectHeaderSize(size.value)"
          >
            {{ size.label }}
          </button>
        </div>
      </div>

      <!-- 名片预览已移至右侧统一预览区 -->
    </div>
  </div>
</template>

<script>
import ImageUpload from '../form/ImageUpload.vue'
import LottieIcon from '@/components/LottieIcon.vue'

export default {
  name: 'LogoConfig',
  
  components: {
    ImageUpload,
    LottieIcon
  },
  
  props: {
    value: {
      type: Object,
      default: () => ({
        logoUrl: '',  // 头部Logo URL
        logoType: 'image',  // 头部Logo类型（image/lottie）
        showInHeader: true,
        showInFooter: true,
        logoSize: 60,  // 头部Logo尺寸
        footerLogoUrl: '',  // 底部品牌图标（独立）
        footerLogoType: 'image',  // 底部Logo类型（image/lottie）
        footerSlogan: '',  // 底部品牌口号
        footerLogoSize: 32  // 底部图标尺寸
      })
    },
    // 接收头部背景配置用于预览
    headerBackground: {
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
      headerSizePresets: [
        { value: 30, label: '小' },
        { value: 50, label: '中' },
        { value: 70, label: '大' },
        { value: 100, label: '特大' }
      ]
    }
  },
  
  computed: {
    // 计算头部预览的背景样式
    previewHeaderStyle() {
      const { backgroundType, gradientStart, gradientEnd, gradientAngle, backgroundImage, solidColor } = this.headerBackground
      
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
      
      // 默认渐变
      return {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }
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
    selectHeaderSize(size) {
      this.localConfig.logoSize = size
      this.handleChange()
    },
    
    handleChange() {
      this.$emit('input', { ...this.localConfig })
    }
  }
}
</script>

<style lang="scss" scoped>
.logo-config {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

/* Logo类型提示 */
.logo-type-hint {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  font-size: 12px;
  line-height: 1.6;
  color: #64748b;
  
  i {
    font-size: 14px;
    flex-shrink: 0;
  }
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

/* Logo上传区域 */
.logo-upload-section {
  margin-bottom: 28px;
}

.current-logo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: white;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  margin-bottom: 16px;
}

.logo-preview {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  border: 2px dashed #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  
  img {
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
  }
}

.remove-btn {
  padding: 10px 20px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.icon-trash::before {
  content: '🗑️';
}

.upload-area {
  background: white;
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 16px;
  text-align: center;
}

.upload-logo-btn {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px 48px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 2px dashed #667eea;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-logo-btn:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-color: #764ba2;
  transform: translateY(-2px);
}

.icon-upload-big::before {
  content: '📤';
  font-size: 48px;
}

.upload-text {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.upload-hint {
  font-size: 13px;
  color: #64748b;
}

/* URL输入 */
.logo-url-section {
  background: white;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.url-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  display: block;
  margin-bottom: 8px;
}

.url-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.url-input {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
}

.url-input:focus {
  outline: none;
  border-color: #667eea;
}

.clear-btn {
  width: 36px;
  height: 36px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.clear-btn:hover {
  background: #ef4444;
  color: white;
}

.icon-close::before {
  content: '✕';
  font-size: 16px;
}

/* 显示设置 */
.display-settings,
.size-settings {
  margin-bottom: 28px;
}

.settings-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.toggle-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.toggle-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.toggle-info {
  flex: 1;
}

.toggle-label {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-hint {
  font-size: 12px;
  color: #64748b;
}

/* 开关 */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: 0.3s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

input:checked + .slider {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

input:checked + .slider:before {
  transform: translateX(22px);
}

/* 尺寸设置 */
.size-slider {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  margin-bottom: 12px;
}

.slider-input {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  -webkit-appearance: none;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.4);
}

.size-value {
  font-size: 16px;
  font-weight: 700;
  color: #667eea;
  min-width: 60px;
  text-align: center;
}

.size-presets {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.size-btn {
  padding: 10px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
}

.size-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.size-btn.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
}

/* 名片预览 */
.card-preview {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.preview-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

.preview-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.preview-name-section {
  flex: 1;
}

.preview-name {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.preview-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.preview-logo-header {
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  padding: 8px;
  backdrop-filter: blur(10px);
}

.preview-middle {
  padding: 32px 24px;
  display: flex;
  justify-content: center;
  border-bottom: 1px solid #e2e8f0;
}

.preview-logo-middle {
  border-radius: 12px;
  background: #f8fafc;
  padding: 12px;
}

.preview-footer {
  padding: 20px 24px;
  background: #f8fafc;
}

.preview-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.preview-btn {
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
}

.preview-footer-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  
  img {
    opacity: 0.6;
  }
}

.company-text {
  font-size: 13px;
  color: #94a3b8;
}

/* 底部品牌横幅配置区域 */
.footer-logo-settings {
  margin-top: 28px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.footer-logo-config {
  margin-top: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.config-group {
  margin-bottom: 20px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.url-label,
.size-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
  
  i {
    font-size: 14px;
  }
}

.config-hint {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
  margin-top: -4px;
}

.text-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #94a3b8;
  }
}

.char-count {
  text-align: right;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.footer-size-settings {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

/* 底部横幅预览 */
.footer-preview {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}

.footer-preview-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.footer-preview-icon {
  flex-shrink: 0;
  object-fit: contain;
  opacity: 0.9;
}

.footer-preview-text {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  line-height: 1.5;
  
  &:empty::before {
    content: '在此输入品牌口号';
    color: #cbd5e1;
  }
}

/* 图标 */
.icon-header::before { content: '📋'; }
.icon-card::before { content: '💳'; }
.icon-footer::before { content: '🔖'; }
.icon-close::before { content: '✕'; }
.icon-image::before { content: '🖼️'; }
.icon-text::before { content: '✏️'; }
</style>

