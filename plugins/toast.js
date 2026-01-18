/**
 * Toast 通知插件
 * 提供全局通知功能
 */

export default function ({ app }, inject) {
  // 简单的toast实现
  const toast = {
    success(message, options = {}) {
      this.show(message, 'success', options)
    },
    
    error(message, options = {}) {
      this.show(message, 'error', options)
    },
    
    info(message, options = {}) {
      this.show(message, 'info', options)
    },
    
    warning(message, options = {}) {
      this.show(message, 'warning', options)
    },
    
    show(message, type = 'info', options = {}) {
      // 只在客户端显示toast
      if (typeof document === 'undefined' || !process.client) {
        console.log(`[Toast ${type}] ${message}`)
        return
      }
      
      // 创建toast元素
      const toastEl = document.createElement('div')
      toastEl.className = `toast toast-${type}`
      toastEl.textContent = message
      
      // 添加样式
      Object.assign(toastEl.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '4px',
        color: 'white',
        fontSize: '14px',
        zIndex: '9999',
        maxWidth: '300px',
        wordWrap: 'break-word',
        opacity: '0',
        transform: 'translateX(100%)',
        transition: 'all 0.3s ease'
      })
      
      // 根据类型设置背景色
      const colors = {
        success: '#52c41a',
        error: '#ff4d4f',
        info: '#1890ff',
        warning: '#faad14'
      }
      toastEl.style.backgroundColor = colors[type] || colors.info
      
      // 添加到页面
      document.body.appendChild(toastEl)
      
      // 显示动画
      setTimeout(() => {
        toastEl.style.opacity = '1'
        toastEl.style.transform = 'translateX(0)'
      }, 10)
      
      // 自动移除
      const duration = options.duration || 3000
      setTimeout(() => {
        toastEl.style.opacity = '0'
        toastEl.style.transform = 'translateX(100%)'
        setTimeout(() => {
          if (toastEl.parentNode) {
            toastEl.parentNode.removeChild(toastEl)
          }
        }, 300)
      }, duration)
    }
  }
  
  // 注入到Vue实例
  inject('toast', toast)
}
