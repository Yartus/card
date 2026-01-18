/**
 * 配置表单防抖 Mixin（轻量优化版）
 * ✅ 避免频繁 JSON.stringify 拖垮 WebView
 * ✅ 使用字段级 diff，减少深拷贝
 */
export default {
  data() {
    return {
      debounceTimer: null,
      _lastDataVersion: 0 // 轻量版本号，替代 checksum
    }
  },
  
  watch: {
    data: {
      handler(newData) {
        // ✅ 轻量比对：只比关键字段，不做 JSON.stringify
        if (this._isDataChanged(newData)) {
          this._lastDataVersion++
          this.localData = this._lightClone(newData)
        }
      },
      deep: true
    }
  },
  
  methods: {
    /**
     * ✅ 轻量比对：只比关键字段，避免 JSON.stringify
     */
    _isDataChanged(newData) {
      if (!this.localData || !newData) return true
      
      // 关键字段比对（不序列化大字段如 items/logos/events）
      const keys = ['title', 'subtitle', 'mode', 'layout', 'theme', 'defaultStyle']
      for (const key of keys) {
        if (this.localData[key] !== newData[key]) return true
      }
      
      // 数组长度比对（不遍历内容）
      const arrayKeys = ['items', 'logos', 'events', 'highlights', 'points', 'credentials']
      for (const key of arrayKeys) {
        const oldLen = this.localData[key]?.length || 0
        const newLen = newData[key]?.length || 0
        if (oldLen !== newLen) return true
      }
      
      return false
    },
    
    /**
     * ✅ 轻量克隆：浅拷贝 + 数组复制，不用 JSON.stringify
     */
    _lightClone(data) {
      if (!data || typeof data !== 'object') return data
      
      const cloned = { ...data }
      
      // 只深拷贝数组（一层）
      for (const key in data) {
        if (Array.isArray(data[key])) {
          cloned[key] = data[key].map(item => 
            (item && typeof item === 'object') ? { ...item } : item
          )
        }
      }
      
      return cloned
    },
    
    /**
     * 🔧 兼容旧代码：保留 _smartClone 方法名
     */
    _smartClone(data) {
      return this._lightClone(data)
    },
    
    /**
     * 防抖的 emitChange 方法
     * @param {number} delay - 防抖延迟时间，默认 300ms
     */
    emitChange(delay = 300) {
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer)
      }
      
      this.debounceTimer = setTimeout(() => {
        this.$emit('change', this.localData)
        this.debounceTimer = null
      }, delay)
    },
    
    /**
     * 立即触发变更（用于删除、添加等操作）
     */
    emitChangeImmediate() {
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer)
        this.debounceTimer = null
      }
      this.$emit('change', this.localData)
    }
  },
  
  beforeDestroy() {
    // 组件销毁时，如果有未完成的防抖，立即触发
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
      this.$emit('change', this.localData)
    }
  }
}

