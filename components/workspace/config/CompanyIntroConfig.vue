<template>
  <div class="module-config company-intro-config">
    <div class="config-section">
      <h4 class="section-title">基础设置</h4>
      
      <TextInput
        v-model="localData.title"
        label="模块标题"
        placeholder="企业简介 / 关于我们 / 公司介绍"
        :required="true"
        hint="显示在模块顶部的标题"
        @input="emitChange"
      />
      
      <div class="info-note">
        <i class="icon-info"></i>
        <span>企业简介适合展示公司背景、核心业务、企业文化、价值观等文字内容</span>
      </div>
    </div>
    
    <div class="config-section">
      <h4 class="section-title">内容编辑</h4>
      
      <div class="form-group">
        <label class="form-label">内容模式</label>
        <div class="mode-selector">
          <label class="radio-option">
            <input
              v-model="localData.mode"
              type="radio"
              value="simple"
              @change="handleModeChange"
            />
            <span>简洁模式</span>
            <span class="mode-desc">纯文本段落</span>
          </label>
          <label class="radio-option">
            <input
              v-model="localData.mode"
              type="radio"
              value="rich"
              @change="handleModeChange"
            />
            <span>丰富模式</span>
            <span class="mode-desc">副标题 + 正文 + 要点列表</span>
          </label>
        </div>
      </div>
      
      <!-- 简洁模式 -->
      <template v-if="localData.mode === 'simple'">
        <TextInput
          v-model="localData.content"
          type="textarea"
          label="企业简介"
          placeholder="请输入企业介绍内容..."
          :rows="8"
          :required="true"
          :maxLength="1000"
          hint="建议300-500字，简明扼要地介绍企业核心信息"
          @input="emitChange"
        />
      </template>
      
      <!-- 丰富模式 -->
      <template v-else>
        <TextInput
          v-model="localData.subtitle"
          label="副标题"
          placeholder="我们的使命 / 核心业务"
          hint="可选，突出的副标题"
          @input="emitChange"
        />
        
        <TextInput
          v-model="localData.summary"
          type="textarea"
          label="主要内容"
          placeholder="详细的企业介绍内容..."
          :rows="6"
          :required="true"
          :maxLength="800"
          hint="介绍企业背景、业务范围等"
          @input="emitChange"
        />
        
        <div class="points-section">
          <div class="section-header">
            <label class="form-label">核心要点</label>
            <button class="btn-add-small" @click="addPoint">
              <i class="icon-plus"></i> 添加要点
            </button>
          </div>
          
          <div v-if="localData.points && localData.points.length > 0" class="points-list">
            <div
              v-for="(point, index) in localData.points"
              :key="`point-${index}`"
              class="point-item"
            >
              <span class="point-number">{{ index + 1 }}</span>
              <input
                v-if="typeof localData.points[index] !== 'undefined'"
                v-model="localData.points[index]"
                type="text"
                class="point-input"
                placeholder="输入要点内容"
                @input="emitChange"
              />
              <button class="btn-remove-small" @click="removePoint(index)">
                <i class="icon-delete"></i>
              </button>
            </div>
          </div>
          
          <p class="hint-text">添加3-5个核心要点，简明扼要地突出企业优势</p>
        </div>
      </template>
    </div>
    
    <div class="config-section">
      <h4 class="section-title">配图设置（可选）</h4>
      
      <div class="form-group">
        <label class="form-label">
          <input
            v-model="localData.showImage"
            type="checkbox"
            @change="emitChange"
          />
          添加配图
        </label>
      </div>
      
      <template v-if="localData.showImage">
        <div class="form-group">
          <label class="form-label">图片位置</label>
          <div class="image-position-selector">
            <label class="radio-option">
              <input
                v-model="localData.imagePosition"
                type="radio"
                value="top"
                @change="emitChange"
              />
              <span>顶部横图</span>
            </label>
            <label class="radio-option">
              <input
                v-model="localData.imagePosition"
                type="radio"
                value="float-left"
                @change="emitChange"
              />
              <span>左上角</span>
            </label>
            <label class="radio-option">
              <input
                v-model="localData.imagePosition"
                type="radio"
                value="float-right"
                @change="emitChange"
              />
              <span>右上角</span>
            </label>
          </div>
          
          <!-- 动态图片比例提示 -->
          <div class="image-ratio-hint">
            <template v-if="localData.imagePosition === 'top'">
              <i class="hint-icon">📐</i>
              <div class="hint-content">
                <strong>顶部横图推荐：</strong>
                <ul>
                  <li>最佳比例：<code>16:9</code> 或 <code>5:3</code>（如 800×450、1200×675）</li>
                  <li>显示区域：宽度100%，高度240px（移动端180px）</li>
                  <li>裁剪方式：<code>object-fit: cover</code>（居中裁剪）</li>
                  <li>适合内容：办公环境全景、团队合影、企业大楼外观</li>
                </ul>
              </div>
            </template>
            <template v-else-if="localData.imagePosition === 'float-left' || localData.imagePosition === 'float-right'">
              <i class="hint-icon">✨</i>
              <div class="hint-content">
                <strong>浮动方图推荐（文字环绕）：</strong>
                <ul>
                  <li>最佳比例：<code>1:1</code> 方形（如 400×400、600×600）</li>
                  <li>显示区域：140×140px（移动端110×110px）</li>
                  <li>布局效果：图片浮动在{{ localData.imagePosition === 'float-left' ? '左上角' : '右上角' }}，文字自然环绕</li>
                  <li>核心数据：在图片下方完整显示一行，不受浮动影响</li>
                  <li>适合内容：企业Logo、标志性建筑、产品特写</li>
                </ul>
              </div>
            </template>
          </div>
        </div>
        
        <ImageUpload
          v-model="localData.image"
          :label="imageUploadLabel"
          :hint="imageUploadHint"
          @change="emitChange"
        />
      </template>
    </div>
    
    <div class="config-section">
      <h4 class="section-title">核心数据亮点（可选）</h4>
      
      <div class="form-group">
        <label class="form-label">
          <input
            v-model="localData.showHighlights"
            type="checkbox"
            @change="emitChange"
          />
          显示数据亮点
        </label>
        <p class="hint-text">展示企业关键数据，如"成立年份"、"服务客户"等</p>
      </div>
      
      <template v-if="localData.showHighlights">
        <div class="form-group">
          <label class="form-label">显示列数</label>
          <div class="columns-selector">
            <label 
              v-for="col in [2, 3]" 
              :key="col" 
              class="column-option"
              :class="{ active: localData.highlightsColumns === col }"
            >
              <input
                v-model="localData.highlightsColumns"
                type="radio"
                :value="col"
                @change="emitChange"
              />
              <div class="column-preview" :data-cols="col">
                <span v-for="i in col" :key="i" class="col-item"></span>
              </div>
              <span class="column-label">{{ col }}列</span>
            </label>
          </div>
        </div>
        
        <div class="section-header">
          <label class="form-label">数据项</label>
          <button class="btn-add-small" @click="addHighlight">
            <i class="icon-plus"></i> 添加数据
          </button>
        </div>
        
        <div v-if="localData.highlights && localData.highlights.length > 0" class="highlights-list">
          <div
            v-for="(highlight, index) in localData.highlights"
            :key="`highlight-${index}-${highlight.label || ''}-${highlight.value || ''}`"
            class="highlight-item"
          >
            <div class="highlight-header">
              <span class="highlight-number">数据 {{ index + 1 }}</span>
              <button class="btn-remove-small" @click="removeHighlight(index)">
                <i class="icon-delete"></i>
              </button>
            </div>
            <div v-if="localData.highlights[index]" class="highlight-body">
              <div class="form-row">
                <div class="form-col">
                  <input
                    v-model="localData.highlights[index].label"
                    type="text"
                    class="mini-input"
                    placeholder="标签（如：成立时间）"
                    @input="emitChange"
                  />
                </div>
                <div class="form-col">
                  <input
                    v-model="localData.highlights[index].value"
                    type="text"
                    class="mini-input"
                    placeholder="数值（如：2010年）"
                    @input="emitChange"
                  />
                </div>
              </div>
              <IconPicker
                v-model="localData.highlights[index].icon"
                :type.sync="localData.highlights[index].iconType"
                label="图标"
                placeholder="选择数据图标"
                @change="handleHighlightIconChange(index)"
                @update:type="handleHighlightIconTypeUpdate(index, $event)"
              />
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import TextInput from '../form/TextInput.vue'
import ImageUpload from '../form/ImageUpload.vue'
import IconPicker from '../form/IconPicker.vue'
import debounceMixin from './debounce-mixin'

export default {
  name: 'CompanyIntroConfig',
  
  mixins: [debounceMixin],
  
  components: {
    TextInput,
    ImageUpload,
    IconPicker
  },
  
  props: {
    data: {
      type: Object,
      required: true
    }
  },
  
  data() {
    // 使用 mixin 的智能克隆方法
    const localData = this._smartClone ? this._smartClone(this.data) : { ...this.data }
    
    // 确保 mode 有默认值
    if (!localData.mode) {
      localData.mode = 'simple'
    }
    
    // 确保 highlightsColumns 有默认值
    if (!localData.highlightsColumns) {
      localData.highlightsColumns = 2
    }
    
    // 确保数组字段初始化
    if (!localData.points) {
      localData.points = []
    }
    if (!localData.highlights) {
      localData.highlights = []
    }
    
    // 确保highlights数组中的每个对象都有完整的字段
    if (localData.highlights && localData.highlights.length > 0) {
      localData.highlights = localData.highlights.map(h => ({
        icon: h.icon || '📊',
        iconType: h.iconType || 'emoji',
        label: h.label || '',
        value: h.value || ''
      }))
    }
    
    // 确保content和summary字段存在（防止undefined）
    if (!localData.content) {
      localData.content = ''
    }
    if (!localData.summary) {
      localData.summary = ''
    }
    if (!localData.subtitle) {
      localData.subtitle = ''
    }
    
    // 确保图片相关字段存在（防止undefined）
    if (localData.showImage === undefined) {
      localData.showImage = false
    }
    if (!localData.imagePosition) {
      localData.imagePosition = 'top'
    }
    if (localData.image === undefined) {
      localData.image = ''
    }
    
    // 确保数据亮点显示字段存在
    if (localData.showHighlights === undefined) {
      localData.showHighlights = false
    }
    
    return {
      localData
    }
  },
  
  computed: {
    // 动态生成图片上传标签
    imageUploadLabel() {
      if (this.localData.imagePosition === 'top') {
        return '配图（横图）'
      } else {
        return '配图（方图）'
      }
    },
    
    // 动态生成图片上传提示
    imageUploadHint() {
      if (this.localData.imagePosition === 'top') {
        return '推荐16:9横图（如800×450），用于展示办公环境、团队合影等'
      } else {
        return '推荐1:1方图（如600×600），文字将自动环绕图片，核心数据完整显示'
      }
    }
  },
  
  // watch 已由 debounce-mixin 提供
  
  methods: {
    // emitChange 方法现在由 debounce-mixin 提供
    
    handleModeChange(event) {
      // 防止重复触发
      if (this._isChangingMode) {
        return
      }
      
      const newMode = event.target.value
      const oldMode = this.localData.mode
      
      // 如果没有实际变化，直接返回
      if (newMode === oldMode) {
        return
      }
      
      // 如果切换到简洁模式，且有丰富模式的内容，则提示
      if (newMode === 'simple') {
        const hasSummary = this.localData.summary && this.localData.summary.trim()
        const hasPoints = this.localData.points && this.localData.points.length > 0
        
        if (hasSummary || hasPoints) {
          this._isChangingMode = true
          const confirmed = confirm('切换到简洁模式将清空副标题、要点列表等内容，是否继续？')
          this._isChangingMode = false
          
          if (!confirmed) {
            // 用户取消，阻止模式切换
            event.preventDefault()
            // 在下一个tick恢复原值
            this.$nextTick(() => {
              this.localData.mode = oldMode
            })
            return
          }
        }
        
        // 用户确认，清空富文本相关字段
        this.localData.subtitle = ''
        this.localData.summary = ''
        this.localData.points = []
      }
      
      // 从丰富模式切换到简洁模式，需要检查图片相关字段
      // 简洁模式下也支持图片，所以不清空图片，但要确保字段存在
      if (newMode === 'simple') {
        // 确保简洁模式所需的字段存在
        if (!this.localData.content) {
          this.localData.content = this.localData.summary || ''
        }
      } else {
        // 切换到丰富模式，确保丰富模式所需的字段存在
        if (!this.localData.summary && this.localData.content) {
          this.localData.summary = this.localData.content
        }
      }
      
      // 确认切换
      this.localData.mode = newMode
      this.$nextTick(() => {
        this.emitChange()
      })
    },
    
    addPoint() {
      if (!this.localData.points) {
        this.$set(this.localData, 'points', [])
      }
      this.localData.points.push('')
      
      // 在下一个tick中触发更新
      this.$nextTick(() => {
        this.emitChange()
      })
    },
    
    removePoint(index) {
      // 防御性检查
      if (!this.localData.points || index < 0 || index >= this.localData.points.length) {
        console.warn('removePoint: 无效的索引', index)
        return
      }
      
      this.localData.points.splice(index, 1)
      
      // 在下一个tick中触发更新
      this.$nextTick(() => {
        this.emitChange()
      })
    },
    
    addHighlight() {
      if (!this.localData.highlights) {
        this.$set(this.localData, 'highlights', [])
      }
      
      // 使用 Vue.set 确保新对象是响应式的
      const newHighlight = {
        icon: '📊',
        iconType: 'emoji',
        label: '',
        value: ''
      }
      
      this.localData.highlights.push(newHighlight)
      
      // 确保新添加的对象是响应式的
      this.$nextTick(() => {
        const index = this.localData.highlights.length - 1
        if (this.localData.highlights[index]) {
          // 强制设置每个属性为响应式
          this.$set(this.localData.highlights[index], 'icon', newHighlight.icon)
          this.$set(this.localData.highlights[index], 'iconType', newHighlight.iconType)
          this.$set(this.localData.highlights[index], 'label', newHighlight.label)
          this.$set(this.localData.highlights[index], 'value', newHighlight.value)
        }
        this.emitChange()
      })
    },
    
    removeHighlight(index) {
      // 防御性检查
      if (!this.localData.highlights || index < 0 || index >= this.localData.highlights.length) {
        console.warn('removeHighlight: 无效的索引', index)
        return
      }
      
      // 使用 Vue 的数组方法确保响应式
      this.localData.highlights.splice(index, 1)
      
      // 在下一个tick中触发更新，避免立即访问已删除的元素
      this.$nextTick(() => {
        this.emitChange()
      })
    },
    
    handleHighlightIconChange(index) {
      // 确保索引有效
      if (!this.localData.highlights || !this.localData.highlights[index]) {
        console.warn('handleHighlightIconChange: 无效的索引', index)
        return
      }
      
      // 确保 iconType 存在
      if (!this.localData.highlights[index].iconType) {
        this.$set(this.localData.highlights[index], 'iconType', 'emoji')
      }
      
      this.emitChange()
    },
    
    handleHighlightIconTypeUpdate(index, newType) {
      // 防御性检查
      if (!this.localData.highlights || !this.localData.highlights[index]) {
        console.warn('handleHighlightIconTypeUpdate: 无效的索引', index)
        return
      }
      
      // 使用 $set 确保响应式更新
      this.$set(this.localData.highlights[index], 'iconType', newType)
      
      // 触发父组件更新
      this.$nextTick(() => {
        this.emitChange()
      })
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
  margin-bottom: 12px;
}

.info-note {
  padding: 12px 16px;
  background: rgba(0, 123, 255, 0.1);
  border-left: 3px solid #007bff;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  display: flex;
  align-items: flex-start;
  gap: 8px;
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
}

.hint-text {
  font-size: 12px;
  color: #666;
  margin: 4px 0 0 0;
}

/* 模式选择器 */
.mode-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.radio-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.radio-option:hover {
  border-color: #00ffaa;
}

.radio-option input[type="radio"]:checked ~ * {
  color: #00ffaa;
}

.radio-option input[type="radio"] {
  margin: 0;
}

.mode-desc {
  font-size: 11px;
  color: #999;
}

/* 图片位置选择器 */
.image-position-selector {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.image-position-selector .radio-option {
  flex: 1;
  flex-direction: row;
  align-items: center;
  padding: 8px 12px;
}

/* 按钮 */
.btn-add-small {
  padding: 6px 12px;
  background: #00ffaa;
  color: #1a1a2e;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.btn-add-small:hover {
  background: #00e69a;
}

.btn-remove-small {
  padding: 4px;
  background: none;
  border: none;
  color: #ff4757;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
}

.btn-remove-small:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 要点列表 */
.points-section {
  margin-top: 16px;
}

.points-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}

.point-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  padding: 8px;
  border-radius: 6px;
}

.point-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #00ffaa;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.point-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
}

.point-input:focus {
  outline: none;
  border-color: #00ffaa;
}

/* 列数选择器 */
.columns-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 300px;
  margin-top: 8px;
}

.column-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.column-option:hover {
  border-color: #00ffaa;
  box-shadow: 0 2px 8px rgba(0, 255, 170, 0.2);
}

.column-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.05);
}

.column-option input[type="radio"] {
  display: none;
}

.column-preview {
  display: flex;
  gap: 4px;
  width: 100%;
  justify-content: center;
}

.column-preview[data-cols="2"] .col-item {
  width: 40px;
  height: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

.column-preview[data-cols="3"] .col-item {
  width: 26px;
  height: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

.column-label {
  font-size: 13px;
  font-weight: 500;
  color: #1a1a2e;
}

.column-option.active .column-label {
  color: #00ffaa;
}

/* 数据亮点 */
.highlights-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.highlight-item {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.highlight-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(0, 255, 170, 0.05);
  border-bottom: 1px solid #e0e0e0;
}

.highlight-number {
  font-size: 12px;
  font-weight: 600;
  color: #1a1a2e;
}

.highlight-body {
  padding: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.mini-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
}

.mini-input:focus {
  outline: none;
  border-color: #00ffaa;
}

/* 图片比例提示 */
.image-ratio-hint {
  margin-top: 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f5ff 100%);
  border: 1px solid #d0e0ff;
  border-left: 4px solid #4a90e2;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.hint-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.hint-content {
  flex: 1;
}

.hint-content strong {
  display: block;
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
}

.hint-content ul {
  margin: 0;
  padding-left: 16px;
  list-style: none;
}

.hint-content li {
  position: relative;
  padding-left: 0;
  margin-bottom: 6px;
  color: #5a6c7d;
}

.hint-content li:before {
  content: "•";
  color: #4a90e2;
  font-weight: bold;
  display: inline-block;
  width: 1em;
  margin-left: -1em;
  position: absolute;
  left: 0;
}

.hint-content code {
  background: rgba(74, 144, 226, 0.1);
  color: #4a90e2;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 768px) {
  .mode-selector {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .image-ratio-hint {
    padding: 10px 12px;
    font-size: 12px;
  }
  
  .hint-content strong {
    font-size: 13px;
  }
  
  .hint-icon {
    font-size: 18px;
  }
}
</style>

