<template>
  <div class="module-config trust-credentials-config">
    <div class="config-section">
      <h4 class="section-title">基础设置</h4>
      
      <TextInput
        v-model="localData.title"
        label="模块标题"
        placeholder="信任背书"
        :required="true"
        @input="emitChange"
      />
    </div>
    
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">资质证书</h4>
        <button class="btn-add" @click="addCredential">
          <i class="icon-plus"></i> 添加证书
        </button>
      </div>
      
      <!-- 配额提示 -->
      <div class="quota-hint" :class="{ 
        'quota-warning': remainingImageSlots <= 5,
        'quota-full': remainingImageSlots === 0 
      }">
        <i class="icon-info"></i>
        <span>已添加 {{ getImageCount() }}/{{ MAX_IMAGES }} 个证书</span>
        <span v-if="remainingImageSlots > 0" class="remaining">
          （还可添加{{ remainingImageSlots }}个）
        </span>
        <span v-else class="full-text">（已达上限）</span>
      </div>
      
      <draggable
        v-model="localData.credentials"
        class="credentials-list"
        handle=".drag-handle"
        @change="emitChange"
      >
        <div
          v-for="(credential, index) in localData.credentials"
          :key="credential.id"
          class="credential-card"
        >
          <div class="credential-header">
            <i class="drag-handle icon-drag"></i>
            <span class="credential-index">证书 {{ index + 1 }}</span>
            <button class="btn-remove" @click="removeCredential(index)">
              <i class="icon-delete"></i>
            </button>
          </div>
          
          <div v-if="localData.credentials[index]" class="credential-body">
            <ImageUpload
              v-model="localData.credentials[index].image"
              label="证书图片"
              :required="true"
              hint="建议尺寸：800x600px"
              @change="emitChange"
            />
            
            <TextInput
              v-model="localData.credentials[index].title"
              label="证书名称"
              placeholder="ISO 9001质量管理体系认证"
              :required="true"
              @input="emitChange"
            />
            
            <TextInput
              v-model="localData.credentials[index].issuer"
              label="颁发机构"
              placeholder="国家认证认可监督管理委员会"
              @input="emitChange"
            />
            
            <TextInput
              v-model="localData.credentials[index].date"
              label="获得时间"
              placeholder="2023-06"
              hint="格式：YYYY-MM"
              @input="emitChange"
            />
          </div>
        </div>
      </draggable>
      
      <div v-if="localData.credentials.length === 0" class="empty-state">
        <p>暂无证书，点击"添加证书"开始配置</p>
      </div>
    </div>
    
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
            <span>{{ layout.label }}</span>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label class="form-label">
          <input
            v-model="localData.showDate"
            type="checkbox"
            @change="emitChange"
          />
          显示获得时间
        </label>
      </div>
      
      <div class="form-group">
        <label class="form-label">
          <input
            v-model="localData.enableZoom"
            type="checkbox"
            @change="emitChange"
          />
          支持点击放大查看
        </label>
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
  name: 'TrustCredentialsConfig',
  
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
    return {
      localData: this.initializeData(),
      
      layoutOptions: [
        { value: 'grid', label: '网格展示' },
        { value: 'carousel', label: '轮播展示' }
      ]
    }
  },
  
  // watch 已由 debounce-mixin 提供
  
  methods: {
    // 实现 upload-security-mixin 要求的方法
    getImageCount() {
      return (this.localData.credentials || []).length
    },
    
    // ✅ 初始化数据，确保credentials数组存在
    initializeData() {
      // 使用智能克隆方法
      const data = this._smartClone ? this._smartClone(this.data) : { ...this.data }
      
      // 确保credentials数组存在
      if (!data.credentials) {
        data.credentials = []
      }
      
      // 确保layout字段存在
      if (!data.layout) {
        data.layout = 'grid'
      }
      
      // 确保showDate字段存在
      if (data.showDate === undefined) {
        data.showDate = true
      }
      
      // 确保enableZoom字段存在
      if (data.enableZoom === undefined) {
        data.enableZoom = true
      }
      
      return data
    },
    
    // emitChange 方法现在由 debounce-mixin 提供
    
    addCredential() {
      // 安全检查：数量限制
      if (!this.canAddMoreImages) {
        alert(`最多只能添加${this.MAX_IMAGES}个证书`)
        return
      }
      
      // 安全检查：上传频率限制
      const frequencyCheck = this.checkUploadFrequency()
      if (!frequencyCheck.allowed) {
        alert(`操作过于频繁，请${frequencyCheck.remaining}秒后再试`)
        return
      }
      
      // 确保 credentials 数组存在
      if (!this.localData.credentials) {
        this.$set(this.localData, 'credentials', [])
      }
      
      // 创建新证书对象
      const newCredential = {
        id: `credential-${Date.now()}`,
        image: '',
        title: '',
        issuer: '',
        date: ''
      }
      
      // 使用 unshift 将新证书添加到数组开头
      this.localData.credentials.unshift(newCredential)
      
      // 在下一个tick中确保响应式并触发更新
      this.$nextTick(() => {
        if (this.localData.credentials[0]) {
          // 强制设置每个属性为响应式
          this.$set(this.localData.credentials[0], 'id', newCredential.id)
          this.$set(this.localData.credentials[0], 'image', newCredential.image)
          this.$set(this.localData.credentials[0], 'title', newCredential.title)
          this.$set(this.localData.credentials[0], 'issuer', newCredential.issuer)
          this.$set(this.localData.credentials[0], 'date', newCredential.date)
        }
        
        this.updateUploadTimestamp()
        this.emitChangeImmediate()
        
        // 添加后自动滚动到顶部
        const container = this.$el.querySelector('.credentials-list')
        if (container) {
          container.scrollTop = 0
        }
      })
    },
    
    removeCredential(index) {
      // 防御性检查
      if (!this.localData.credentials || index < 0 || index >= this.localData.credentials.length) {
        console.warn('removeCredential: 无效的索引', index)
        return
      }
      
      if (confirm('确定要删除这个证书吗？')) {
        this.localData.credentials.splice(index, 1)
        
        // 在下一个tick中触发更新
        this.$nextTick(() => {
          this.emitChangeImmediate()
        })
      }
    },
    
    selectLayout(layout) {
      this.localData.layout = layout
      this.emitChangeImmediate()
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
}

.credentials-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.credential-card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.credential-header {
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

.credential-index {
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

.credential-body {
  padding: 20px;
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
}

.layout-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.layout-option {
  padding: 12px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
}

.layout-option.active {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.05);
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
</style>

