/**
 * 图片上传安全限制 Mixin
 * 
 * 统一的安全配置，适用于所有多图片上传模块
 * 支持租户级别的自定义配置
 */

import getUploadLimits from './upload-limits'

export default {
  data() {
    // 获取租户配置（从Vuex store或默认配置）
    const tenantId = this.$store?.state?.tenant?.id || null
    const limits = getUploadLimits(tenantId)
    
    return {
      // 安全限制配置（从租户配置加载）
      MAX_IMAGES: limits.MAX_IMAGES,
      MAX_BATCH_UPLOAD: limits.MAX_BATCH_UPLOAD,
      UPLOAD_COOLDOWN: limits.UPLOAD_COOLDOWN,
      MAX_FILE_SIZE: limits.MAX_FILE_SIZE,
      
      // 允许的文件类型
      ALLOWED_MIME_TYPES: limits.ALLOWED_MIME_TYPES,
      ALLOWED_EXTENSIONS: limits.ALLOWED_EXTENSIONS,
      
      // 上传控制状态
      lastUploadTime: 0,
      isUploading: false,
      uploadCount: 0
    }
  },
  
  created() {
    // 监听租户配置变化（如果需要）
    if (this.$store) {
      this.$store.watch(
        (state) => state.tenant?.uploadLimits,
        (newLimits) => {
          if (newLimits) {
            this.updateLimits(newLimits)
          }
        }
      )
    }
  },
  
  computed: {
    /**
     * 检查是否可以添加更多图片
     */
    canAddMoreImages() {
      const imageCount = this.getImageCount()
      return imageCount < this.MAX_IMAGES
    },
    
    /**
     * 还能添加多少张图片
     */
    remainingImageSlots() {
      const imageCount = this.getImageCount()
      return Math.max(0, this.MAX_IMAGES - imageCount)
    }
  },
  
  methods: {
    /**
     * 更新限制配置（运行时动态更新）
     * @param {Object} newLimits - 新的限制配置
     */
    updateLimits(newLimits) {
      if (newLimits.MAX_IMAGES !== undefined) {
        this.MAX_IMAGES = newLimits.MAX_IMAGES
      }
      if (newLimits.MAX_BATCH_UPLOAD !== undefined) {
        this.MAX_BATCH_UPLOAD = newLimits.MAX_BATCH_UPLOAD
      }
      if (newLimits.UPLOAD_COOLDOWN !== undefined) {
        this.UPLOAD_COOLDOWN = newLimits.UPLOAD_COOLDOWN
      }
      if (newLimits.MAX_FILE_SIZE !== undefined) {
        this.MAX_FILE_SIZE = newLimits.MAX_FILE_SIZE
      }
      if (newLimits.ALLOWED_MIME_TYPES) {
        this.ALLOWED_MIME_TYPES = newLimits.ALLOWED_MIME_TYPES
      }
      if (newLimits.ALLOWED_EXTENSIONS) {
        this.ALLOWED_EXTENSIONS = newLimits.ALLOWED_EXTENSIONS
      }
    },
    
    /**
     * 获取当前图片数量
     * 子组件需要实现这个方法
     */
    getImageCount() {
      console.warn('getImageCount() 方法未实现，请在子组件中实现')
      return 0
    },
    
    /**
     * 上传频率检查
     * @returns {Object} { allowed: boolean, remaining: number }
     */
    checkUploadFrequency() {
      const now = Date.now()
      const timeSinceLastUpload = now - this.lastUploadTime
      
      if (timeSinceLastUpload < this.UPLOAD_COOLDOWN) {
        const remaining = Math.ceil((this.UPLOAD_COOLDOWN - timeSinceLastUpload) / 1000)
        return { allowed: false, remaining }
      }
      
      return { allowed: true, remaining: 0 }
    },
    
    /**
     * 数量限制检查
     * @param {number} newImageCount - 要添加的图片数量
     * @returns {Object} { allowed: boolean, message: string }
     */
    checkImageQuota(newImageCount) {
      const currentCount = this.getImageCount()
      
      // 检查1：是否已达上限
      if (currentCount >= this.MAX_IMAGES) {
        return {
          allowed: false,
          message: `最多只能添加${this.MAX_IMAGES}张图片，已达上限`
        }
      }
      
      // 检查2：单次批量上传限制
      if (newImageCount > this.MAX_BATCH_UPLOAD) {
        return {
          allowed: false,
          message: `单次最多上传${this.MAX_BATCH_UPLOAD}张图片，您选择了${newImageCount}张`
        }
      }
      
      // 检查3：总数量限制
      const availableSlots = this.MAX_IMAGES - currentCount
      if (newImageCount > availableSlots) {
        return {
          allowed: false,
          message: `最多只能添加${this.MAX_IMAGES}张图片，当前已有${currentCount}张，还能添加${availableSlots}张`
        }
      }
      
      return { allowed: true, message: '' }
    },
    
    /**
     * 文件类型和大小验证
     * @param {File[]} files - 要验证的文件列表
     * @returns {Object} { valid: boolean, invalidFiles: string[], validFiles: File[] }
     */
    validateFiles(files) {
      const invalidFiles = []
      const validFiles = []
      
      for (const file of files) {
        let isValid = true
        let reason = ''
        
        // 检查1：MIME类型
        if (!this.ALLOWED_MIME_TYPES.includes(file.type)) {
          isValid = false
          reason = '不支持的文件类型'
        }
        
        // 检查2：文件扩展名
        if (isValid) {
          const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
          if (!this.ALLOWED_EXTENSIONS.includes(extension)) {
            isValid = false
            reason = '不支持的文件扩展名'
          }
        }
        
        // 检查3：文件大小
        if (isValid && file.size > this.MAX_FILE_SIZE) {
          isValid = false
          reason = `超过${this.MAX_FILE_SIZE / 1024}KB限制`
        }
        
        if (isValid) {
          validFiles.push(file)
        } else {
          invalidFiles.push(`${file.name} (${reason})`)
        }
      }
      
      return {
        valid: invalidFiles.length === 0,
        invalidFiles,
        validFiles
      }
    },
    
    /**
     * ✅ 上传前简单检查（无参数版本，供BlockEditor/AssetEditorModal调用）
     * @returns {Object} { allowed: boolean, reason: string, message: string, waitTime: number }
     */
    quickSecurityCheck() {
      // 1. 检查上传频率
      const frequencyCheck = this.checkUploadFrequency()
      if (!frequencyCheck.allowed) {
        return {
          allowed: false,
          reason: 'frequency',
          message: `上传过于频繁，请${frequencyCheck.remaining}秒后再试`,
          waitTime: frequencyCheck.remaining
        }
      }
      
      // 2. 检查图片数量配额
      const currentCount = this.getImageCount()
      if (currentCount >= this.MAX_IMAGES) {
        return {
          allowed: false,
          reason: 'quota',
          message: `图片数量已达上限（${this.MAX_IMAGES}张）`,
          waitTime: 0
        }
      }
      
      // 3. 通过所有检查
      return {
        allowed: true,
        reason: '',
        message: '',
        waitTime: 0
      }
    },
    
    /**
     * 完整的上传前安全检查（带文件验证）
     * @param {File[]} files - 要上传的文件列表
     * @returns {Object} { allowed: boolean, message: string, validFiles: File[] }
     */
    securityCheckBeforeUpload(files) {
      // 检查1：上传频率
      const frequencyCheck = this.checkUploadFrequency()
      if (!frequencyCheck.allowed) {
        return {
          allowed: false,
          message: `操作过于频繁，请${frequencyCheck.remaining}秒后再试`,
          validFiles: []
        }
      }
      
      // 检查2：数量限制
      const quotaCheck = this.checkImageQuota(files.length)
      if (!quotaCheck.allowed) {
        return {
          allowed: false,
          message: quotaCheck.message,
          validFiles: []
        }
      }
      
      // 检查3：文件验证
      const fileValidation = this.validateFiles(files)
      if (!fileValidation.valid) {
        const message = `以下文件不符合要求：\n${fileValidation.invalidFiles.join('\n')}\n\n只支持JPG、PNG、GIF、SVG、WebP格式，单个文件最大${this.MAX_FILE_SIZE / 1024}KB`
        return {
          allowed: false,
          message,
          validFiles: []
        }
      }
      
      return {
        allowed: true,
        message: '',
        validFiles: fileValidation.validFiles
      }
    },
    
    /**
     * 更新上传时间戳
     */
    updateUploadTimestamp() {
      this.lastUploadTime = Date.now()
    },
    
    /**
     * 增加上传计数
     * @param {number} count - 上传的文件数量
     */
    incrementUploadCount(count) {
      this.uploadCount += count
      console.log(`📊 累计上传: ${this.uploadCount} 张图片`)
    }
  }
}

