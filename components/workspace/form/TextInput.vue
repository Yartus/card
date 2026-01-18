<template>
  <div class="text-input">
    <label v-if="label" class="input-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
      <span v-if="maxLength" class="char-count">
        {{ currentLength }}/{{ maxLength }}
      </span>
    </label>
    
    <input
      v-if="type !== 'textarea'"
      :type="type"
      :value="value"
      :placeholder="placeholder"
      :maxlength="maxLength"
      :required="required"
      :disabled="disabled"
      class="input-field"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />
    
    <textarea
      v-else
      :value="value"
      :placeholder="placeholder"
      :maxlength="maxLength"
      :required="required"
      :disabled="disabled"
      :rows="rows"
      class="textarea-field"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />
    
    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="hint && !error" class="hint-message">{{ hint }}</p>
  </div>
</template>

<script>
export default {
  name: 'TextInput',
  
  props: {
    value: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text',
      validator: (value) => ['text', 'email', 'url', 'tel', 'number', 'textarea'].includes(value)
    },
    placeholder: {
      type: String,
      default: ''
    },
    hint: {
      type: String,
      default: ''
    },
    required: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    maxLength: {
      type: Number,
      default: null
    },
    rows: {
      type: Number,
      default: 4
    },
    validation: {
      type: Function,
      default: null
    }
  },
  
  data() {
    return {
      error: '',
      isFocused: false
    }
  },
  
  computed: {
    currentLength() {
      return String(this.value || '').length
    }
  },
  
  methods: {
    handleInput(event) {
      const value = event.target.value
      this.$emit('input', value)
      
      // 清除错误提示
      if (this.error) {
        this.error = ''
      }
    },
    
    handleBlur(event) {
      this.isFocused = false
      this.$emit('blur', event)
      
      // 执行验证
      this.validate()
    },
    
    handleFocus(event) {
      this.isFocused = true
      this.$emit('focus', event)
    },
    
    validate() {
      this.error = ''
      
      // 必填验证
      if (this.required && !this.value) {
        this.error = '此字段为必填项'
        return false
      }
      
      // 自定义验证
      if (this.validation && this.value) {
        const validationResult = this.validation(this.value)
        if (validationResult !== true) {
          this.error = validationResult
          return false
        }
      }
      
      // 类型验证
      if (this.value) {
        if (this.type === 'email' && !this.isValidEmail(this.value)) {
          this.error = '请输入有效的邮箱地址'
          return false
        }
        
        if (this.type === 'url' && !this.isValidUrl(this.value)) {
          this.error = '请输入有效的URL地址'
          return false
        }
      }
      
      return true
    },
    
    isValidEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    
    isValidUrl(url) {
      try {
        new URL(url)
        return true
      } catch {
        return false
      }
    }
  }
}
</script>

<style scoped>
.text-input {
  width: 100%;
  margin-bottom: 16px;
}

.input-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.required {
  color: #ff4757;
  margin-left: 4px;
}

.char-count {
  font-size: 12px;
  color: #666;
  font-weight: normal;
}

.input-field,
.textarea-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  color: #1a1a2e;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 170, 0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.input-field:focus,
.textarea-field:focus {
  outline: none;
  border-color: #00ffaa;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(0, 255, 170, 0.1);
}

.input-field:disabled,
.textarea-field:disabled {
  background: rgba(0, 0, 0, 0.05);
  cursor: not-allowed;
  opacity: 0.6;
}

.textarea-field {
  resize: vertical;
  min-height: 100px;
}

.error-message {
  color: #ff4757;
  font-size: 12px;
  margin-top: 4px;
}

.hint-message {
  color: #666;
  font-size: 12px;
  margin-top: 4px;
}
</style>

