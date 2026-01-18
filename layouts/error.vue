<template>
  <section class="error-page">
    <div class="error-content">
      <h1 class="error-title">
        {{ error.statusCode === 404 ? '页面未找到' : '系统发生错误' }}
      </h1>
      <p class="error-desc">
        {{ error.statusCode === 404
          ? '您访问的页面不存在或授权链接已失效。请返回首页或重新发起企业授权。'
          : '请稍后重试，若问题持续存在，请联系技术支持。' }}
      </p>
      <div class="error-actions">
        <NuxtLink to="/" class="error-link">
          返回首页
        </NuxtLink>
        <a v-if="error.statusCode === 404" href="https://zjemail.cn/wecom/install" class="error-link">
          重新发起授权
        </a>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'error',
  layout: 'empty', //OR layout:'default'
  props: {
    error: {
      type: Object,
      required: true
    },
  },
};
</script>