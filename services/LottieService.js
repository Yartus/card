/**
 * Lottie动画服务 - 简化版
 * 只保留核心功能，去除复杂的缓存和多数据源
 */

import { getAnimationUrl } from '../config/lottie.config.js'

class SimpleLottieService {
  constructor() {
    this.cache = new Map()
  }
  
  /**
   * 获取动画数据
   * @param {string} name - 动画名称
   * @returns {Promise<Object>} 动画JSON数据
   */
  async getAnimation(name) {
    // 检查缓存
    if (this.cache.has(name)) {
      return this.cache.get(name)
    }
    
    const url = getAnimationUrl(name)
    if (!url) {
      throw new Error(`Animation "${name}" not found`)
    }
    
    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Failed to load animation: ${response.status}`)
      }
      
      const data = await response.json()
      
      // 简单缓存
      this.cache.set(name, data)
      
      return data
    } catch (error) {
      console.warn(`Failed to load Lottie animation "${name}":`, error)
      throw error
    }
  }
  
  /**
   * 预加载动画
   * @param {Array<string>} names - 动画名称数组
   */
  async preload(names = ['phone-ring', 'share-float']) {
    const promises = names.map(name => 
      this.getAnimation(name).catch(error => 
        console.warn(`Failed to preload animation "${name}":`, error)
      )
    )
    
    await Promise.allSettled(promises)
  }
  
  /**
   * 清理缓存
   */
  clearCache() {
    this.cache.clear()
  }
}

// 创建单例
const simpleLottieService = new SimpleLottieService()

export default simpleLottieService
