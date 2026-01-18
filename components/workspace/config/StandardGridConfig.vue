<template>
  <div class="module-config standard-grid-config">
    <div class="config-section">
      <h4 class="section-title">基础设置</h4>
      
      <TextInput
        v-model="localData.title"
        label="模块标题"
        placeholder="产品展示 / 合作伙伴 / 服务项目"
        :required="true"
        hint="根据内容类型自定义标题"
        @input="emitChange"
      />
      
      <TextInput
        v-model="localData.subtitle"
        type="textarea"
        label="模块描述"
        placeholder="可选的模块描述文字"
        :rows="2"
        @input="emitChange"
      />
    </div>
    
    <div class="config-section">
      <h4 class="section-title">显示模式</h4>
      
      <div class="mode-selector">
        <div
          v-for="mode in modeOptions"
          :key="mode.value"
          class="mode-option"
          :class="{ active: localData.mode === mode.value }"
          @click="selectMode(mode.value)"
        >
          <div class="mode-icon">{{ mode.icon }}</div>
          <div class="mode-info">
            <span class="mode-name">{{ mode.label }}</span>
            <span class="mode-desc">{{ mode.description }}</span>
          </div>
        </div>
      </div>
      
      <div class="mode-hint">
        <i class="icon-info"></i>
        <span>{{ getModeHint(localData.mode) }}</span>
      </div>
    </div>
    
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">内容项目</h4>
        <button class="btn-add" @click="addItem">
          <i class="icon-plus"></i> 添加项目
        </button>
      </div>
      
      <!-- 配额提示 -->
      <div class="quota-hint" :class="{ 
        'quota-warning': remainingImageSlots <= 5,
        'quota-full': remainingImageSlots === 0 
      }">
        <i class="icon-info"></i>
        <span>已添加 {{ getImageCount() }}/{{ MAX_IMAGES }} 个项目</span>
        <span v-if="remainingImageSlots > 0" class="remaining">
          （还可添加{{ remainingImageSlots }}个）
        </span>
        <span v-else class="full-text">（已达上限）</span>
      </div>
      
      <draggable
        v-model="localData.items"
        class="items-list"
        handle=".drag-handle"
        @change="emitChange"
      >
        <div
          v-for="(item, index) in localData.items"
          :key="item.id"
          class="item-card"
        >
          <div class="item-header">
            <i class="drag-handle icon-drag"></i>
            <span class="item-index">项目 {{ index + 1 }}</span>
            <span class="item-mode-badge">{{ getModeLabel(localData.mode) }}</span>
            <button class="btn-remove" @click="removeItem(index)">
              <i class="icon-delete"></i>
            </button>
          </div>
          
          <div v-if="localData.items[index]" class="item-body">
            <!-- 图标模式 -->
            <template v-if="localData.mode === 'icon'">
              <div class="form-row">
                <IconPicker
                  v-model="localData.items[index].icon"
                  :type.sync="localData.items[index].iconType"
                  label="图标"
                  placeholder="选择图标"
                  @change="handleItemIconChange(index)"
                  @update:type="handleItemIconTypeUpdate(index, $event)"
                />
                
                <ColorPicker
                  v-model="localData.items[index].color"
                  label="图标颜色"
                  @change="emitChange"
                />
              </div>
              
              <TextInput
                v-model="localData.items[index].title"
                label="标题"
                placeholder="服务名称"
                :required="true"
                @input="emitChange"
              />
              
              <TextInput
                v-model="localData.items[index].description"
                type="textarea"
                label="描述"
                placeholder="服务的详细描述..."
                :rows="3"
                @input="emitChange"
              />
            </template>
            
            <!-- 图片模式 -->
            <template v-else-if="localData.mode === 'image'">
              <ImageUpload
                v-model="localData.items[index].image"
                label="展示图片"
                :required="true"
                hint="建议尺寸：800x600px，支持 JPG、PNG"
                @change="emitChange"
              />
              
              <TextInput
                v-model="localData.items[index].title"
                label="标题"
                placeholder="案例名称 / 产品名称"
                :required="true"
                @input="emitChange"
              />
              
              <TextInput
                v-model="localData.items[index].description"
                type="textarea"
                label="描述"
                placeholder="详细描述..."
                :rows="3"
                @input="emitChange"
              />
              
              <TextInput
                v-model="localData.items[index].tagsText"
                label="标签"
                placeholder="标签1,标签2,标签3"
                hint="用逗号分隔多个标签"
                @input="updateTags(index)"
              />
            </template>
            
            <!-- Logo模式 -->
            <template v-else-if="localData.mode === 'logo'">
              <ImageUpload
                v-model="localData.items[index].logo"
                label="Logo图片"
                :required="true"
                hint="建议尺寸：400x400px，支持透明背景PNG"
                @change="emitChange"
              />
              
              <TextInput
                v-model="localData.items[index].name"
                label="公司/品牌名称"
                placeholder="合作伙伴名称"
                :required="true"
                @input="emitChange"
              />
              
              <TextInput
                v-model="localData.items[index].url"
                type="url"
                label="链接地址"
                placeholder="https://example.com"
                hint="可选，点击后跳转"
                @input="emitChange"
              />
            </template>
            
            <!-- 文本模式 -->
            <template v-else-if="localData.mode === 'text'">
              <TextInput
                v-model="localData.items[index].title"
                label="标题"
                placeholder="标题文字"
                :required="true"
                @input="emitChange"
              />
              
              <TextInput
                v-model="localData.items[index].description"
                type="textarea"
                label="内容"
                placeholder="详细文字内容..."
                :rows="4"
                :required="true"
                @input="emitChange"
              />
            </template>
          </div>
        </div>
      </draggable>
      
      <div v-if="localData.items.length === 0" class="empty-state">
        <p>暂无项目，点击"添加项目"开始配置</p>
      </div>
    </div>
    
    <div class="config-section">
      <h4 class="section-title">展示设置</h4>
      
      <div class="form-group">
        <label class="form-label">网格列数</label>
        <div class="columns-selector">
          <div
            v-for="col in [2, 3]"
            :key="col"
            class="column-option"
            :class="{ active: localData.columns === col }"
            @click="selectColumns(col)"
          >
            <div class="column-preview" :data-cols="col"></div>
            <span>{{ col }}列</span>
          </div>
        </div>
        <p class="hint-text">建议使用2-3列布局，视觉效果最佳</p>
      </div>
      
      <div class="form-group" v-if="localData.mode === 'image'">
        <label class="form-label">
          <input
            v-model="localData.showOverlay"
            type="checkbox"
            @change="emitChange"
          />
          显示图片悬停遮罩效果
        </label>
      </div>
      
      <div class="form-group">
        <label class="form-label">
          <input
            v-model="localData.clickable"
            type="checkbox"
            @change="emitChange"
          />
          支持点击交互
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import TextInput from '../form/TextInput.vue'
import ImageUpload from '../form/ImageUpload.vue'
import IconPicker from '../form/IconPicker.vue'
import ColorPicker from '../form/ColorPicker.vue'
import debounceMixin from './debounce-mixin'
import uploadSecurityMixin from './upload-security-mixin'

export default {
  name: 'StandardGridConfig',
  
  mixins: [debounceMixin, uploadSecurityMixin],
  
  components: {
    draggable,
    TextInput,
    ImageUpload,
    IconPicker,
    ColorPicker
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
      title: '网格展示',
      subtitle: '',
      mode: 'image',
      columns: 2,
      items: [],
      ...baseData // 覆盖默认值
    }
    
    // 确保items是数组
    if (!Array.isArray(localData.items)) {
      localData.items = []
    }
    
    // 确保每个 item 都有必需的字段（防御性初始化）
    localData.items = localData.items.map(item => {
      if (!item || typeof item !== 'object') {
        return { id: `item-${Date.now()}-${Math.random()}`, title: '', description: '' }
      }
      // 确保每个 item 至少有基础字段
      return {
        id: item.id || `item-${Date.now()}-${Math.random()}`,
        title: item.title || '',
        description: item.description || '',
        ...item // 保留其他字段
      }
    })
    
    return {
      localData,
      
      modeOptions: [
        {
          value: 'icon',
          label: '图标模式',
          icon: '🎯',
          description: '图标+文字，适合服务项目、特点展示'
        },
        {
          value: 'image',
          label: '图片模式',
          icon: '🖼️',
          description: '图片展示，适合案例、产品、环境'
        },
        {
          value: 'logo',
          label: 'Logo模式',
          icon: '🏆',
          description: 'Logo展示，适合合作伙伴、客户'
        },
        {
          value: 'text',
          label: '文本模式',
          icon: '📝',
          description: '纯文字，适合理念、价值观'
        }
      ]
    }
  },
  
  // watch 已由 debounce-mixin 提供
  
  methods: {
    // emitChange 方法现在由 debounce-mixin 提供
    
    // 实现 upload-security-mixin 要求的方法
    getImageCount() {
      return (this.localData.items || []).length
    },
    
    selectMode(mode) {
      if (this.localData.mode === mode) return
      
      // 切换模式时提醒用户
      if (this.localData.items.length > 0) {
        if (!confirm('切换模式将清空现有项目，是否继续？')) {
          return
        }
      }
      
      this.localData.mode = mode
      this.localData.items = []
      this.emitChange()
    },
    
    getModeLabel(mode) {
      const option = this.modeOptions.find(m => m.value === mode)
      return option ? option.label : mode
    },
    
    getModeHint(mode) {
      const hints = {
        icon: '图标模式适合展示服务项目、核心优势、功能特点等',
        image: '图片模式适合展示产品案例、设计作品、办公环境等',
        logo: 'Logo模式适合展示合作伙伴、客户Logo、认证标志等',
        text: '文本模式适合展示企业理念、价值观、服务承诺等'
      }
      return hints[mode] || ''
    },
    
    addItem() {
      // 安全检查：数量限制
      if (!this.canAddMoreImages) {
        alert(`最多只能添加${this.MAX_IMAGES}个项目`)
        return
      }
      
      // 安全检查：上传频率限制
      const frequencyCheck = this.checkUploadFrequency()
      if (!frequencyCheck.allowed) {
        alert(`操作过于频繁，请${frequencyCheck.remaining}秒后再试`)
        return
      }
      
      // 确保 items 数组存在
      if (!this.localData.items) {
        this.$set(this.localData, 'items', [])
      }
      
      const newItem = this.createEmptyItem()
      this.localData.items.unshift(newItem) // 添加到数组开头
      
      // 在下一个tick中确保响应式并触发更新
      this.$nextTick(() => {
        if (this.localData.items[0]) {
          // 强制设置每个属性为响应式
          Object.keys(newItem).forEach(key => {
            this.$set(this.localData.items[0], key, newItem[key])
          })
        }
        
        this.updateUploadTimestamp()
        this.emitChange()
        
        // 滚动到顶部
        const container = this.$el.querySelector('.items-list')
        if (container) {
          container.parentElement.scrollTop = 0
        }
      })
    },
    
    createEmptyItem() {
      const baseItem = {
        id: `item-${Date.now()}`,
      }
      
      switch (this.localData.mode) {
        case 'icon':
          return {
            ...baseItem,
            icon: '⭐',
            iconType: 'emoji',
            color: '#00ffaa',
            title: '',
            description: ''
          }
        case 'image':
          return {
            ...baseItem,
            image: '',
            title: '',
            description: '',
            tags: [],
            tagsText: ''
          }
        case 'logo':
          return {
            ...baseItem,
            logo: '',
            name: '',
            url: ''
          }
        case 'text':
          return {
            ...baseItem,
            title: '',
            description: ''
          }
        default:
          return baseItem
      }
    },
    
    removeItem(index) {
      // 防御性检查
      if (!this.localData.items || index < 0 || index >= this.localData.items.length) {
        console.warn('removeItem: 无效的索引', index)
        return
      }
      
      if (confirm('确定要删除这个项目吗？')) {
        this.localData.items.splice(index, 1)
        
        // 在下一个tick中触发更新
        this.$nextTick(() => {
          this.emitChange()
        })
      }
    },
    
    updateTags(index) {
      // 防御性检查
      if (!this.localData.items || !this.localData.items[index]) {
        console.warn('updateTags: 无效的索引', index)
        return
      }
      
      const item = this.localData.items[index]
      
      // 将逗号分隔的字符串转换为数组
      if (item.tagsText) {
        const tags = item.tagsText.split(',').map(tag => tag.trim()).filter(tag => tag)
        this.$set(this.localData.items[index], 'tags', tags)
      } else {
        this.$set(this.localData.items[index], 'tags', [])
      }
      this.emitChange()
    },
    
    handleItemIconChange(index) {
      // 确保索引有效
      if (!this.localData.items || !this.localData.items[index]) {
        console.warn('handleItemIconChange: 无效的索引', index)
        return
      }
      
      // 确保 iconType 存在
      if (!this.localData.items[index].iconType) {
        this.$set(this.localData.items[index], 'iconType', 'emoji')
      }
      
      this.emitChange()
    },
    
    handleItemIconTypeUpdate(index, newType) {
      // 防御性检查
      if (!this.localData.items || !this.localData.items[index]) {
        console.warn('handleItemIconTypeUpdate: 无效的索引', index)
        return
      }
      
      // 使用 $set 确保响应式更新
      this.$set(this.localData.items[index], 'iconType', newType)
      
      // 触发父组件更新
      this.$nextTick(() => {
        this.emitChange()
      })
    },
    
    selectColumns(columns) {
      this.localData.columns = columns
      this.emitChange()
    }
  },
  
  mounted() {
    // 初始化标签文本
    if (this.localData.mode === 'image') {
      this.localData.items.forEach(item => {
        if (item.tags && !item.tagsText) {
          item.tagsText = item.tags.join(',')
        }
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
  margin-bottom: 16px;
}

/* 模式选择器 */
.mode-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.mode-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-option:hover {
  border-color: rgba(0, 255, 170, 0.5);
  background: rgba(0, 255, 170, 0.05);
}

.mode-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.1);
  box-shadow: 0 0 0 3px rgba(0, 255, 170, 0.1);
}

.mode-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.mode-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.mode-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.mode-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.mode-hint {
  padding: 12px 16px;
  background: rgba(0, 255, 170, 0.1);
  border-left: 3px solid #00ffaa;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

/* 列数选择器 */
.columns-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 8px;
  max-width: 300px;
}

.column-option {
  padding: 16px 12px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.column-option:hover {
  border-color: #00ffaa;
}

.column-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.05);
}

.column-preview {
  width: 60px;
  height: 40px;
  background: #f0f0f0;
  border-radius: 4px;
  position: relative;
}

.column-preview[data-cols="1"]::before {
  content: '';
  position: absolute;
  inset: 4px;
  background: repeating-linear-gradient(0deg, #ddd 0px, #ddd 10px, transparent 10px, transparent 14px);
}

.column-preview[data-cols="2"]::before {
  content: '';
  position: absolute;
  inset: 4px;
  background: 
    repeating-linear-gradient(0deg, #ddd 0px, #ddd 8px, transparent 8px, transparent 10px),
    linear-gradient(90deg, #ddd 50%, transparent 50%);
}

.column-preview[data-cols="3"]::before {
  content: '';
  position: absolute;
  inset: 4px;
  background: 
    repeating-linear-gradient(0deg, #ddd 0px, #ddd 6px, transparent 6px, transparent 8px),
    repeating-linear-gradient(90deg, #ddd 0px, #ddd 18px, transparent 18px, transparent 20px);
}

.column-preview[data-cols="4"]::before {
  content: '';
  position: absolute;
  inset: 4px;
  background: 
    repeating-linear-gradient(0deg, #ddd 0px, #ddd 6px, transparent 6px, transparent 8px),
    repeating-linear-gradient(90deg, #ddd 0px, #ddd 13px, transparent 13px, transparent 14px);
}

.column-option span {
  font-size: 13px;
  font-weight: 500;
  color: #1a1a2e;
}

/* 按钮样式 */
.btn-add {
  padding: 8px 16px;
  background: #00ffaa;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-add:hover {
  background: #00e69a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 170, 0.3);
}

/* 项目列表 */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.item-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(0, 255, 170, 0.05);
  border-bottom: 1px solid #e0e0e0;
}

.drag-handle {
  cursor: move;
  color: #666;
  font-size: 18px;
}

.item-index {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.item-mode-badge {
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
}

.btn-remove:hover {
  background: rgba(255, 71, 87, 0.1);
}

.item-body {
  padding: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #666;
  background: #fff;
  border: 2px dashed #e0e0e0;
  border-radius: 12px;
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
  cursor: pointer;
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

/* 响应式 */
@media (max-width: 768px) {
  .mode-selector {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

