<template>
  <div class="quick-actions qa-light">
    <div class="qa-bar">
      <button
        v-for="action in availableActions"
        :key="action.type"
        class="qa-btn"
        :class="`qa-${action.type}`"
        @click="handleActionClick(action)"
        :disabled="!action.enabled"
        :aria-label="action.label"
      >
        <i :class="action.icon" class="qa-icon"></i>
        <span class="qa-text">{{ action.label }}</span>
      </button>
    </div>
  </div>
  
</template>

<script>
export default {
  name: 'QuickActions',
  
  props: {
    contactInfo: {
      type: Object,
      required: true,
      default: () => ({})
    },
    interactiveFeatures: {
      type: Object,
      default: () => ({})
    }
  },
  
  computed: {
    // 可用的快速操作
    availableActions() {
      const actions = []
      // 仅保留 三项：拨打电话 / 复制微信 / 分享名片（顺序固定，一行展示）
      if (this.contactInfo.mobile) {
        actions.push({ type: 'call', label: '电话', icon: 'icon-phone', value: this.contactInfo.mobile, enabled: true })
      }
      if (this.contactInfo.wechat) {
        actions.push({ type: 'wechat', label: '微信', icon: 'icon-wechat', value: this.contactInfo.wechat, enabled: true })
      }
      if (this.interactiveFeatures.share_card !== false) {
        actions.push({ type: 'share', label: '分享', icon: 'icon-share', value: null, enabled: true })
      }
      return actions
    }
  },
  
  methods: {
    // 处理操作点击
    handleActionClick(action) {
      if (!action.enabled) return
      
      this.$emit('action-click', {
        type: action.type,
        value: action.value,
        label: action.label
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.qa-light {
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 1px solid #eef1f6;
}

.qa-bar { display:flex; align-items:center; justify-content:center; gap:6px; overflow-x:auto; }

.qa-btn { display:inline-flex; align-items:center; gap:6px; height:32px; padding:0 10px; border:1px solid #d9e2ec; border-radius:9999px; background:#fff; color:#1f1f1f; font-size:12px; line-height:1; cursor:pointer; transition:all .2s ease; white-space:nowrap; }

.qa-btn:hover {
  box-shadow: 0 2px 8px rgba(31, 35, 41, 0.08);
  border-color: #c6d3e1;
}

.qa-btn:active { transform: translateY(0.5px); }
.qa-btn:disabled { opacity: .5; cursor: not-allowed; }

.qa-icon { font-size: 14px; }

/* 规范化配色 */
.qa-call { border-color: #91caff; color: #1677ff; }
.qa-call .qa-icon { color: #1677ff; }

.qa-wechat { border-color: #95de64; color: #389e0d; }
.qa-wechat .qa-icon { color: #389e0d; }

.qa-share { border-color: #d3adf7; color: #722ed1; }
.qa-share .qa-icon { color: #722ed1; }

/* 简化的图标（可替换为真正的 SVG/Iconfont） */
.icon-phone::before { content: "📞"; }
.icon-wechat::before { content: "💬"; }
.icon-share::before { content: "📤"; }
</style>
