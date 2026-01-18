<template>
  <div class="settings-page">
    <div class="card">
      <div v-if="loading" class="status loading">
        <div class="spinner"></div>
        <p>正在校验企业微信授权，请稍候...</p>
      </div>

      <div v-else-if="status === 'success'" class="status success">
        <h1>授权成功</h1>
        <p class="corp-name">{{ corpName }}</p>
        <ul class="info">
          <li><strong>企业 CorpID：</strong>{{ corpId }}</li>
          <li><strong>租户编号：</strong>{{ tenantId }}</li>
        </ul>
        <p>您可以前往管理后台配置名片与素材：</p>
        <NuxtLink to="/admin" class="btn">进入服务商后台</NuxtLink>
      </div>

      <div v-else class="status error">
        <h1>授权失败</h1>
        <p>{{ message }}</p>
        <div class="actions">
          <NuxtLink to="/" class="link">返回首页</NuxtLink>
          <NuxtLink to="/wecom/install" class="link">重新发起授权</NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WecomSettingsPage',
  data () {
    return {
      loading: true,
      status: 'pending',
      message: '',
      corpName: '',
      corpId: '',
      tenantId: null
    }
  },
  async mounted () {
    const authCode = this.$route.query.auth_code
    if (!authCode) {
      this.loading = false
      this.status = 'error'
      this.message = '链接缺少 auth_code 参数，请重新发起授权。'
      return
    }

    try {
      const { data } = await this.$axios.post('/api/v1/wecom/auth', { auth_code: authCode })
      this.status = 'success'
      this.corpName = data.corp_name || '已授权企业'
      this.corpId = data.corp_id
      this.tenantId = data.tenant_id
    } catch (error) {
      const apiMsg = (error.response && error.response.data && error.response.data.error) || error.message
      this.status = 'error'
      this.message = `授权校验失败：${apiMsg || '未知错误'}`
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  padding: 24px;
  color: #fff;
}
.card {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 560px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(12px);
}
.status {
  text-align: center;
}
.status h1 {
  font-size: 28px;
  margin-bottom: 16px;
}
.status p {
  margin-bottom: 12px;
  line-height: 1.6;
}
.corp-name {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 8px;
}
.info {
  list-style: none;
  padding: 0;
  margin: 16px 0;
  text-align: left;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 8px;
  padding: 16px;
}
.info li + li {
  margin-top: 8px;
}
.spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto 24px;
  border-radius: 50%;
  border: 4px solid rgba(148, 163, 184, 0.3);
  border-top-color: #60a5fa;
  animation: spin 1s linear infinite;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  background: #38bdf8;
  border-radius: 8px;
  color: #0f172a;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s ease;
}
.btn:hover {
  background: #0ea5e9;
}
.actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 16px;
}
.link {
  color: #38bdf8;
  text-decoration: none;
}
.link:hover {
  text-decoration: underline;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
