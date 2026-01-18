/**
 * Lottie 动画插件
 * 提供Lottie动画支持
 */

export default function ({ app }, inject) {
  // 只在客户端加载lottie-web
  if (process.client) {
    const lottie = require('lottie-web')
    
    // 注入Lottie到Vue实例
    inject('lottie', lottie)
    
    // 提供便捷的Lottie方法
    const lottieUtils = {
      /**
       * 创建Lottie动画
       * @param {HTMLElement} container - 容器元素
       * @param {Object} options - 动画选项
       * @returns {Object} Lottie实例
       */
      create(container, options = {}) {
        const defaultOptions = {
          loop: true,
          autoplay: true,
          renderer: 'svg',
          ...options
        }
        
        return lottie.loadAnimation({
          container,
          ...defaultOptions
        })
      },
      
      /**
       * 播放动画
       * @param {Object} animation - Lottie实例
       */
      play(animation) {
        if (animation) {
          animation.play()
        }
      },
      
      /**
       * 暂停动画
       * @param {Object} animation - Lottie实例
       */
      pause(animation) {
        if (animation) {
          animation.pause()
        }
      },
      
      /**
       * 停止动画
       * @param {Object} animation - Lottie实例
       */
      stop(animation) {
        if (animation) {
          animation.stop()
        }
      },
      
      /**
       * 销毁动画
       * @param {Object} animation - Lottie实例
       */
      destroy(animation) {
        if (animation) {
          animation.destroy()
        }
      }
    }
    
    inject('lottieUtils', lottieUtils)
  } else {
    // 服务端渲染时提供空的实现
    inject('lottie', null)
    inject('lottieUtils', {
      create: () => null,
      play: () => {},
      pause: () => {},
      stop: () => {},
      destroy: () => {}
    })
  }
}
