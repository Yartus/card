<template>
  <div v-if="sloganText" class="slogan-section">
    <div class="slogan-content">
      <p class="slogan-text">{{ sloganText }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SloganSection',
  
  props: {
    sloganText: {
      type: String,
      default: ''
    }
  }
}
</script>

<style lang="scss" scoped>
.slogan-section {
  padding: 12px 20px 16px 20px;
  background: #ffffff;
  border-bottom: 1px solid #f0f2f5;
}

.slogan-content {
  text-align: center;
}

.slogan-text {
  font-size: 14px;
  font-weight: 500;
  color: #595959;
  margin: 0;
  line-height: 1.5;
  font-style: italic;
  letter-spacing: 0.2px;
}

@media (max-width: 480px) {
  .slogan-section {
    padding: 10px 16px 14px 16px;
  }
  
  .slogan-text {
    font-size: 13px;
  }
}
</style>
