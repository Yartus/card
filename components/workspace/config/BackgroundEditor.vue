<template>
  <div class="background-editor">
    <div class="editor-header">
      <h3 class="editor-title">
        <span class="icon">🎨</span>
        背景编辑器
      </h3>
      <p class="editor-desc">可视化编辑名片头部背景，支持SVG图案、图片、纯色三种模式</p>
    </div>

    <div class="editor-body">
      <!-- 背景类型选择 -->
      <div class="type-tabs">
        <button
          v-for="type in bgTypes"
          :key="type.value"
          :class="['type-tab', { active: localConfig.backgroundType === type.value }]"
          @click="selectType(type.value)"
        >
          <span class="tab-icon">{{ type.icon }}</span>
          <span class="tab-label">{{ type.label }}</span>
        </button>
      </div>

      <!-- SVG图案编辑器 -->
      <div v-if="localConfig.backgroundType === 'svg'" class="svg-editor">
        <!-- 预设图案选择 -->
        <div class="pattern-presets">
          <label class="section-label">选择图案样式</label>
          <div class="preset-grid">
            <button
              v-for="pattern in svgPatterns"
              :key="pattern.id"
              :class="['pattern-btn', { active: localConfig.svgPattern === pattern.id }]"
              @click="selectPattern(pattern.id)"
            >
              <div class="pattern-preview" v-html="pattern.preview"></div>
              <span class="pattern-name">{{ pattern.name }}</span>
            </button>
          </div>
        </div>

        <!-- 渐变配置 -->
        <div class="gradient-settings">
          <label class="section-label">渐变颜色</label>
          <div class="color-pickers-row">
            <div class="color-picker-item">
              <label>起始色</label>
              <div class="color-input-group">
                <input
                  v-model="localConfig.svgGradientStart"
                  type="color"
                  class="color-picker"
                  @input="handleChange"
                />
                <input
                  v-model="localConfig.svgGradientStart"
                  type="text"
                  class="color-text"
                  placeholder="#ffffff"
                  @input="handleChange"
                />
              </div>
            </div>
            <div class="color-picker-item">
              <label>结束色</label>
              <div class="color-input-group">
                <input
                  v-model="localConfig.svgGradientEnd"
                  type="color"
                  class="color-picker"
                  @input="handleChange"
                />
                <input
                  v-model="localConfig.svgGradientEnd"
                  type="text"
                  class="color-text"
                  placeholder="#FC726E"
                  @input="handleChange"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 图案参数调整 -->
        <div class="pattern-params">
          <label class="section-label">图案参数</label>
          <div class="param-item">
            <label>图案密度</label>
            <input
              v-model.number="localConfig.svgDensity"
              type="range"
              min="50"
              max="300"
              step="10"
              class="param-slider"
              @input="handleChange"
            />
            <span class="param-value">{{ localConfig.svgDensity }}px</span>
          </div>
          <div class="param-item">
            <label>图案透明度</label>
            <input
              v-model.number="localConfig.svgOpacity"
              type="range"
              min="0.1"
              max="1"
              step="0.1"
              class="param-slider"
              @input="handleChange"
            />
            <span class="param-value">{{ Math.round(localConfig.svgOpacity * 100) }}%</span>
          </div>
        </div>
      </div>

      <!-- 图片上传编辑器 -->
      <div v-else-if="localConfig.backgroundType === 'image'" class="image-editor">
        <div class="image-upload-section">
          <ImageUpload
            v-model="localConfig.backgroundImage"
            label="背景图片"
            hint="建议尺寸：750x400px，支持JPG/PNG格式，文件小于2MB"
            :max-size="2 * 1024 * 1024"
            @change="handleChange"
          />
        </div>

        <!-- 图片调整选项 -->
        <div v-if="localConfig.backgroundImage" class="image-adjustments">
          <label class="section-label">图片显示效果</label>
          <div class="adjust-item">
            <label>透明度</label>
            <input
              v-model.number="localConfig.imageOpacity"
              type="range"
              min="0.3"
              max="1"
              step="0.1"
              class="param-slider"
              @input="handleChange"
            />
            <span class="param-value">{{ Math.round(localConfig.imageOpacity * 100) }}%</span>
          </div>
          <div class="adjust-item">
            <label>模糊度</label>
            <input
              v-model.number="localConfig.imageBlur"
              type="range"
              min="0"
              max="10"
              step="0.5"
              class="param-slider"
              @input="handleChange"
            />
            <span class="param-value">{{ localConfig.imageBlur }}px</span>
          </div>
          <div class="adjust-item">
            <label>饱和度</label>
            <input
              v-model.number="localConfig.imageSaturation"
              type="range"
              min="0"
              max="2"
              step="0.1"
              class="param-slider"
              @input="handleChange"
            />
            <span class="param-value">{{ localConfig.imageSaturation.toFixed(1) }}x</span>
          </div>
        </div>
      </div>

      <!-- 纯色编辑器 -->
      <div v-else-if="localConfig.backgroundType === 'solid'" class="solid-editor">
        <div class="color-picker-section">
          <label class="section-label">背景颜色</label>
          <div class="color-picker-large">
            <input
              v-model="localConfig.solidColor"
              type="color"
              class="color-picker-big"
              @input="handleChange"
            />
            <input
              v-model="localConfig.solidColor"
              type="text"
              class="color-text-large"
              placeholder="#667eea"
              @input="handleChange"
            />
          </div>
        </div>

        <!-- 纯色预设 -->
        <div class="solid-presets">
          <label class="section-label">快速选色</label>
          <div class="preset-color-grid">
            <button
              v-for="color in solidPresets"
              :key="color.value"
              class="preset-color-btn"
              :style="{ background: color.value }"
              :class="{ active: localConfig.solidColor === color.value }"
              @click="applySolidPreset(color.value)"
            >
              <span v-if="localConfig.solidColor === color.value" class="check-mark">✓</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 实时预览 -->
      <div class="preview-section">
        <label class="section-label">实时预览</label>
        <div class="preview-card" :style="previewStyle">
          <div class="preview-content">
            <div class="preview-avatar"></div>
            <div class="preview-info">
              <div class="preview-name">张三</div>
              <div class="preview-title">产品经理</div>
              <div class="preview-company">公司简称 - Slogan</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageUpload from '../form/ImageUpload.vue'

export default {
  name: 'BackgroundEditor',
  
  components: {
    ImageUpload
  },
  
  props: {
    value: {
      type: Object,
      default: () => ({
        backgroundType: 'svg', // svg, image, solid
        // SVG配置
        svgPattern: 'geometric',
        svgGradientStart: '#ffffff',
        svgGradientEnd: '#FC726E',
        svgDensity: 300,
        svgOpacity: 0.5,
        // 图片配置
        backgroundImage: '',
        imageOpacity: 0.8,
        imageBlur: 0,
        imageSaturation: 1.2,
        // 纯色配置
        solidColor: '#667eea'
      })
    }
  },
  
  data() {
    return {
      localConfig: { ...this.value },
      bgTypes: [
        { value: 'svg', icon: '🎨', label: 'SVG图案' },
        { value: 'image', icon: '🖼️', label: '上传图片' },
        { value: 'solid', icon: '🎯', label: '纯色背景' }
      ],
      svgPatterns: [
        {
          id: 'geometric',
          name: '几何图案',
          preview: this.generateGeometricPreview()
        },
        {
          id: 'dots',
          name: '圆点网格',
          preview: this.generateDotsPreview()
        },
        {
          id: 'lines',
          name: '线条',
          preview: this.generateLinesPreview()
        },
        {
          id: 'waves',
          name: '波浪',
          preview: this.generateWavesPreview()
        },
        {
          id: 'grid',
          name: '网格',
          preview: this.generateGridPreview()
        },
        {
          id: 'circles',
          name: '圆形',
          preview: this.generateCirclesPreview()
        }
      ],
      solidPresets: [
        { value: '#667eea', name: '紫色' },
        { value: '#2196F3', name: '蓝色' },
        { value: '#4CAF50', name: '绿色' },
        { value: '#FF9800', name: '橙色' },
        { value: '#E91E63', name: '粉色' },
        { value: '#9C27B0', name: '紫红' },
        { value: '#00BCD4', name: '青色' },
        { value: '#F44336', name: '红色' },
        { value: '#795548', name: '棕色' },
        { value: '#607D8B', name: '蓝灰' },
        { value: '#000000', name: '黑色' },
        { value: '#FFFFFF', name: '白色' }
      ]
    }
  },
  
  computed: {
    previewStyle() {
      const config = this.localConfig
      
      if (config.backgroundType === 'svg') {
        // 生成SVG背景
        const svg = this.generateSVG(config)
        return {
          backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(svg)}")`,
          backgroundSize: `${config.svgDensity}px ${config.svgDensity}px`,
          backgroundRepeat: 'repeat'
        }
      } else if (config.backgroundType === 'image' && config.backgroundImage) {
        return {
          backgroundImage: `url(${config.backgroundImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: config.imageOpacity,
          filter: `blur(${config.imageBlur}px) saturate(${config.imageSaturation})`
        }
      } else if (config.backgroundType === 'solid') {
        return {
          background: config.solidColor
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
    
    selectPattern(patternId) {
      this.localConfig.svgPattern = patternId
      this.handleChange()
    },
    
    applySolidPreset(color) {
      this.localConfig.solidColor = color
      this.handleChange()
    },
    
    handleChange() {
      this.$emit('input', { ...this.localConfig })
    },
    
    // 生成SVG背景
    generateSVG(config) {
      const { svgPattern, svgGradientStart, svgGradientEnd, svgOpacity } = config
      
      switch (svgPattern) {
        case 'geometric':
          return this.generateGeometricSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'dots':
          return this.generateDotsSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'lines':
          return this.generateLinesSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'waves':
          return this.generateWavesSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'grid':
          return this.generateGridSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        case 'circles':
          return this.generateCirclesSVG(svgGradientStart, svgGradientEnd, svgOpacity)
        default:
          return this.generateGeometricSVG(svgGradientStart, svgGradientEnd, svgOpacity)
      }
    },
    
    // 几何图案SVG - 改进版：六边形蜂窝图案
    generateGeometricSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="hexPattern" patternUnits="userSpaceOnUse" width="60" height="52" patternTransform="rotate(0)">
            <g fill="none" stroke="rgba(255,255,255,${opacity})" stroke-width="1.5">
              <path d="M30,0 L50,13 L50,39 L30,52 L10,39 L10,13 Z"/>
            </g>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#hexPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 圆点网格SVG - 改进版：密集圆点阵列
    generateDotsSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="dotsPattern" patternUnits="userSpaceOnUse" width="20" height="20">
            <circle cx="10" cy="10" r="2.5" fill="rgba(255,255,255,${opacity})"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#dotsPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 线条SVG - 改进版：斜线纹理
    generateLinesSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="linesPattern" patternUnits="userSpaceOnUse" width="40" height="40" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="40" stroke="rgba(255,255,255,${opacity})" stroke-width="1.5"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#linesPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 波浪SVG - 改进版：多层波浪
    generateWavesSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <path d="M0,100 Q100,60 200,100 T400,100" stroke="rgba(255,255,255,${opacity})" stroke-width="2.5" fill="none"/>
        <path d="M0,120 Q100,80 200,120 T400,120" stroke="rgba(255,255,255,${opacity * 0.7})" stroke-width="2" fill="none"/>
        <path d="M0,80 Q100,40 200,80 T400,80" stroke="rgba(255,255,255,${opacity * 0.7})" stroke-width="2" fill="none"/>
      </svg>`
    },
    
    // 网格SVG - 改进版：精细网格
    generateGridSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
          <pattern id="gridPattern" patternUnits="userSpaceOnUse" width="20" height="20">
            <line x1="0" y1="0" x2="0" y2="20" stroke="rgba(255,255,255,${opacity})" stroke-width="1"/>
            <line x1="0" y1="0" x2="20" y2="0" stroke="rgba(255,255,255,${opacity})" stroke-width="1"/>
          </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <rect x="0" y="0" fill="url(#gridPattern)" width="100%" height="100%"></rect>
      </svg>`
    },
    
    // 圆形SVG - 改进版：同心圆
    generateCirclesSVG(start, end, opacity) {
      return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="0" y2="100%">
            <stop offset="0" stop-color="${start}"></stop>
            <stop offset="1" stop-color="${end}"></stop>
          </linearGradient>
        </defs>
        <rect x="0" y="0" fill="url(#grad)" width="100%" height="100%"></rect>
        <circle cx="100" cy="100" r="30" fill="none" stroke="rgba(255,255,255,${opacity})" stroke-width="2"/>
        <circle cx="100" cy="100" r="50" fill="none" stroke="rgba(255,255,255,${opacity * 0.7})" stroke-width="1.5"/>
        <circle cx="100" cy="100" r="70" fill="none" stroke="rgba(255,255,255,${opacity * 0.5})" stroke-width="1"/>
      </svg>`
    },
    
    // 生成预览HTML（简化版）
    generateGeometricPreview() {
      return '<div style="width:60px;height:60px;background:linear-gradient(135deg,#fff,#FC726E);border-radius:4px;"></div>'
    },
    generateDotsPreview() {
      return '<div style="width:60px;height:60px;background:linear-gradient(135deg,#fff,#FC726E);border-radius:4px;position:relative;"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:8px;height:8px;background:white;border-radius:50%;"></div></div>'
    },
    generateLinesPreview() {
      return '<div style="width:60px;height:60px;background:linear-gradient(135deg,#fff,#FC726E);border-radius:4px;position:relative;"><div style="position:absolute;top:50%;left:0;right:0;height:2px;background:white;"></div></div>'
    },
    generateWavesPreview() {
      return '<div style="width:60px;height:60px;background:linear-gradient(135deg,#fff,#FC726E);border-radius:4px;"></div>'
    },
    generateGridPreview() {
      return '<div style="width:60px;height:60px;background:linear-gradient(135deg,#fff,#FC726E);border-radius:4px;position:relative;"><div style="position:absolute;top:50%;left:0;right:0;height:1px;background:white;"></div><div style="position:absolute;left:50%;top:0;bottom:0;width:1px;background:white;"></div></div>'
    },
    generateCirclesPreview() {
      return '<div style="width:60px;height:60px;background:linear-gradient(135deg,#fff,#FC726E);border-radius:4px;position:relative;"><div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:30px;height:30px;border:2px solid white;border-radius:50%;"></div></div>'
    }
  }
}
</script>

<style lang="scss" scoped>
.background-editor {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.editor-header {
  margin-bottom: 24px;
}

.editor-title {
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

.editor-title .icon {
  font-size: 24px;
}

.editor-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

/* 类型标签页 */
.type-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e2e8f0;
}

.type-tab {
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  transition: all 0.3s ease;
  margin-bottom: -2px;
}

.type-tab:hover {
  color: #667eea;
}

.type-tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.tab-icon {
  font-size: 18px;
}

/* SVG编辑器 */
.svg-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.pattern-presets {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.pattern-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pattern-btn:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.pattern-btn.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.pattern-preview {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
}

.pattern-name {
  font-size: 12px;
  color: #475569;
  font-weight: 500;
}

.gradient-settings,
.pattern-params {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.color-pickers-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 12px;
}

.color-picker-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.color-picker-item label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.color-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.color-picker {
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

.param-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.param-item label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  min-width: 100px;
}

.param-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  -webkit-appearance: none;
}

.param-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.4);
}

.param-value {
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  min-width: 60px;
  text-align: right;
}

/* 图片编辑器 */
.image-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.image-upload-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.image-adjustments {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.adjust-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.adjust-item label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  min-width: 100px;
}

/* 纯色编辑器 */
.solid-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.color-picker-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.color-picker-large {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
}

.color-picker-big {
  width: 80px;
  height: 60px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
}

.color-text-large {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  font-family: monospace;
  font-weight: 600;
}

.solid-presets {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.preset-color-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.preset-color-btn {
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

.preset-color-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.preset-color-btn.active {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

.check-mark {
  color: white;
  font-size: 18px;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 预览区域 */
.preview-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px dashed #e2e8f0;
}

.preview-card {
  height: 200px;
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
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.preview-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-name {
  font-size: 20px;
  font-weight: 700;
}

.preview-title {
  font-size: 14px;
  opacity: 0.95;
}

.preview-company {
  font-size: 12px;
  opacity: 0.85;
  margin-top: 4px;
}

.section-label {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .preset-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .preset-color-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .color-pickers-row {
    grid-template-columns: 1fr;
  }
}
</style>

