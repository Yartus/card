<template>
  <div class="admin-overview">
    <header class="overview-header">
      <div>
        <h1>服务商控制台</h1>
        <p>汇总所有租户的授权状态、资源占用与活跃度。</p>
      </div>
      <button class="refresh-btn" @click="fetchTenants" :disabled="loading">
        <span v-if="loading">刷新中...</span>
        <span v-else>刷新数据</span>
      </button>
    </header>

    <section class="overview-stats" v-if="summary">
      <div class="stat-card">
        <div class="stat-label">租户总数</div>
        <div class="stat-value">{{ summary.total_tenants }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">近30天活跃租户</div>
        <div class="stat-value">{{ summary.active_last_30d }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">累计访问量</div>
        <div class="stat-value">{{ formatNumber(summary.total_views) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">素材总数</div>
        <div class="stat-value">{{ formatNumber(summary.total_assets) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">预计存储占用</div>
        <div class="stat-value">{{ formatBytes(summary.storage_used_bytes) }}</div>
      </div>
    </section>

    <section class="overview-table">
      <div class="table-header">
        <h2>租户列表</h2>
        <input
          v-model="filters.keyword"
          @input="debounceSearch"
          type="text"
          placeholder="搜索企业名称 / CorpID"
        />
      </div>

      <table>
        <thead>
          <tr>
            <th>企业名称</th>
            <th>CorpID</th>
            <th>套餐</th>
            <th>成员数</th>
            <th>素材数</th>
            <th>近30天访问</th>
            <th>存储占用</th>
            <th>最近同步</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!loading && tenants.length === 0">
            <td colspan="8" class="empty">暂无租户数据</td>
          </tr>
          <tr v-for="tenant in tenants" :key="tenant.id">
            <td class="tenant-name">
              <NuxtLink :to="`/admin/tenant/${tenant.id}`">
                {{ tenant.company_name || '未命名租户' }}
              </NuxtLink>
            </td>
            <td>{{ tenant.corp_id }}</td>
            <td>{{ tenant.plan || 'free' }}</td>
            <td>{{ tenant.member_count }}</td>
            <td>{{ tenant.asset_count }}</td>
            <td>{{ formatNumber(tenant.views_last_30d) }}</td>
            <td>{{ formatBytes(tenant.storage_used_bytes) }}</td>
            <td>{{ formatDate(tenant.last_synced_at) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="pagination.pages > 1" class="pagination">
        <button @click="changePage(pagination.page - 1)" :disabled="!pagination.has_prev">上一页</button>
        <span>第 {{ pagination.page }} / {{ pagination.pages }} 页</span>
        <button @click="changePage(pagination.page + 1)" :disabled="!pagination.has_next">下一页</button>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'AdminOverviewPage',
  middleware: 'auth',
  data () {
    return {
      tenants: [],
      summary: null,
      pagination: { page: 1, pages: 1 },
      loading: false,
      searchTimer: null,
      filters: {
        keyword: ''
      }
    }
  },
  async fetch () {
    await this.fetchTenants()
  },
  methods: {
    async fetchTenants (page = 1) {
      this.loading = true
      try {
        const { data } = await this.$axios.get('/api/admin/tenants', {
          params: {
            page,
            keyword: this.filters.keyword
          }
        })
        this.tenants = data.items
        this.pagination = data.pagination
        this.summary = data.summary
      } catch (error) {
        console.error('加载租户列表失败', error)
        this.$toast && this.$toast.error('加载租户数据失败')
      } finally {
        this.loading = false
      }
    },
    debounceSearch () {
      clearTimeout(this.searchTimer)
      this.searchTimer = setTimeout(() => {
        this.fetchTenants(1)
      }, 400)
    },
    changePage (page) {
      if (page < 1 || page > this.pagination.pages) return
      this.fetchTenants(page)
    },
    formatNumber (val) {
      if (!val) return '0'
      if (val >= 10000) return (val / 10000).toFixed(1) + '万'
      if (val >= 1000) return (val / 1000).toFixed(1) + 'k'
      return String(val)
    },
    formatBytes (bytes) {
      if (!bytes) return '0 B'
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let i = 0
      let value = bytes
      while (value >= 1024 && i < units.length - 1) {
        value /= 1024
        i++
      }
      return `${value.toFixed(1)} ${units[i]}`
    },
    formatDate (dateString) {
      if (!dateString) return '未同步'
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.admin-overview {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.overview-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}
.overview-header p {
  margin: 4px 0 0;
  color: #8c8c8c;
}
.refresh-btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #1890ff;
  background: white;
  color: #1890ff;
  cursor: pointer;
}
.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}
.stat-card {
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  background: #fff;
}
.stat-label {
  color: #8c8c8c;
  font-size: 14px;
}
.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-top: 8px;
}
.overview-table {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  background: #fff;
  padding: 16px;
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.table-header input {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 8px 12px;
  width: 240px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
thead th {
  text-align: left;
  padding: 12px;
  background: #fafafa;
  font-weight: 600;
  color: #262626;
}
tbody td {
  padding: 12px;
  border-top: 1px solid #f0f0f0;
  color: #595959;
}
.tenant-name a {
  color: #1890ff;
}
.empty {
  text-align: center;
  padding: 24px;
  color: #999;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
}
.pagination button {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fff;
}
@media (max-width: 768px) {
  .admin-overview {
    padding: 16px;
  }
  .overview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .overview-table {
    padding: 12px;
    overflow-x: auto;
  }
  table {
    min-width: 900px;
  }
}
</style>
