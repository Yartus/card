/**
 * 网店唤醒工具函数
 * 统一处理电商平台（天猫/京东/拼多多/1688/淘宝/自定义）和微信生态（小程序/小店）的唤醒逻辑
 */

export default {
  /**
   * 打开网店/小程序/小店
   * @param {Object} shop - 网店配置对象
   */
  async openShop(shop) {
    // 根据平台类型选择不同的唤醒方式
    if (shop.platform === 'miniprogram' || shop.platform === 'wechat_shop') {
      // 微信小程序/小店：使用小程序唤醒逻辑
      return this.openMiniProgram(shop)
    } else {
      // 所有其他平台（包括天猫/京东/拼多多/1688/淘宝/自定义）：使用APP唤醒逻辑
      return this.openApp(shop)
    }
  },

  /**
   * 打开微信小程序（个人微信环境）
   * @param {Object} shop - 小程序配置
   */
  async openMiniProgram(shop) {
    const isWechat = /MicroMessenger/i.test(navigator.userAgent)
    const isWecom = /wxwork/i.test(navigator.userAgent)
    const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent)

    // 方案1：个人微信环境（主要场景）
    if (isWechat && !isWecom) {
      // 优先使用 URL Scheme
      if (shop.urlScheme) {
        try {
          window.location.href = shop.urlScheme
          // 3秒后如果未跳转，显示小程序码
          setTimeout(() => {
            this.showMiniProgramQR(shop)
          }, 3000)
          return
        } catch (error) {
          console.error('URL Scheme跳转失败:', error)
        }
      }
      
      // 如果没有 URL Scheme，尝试使用小程序链接
      // 小程序链接格式：https://mp.weixin.qq.com/mp/waerrpage?appid=xxx&path=xxx
      if (shop.appId) {
        const miniProgramUrl = `https://mp.weixin.qq.com/mp/waerrpage?appid=${shop.appId}&path=${encodeURIComponent(shop.path || '')}`
        try {
          window.location.href = miniProgramUrl
          return
        } catch (error) {
          console.error('小程序链接跳转失败:', error)
        }
      }
    }

    // 方案2：企业微信环境
    if (isWecom && typeof window !== 'undefined' && window.wx) {
      try {
        window.wx.invoke('navigateToMiniProgram', {
          appid: shop.appId,
          path: shop.path || '',
          envVersion: 'release'
        }, (res) => {
          if (res.err_msg !== 'navigateToMiniProgram:ok') {
            console.warn('企业微信小程序唤醒失败:', res.err_msg)
            this.fallbackToScheme(shop)
          }
        })
        return
      } catch (error) {
        console.error('企业微信API调用失败:', error)
        this.fallbackToScheme(shop)
      }
    }

    // 方案3：使用URL Scheme（外部环境）
    if (shop.urlScheme) {
      try {
        window.location.href = shop.urlScheme
        // 3秒后如果未跳转，显示小程序码
        setTimeout(() => {
          this.showMiniProgramQR(shop)
        }, 3000)
        return
      } catch (error) {
        console.error('URL Scheme跳转失败:', error)
      }
    }

    // 方案4：显示小程序码（最终降级）
    this.showMiniProgramQR(shop)
  },

  /**
   * 显示小程序码（降级方案）
   */
  showMiniProgramQR(shop) {
    if (!shop.qrCode) {
      alert(`请在微信中搜索小程序：${shop.name}`)
      return
    }

    // 创建模态框显示小程序码
    const modal = document.createElement('div')
    modal.style.cssText = `
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.7); z-index: 10000;
      display: flex; align-items: center; justify-content: center;
    `
    modal.innerHTML = `
      <div style="background: white; padding: 20px; border-radius: 12px; text-align: center; max-width: 90%;">
        <h3 style="margin: 0 0 10px 0;">${shop.name}</h3>
        <p style="color: #666; font-size: 14px; margin: 0 0 20px 0;">请使用微信扫描下方小程序码</p>
        <img src="${shop.qrCode}" style="max-width: 300px; width: 100%; margin: 0 auto 20px; display: block; border-radius: 8px;" />
        <button onclick="this.closest('div[style*=\"position: fixed\"]').remove()" 
                style="padding: 8px 20px; background: #1890FF; color: white; border: none; border-radius: 6px; cursor: pointer;">
          关闭
        </button>
      </div>
    `
    document.body.appendChild(modal)
    modal.onclick = (e) => {
      if (e.target === modal) {
        document.body.removeChild(modal)
      }
    }
  },

  /**
   * 降级到URL Scheme
   */
  fallbackToScheme(shop) {
    if (shop.urlScheme) {
      window.location.href = shop.urlScheme
    } else {
      this.showMiniProgramQR(shop)
    }
  },

  /**
   * 打开APP（支持所有电商平台：天猫、京东、拼多多、1688、淘宝、自定义平台等）
   * @param {Object} shop - 网店配置
   */
  async openApp(shop) {
    const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent)
    
    // 方案1：移动端尝试APP唤醒
    if (isMobile && shop.appScheme) {
      try {
        // 使用隐藏的iframe尝试唤醒APP
        const iframe = document.createElement('iframe')
        iframe.style.display = 'none'
        iframe.src = shop.appScheme
        document.body.appendChild(iframe)
        
        // 2-3秒后如果未跳转，降级到H5
        const timer = setTimeout(() => {
          document.body.removeChild(iframe)
          if (shop.webUrl) {
            window.open(shop.webUrl, '_blank')
          } else {
            alert('请安装对应的APP或访问网页版')
          }
        }, 2500)
        
        // 监听页面可见性，如果APP被唤醒，页面会隐藏
        const handleVisibilityChange = () => {
          if (document.hidden) {
            // APP被唤醒，清理定时器
            clearTimeout(timer)
            document.removeEventListener('visibilitychange', handleVisibilityChange)
          }
        }
        document.addEventListener('visibilitychange', handleVisibilityChange)
        
        return
      } catch (error) {
        console.error('APP唤醒失败:', error)
      }
    }
    
    // 方案2：PC端或APP未安装，直接打开H5链接
    if (shop.webUrl) {
      window.open(shop.webUrl, '_blank')
    } else {
      alert('请访问网页版或安装对应的APP')
    }
  }
}

