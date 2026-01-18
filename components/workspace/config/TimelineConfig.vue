<template>
  <div class="module-config timeline-config">
    <div class="config-section">
      <h4 class="section-title">基础设置</h4>
      
      <TextInput
        v-model="localData.title"
        label="模块标题"
        placeholder="发展历程"
        :required="true"
        @input="emitChange"
      />
      
      <TextInput
        v-model="localData.subtitle"
        type="textarea"
        label="模块描述"
        placeholder="我们的成长与里程碑"
        :rows="2"
        @input="emitChange"
      />
    </div>
    
    <!-- 展示设置移到前面 -->
    <div class="config-section">
      <h4 class="section-title">展示设置</h4>
      
      <div class="form-group">
        <label class="form-label">布局样式</label>
        <div class="layout-options">
          <div
            v-for="layout in layoutOptions"
            :key="layout.value"
            class="layout-option"
            :class="{ active: localData.layout === layout.value }"
            @click="selectLayout(layout.value)"
          >
            <div class="layout-icon">{{ layout.icon }}</div>
            <span>{{ layout.label }}</span>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label class="form-label">时间线样式</label>
        <div class="style-options">
          <label class="radio-option">
            <input
              v-model="localData.lineStyle"
              type="radio"
              value="solid"
              @change="emitChange"
            />
            <span>实线</span>
          </label>
          <label class="radio-option">
            <input
              v-model="localData.lineStyle"
              type="radio"
              value="dashed"
              @change="emitChange"
            />
            <span>虚线</span>
          </label>
        </div>
      </div>
      
      <ColorPicker
        v-model="localData.accentColor"
        label="强调色"
        hint="时间线和图标的颜色"
        @change="emitChange"
      />
    </div>
    
    <!-- 时间线事件内容移到后面 -->
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">时间线内容</h4>
        <button class="btn-add" @click="addEvent">
          <i class="icon-plus"></i> 添加事件
        </button>
      </div>
      
      <div v-if="planLimit" class="plan-limit-hint">
        <i class="icon-info"></i>
        当前套餐最多可添加 {{ planLimit }} 个事件（已添加 {{ localData.events.length }}）
      </div>
      
      <draggable
        v-model="localData.events"
        class="events-list"
        handle=".drag-handle"
        @change="emitChange"
      >
        <div
          v-for="(event, index) in localData.events"
          :key="event.id"
          class="event-card"
        >
          <div class="event-header">
            <i class="drag-handle icon-drag"></i>
            <span class="event-index">事件 {{ index + 1 }}</span>
            <button class="btn-remove" @click="removeEvent(index)">
              <i class="icon-delete"></i>
            </button>
          </div>
          
          <div v-if="localData.events[index]" class="event-body">
            <TextInput
              v-model="localData.events[index].date"
              label="时间"
              placeholder="2023-01"
              :required="true"
              hint="格式：YYYY-MM 或 YYYY"
              @input="emitChange"
              class="full-width-input"
            />
            
            <IconPicker
              v-model="localData.events[index].icon"
              :type.sync="localData.events[index].iconType"
              label="事件图标（可选）"
              placeholder="选择图标"
              @change="handleEventIconChange(index)"
              @update:type="handleEventIconTypeUpdate(index, $event)"
            />
            
            <TextInput
              v-model="localData.events[index].title"
              label="事件标题"
              placeholder="公司成立 / 获得融资"
              :required="true"
              @input="emitChange"
            />
            
            <TextInput
              v-model="localData.events[index].description"
              type="textarea"
              label="事件描述"
              placeholder="详细描述这个里程碑事件..."
              :rows="3"
              @input="emitChange"
            />
          </div>
        </div>
      </draggable>
      
      <div v-if="localData.events.length === 0" class="empty-state">
        <p>暂无事件，点击"添加事件"开始配置</p>
      </div>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import TextInput from '../form/TextInput.vue'
import ColorPicker from '../form/ColorPicker.vue'
import IconPicker from '../form/IconPicker.vue'
import debounceMixin from './debounce-mixin'

export default {
  name: 'TimelineConfig',
  
  mixins: [debounceMixin],
  
  components: {
    draggable,
    TextInput,
    ColorPicker,
    IconPicker
  },
  
  props: {
    data: {
      type: Object,
      required: true
    },
    planLimit: {
      type: Number,
      default: null
    }
  },
  
  data() {
    // 确保 events 数组存在
    const localData = this._smartClone ? this._smartClone(this.data) : { ...this.data }
    if (!localData.events) {
      localData.events = []
    }
    // 确保每个 event 都有必需的字段
    if (Array.isArray(localData.events)) {
      localData.events = localData.events.map(event => ({
        id: event.id || `event-${Date.now()}-${Math.random()}`,
        date: event.date || '',
        icon: event.icon || '⭐',
        iconType: event.iconType || 'emoji',
        title: event.title || '',
        description: event.description || ''
      }))
    }
    
    return {
      localData,
      
      layoutOptions: [
        { value: 'vertical', label: '垂直布局', icon: '│' }
      ]
    }
  },
  
  // watch 已由 debounce-mixin 提供
  
  methods: {
    // emitChange 方法现在由 debounce-mixin 提供
    
    addEvent() {
      if (this.planLimit && this.localData.events.length >= this.planLimit) {
        alert(`当前套餐最多支持 ${this.planLimit} 个事件`)
        return
      }
      
      // 确保 events 数组存在
      if (!this.localData.events) {
        this.$set(this.localData, 'events', [])
      }
      
      // 创建新事件对象
      const newEvent = {
        id: `event-${Date.now()}`,
        date: '',
        icon: '⭐',
        iconType: 'emoji',
        title: '',
        description: ''
      }
      
      // 使用 unshift 将新事件添加到数组开头
      this.localData.events.unshift(newEvent)
      
      // 在下一个tick中确保响应式并触发更新
      this.$nextTick(() => {
        if (this.localData.events[0]) {
          // 强制设置每个属性为响应式
          this.$set(this.localData.events[0], 'id', newEvent.id)
          this.$set(this.localData.events[0], 'date', newEvent.date)
          this.$set(this.localData.events[0], 'icon', newEvent.icon)
          this.$set(this.localData.events[0], 'iconType', newEvent.iconType)
          this.$set(this.localData.events[0], 'title', newEvent.title)
          this.$set(this.localData.events[0], 'description', newEvent.description)
        }
        
        this.emitChangeImmediate()
        
        // 添加后自动滚动到顶部
        const container = this.$el.querySelector('.events-list')
        if (container) {
          container.scrollTop = 0
        }
      })
    },
    
    removeEvent(index) {
      // 防御性检查
      if (!this.localData.events || index < 0 || index >= this.localData.events.length) {
        console.warn('removeEvent: 无效的索引', index)
        return
      }
      
      if (confirm('确定要删除这个事件吗？')) {
        this.localData.events.splice(index, 1)
        
        // 在下一个tick中触发更新
        this.$nextTick(() => {
          this.emitChangeImmediate()
        })
      }
    },
    
    selectLayout(layout) {
      this.localData.layout = layout
      this.emitChangeImmediate()
    },
    
    handleEventIconChange(index) {
      // 确保索引有效
      if (!this.localData.events || !this.localData.events[index]) {
        console.warn('handleEventIconChange: 无效的索引', index)
        return
      }
      
      // 确保 iconType 存在
      if (!this.localData.events[index].iconType) {
        this.$set(this.localData.events[index], 'iconType', 'emoji')
      }
      
      this.emitChange()
    },
    
    handleEventIconTypeUpdate(index, newType) {
      // 防御性检查
      if (!this.localData.events || !this.localData.events[index]) {
        console.warn('handleEventIconTypeUpdate: 无效的索引', index)
        return
      }
      
      // 使用 $set 确保响应式更新
      this.$set(this.localData.events[index], 'iconType', newType)
      
      // 触发父组件更新
      this.$nextTick(() => {
        this.emitChange()
      })
    }
  },
  
  errorCaptured(err, vm, info) {
    console.error('TimelineConfig: Error captured:', err, info)
    // 防止错误传播导致整个应用崩溃
    return false
  }
}
</script>

<style scoped>
/* 复用 ProductServiceConfig 的样式并添加特定样式 */
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

.plan-limit-hint {
  padding: 12px 16px;
  background: rgba(0, 255, 170, 0.1);
  border-left: 3px solid #00ffaa;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

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

.events-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.event-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.event-header {
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
}

.event-index {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.btn-remove {
  padding: 6px;
  background: none;
  border: none;
  color: #ff4757;
  cursor: pointer;
}

.event-body {
  padding: 20px;
}

/* 图标选择行 */
.icon-row {
  margin: 16px 0;
}

.icon-preview-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.icon-display {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: #f8f9fa;
}

.icon-preview {
  font-size: 32px;
  line-height: 1;
}

.icon-placeholder {
  font-size: 12px;
  color: #999;
}

.btn-select-icon {
  padding: 10px 20px;
  background: #1890FF;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-select-icon:hover {
  background: #40a9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

/* 图标选择器Modal */
.icon-picker-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 99999;  /* 提高到99999，确保在最顶层 */
  overflow-y: auto; /* 允许Modal容器滚动 */
  overflow-x: hidden;
  /* 使用padding确保内容不会贴边 */
  padding: 40px 20px;
  /* 移除flex布局，改用padding来实现居中效果 */
  animation: fadeIn 0.3s ease;
}

.icon-picker-container {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  /* 移除max-height限制，让内容完全显示 */
  min-height: 300px; /* 最小高度，确保可见 */
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  /* 使用margin实现水平居中 */
  margin: 0 auto;
  /* 为小屏幕设备优化 */
  position: relative;
  animation: modalSlideUp 0.3s ease;
}

.icon-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.icon-picker-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.icon-picker-header .btn-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.icon-picker-header .btn-close:hover {
  color: #262626;
  transform: rotate(90deg);
}

.icon-picker-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 8px;
}

.icon-item {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.icon-item:hover {
  border-color: #1890FF;
  background: #f0f8ff;
  transform: scale(1.1);
}

.icon-item.active {
  border-color: #1890FF;
  background: #e6f7ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.2);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  margin-bottom: 8px;
}

.layout-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.layout-option {
  padding: 16px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.layout-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.05);
}

.layout-icon {
  font-size: 32px;
  margin-bottom: 8px;
  color: #666;
}

.style-options {
  display: flex;
  gap: 16px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}
</style>

