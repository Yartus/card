<template>
  <div 
    ref="container" 
    class="simple-lottie-icon"
    :style="containerStyle"
  ></div>
</template>

<script>
let lottie = null
if (process.client) {
  lottie = require('lottie-web')
}

export default {
  name: 'SimpleLottieIcon',
  
  props: {
    // 动画数据（JSON对象或URL）
    animationData: { 
      type: [Object, String], 
      required: true 
    },
    // 尺寸
    width: { 
      type: Number, 
      default: 24 
    },
    height: { 
      type: Number, 
      default: 24 
    },
    // 是否自动播放
    autoplay: { 
      type: Boolean, 
      default: true 
    },
    // 是否循环
    loop: { 
      type: Boolean, 
      default: true 
    },
    // 播放速度
    speed: {
      type: Number,
      default: 1
    },
    // 降级图标
    fallbackIcon: {
      type: String,
      default: ''
    }
  },
  
  data() {
    return {
      animation: null,
      hasError: false
    }
  },
  
  computed: {
    containerStyle() {
      return {
        width: `${this.width}px`,
        height: `${this.height}px`
      }
    }
  },
  
  mounted() {
    if (process.client) {
      this.initAnimation()
    }
  },
  
  beforeUnmount() {
    this.destroyAnimation()
  },
  
  methods: {
    async initAnimation() {
      try {
        // 确保在客户端且lottie库已加载
        if (!process.client || !lottie) {
          this.showFallback()
          return
        }
        
        let animData = this.animationData
        
        // 如果是URL，加载JSON
        if (typeof this.animationData === 'string') {
          const response = await fetch(this.animationData)
          animData = await response.json()
        }
        
        // 创建动画
        this.animation = lottie.loadAnimation({
          container: this.$refs.container,
          renderer: 'svg',
          loop: this.loop,
          autoplay: this.autoplay,
          animationData: animData
        })
        
        this.animation.setSpeed(this.speed)
        
        this.$emit('loaded', this.animation)
        
      } catch (error) {
        console.warn('Lottie animation failed:', error)
        this.showFallback()
        this.$emit('error', error)
      }
    },
    
    destroyAnimation() {
      if (this.animation) {
        this.animation.destroy()
        this.animation = null
      }
    },
    
    showFallback() {
      if (this.fallbackIcon && this.$refs.container) {
        this.$refs.container.innerHTML = `<i class="${this.fallbackIcon}"></i>`
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.simple-lottie-icon {
  display: inline-block;
  
  :deep(svg) {
    width: 100% !important;
    height: 100% !important;
  }
  
  :deep(i) {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    font-size: inherit;
  }
}

// 减少动画模式支持
@media (prefers-reduced-motion: reduce) {
  .simple-lottie-icon {
    :deep(svg) {
      animation-play-state: paused !important;
    }
  }
}
</style>
