<template>
  <div class="terms-page" data-theme="cyber">
    <div class="cyber-grid-bg"></div>
    
    <div class="container">
      <div class="terms-header">
        <h1 class="cyber-title gradient-text">服务条款</h1>
        <p class="cyber-text">最后更新时间：{{ updateDate }}</p>
      </div>
      
      <div class="cyber-card terms-content">
        <section class="terms-section">
          <h2 class="cyber-subtitle">1. 服务说明</h2>
          <p class="cyber-text">
            WeCard数字名片是一个企业级SaaS平台，为企业提供数字名片创建、管理和分享服务。通过使用我们的服务，您同意遵守本服务条款。
          </p>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">2. 账户注册</h2>
          <p class="cyber-text">
            使用WeCard服务需要：
          </p>
          <ul class="cyber-list">
            <li>提供真实、准确的企业信息</li>
            <li>确保联系信息的有效性</li>
            <li>妥善保管账户信息和密码</li>
            <li>及时更新变更的信息</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">3. 服务使用</h2>
          <p class="cyber-text">
            在使用我们的服务时，您同意：
          </p>
          <ul class="cyber-list">
            <li>遵守相关法律法规</li>
            <li>不发布违法、有害或不当内容</li>
            <li>不进行恶意攻击或滥用服务</li>
            <li>尊重他人的知识产权</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">4. 服务费用</h2>
          <p class="cyber-text">
            WeCard提供多种服务套餐：
          </p>
          <ul class="cyber-list">
            <li>基础版：免费使用，功能有限</li>
            <li>专业版：付费服务，功能完整</li>
            <li>企业版：定制服务，按需报价</li>
            <li>费用变更将提前30天通知</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">5. 知识产权</h2>
          <p class="cyber-text">
            关于知识产权的约定：
          </p>
          <ul class="cyber-list">
            <li>WeCard平台的所有权归我们所有</li>
            <li>您保留对自己内容的所有权</li>
            <li>授权我们使用您的内容提供服务</li>
            <li>尊重第三方的知识产权</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">6. 服务变更</h2>
          <p class="cyber-text">
            我们保留以下权利：
          </p>
          <ul class="cyber-list">
            <li>随时修改或更新服务功能</li>
            <li>暂停或终止部分服务</li>
            <li>更新服务条款和政策</li>
            <li>重要变更将提前通知用户</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">7. 责任限制</h2>
          <p class="cyber-text">
            在法律允许的范围内：
          </p>
          <ul class="cyber-list">
            <li>我们不对间接损失承担责任</li>
            <li>服务按"现状"提供，不提供保证</li>
            <li>用户应备份重要数据</li>
            <li>我们的责任限于服务费用</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">8. 服务终止</h2>
          <p class="cyber-text">
            服务可能在以下情况下终止：
          </p>
          <ul class="cyber-list">
            <li>用户主动取消服务</li>
            <li>违反服务条款</li>
            <li>长期未使用账户</li>
            <li>其他合理原因</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">9. 争议解决</h2>
          <p class="cyber-text">
            如发生争议：
          </p>
          <ul class="cyber-list">
            <li>优先通过友好协商解决</li>
            <li>适用中华人民共和国法律</li>
            <li>由我方所在地法院管辖</li>
            <li>可通过客服渠道联系我们</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2 class="cyber-subtitle">10. 联系方式</h2>
          <p class="cyber-text">
            如有疑问，请联系我们：
          </p>
          <div class="contact-info">
            <p class="cyber-text">邮箱：support@wecard.com</p>
            <p class="cyber-text">电话：400-xxx-xxxx</p>
            <p class="cyber-text">地址：[您的公司地址]</p>
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
  name: 'TermsOfService',
  
  head() {
    return {
      title: '服务条款 - WeCard数字名片',
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: 'WeCard数字名片平台的服务条款，了解使用我们服务的权利和义务。'
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

.terms-page {
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

.terms-header {
  text-align: center;
  margin-bottom: 40px;
}

.terms-header h1 {
  font-size: 36px;
  margin-bottom: 16px;
}

.terms-content {
  padding: 40px;
  margin-bottom: 30px;
}

.terms-section {
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.terms-section h2 {
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
  
  .terms-content {
    padding: 24px 20px;
  }
  
  .terms-header h1 {
    font-size: 28px;
  }
  
  .terms-section h2 {
    font-size: 20px;
  }
}
</style>
