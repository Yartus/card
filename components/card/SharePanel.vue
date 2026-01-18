<template>
  <div class="share-panel sp-light">
    <div class="sp-header">
      <h3 class="sp-title">分享名片</h3>
    </div>
    <div class="sp-actions">
      <button class="sp-btn" @click="copyLink" :disabled="copying">
        <i class="icon-link"></i>
        <span>{{ copying ? '复制中…' : '复制链接' }}</span>
      </button>
      <button class="sp-btn" @click="toggleQr">
        <i class="icon-qr"></i>
        <span>二维码</span>
      </button>
      <button class="sp-btn" @click="refreshThumbnail" :disabled="refreshing">
        <i class="icon-thumb"></i>
        <span>{{ refreshing ? '刷新中…' : '刷新缩略图' }}</span>
      </button>
    </div>

    <!-- 微信环境引导层（仅在微信内非企微时提示使用右上角菜单分享） -->
    <div v-if="showWechatHint" class="wechat-hint" @click="showWechatHint=false">
      <div class="hint-card">
        <div class="hint-text">请点击右上角 ··· 使用“分享”功能</div>
        <div class="hint-close">点此关闭</div>
      </div>
    </div>

    <!-- 二维码弹层 -->
    <div v-if="qrVisible" class="qr-overlay" @click="toggleQr">
      <div class="qr-card" @click.stop>
        <div ref="qrBox" class="qr-box"></div>
        <div class="qr-tip">扫一扫，在手机中查看名片</div>
        <button class="qr-close" @click="toggleQr">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SharePanel',
  props: {
    cardId: {
      type: [String, Number],
      required: true
    },
    cardData: {
      type: Object,
      default: () => ({})
    },
    isWecomEnv: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      copying: false,
      refreshing: false,
      qrVisible: false,
      showWechatHint: false
    }
  },
  mounted() {
    // 若在微信内（但非企微），优先提示使用原生分享
    if (/MicroMessenger/i.test(navigator.userAgent) && !this.isWecomEnv) {
      this.showWechatHint = true
    }
  },
  methods: {
    getShareUrl() {
      // 使用当前页面地址作为分享链接
      try {
        return typeof window !== 'undefined' ? window.location.href : ''
      } catch (e) {
        return ''
      }
    },
    async copyLink() {
      const url = this.getShareUrl()
      if (!url) return
      this.copying = true
      try {
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(url)
        } else {
          const ta = document.createElement('textarea')
          ta.value = url
          document.body.appendChild(ta)
          ta.select()
          document.execCommand('copy')
          document.body.removeChild(ta)
        }
        this.$emit('track-event', { event_type: 'share_card', event_data: { method: 'copy_link' }, card_id: this.cardId, timestamp: Date.now() })
        this.toast('链接已复制')
      } catch (e) {
        this.toast('复制失败，请重试')
      } finally {
        this.copying = false
      }
    },
    toggleQr() {
      this.qrVisible = !this.qrVisible
      if (this.qrVisible) {
        this.$nextTick(() => {
          this.renderQr()
        })
        this.$emit('track-event', { event_type: 'share_card', event_data: { method: 'qrcode' }, card_id: this.cardId, timestamp: Date.now() })
      }
    },
    renderQr() {
      try {
        const url = this.getShareUrl()
        const box = this.$refs.qrBox
        if (!box) return
        box.innerHTML = ''
        // 依赖 /qrcode.min.js（已在 nuxt head 注入）
        if (typeof window !== 'undefined' && window.QRCode) {
          /* global QRCode */
          new window.QRCode(box, { text: url, width: 220, height: 220, correctLevel: window.QRCode.CorrectLevel.M })
        } else {
          // 兜底：展示纯链接
          const a = document.createElement('a')
          a.href = url
          a.textContent = url
          a.target = '_blank'
          box.appendChild(a)
        }
      } catch (e) {
        // 忽略渲染异常
      }
    },
    async refreshThumbnail() {
      this.refreshing = true
      try {
        const resp = await fetch('/api/card/preview/thumbnail', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ member_id: String(this.cardId), override: false })
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const data = await resp.json()
        this.$emit('track-event', { event_type: 'share_thumbnail', event_data: { status: 'ok', thumbnail_url: data.thumbnail_url }, card_id: this.cardId, timestamp: Date.now() })
        this.toast('缩略图已刷新')
      } catch (e) {
        this.$emit('track-event', { event_type: 'share_thumbnail', event_data: { status: 'error' }, card_id: this.cardId, timestamp: Date.now() })
        this.toast('刷新失败，请稍后重试')
      } finally {
        this.refreshing = false
      }
    },
    toast(msg) {
      const div = document.createElement('div')
      div.className = 'sp-toast'
      div.textContent = msg
      document.body.appendChild(div)
      setTimeout(() => document.body.removeChild(div), 1800)
    }
  }
}
</script>

<style lang="scss" scoped>
.sp-light { padding: 12px 16px; background: #ffffff; border-top: 1px solid #eef1f6; }
.sp-header { margin-bottom: 8px; }
.sp-title { font-size: 14px; font-weight: 600; color: #1f1f1f; margin: 0; }
.sp-actions { display:flex; gap:8px; flex-wrap:wrap; }
.sp-btn { display:inline-flex; align-items:center; gap:6px; height:32px; padding:0 10px; border:1px solid #d9e2ec; border-radius:8px; background:#fff; font-size:12px; cursor:pointer; }
.sp-btn:hover { box-shadow: 0 2px 8px rgba(31,35,41,.08); border-color:#c6d3e1; }
.icon-link::before { content: "🔗"; }
.icon-qr::before { content: "🧾"; }
.icon-thumb::before { content: "🖼️"; }

.qr-overlay { position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; z-index:9999; }
.qr-card { background:#fff; padding:16px; border-radius:10px; width:min(90vw,320px); text-align:center; }
.qr-box { width:220px; height:220px; margin:0 auto 8px; }
.qr-tip { font-size:12px; color:#666; margin-bottom:8px; }
.qr-close { border:1px solid #e5e7eb; background:#fff; border-radius:6px; padding:6px 12px; cursor:pointer; }

.wechat-hint { position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:flex-start; justify-content:flex-end; z-index:9998; }
.hint-card { margin:16px; background:rgba(255,255,255,.95); border:1px solid #e5e7eb; border-radius:8px; padding:12px; }
.hint-text { font-size:13px; color:#111; margin-bottom:6px; }
.hint-close { font-size:12px; color:#666; text-align:right; }

/* 轻量提示 */
.sp-toast { position:fixed; left:50%; top:50%; transform:translate(-50%,-50%); background:rgba(0,0,0,.8); color:#fff; padding:8px 12px; border-radius:8px; font-size:12px; z-index:10000; }
</style>
