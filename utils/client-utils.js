/**
 * 客户端环境检测工具函数
 * 用于安全地检测和访问浏览器环境中的对象
 */

/**
 * 安全地检测 window 对象是否存在
 * @returns {boolean}
 */
export function isClient() {
  return typeof window !== 'undefined' && process.client
}

/**
 * 安全地访问 window 对象
 * @param {Function} callback - 回调函数，参数为 window 对象
 * @returns {any} 回调函数的返回值，如果不在客户端则返回 undefined
 */
export function safeWindow(callback) {
  if (isClient()) {
    return callback(window)
  }
  return undefined
}

/**
 * 安全地执行需要 window 对象的操作
 * @param {Function} operation - 需要 window 对象的操作
 * @param {any} fallback - 非客户端环境下的回退值
 * @returns {any}
 */
export function safeWindowOperation(operation, fallback = undefined) {
  if (isClient()) {
    try {
      return operation(window)
    } catch (error) {
      console.warn('Window operation failed:', error)
      return fallback
    }
  }
  return fallback
}

/**
 * 安全地打开新窗口
 * @param {string} url - 要打开的URL
 * @param {string} target - 目标窗口（默认为 '_blank'）
 * @returns {Window|null}
 */
export function safeOpenWindow(url, target = '_blank') {
  return safeWindowOperation(
    (win) => win.open(url, target),
    null
  )
}

/**
 * 安全地重定向到新URL
 * @param {string} url - 要重定向到的URL
 */
export function safeRedirect(url) {
  safeWindowOperation((win) => {
    win.location.href = url
  })
}

/**
 * 安全地访问 navigator 对象
 * @param {Function} callback - 回调函数，参数为 navigator 对象
 * @returns {any}
 */
export function safeNavigator(callback) {
  if (isClient() && typeof navigator !== 'undefined') {
    try {
      return callback(navigator)
    } catch (error) {
      console.warn('Navigator operation failed:', error)
      return undefined
    }
  }
  return undefined
}

/**
 * 安全地访问 document 对象
 * @param {Function} callback - 回调函数，参数为 document 对象
 * @returns {any}
 */
export function safeDocument(callback) {
  if (isClient() && typeof document !== 'undefined') {
    try {
      return callback(document)
    } catch (error) {
      console.warn('Document operation failed:', error)
      return undefined
    }
  }
  return undefined
}

/**
 * 检测是否为移动设备
 * @returns {boolean}
 */
export function isMobileDevice() {
  return safeNavigator((nav) => 
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(nav.userAgent)
  ) || false
}

/**
 * 检测企业微信环境
 * @returns {boolean}
 */
export function isWecomEnvironment() {
  return safeWindow((win) => 
    win.wx && win.wx.config
  ) || false
}

/**
 * 检测微信环境
 * @returns {boolean}
 */
export function isWechatEnvironment() {
  return safeNavigator((nav) => 
    /MicroMessenger/i.test(nav.userAgent)
  ) || false
}

/**
 * 安全地复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<boolean>} 是否复制成功
 */
export async function safeCopyToClipboard(text) {
  if (!isClient()) return false
  
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      // 降级方案
      return safeDocument((doc) => {
        const textarea = doc.createElement('textarea')
        textarea.value = text
        doc.body.appendChild(textarea)
        textarea.select()
        const success = doc.execCommand('copy')
        doc.body.removeChild(textarea)
        return success
      }) || false
    }
  } catch (error) {
    console.warn('Copy to clipboard failed:', error)
    return false
  }
}

/**
 * 安全地显示原生分享
 * @param {Object} shareData - 分享数据 {title, text, url}
 * @returns {Promise<boolean>} 是否分享成功
 */
export async function safeNativeShare(shareData) {
  if (!isClient() || !navigator.share) return false
  
  try {
    await navigator.share(shareData)
    return true
  } catch (error) {
    console.warn('Native share failed:', error)
    return false
  }
}

/**
 * 获取当前页面URL
 * @returns {string}
 */
export function getCurrentUrl() {
  return safeWindow((win) => win.location.href) || ''
}

/**
 * 获取当前页面域名
 * @returns {string}
 */
export function getCurrentOrigin() {
  return safeWindow((win) => win.location.origin) || ''
}
