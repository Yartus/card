<template>
  <div class="tenant-detail" v-if="tenant">
    <header class="detail-header">
      <div>
        <h1>{{ tenant.company_name || '未命名租户' }}</h1>
        <p>CorpID：{{ tenant.corp_id }}</p>
        <p>套餐：{{ tenant.plan || 'free' }} ｜ 创建时间：{{ formatDate(tenant.created_at) }}</p>
      </div>
      <NuxtLink to="/admin">返回列表</NuxtLink>
    </header>

    <section class="summary">
      <div class="summary-card">
        <span>成员数</span>
        <strong>{{ tenant.member_count }}</strong>
      </div>
      <div class="summary-card">
        <span>素材数</span>
        <strong>{{ tenant.asset_count }}</strong>
      </div>
      <div class="summary-card">
        <span>近30天访问</span>
        <strong>{{ tenant.views_last_30d }}</strong>
      </div>
      <div class="summary-card">
        <span>存储占用</span>
        <strong>{{ formatBytes(tenant.storage_used_bytes) }}</strong>
      </div>
    </section>

    <section class="logs" v-if="logs && logs.length">
      <h2>最新访问/操作记录</h2>
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>成员</th>
            <th>事件</th>
            <th>描述</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ formatDate(log.created_at) }}</td>
            <td>{{ log.member_name || '系统' }}</td>
            <td>{{ log.event }}</td>
            <td>{{ log.meta_summary || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="members" v-if="members && members.length">
      <h2>成员列表</h2>
      <table>
        <thead>
          <tr>
            <th>姓名</th>
            <th>职位</th>
            <th>部门</th>
            <th>手机</th>
            <th>邮箱</th>
            <th>更新时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in members" :key="member.id">
            <td>{{ member.name }}</td>
            <td>{{ member.position || '-' }}</td>
            <td>{{ member.department || '-' }}</td>
            <td>{{ member.mobile || '-' }}</td>
            <td>{{ member.email || '-' }}</td>
            <td>{{ formatDate(member.updated_at) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
  <div v-else class="loading">加载中...</div>
</template>

<script>
export default {
  name: 'TenantDetailPage',
  middleware: 'auth',
  data () {
    return {
      tenant: null,
      members: [],
      logs: []
    }
  },
  async fetch () {
    const id = this.$route.params.id
    try {
      const { data } = await this.$axios.get(`/api/admin/tenants/${id}`)
      this.tenant = data.tenant
      this.members = data.members
      this.logs = data.logs
    } catch (error) {
      console.error('加载租户详情失败', error)
      this.$toast && this.$toast.error('加载租户详情失败')
    }
  },
  methods: {
    formatDate (value) {
      if (!value) return '-'
      return new Date(value).toLocaleString('zh-CN')
    },
    formatBytes (bytes) {
      if (!bytes) return '0 B'
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let i = 0
      let val = bytes
      while (val >= 1024 && i < units.length - 1) {
        val /= 1024
        i++
      }
      return `${val.toFixed(1)} ${units[i]}`
    }
  }
}
</script>

<style scoped>
.tenant-detail {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.detail-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}
.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}
.summary-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}
.summary-card span {
  display: block;
  color: #8c8c8c;
  margin-bottom: 8px;
}
.summary-card strong {
  font-size: 22px;
  font-weight: 600;
}
section {
  margin-top: 24px;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 16px;
}
h2 {
  margin: 0 0 16px;
  font-size: 18px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
thead th {
  text-align: left;
  background: #fafafa;
  padding: 12px;
}
tbody td {
  padding: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 14px;
}
.loading {
  padding: 48px;
  text-align: center;
  color: #999;
}
@media (max-width: 768px) {
  .tenant-detail {
    padding: 16px;
  }
  section {
    overflow-x: auto;
  }
  table {
    min-width: 720px;
  }
}
</style>
