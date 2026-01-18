<template>
  <div class="policy-page" data-theme="cyber">
    <div class="cyber-grid-bg"></div>
    
    <div class="container">
      <div class="policy-header">
        <h1 class="cyber-title gradient-text">隐私政策</h1>
        <p class="cyber-text">最后更新时间：{{ updateDate }}</p>
      </div>
      
      <div class="cyber-card policy-content">
        <section class="policy-section">
          <h2 class="cyber-subtitle">1. 信息收集</h2>
          <p class="cyber-text">
            WeCard数字名片平台在您使用我们的服务时，可能会收集以下信息：
          </p>
          <ul class="cyber-list">
            <li>企业基本信息（企业名称、统一社会信用代码等）</li>
            <li>员工基本信息（姓名、职位、联系方式等）</li>
            <li>名片访问和使用统计数据</li>
            <li>设备信息和日志数据</li>
          </ul>
        </section>

        <section class="policy-section">
          <h2 class="cyber-subtitle">2. 信息使用</h2>
          <p class="cyber-text">
            我们收集的信息将用于：
          </p>
          <ul class="cyber-list">
            <li>提供数字名片服务</li>
            <li>改进产品功能和用户体验</li>
            <li>提供技术支持和客户服务</li>
            <li>进行数据分析和统计</li>
          </ul>
        </section>

        <section class="policy-section">
          <h2 class="cyber-subtitle">3. 信息保护</h2>
          <p class="cyber-text">
            我们采取以下措施保护您的信息安全：
          </p>
          <ul class="cyber-list">
            <li>使用HTTPS加密传输</li>
            <li>实施访问控制和权限管理</li>
            <li>定期进行安全审计</li>
            <li>遵循数据最小化原则</li>
          </ul>
        </section>

        <section class="policy-section">
          <h2 class="cyber-subtitle">4. 信息共享</h2>
          <p class="cyber-text">
            除以下情况外，我们不会与第三方共享您的个人信息：
          </p>
          <ul class="cyber-list">
            <li>获得您的明确同意</li>
            <li>法律法规要求</li>
            <li>保护我们的合法权益</li>
            <li>与可信的服务提供商合作（如云服务商）</li>
          </ul>
        </section>

        <section class="policy-section">
          <h2 class="cyber-subtitle">5. 您的权利</h2>
          <p class="cyber-text">
            您对自己的个人信息享有以下权利：
          </p>
          <ul class="cyber-list">
            <li>访问和查看您的个人信息</li>
            <li>更正不准确的信息</li>
            <li>删除您的个人信息</li>
            <li>限制或反对信息处理</li>
          </ul>
        </section>

        <section class="policy-section">
          <h2 class="cyber-subtitle">6. 联系我们</h2>
          <p class="cyber-text">
            如果您对本隐私政策有任何疑问，请通过以下方式联系我们：
          </p>
          <div class="contact-info">
            <p class="cyber-text">邮箱：privacy@wecard.com</p>
            <p class="cyber-text">电话：400-xxx-xxxx</p>
          </div>
        </section>
      </div>
      
      <div class="back-link">
        <nuxt-link to="/" class="cyber-button">返回首页</nuxt-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrivacyPolicy',
  
  head() {
    return {
      title: '隐私政策 - WeCard数字名片',
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: 'WeCard数字名片平台的隐私政策，了解我们如何收集、使用和保护您的个人信息。'
        }
      ]
    }
  },
  
  data() {
    return {
      updateDate: '2024年1月1日'
    }
  }
}
</script>

<style lang="scss" scoped>
@import '~/assets/css/cyber-theme-system.css';

.policy-page {
  min-height: 100vh;
  background: var(--bg-gradient);
  position: relative;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  position: relative;
  z-index: 2;
}

.policy-header {
  text-align: center;
  margin-bottom: 40px;
}

.policy-header h1 {
  font-size: 36px;
  margin-bottom: 16px;
}

.policy-content {
  padding: 40px;
  margin-bottom: 30px;
}

.policy-section {
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.policy-section h2 {
  font-size: 24px;
  margin-bottom: 16px;
  color: var(--primary-color);
}

.cyber-list {
  list-style: none;
  padding: 0;
  margin: 16px 0;
  
  li {
    position: relative;
    padding-left: 24px;
    margin-bottom: 8px;
    color: var(--text-secondary);
    line-height: 1.6;
    
    &::before {
      content: '▶';
      position: absolute;
      left: 0;
      color: var(--primary-color);
      font-size: 12px;
    }
  }
}

.contact-info {
  background: rgba(0, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 8px;
  padding: 20px;
  margin-top: 16px;
}

.back-link {
  text-align: center;
}

@media (max-width: 768px) {
  .container {
    padding: 20px 16px;
  }
  
  .policy-content {
    padding: 24px 20px;
  }
  
  .policy-header h1 {
    font-size: 28px;
  }
  
  .policy-section h2 {
    font-size: 20px;
  }
}
</style>
