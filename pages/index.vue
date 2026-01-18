<template>
  <div class="redirect-page">
    <div class="loading-spinner"></div>
    <p>正在跳转...</p>
  </div>
</template>

<script>
export default {
  name: 'IndexPage',
  
  mounted() {
    // 检测是否在企业微信环境
    const isWecom = /wxwork/i.test(navigator.userAgent)
    
    if (isWecom) {
      // 企业微信环境：跳转到工作台（会自动根据角色和移动端跳转）
      this.$router.replace('/wecom/workspace')
    } else {
      // 非企微环境：跳转到安装页面
      this.$router.replace('/wecom/install')
    }
  }
}
</script>

<style scoped>
.redirect-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  color: #666;
  font-size: 14px;
}
</style>





