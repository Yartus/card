<template>
  <div class="config-section push-config-section">
    <div class="section-header">
      <h3 class="section-title">
        <span class="icon">📨</span>
        推送消息配置
      </h3>
      <p class="section-desc">
        配置添加好友后自动推送给客户的名片消息内容
      </p>
    </div>

    <div class="section-body">
      <!-- 消息标题 -->
      <div class="form-group">
        <label class="form-label required">
          消息标题
          <span class="label-tip">添加好友后推送的第一条文字消息（建议15字以内）</span>
        </label>
        <input
          v-model="localConfig.cardTitle"
          type="text"
          class="form-input"
          placeholder="例如：这是我的数字名片 👋"
          maxlength="30"
          @input="handleChange"
        />
        <div class="char-count">{{ localConfig.cardTitle?.length || 0 }} / 30</div>
      </div>

      <!-- 说明提示 -->
      <div class="info-box">
        <div class="info-header">ℹ️ 消息说明</div>
        <p class="info-text">
          添加客户后会自动发送<strong>两条消息</strong>：<br>
          1. 第一条：纯文字消息（使用上方的"消息标题"）<br>
          2. 第二条：卡片消息（链接到下方的卡片预览页面）<br>
          客户点击卡片中的<strong>"联系我"</strong>按钮，会跳转到完整名片页面。
        </p>
      </div>

      <!-- 卡片预览样式配置 -->
      <CardPreviewEditor
        v-model="localConfig.cardPreviewConfig"
        :wecom-avatar="wecomAvatar"
        @input="handleCardPreviewChange"
      />

      <!-- 卡片预览效果 -->
      <CardPreviewDisplay
        :preview-data="previewData"
        :card-config="localConfig.cardPreviewConfig"
        :wecom-avatar="wecomAvatar"
      />
    </div>
  </div>
</template>

<script>
import ImageUpload from '../form/ImageUpload.vue'
import CardPreviewEditor from './CardPreviewEditor.vue'
import CardPreviewDisplay from './CardPreviewDisplay.vue'

export default {
  name: 'PushConfigSection',
  
  components: {
    ImageUpload,
    CardPreviewEditor,
    CardPreviewDisplay
  },
  
  props: {
    value: {
      type: Object,
      default: () => ({})
    },
    wecomAvatar: {
      type: String,
      default: ''
    },
    memberInfo: {
      type: Object,
      default: () => ({
        name: '张三',
        title: '产品经理',
        mobile: '13800138000'
      })
    }
  },

  data() {
    return {
      localConfig: {
        cardTitle: '',
        cardPreviewConfig: {
          avatarMode: 'company',
          companyAvatar: '',
          backgroundType: 'svg',
          svgPattern: 'geometric',
          svgGradientStart: '#ffffff',
          svgGradientEnd: '#FC726E',
          backgroundImage: '',
          backgroundColor: '#f5f5f5',
          bottomColor: '#fbb9b6',
          phoneIconColor: '#fbb9b6',
          personalIntro: ''
        }
      }
    }
  },

  computed: {
    previewData() {
      return {
        name: '张三', // 预览时统一使用"张三"
        title: this.memberInfo.title || '产品经理',
        companyShort: this.memberInfo.companyShort || '',
        companyIntro: this.memberInfo.companyIntro || '',
        personalIntro: this.localConfig.cardPreviewConfig?.personalIntro || '',
        mobile: this.memberInfo.mobile || '13800138000',
        avatar: this.wecomAvatar || ''
      }
    }
  },

  watch: {
    value: {
      handler(newVal) {
        if (newVal) {
          this.localConfig = {
            cardTitle: newVal.cardTitle || '',
            cardPreviewConfig: newVal.cardPreviewConfig || {
              avatarMode: 'company',
              companyAvatar: '',
              backgroundType: 'svg',
              svgPattern: 'geometric',
              svgGradientStart: '#ffffff',
              svgGradientEnd: '#FC726E',
              backgroundImage: '',
              backgroundColor: '#f5f5f5',
              bottomColor: '#fbb9b6',
              phoneIconColor: '#fbb9b6',
              personalIntro: ''
            }
          }
        }
      },
      immediate: true,
      deep: true
    }
  },

  methods: {
    handleChange() {
      this.$emit('input', { ...this.localConfig })
    },

    handleCardPreviewChange(config) {
      this.localConfig.cardPreviewConfig = { ...config }
      this.$emit('input', { ...this.localConfig })
    },

    handleImageError(e) {
      e.target.style.display = 'none'
      this.$toast?.warning('图片加载失败，请检查URL是否正确')
    }
  }
}
</script>

<style scoped>
.push-config-section {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  letter-spacing: -0.5px;
}

.section-title .icon {
  font-size: 32px;
  filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
}

.section-desc {
  font-size: 15px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
  font-weight: 500;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.form-label.required::after {
  content: '*';
  color: #f56c6c;
  margin-left: 4px;
}

.label-tip {
  font-size: 12px;
  color: #999;
  font-weight: normal;
  margin-left: 8px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
  font-weight: 500;
}

.form-input:hover,
.form-textarea:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

/* 图片预览容器 */
.image-preview-container {
  margin-top: 16px;
}

.image-preview-large {
  position: relative;
  display: inline-block;
  max-width: 200px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-preview-large img {
  width: 200px;
  height: 400px;
  object-fit: cover;
  display: block;
}

.remove-image-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
}

.remove-image-btn:hover {
  background: rgba(239, 68, 68, 0.9);
  transform: scale(1.1);
}

.icon-close::before {
  content: '✕';
  font-size: 16px;
  font-weight: bold;
}

/* 上传区域 */
.upload-area {
  margin-top: 16px;
  padding: 32px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.upload-image-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.upload-image-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.icon-upload::before {
  content: '📤';
  font-size: 18px;
}

.upload-hint {
  margin-top: 12px;
  font-size: 13px;
  color: #64748b;
}

/* URL输入区域 */
.url-input-section {
  margin-top: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.url-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  display: block;
  margin-bottom: 8px;
}

.url-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.url-input {
  flex: 1;
  margin-bottom: 0 !important;
}

.clear-url-btn {
  width: 36px;
  height: 36px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.clear-url-btn:hover {
  background: #ef4444;
  color: white;
}

.icon-close-circle::before {
  content: '✕';
  font-size: 16px;
}

.image-preview {
  margin-top: 12px;
  max-width: 200px;
}

.image-preview img {
  width: 100%;
  border-radius: 4px;
  border: 1px solid #eee;
}

/* 消息预览 */
.preview-box {
  margin: 32px 0;
  padding: 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%);
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}

.preview-box::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.preview-label {
  font-size: 14px;
  color: #475569;
  margin-bottom: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.preview-label::before {
  content: '👁️';
  font-size: 18px;
}

.message-card-preview {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  max-width: 360px;
  transition: transform 0.3s ease;
  position: relative;
  z-index: 1;
}

.message-card-preview:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 16px 56px rgba(0, 0, 0, 0.2);
}

.preview-image {
  width: 100%;
  height: 160px;
  overflow: hidden;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-content {
  padding: 16px;
}

.preview-title {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 10px;
  line-height: 1.5;
  letter-spacing: -0.3px;
}

.preview-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 16px;
}

.preview-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.preview-action:hover {
  transform: translateX(4px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

.preview-action::after {
  content: '→';
  font-size: 16px;
}

/* 说明提示框 */
.info-box {
  margin: 24px 0;
  padding: 16px 20px;
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-left: 4px solid #3b82f6;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.info-header {
  font-size: 14px;
  font-weight: 600;
  color: #1e40af;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-text {
  font-size: 13px;
  color: #1e3a8a;
  line-height: 1.6;
  margin: 0;
}

.info-text strong {
  color: #1e40af;
  font-weight: 600;
}
</style>

