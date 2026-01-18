/**
 * Lottie动画简化配置
 * 最简单的配置方式，只包含必要的设置
 */

// 基础配置
export const SIMPLE_LOTTIE_CONFIG = {
  // 动画资源路径
  basePath: '/assets/animations/',
  
  // 全局默认设置
  defaults: {
    autoplay: true,
    loop: true,
    speed: 1,
    width: 24,
    height: 24
  },
  
  // 动画定义（只保留当前使用的）
  animations: {
    'phone-ring': 'phone/ring.json',
    'share-float': 'share/float.json'
  },
  
  // 降级图标
  fallbacks: {
    'phone-ring': 'icon-phone-animated',
    'share-float': 'icon-share-animated'
  }
}

// 检查是否应该禁用动画
export function shouldDisableAnimations() {
  if (typeof window === 'undefined' || !process.client) {
    return false
  }
  return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// 获取动画URL
export function getAnimationUrl(name) {
  const path = SIMPLE_LOTTIE_CONFIG.animations[name]
  return path ? SIMPLE_LOTTIE_CONFIG.basePath + path : null
}

// 获取降级图标
export function getFallbackIcon(name) {
  return SIMPLE_LOTTIE_CONFIG.fallbacks[name] || 'icon-default'
}

export default SIMPLE_LOTTIE_CONFIG
