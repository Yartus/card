<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>编辑素材</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="saveAsset">
          <div class="form-group">
            <label>素材名称</label>
            <input 
              v-model="formData.name" 
              type="text" 
              class="form-input"
              placeholder="请输入素材名称"
              required
            >
          </div>
          
          <div class="form-group">
            <label>素材描述</label>
            <textarea 
              v-model="formData.description" 
              class="form-textarea"
              placeholder="请输入素材描述"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>标签</label>
            <input 
              v-model="tagInput" 
              type="text" 
              class="form-input"
              placeholder="输入标签后按回车添加"
              @keyup.enter="addTag"
            >
            <div v-if="formData.tags.length > 0" class="tags-list">
              <span 
                v-for="(tag, index) in formData.tags" 
                :key="index" 
                class="tag"
              >
                {{ tag }}
                <button type="button" @click="removeTag(index)" class="tag-remove">&times;</button>
              </span>
            </div>
          </div>
          
          <div class="form-group">
            <label>分类</label>
            <select v-model="formData.category" class="form-select">
              <option value="">请选择分类</option>
              <option value="image">图片</option>
              <option value="video">视频</option>
              <option value="document">文档</option>
              <option value="other">其他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>可见性</label>
            <div class="radio-group">
              <label class="radio-item">
                <input 
                  v-model="formData.isPublic" 
                  type="radio" 
                  :value="true"
                >
                公开
              </label>
              <label class="radio-item">
                <input 
                  v-model="formData.isPublic" 
                  type="radio" 
                  :value="false"
                >
                私有
              </label>
            </div>
          </div>
        </form>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">取消</button>
        <button 
          class="btn btn-primary" 
          @click="saveAsset"
          :disabled="saving"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetEditModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    asset: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      formData: {
        name: '',
        description: '',
        tags: [],
        category: '',
        isPublic: true
      },
      tagInput: '',
      saving: false
    }
  },
  watch: {
    asset: {
      handler(newAsset) {
        if (newAsset && Object.keys(newAsset).length > 0) {
          this.formData = {
            name: newAsset.name || '',
            description: newAsset.description || '',
            tags: [...(newAsset.tags || [])],
            category: newAsset.category || '',
            isPublic: newAsset.isPublic !== false
          }
        }
      },
      immediate: true
    }
  },
  methods: {
    close() {
      this.$emit('close')
      this.resetForm()
    },
    
    resetForm() {
      this.formData = {
        name: '',
        description: '',
        tags: [],
        category: '',
        isPublic: true
      }
      this.tagInput = ''
    },
    
    addTag() {
      const tag = this.tagInput.trim()
      if (tag && !this.formData.tags.includes(tag)) {
        this.formData.tags.push(tag)
        this.tagInput = ''
      }
    },
    
    removeTag(index) {
      this.formData.tags.splice(index, 1)
    },
    
    async saveAsset() {
      if (!this.formData.name.trim()) {
        this.$toast.error('请输入素材名称')
        return
      }
      
      this.saving = true
      try {
        const response = await this.$axios.put(`/api/admin/assets/${this.asset.id}`, this.formData)
        this.$emit('saved', response.data)
        this.close()
        this.$toast.success('素材更新成功')
      } catch (error) {
        console.error('保存失败:', error)
        this.$toast.error('保存失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.tags-list {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.tag-remove {
  background: none;
  border: none;
  margin-left: 4px;
  cursor: pointer;
  color: #999;
  font-size: 16px;
  line-height: 1;
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-item input {
  margin-right: 6px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
