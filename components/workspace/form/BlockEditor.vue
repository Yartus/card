<template>
  <div class="block-editor">
    <!-- 工具栏 -->
    <div class="editor-toolbar">
      <button 
        class="btn-add-block" 
        @click="addTextBlock"
        :disabled="!canAddMoreBlocks"
      >
        <i class="icon-text">📝</i>
        添加文字
      </button>
      <button 
        class="btn-add-block" 
        @click="addImageBlock"
        :disabled="!canAddMoreImages"
      >
        <i class="icon-image">🖼</i>
        添加图片
      </button>
      <button 
        class="btn-add-block" 
        @click="addHighlightBlock"
        :disabled="!canAddMoreBlocks"
      >
        <i class="icon-highlight">💡</i>
        添加亮点
      </button>
      <button 
        class="btn-add-block" 
        @click="addShopDirectBlock"
        :disabled="!canAddMoreBlocks"
      >
        <i class="icon-shop">🛒</i>
        添加网店直达
      </button>
    </div>

    <!-- 配额提示 -->
    <div v-if="quotaInfo" class="quota-info" :class="quotaClass">
      <i class="icon-info">ℹ️</i>
      <span>{{ quotaInfo }}</span>
    </div>

    <!-- 内容块列表 -->
    <div v-if="localBlocks.length === 0" class="empty-state">
      <div class="empty-icon">📄</div>
      <p class="empty-text">开始创建内容块</p>
      <p class="empty-hint">点击上方按钮添加文字、图片或数据亮点</p>
    </div>

    <draggable
      v-else
      v-model="localBlocks"
      class="blocks-list"
      handle=".drag-handle"
      :move="onBlockMove"
      @change="emitChange"
    >
      <div
        v-for="(block, index) in localBlocks"
        :key="block.id"
        :class="['block-card', `block-type-${block.type}`]"
      >
        <!-- 拖拽手柄 -->
        <div class="block-header">
          <i class="drag-handle icon-drag">☰</i>
          <span class="block-type-badge">
            {{ getBlockTypeName(block.type) }}
          </span>
          <button class="btn-remove-block" @click="removeBlock(index)">
            <i class="icon-delete">✕</i>
          </button>
        </div>

        <!-- 文字块 -->
        <div v-if="block.type === 'text'" class="block-content">
          <TextInput
            v-model="localBlocks[index].content"
            type="textarea"
            label=""
            placeholder="输入文字内容，支持换行..."
            :rows="6"
            :required="true"
            @input="emitChange"
          />
        </div>

        <!-- 图片块 -->
        <div v-if="block.type === 'image'" class="block-content">
          <div class="image-preview-area">
            <div v-if="localBlocks[index].src" class="image-preview">
              <img :src="localBlocks[index].src" alt="图片" />
              <div class="image-actions">
                <button class="btn-image-action" @click="replaceImage(index)">
                  <i class="icon-upload">📤</i>
                  更换
                </button>
              </div>
            </div>
            <div v-else class="image-upload-placeholder" @click="uploadImage(index)">
              <i class="icon-image-upload">🖼</i>
              <span>点击上传图片</span>
              <p class="upload-hint">推荐横图，比例 16:9 或 4:3</p>
            </div>
          </div>
          <TextInput
            v-model="localBlocks[index].caption"
            label="图片说明（可选）"
            placeholder="添加图片说明文字"
            @input="emitChange"
          />
        </div>

        <!-- 数据亮点块 -->
        <div v-if="block.type === 'highlight'" class="block-content">
          <div class="highlight-fields">
            <div class="highlight-row">
              <TextInput
                v-model="localBlocks[index].label"
                label="标签"
                placeholder="例如：客户数量"
                :required="true"
                @input="emitChange"
              />
              <TextInput
                v-model="localBlocks[index].value"
                label="数值"
                placeholder="例如：10000+"
                :required="true"
                @input="emitChange"
              />
            </div>
            <IconPicker
              v-if="localBlocks[index] && localBlocks[index].type === 'highlight'"
              :value="localBlocks[index].icon || '📊'"
              :type="localBlocks[index].iconType || 'emoji'"
              label="图标（可选）"
              placeholder="选择图标"
              @input="updateIcon(index, $event)"
              @update:type="updateIconType(index, $event)"
            />
          </div>
        </div>

        <!-- 网店直达块 -->
        <div v-if="block.type === 'shop-direct'" class="block-content shop-direct-block-editor">
          <ShopDirectBlockEditor
            :block-index="index"
            :block-data="localBlocks[index]"
            @update="updateShopDirectBlock(index, $event)"
          />
        </div>
      </div>
    </draggable>

    <!-- 隐藏的文件上传输入 -->
    <input
      ref="imageInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleImageUpload"
    />
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import TextInput from './TextInput.vue'
import IconPicker from './IconPicker.vue'
import ShopDirectBlockEditor from './ShopDirectBlockEditor.vue'
import uploadSecurityMixin from '../config/upload-security-mixin'

export default {
  name: 'BlockEditor',
  
  components: {
    draggable,
    TextInput,
    IconPicker,
    ShopDirectBlockEditor
  },
  
  mixins: [uploadSecurityMixin],
  
  props: {
    value: {
      type: Array,
      default: () => []
    },
    maxBlocks: {
      type: Number,
      default: 20
    },
    maxImages: {
      type: Number,
      default: 10
    }
  },
  
  data() {
    return {
      localBlocks: [],
      currentUploadIndex: null
    }
  },
  
  computed: {
    imageCount() {
      return this.localBlocks.filter(b => b.type === 'image').length
    },
    
    canAddMoreBlocks() {
      return this.localBlocks.length < this.maxBlocks
    },
    
    canAddMoreImages() {
      return this.imageCount < this.maxImages && this.canAddMoreBlocks
    },
    
    quotaInfo() {
      const imageUsed = this.imageCount
      const imageLeft = this.maxImages - imageUsed
      const blocksUsed = this.localBlocks.length
      const blocksLeft = this.maxBlocks - blocksUsed
      
      if (blocksLeft <= 3) {
        return `内容块已使用 ${blocksUsed}/${this.maxBlocks}，剩余 ${blocksLeft} 个`
      }
      
      if (imageLeft <= 2 && imageLeft > 0) {
        return `图片已使用 ${imageUsed}/${this.maxImages}，剩余 ${imageLeft} 张`
      }
      
      if (imageLeft === 0) {
        return `图片数量已达上限（${this.maxImages}张）`
      }
      
      if (blocksLeft === 0) {
        return `内容块数量已达上限（${this.maxBlocks}个）`
      }
      
      return null
    },
    
    quotaClass() {
      const imageLeft = this.maxImages - this.imageCount
      const blocksLeft = this.maxBlocks - this.localBlocks.length
      
      if (imageLeft === 0 || blocksLeft === 0) {
        return 'quota-full'
      }
      
      if (imageLeft <= 2 || blocksLeft <= 3) {
        return 'quota-warning'
      }
      
      return 'quota-normal'
    }
  },
  
  watch: {
    value: {
      immediate: true,
      deep: true,
      handler(newValue, oldValue) {
        if (Array.isArray(newValue)) {
          // 只有当值真正变化时才更新（避免循环更新）
          const newStr = JSON.stringify(newValue)
          const oldStr = JSON.stringify(this.localBlocks)
          if (newStr !== oldStr) {
            this.localBlocks = JSON.parse(JSON.stringify(newValue))
          }
        } else if (!newValue && this.localBlocks.length > 0) {
          // 如果外部传入空值，清空本地数据
          this.localBlocks = []
        }
      }
    }
  },
  
  methods: {
    // 实现 upload-security-mixin 要求的方法
    getImageCount() {
      return this.imageCount
    },
    
    // ✅ 封装上传安全检查方法
    checkUploadLimit() {
      const check = this.quickSecurityCheck()  // ✅ 修复：调用无参数版本
      
      if (!check.allowed) {
        // 根据不同的拒绝原因显示不同提示
        if (check.reason === 'frequency') {
          this.$toast?.error(`上传过于频繁，请${check.waitTime}秒后再试`)
        } else if (check.reason === 'quota') {
          this.$toast?.error(`图片数量已达上限（${this.maxImages}张）`)
        } else {
          this.$toast?.error(check.message || '暂时无法上传')
        }
        return false
      }
      
      return true
    },
    
    getBlockTypeName(type) {
      const names = {
        text: '📝 文字',
        image: '🖼 图片',
        highlight: '💡 亮点',
        'shop-direct': '🛒 网店直达'
      }
      return names[type] || type
    },
    
    addTextBlock() {
      if (!this.canAddMoreBlocks) {
        this.$toast?.warning('内容块数量已达上限')
        return
      }
      
      const newBlock = {
        id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'text',
        content: ''
      }
      
      // ✅ 按时间顺序添加：先添加的在上面，后添加的在下面
      // 但需要排除网店直达块，确保网店直达始终在最后
      const shopDirectIndex = this.localBlocks.findIndex(b => b.type === 'shop-direct')
      if (shopDirectIndex >= 0) {
        // 如果存在网店直达块，插入到它之前
        this.localBlocks.splice(shopDirectIndex, 0, newBlock)
      } else {
        // 如果没有网店直达块，直接添加到末尾
        this.localBlocks.push(newBlock)
      }
      this.emitChange()
    },
    
    addImageBlock() {
      if (!this.canAddMoreImages) {
        if (this.imageCount >= this.maxImages) {
          this.$toast?.warning(`图片数量已达上限（${this.maxImages}张）`)
        } else {
          this.$toast?.warning('内容块数量已达上限')
        }
        return
      }
      
      // ✅ 使用封装的安全检查方法
      if (!this.checkUploadLimit()) {
        return
      }
      
      const newBlock = {
        id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'image',
        src: '',
        caption: ''
      }
      
      // ✅ 按时间顺序添加：先添加的在上面，后添加的在下面
      // 但需要排除网店直达块，确保网店直达始终在最后
      const shopDirectIndex = this.localBlocks.findIndex(b => b.type === 'shop-direct')
      if (shopDirectIndex >= 0) {
        // 如果存在网店直达块，插入到它之前
        this.localBlocks.splice(shopDirectIndex, 0, newBlock)
        this.currentUploadIndex = shopDirectIndex
      } else {
        // 如果没有网店直达块，直接添加到末尾
        this.localBlocks.push(newBlock)
        this.currentUploadIndex = this.localBlocks.length - 1
      }
      this.emitChange()
      
      // 自动触发上传
      this.$nextTick(() => {
        this.$refs.imageInput.click()
      })
    },
    
    addHighlightBlock() {
      if (!this.canAddMoreBlocks) {
        this.$toast?.warning('内容块数量已达上限')
        return
      }
      
      try {
        const newBlock = {
          id: `block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'highlight',
          label: '',
          value: '',
          icon: '📊',
          iconType: 'emoji'
        }
        
        // ✅ 按时间顺序添加：先添加的在上面，后添加的在下面
        // 但需要排除网店直达块，确保网店直达始终在最后
        const shopDirectIndex = this.localBlocks.findIndex(b => b.type === 'shop-direct')
        let insertedIndex
        if (shopDirectIndex >= 0) {
          // 如果存在网店直达块，插入到它之前
          this.localBlocks.splice(shopDirectIndex, 0, newBlock)
          insertedIndex = shopDirectIndex
        } else {
          // 如果没有网店直达块，直接添加到末尾
          this.localBlocks.push(newBlock)
          insertedIndex = this.localBlocks.length - 1
        }
        // 确保新添加的块有正确的属性
        if (this.localBlocks[insertedIndex]) {
          this.$set(this.localBlocks[insertedIndex], 'icon', newBlock.icon)
          this.$set(this.localBlocks[insertedIndex], 'iconType', newBlock.iconType)
        }
        
        this.$nextTick(() => {
          this.emitChange()
        })
      } catch (error) {
        console.error('⚠️ 添加亮点块失败:', error)
        this.$toast?.error('添加亮点块失败，请重试')
      }
    },
    
    addShopDirectBlock() {
      if (!this.canAddMoreBlocks) {
        this.$toast?.warning('内容块数量已达上限')
        return
      }
      
      try {
        // ✅ 检查是否已存在网店直达块
        const existingIndex = this.localBlocks.findIndex(b => b.type === 'shop-direct')
        
        if (existingIndex >= 0) {
          // 如果已存在，提示用户并询问是否替换
          if (confirm('已存在网店直达模块，是否替换为新的网店直达模块？')) {
            // 替换现有的网店直达块
            const newBlock = {
              id: `block-shop-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              type: 'shop-direct',
              data: {
                title: '网店直达',
                subtitle: '',
                shops: []
              }
            }
            this.$set(this.localBlocks, existingIndex, newBlock)
            this.emitChange()
          } else {
            // 用户选择不替换，直接返回
            return
          }
        } else {
          // 如果不存在，添加到末尾（作为标准结尾）
          const newBlock = {
            id: `block-shop-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            type: 'shop-direct',
            data: {
              title: '网店直达',
              subtitle: '',
              shops: []
            }
          }
          this.localBlocks.push(newBlock)
          this.$nextTick(() => {
            this.emitChange()
          })
        }
      } catch (error) {
        console.error('⚠️ 添加网店直达块失败:', error)
        this.$toast?.error('添加网店直达块失败，请重试')
      }
    },
    
    updateShopDirectBlock(index, newData) {
      if (index < 0 || index >= this.localBlocks.length) return
      if (this.localBlocks[index].type !== 'shop-direct') return
      
      this.$set(this.localBlocks[index], 'data', newData)
      this.emitChange()
    },
    
    removeBlock(index) {
      if (index < 0 || index >= this.localBlocks.length) return
      
      this.localBlocks.splice(index, 1)
      this.emitChange()
    },
    
    uploadImage(index) {
      // ✅ 使用封装的安全检查方法
      if (!this.checkUploadLimit()) {
        return
      }
      
      this.currentUploadIndex = index
      this.$refs.imageInput.click()
    },
    
    replaceImage(index) {
      // ✅ 使用封装的安全检查方法
      if (!this.checkUploadLimit()) {
        return
      }
      
      this.currentUploadIndex = index
      this.$refs.imageInput.click()
    },
    
    async handleImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      if (this.currentUploadIndex === null) {
        this.$toast?.error('上传索引错误')
        return
      }
      
      try {
        // 使用 ImageUpload 组件的压缩逻辑
        const compressedFile = await this.compressImage(file)
        
        // 上传到服务器
        const formData = new FormData()
        formData.append('file', compressedFile)
        formData.append('file_type', 'image')
        
        const token = this.$wecomAuth?.getToken()
        const response = await this.$axios.post('/api/v1/files/upload', formData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (response.data.success) {
          // 更新图片块的 src
          this.$set(this.localBlocks[this.currentUploadIndex], 'src', response.data.url)
          this.emitChange()
          this.$toast?.success('图片上传成功')
        } else {
          throw new Error(response.data.error || '上传失败')
        }
      } catch (error) {
        console.error('图片上传失败:', error)
        this.$toast?.error(error.response?.data?.error || '图片上传失败')
      } finally {
        // 清空文件输入
        event.target.value = ''
        this.currentUploadIndex = null
      }
    },
    
    async compressImage(file) {
      // 复用 ImageUpload 的压缩逻辑
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = new Image()
          img.onload = () => {
            const MAX_WIDTH = 1200
            let width = img.width
            let height = img.height
            
            if (width > MAX_WIDTH) {
              height = Math.round((height * MAX_WIDTH) / width)
              width = MAX_WIDTH
            }
            
            const canvas = document.createElement('canvas')
            canvas.width = width
            canvas.height = height
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)
            
            canvas.toBlob((blob) => {
              if (blob) {
                const compressedFile = new File([blob], file.name, {
                  type: 'image/jpeg',
                  lastModified: Date.now()
                })
                resolve(compressedFile)
              } else {
                reject(new Error('压缩失败'))
              }
            }, 'image/jpeg', 0.75)
          }
          img.onerror = () => reject(new Error('图片加载失败'))
          img.src = e.target.result
        }
        reader.onerror = () => reject(new Error('文件读取失败'))
        reader.readAsDataURL(file)
      })
    },
    
    // 更新图标值
    updateIcon(index, newIcon) {
      try {
        if (index < 0 || index >= this.localBlocks.length) {
          console.warn('updateIcon: 索引超出范围', index)
          return
        }
        if (!this.localBlocks[index]) {
          console.warn('updateIcon: 块不存在', index)
          return
        }
        if (this.localBlocks[index].type !== 'highlight') {
          console.warn('updateIcon: 块类型不是亮点', this.localBlocks[index].type)
          return
        }
        
        this.$set(this.localBlocks[index], 'icon', newIcon || '📊')
        this.emitChange()
      } catch (error) {
        console.error('⚠️ 更新图标失败:', error)
        this.$toast?.error('更新图标失败，请重试')
      }
    },
    
    // 更新图标类型
    updateIconType(index, newType) {
      try {
        if (index < 0 || index >= this.localBlocks.length) {
          console.warn('updateIconType: 索引超出范围', index)
          return
        }
        if (!this.localBlocks[index]) {
          console.warn('updateIconType: 块不存在', index)
          return
        }
        if (this.localBlocks[index].type !== 'highlight') {
          console.warn('updateIconType: 块类型不是亮点', this.localBlocks[index].type)
          return
        }
        
        this.$set(this.localBlocks[index], 'iconType', newType || 'emoji')
        this.emitChange()
      } catch (error) {
        console.error('⚠️ 更新图标类型失败:', error)
        this.$toast?.error('更新图标类型失败，请重试')
      }
    },
    
    // ✅ 限制网店直达块的拖拽位置：只能放在最后
    onBlockMove(evt) {
      const draggedBlock = evt.draggedContext.element
      
      // 如果拖拽的是网店直达块
      if (draggedBlock.type === 'shop-direct') {
        // 检查目标位置是否是最后一个位置
        const targetIndex = evt.draggedContext.futureIndex
        const maxIndex = this.localBlocks.length - 1
        
        if (targetIndex !== maxIndex) {
          // 不允许移动到非最后位置
          this.$toast?.info('网店直达模块必须放在最后位置')
          return false // 阻止移动
        }
      } else {
        // 如果拖拽的是其他块，检查目标位置是否在网店直达块之后
        const shopDirectIndex = this.localBlocks.findIndex(b => b.type === 'shop-direct')
        if (shopDirectIndex >= 0) {
          const targetIndex = evt.draggedContext.futureIndex
          if (targetIndex > shopDirectIndex) {
            // 不允许移动到网店直达块之后
            this.$toast?.info('网店直达模块必须放在最后位置')
            return false // 阻止移动
          }
        }
      }
      
      return true // 允许移动
    },
    
    emitChange() {
      // 深拷贝避免引用问题
      const blocksCopy = JSON.parse(JSON.stringify(this.localBlocks))
      this.$emit('input', blocksCopy)
      this.$emit('change', blocksCopy)
    }
  }
}
</script>

<style lang="scss" scoped>
.block-editor {
  width: 100%;
}

/* 工具栏 */
.editor-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9ff;
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.btn-add-block {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: white;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #595959;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    border-color: #667eea;
    background: #f0f4ff;
    color: #667eea;
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  i {
    font-size: 18px;
  }
}

/* 配额信息 */
.quota-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  border-radius: 8px;
  font-size: 13px;
  
  &.quota-normal {
    background: #e6f7ff;
    border: 1px solid #91d5ff;
    color: #0050b3;
  }
  
  &.quota-warning {
    background: #fffbe6;
    border: 1px solid #ffe58f;
    color: #d46b08;
  }
  
  &.quota-full {
    background: #fff1f0;
    border: 1px solid #ffccc7;
    color: #cf1322;
  }
  
  i {
    font-size: 16px;
  }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #fafafa;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .empty-text {
    font-size: 16px;
    font-weight: 600;
    color: #595959;
    margin: 0 0 8px 0;
  }
  
  .empty-hint {
    font-size: 13px;
    color: #8c8c8c;
    margin: 0;
  }
}

/* 内容块列表 */
.blocks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.block-card {
  background: white;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  }
}

.block-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.drag-handle {
  font-size: 18px;
  color: #bfbfbf;
  cursor: move;
  
  &:hover {
    color: #667eea;
  }
}

.block-type-badge {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #667eea;
}

.btn-remove-block {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff1f0;
  border: none;
  border-radius: 6px;
  color: #ff4d4f;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #ff4d4f;
    color: white;
    transform: scale(1.1);
  }
  
  i {
    font-size: 14px;
  }
}

/* 图片块 */
.image-preview-area {
  margin-bottom: 12px;
}

.image-preview {
  position: relative;
  width: 100%;
  max-width: 500px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  
  img {
    width: 100%;
    height: auto;
    display: block;
  }
  
  .image-actions {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 12px;
    background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
    display: flex;
    gap: 8px;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover .image-actions {
    opacity: 1;
  }
}

.btn-image-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
  }
  
  i {
    font-size: 14px;
  }
}

.image-upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 60px 20px;
  background: #f8f9ff;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f0f4ff;
  }
  
  i {
    font-size: 32px;
    color: #667eea;
  }
  
  span {
    font-size: 14px;
    font-weight: 600;
    color: #595959;
  }
  
  .upload-hint {
    font-size: 12px;
    color: #8c8c8c;
    margin: 0;
  }
}

/* 数据亮点块 */
.highlight-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.highlight-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-direction: column;
  }
  
  .highlight-row {
    grid-template-columns: 1fr;
  }
}
</style>

