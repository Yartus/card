<template>
  <div class="install-page">
    <div class="card">
      <h1>企业微信扫码授权</h1>
      <p class="desc">请企业管理员使用企业微信扫码安装并授权 WeCard 应用。</p>

      <div v-if="loading" class="status">
        <div class="spinner"></div>
        <p>正在获取授权二维码...</p>
      </div>

      <div v-else-if="error" class="status error">
        <p>{{ error }}</p>
        <button @click="fetchQr" class="btn">重新获取</button>
      </div>

      <div v-else class="qr-section">
        <iframe :src="qrUrl" class="qr-frame" frameborder="0"></iframe>
        <p class="hint">若二维码无法显示，请<a :href="qrUrl" target="_blank">点击此处</a>打开授权页面。</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WecomInstallPage',
  data () {
    return {
      loading: true,
      error: '',
      qrUrl: ''
    }
  },
  created () {
    this.fetchQr()
  },
  methods: {
    async fetchQr () {
      this.loading = true
      this.error = ''
      try {
        const redirect = encodeURIComponent('https://zjemail.cn/wecom/settings')
        const { data } = await this.$axios.get('/api/v1/wecom/install', { params: { redirect_uri: redirect } })
        this.qrUrl = data.qr_url
      } catch (err) {
        this.error = (err.response && err.response.data && err.response.data.error) || '获取二维码失败，请检查服务商配置。'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.install-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top, #0f172a, #020617);
  padding: 24px;
}
.card {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.4);
  padding: 32px;
  width: 100%;
  max-width: 520px;
  color: #e2e8f0;
  text-align: center;
}
.card h1 {
  font-size: 26px;
  margin-bottom: 12px;
}
.card .desc {
  margin-bottom: 24px;
  line-height: 1.6;
  color: #cbd5f5;
}
.status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.spinner {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 3px solid rgba(148, 163, 184, 0.3);
  border-top-color: #38bdf8;
  animation: spin 1s linear infinite;
}
.error {
  color: #fca5a5;
}
.btn {
  padding: 10px 20px;
  background: #38bdf8;
  color: #02152f;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.qr-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.qr-frame {
  width: 320px;
  height: 480px;
  border-radius: 12px;
  background: #0f172a;
}
.hint a {
  color: #38bdf8;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
