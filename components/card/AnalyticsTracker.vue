<template>
  <div style="display: none;">
    <!-- 隐藏的统计组件 -->
  </div>
</template>

<script>
export default {
  name: 'AnalyticsTracker',
  
  props: {
    cardId: {
      type: [String, Number],
      required: true
    },
    visitorInfo: {
      type: Object,
      default: () => ({})
    }
  },
  
  data() {
    return {
      sessionId: this.generateSessionId(),
      startTime: Date.now(),
      events: []
    }
  },
  
  mounted() {
    // 记录页面访问
    this.trackPageView()
    
    // 监听页面离开
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', this.handlePageUnload)
    }
    
    // 监听页面可见性变化
    document.addEventListener('visibilitychange', this.handleVisibilityChange)
  },
  
  beforeDestroy() {
    // 清理事件监听器
    if (typeof window !== 'undefined') {
      window.removeEventListener('beforeunload', this.handlePageUnload)
    }
    if (typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', this.handleVisibilityChange)
    }
    
    // 发送最后的统计数据
    this.sendPendingEvents()
  },
  
  methods: {
    // 记录页面访问
    trackPageView() {
      this.trackEvent('page_view', {
        card_id: this.cardId,
        session_id: this.sessionId,
        visitor_info: this.visitorInfo,
        timestamp: Date.now()
      })
    },
    
    // 记录事件
    trackEvent(eventType, eventData = {}) {
      const event = {
        event_type: eventType,
        event_data: eventData,
        card_id: this.cardId,
        session_id: this.sessionId,
        timestamp: Date.now()
      }
      
      this.events.push(event)
      
      // 触发父组件事件
      this.$emit('track-event', event)
      
      // 批量发送事件（每10个事件或每30秒）
      if (this.events.length >= 10) {
        this.sendEvents()
      }
    },
    
    // 发送事件到后端
    async sendEvents() {
      if (this.events.length === 0) return
      
      const eventsToSend = [...this.events]
      this.events = []
      
      try {
        // 这里应该调用实际的API
        await this.sendToAnalyticsAPI(eventsToSend)
        console.log('统计事件已发送:', eventsToSend)
      } catch (error) {
        console.error('发送统计事件失败:', error)
        // 失败的事件重新加入队列
        this.events.unshift(...eventsToSend)
      }
    },
    
    // 发送到统计API（模拟）
    async sendToAnalyticsAPI(events) {
      // 模拟API调用
      return new Promise((resolve) => {
        setTimeout(() => {
          // 在实际项目中，这里应该是真实的API调用
          // fetch('/api/analytics/track', {
          //   method: 'POST',
          //   headers: { 'Content-Type': 'application/json' },
          //   body: JSON.stringify({ events })
          // })
          resolve()
        }, 100)
      })
    },
    
    // 处理页面离开
    handlePageUnload() {
      // 记录页面停留时间
      const stayDuration = Date.now() - this.startTime
      this.trackEvent('page_unload', {
        stay_duration: stayDuration
      })
      
      // 立即发送待处理的事件
      this.sendPendingEvents()
    },
    
    // 处理页面可见性变化
    handleVisibilityChange() {
      if (document.hidden) {
        this.trackEvent('page_hidden')
      } else {
        this.trackEvent('page_visible')
      }
    },
    
    // 发送待处理的事件
    sendPendingEvents() {
      if (this.events.length > 0) {
        // 🔇 Analytics功能已禁用，等待后端API实现
        // TODO: 实现后端 /api/analytics/track 接口后启用
        if (process.env.NODE_ENV === 'development') {
          console.log('📊 [Analytics] 待发送事件:', this.events)
        }
        
        // 使用 sendBeacon API 确保数据发送（已禁用）
        // if (navigator.sendBeacon) {
        //   const data = JSON.stringify({ events: this.events })
        //   navigator.sendBeacon('/api/analytics/track', data)
        // } else {
        //   // 降级方案
        //   this.sendEvents()
        // }
        
        // 清空事件队列
        this.events = []
      }
    },
    
    // 生成会话ID
    generateSessionId() {
      return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    },
    
    // 获取设备信息
    getDeviceInfo() {
      return {
        user_agent: navigator.userAgent,
        screen_width: screen.width,
        screen_height: screen.height,
        viewport_width: typeof window !== 'undefined' ? window.innerWidth : 0,
        viewport_height: typeof window !== 'undefined' ? window.innerHeight : 0,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language
      }
    },
    
    // 获取页面性能信息
    getPerformanceInfo() {
      if (typeof window !== 'undefined' && window.performance && window.performance.timing) {
        const timing = window.performance.timing
        return {
          page_load_time: timing.loadEventEnd - timing.navigationStart,
          dom_ready_time: timing.domContentLoadedEventEnd - timing.navigationStart,
          first_paint_time: timing.responseEnd - timing.navigationStart
        }
      }
      return {}
    }
  }
}
</script>

<style scoped>
/* 隐藏组件，无需样式 */
</style>
