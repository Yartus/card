<template>
  <div class="media-selector">
    <!-- 类型选择 -->
    <div class="media-type-tabs">
      <button
        v-for="type in mediaTypes"
        :key="type.value"
        :class="['type-tab', { active: localType === type.value }]"
        @click="selectType(type.value)"
      >
        <i :class="type.icon"></i>
        <span>{{ type.label }}</span>
      </button>
    </div>

    <!-- 图片上传 -->
    <div v-if="localType === 'image'" class="media-content">
      <div class="url-input-group">
        <input
          v-model="localValue"
          type="url"
          class="url-input"
          :placeholder="placeholder || '输入图片URL'"
          @input="handleChange"
        />
        <button
          v-if="localValue"
          class="clear-btn"
          @click="clearValue"
        >
          <i class="icon-close"></i>
        </button>
      </div>
      
      <!-- 图片预览 -->
      <div v-if="localValue" class="media-preview">
        <img :src="localValue" alt="预览" class="preview-image" />
      </div>
      
      <div class="upload-hint">
        <i class="icon-info"></i>
        支持JPG、PNG格式，建议小于2MB
      </div>
    </div>

    <!-- Lottie 动画选择 -->
    <div v-if="localType === 'lottie'" class="media-content">
      <div class="url-input-group">
        <input
          v-model="localValue"
          type="text"
          class="url-input"
          placeholder="输入Lottie动画URL（JSON格式）"
          @input="handleChange"
        />
        <button
          v-if="localValue"
          class="clear-btn"
          @click="clearValue"
        >
          <i class="icon-close"></i>
        </button>
      </div>

      <!-- Lottie 预览 -->
      <div v-if="localValue" class="media-preview">
        <LottieIcon
          :animation-data="localValue"
          :width="previewSize"
          :height="previewSize"
          :autoplay="true"
          :loop="true"
          fallback-icon="icon-animation"
          @error="handleLottieError"
        />
      </div>

      <div class="upload-hint">
        <i class="icon-info"></i>
        输入Lottie JSON文件URL，例如：/assets/animations/logo.json
      </div>
      
      <div class="lottie-resources">
        <p class="resources-title">📚 免费资源推荐：</p>
        <ul class="resources-list">
          <li><a href="https://lottiefiles.com/" target="_blank">LottieFiles</a> - 最大的动画库</li>
          <li><a href="https://iconscout.com/lottie-animations" target="_blank">Iconscout</a> - 高质量动画</li>
          <li><a href="https://lordicon.com/" target="_blank">Lordicon</a> - 专业图标动画</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MediaSelector',
  
  props: {
    // 当前值（图片URL或Lottie URL）
    value: {
      type: String,
      default: ''
    },
    // 当前类型（image/lottie）
    type: {
      type: String,
      default: 'image',
      validator: v => ['image', 'lottie'].includes(v)
    },
    // 占位符
    placeholder: {
      type: String,
      default: ''
    },
    // 预览尺寸
    previewSize: {
      type: Number,
      default: 80
    }
  },
  
  data() {
    return {
      localValue: this.value || '',
      localType: this.type || 'image',
      mediaTypes: [
        { value: 'image', label: '图片', icon: 'icon-image' },
        { value: 'lottie', label: 'Lottie动画', icon: 'icon-animation' }
      ]
    }
  },
  
  watch: {
    value(newVal) {
      this.localValue = newVal || ''
    },
    type(newVal) {
      this.localType = newVal || 'image'
    }
  },
  
  methods: {
    selectType(type) {
      this.localType = type
      // 切换类型时清空值
      this.localValue = ''
      this.emitChange()
    },
    
    handleChange() {
      this.emitChange()
    },
    
    clearValue() {
      this.localValue = ''
      this.emitChange()
    },
    
    emitChange() {
      this.$emit('input', this.localValue)
      this.$emit('type-change', this.localType)
      this.$emit('change', {
        value: this.localValue,
        type: this.localType
      })
    },
    
    handleLottieError(error) {
      console.warn('Lottie加载失败:', error)
      this.$toast?.error('动画加载失败，请检查URL是否正确')
    }
  }
}
</script>

<style lang="scss" scoped>
.media-selector {
  width: 100%;
}

/* 类型选择标签 */
.media-type-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 4px;
  background: #f8fafc;
  border-radius: 10px;
}

.type-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  
  i {
    font-size: 16px;
  }
  
  &:hover {
    color: #475569;
    background: rgba(102, 126, 234, 0.05);
  }
  
  &.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
  }
}

/* 内容区域 */
.media-content {
  width: 100%;
}

/* URL输入框 */
.url-input-group {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.url-input {
  flex: 1;
  padding: 10px 14px;
  padding-right: 40px;
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

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e2e8f0;
    color: #475569;
  }
  
  i {
    font-size: 12px;
  }
}

/* 预览区域 */
.media-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 2px dashed #cbd5e1;
  margin-bottom: 12px;
  min-height: 120px;
}

.preview-image {
  max-width: 100%;
  max-height: 100px;
  object-fit: contain;
  border-radius: 8px;
}

/* 提示文字 */
.upload-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
  
  i {
    font-size: 14px;
    color: #667eea;
  }
}

/* Lottie资源推荐 */
.lottie-resources {
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.resources-title {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.resources-list {
  list-style: none;
  padding: 0;
  margin: 0;
  
  li {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 6px;
    padding-left: 16px;
    position: relative;
    
    &::before {
      content: '•';
      position: absolute;
      left: 4px;
      color: #667eea;
    }
    
    a {
      color: #667eea;
      text-decoration: none;
      font-weight: 500;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

/* 图标 */
.icon-image::before { content: '🖼️'; }
.icon-animation::before { content: '✨'; }
.icon-close::before { content: '✕'; }
.icon-info::before { content: 'ℹ️'; }
</style>

