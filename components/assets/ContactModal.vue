<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>联系方式</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="contact-info">
          <div class="contact-item">
            <div class="contact-icon">
              <i class="icon">📞</i>
            </div>
            <div class="contact-details">
              <h4>电话</h4>
              <p class="contact-value">{{ contactInfo.phone || '未提供' }}</p>
              <button 
                v-if="contactInfo.phone" 
                class="contact-action"
                @click="callPhone(contactInfo.phone)"
              >
                拨打电话
              </button>
            </div>
          </div>
          
          <div class="contact-item">
            <div class="contact-icon">
              <i class="icon">📧</i>
            </div>
            <div class="contact-details">
              <h4>邮箱</h4>
              <p class="contact-value">{{ contactInfo.email || '未提供' }}</p>
              <button 
                v-if="contactInfo.email" 
                class="contact-action"
                @click="sendEmail(contactInfo.email)"
              >
                发送邮件
              </button>
            </div>
          </div>
          
          <div class="contact-item">
            <div class="contact-icon">
              <i class="icon">💬</i>
            </div>
            <div class="contact-details">
              <h4>微信</h4>
              <p class="contact-value">{{ contactInfo.wechat || '未提供' }}</p>
              <button 
                v-if="contactInfo.wechat" 
                class="contact-action"
                @click="copyWechat(contactInfo.wechat)"
              >
                复制微信号
              </button>
            </div>
          </div>
          
          <div class="contact-item">
            <div class="contact-icon">
              <i class="icon">🏢</i>
            </div>
            <div class="contact-details">
              <h4>公司</h4>
              <p class="contact-value">{{ contactInfo.company || '未提供' }}</p>
            </div>
          </div>
          
          <div class="contact-item">
            <div class="contact-icon">
              <i class="icon">👤</i>
            </div>
            <div class="contact-details">
              <h4>职位</h4>
              <p class="contact-value">{{ contactInfo.position || '未提供' }}</p>
            </div>
          </div>
          
          <div v-if="contactInfo.address" class="contact-item">
            <div class="contact-icon">
              <i class="icon">📍</i>
            </div>
            <div class="contact-details">
              <h4>地址</h4>
              <p class="contact-value">{{ contactInfo.address }}</p>
              <button 
                class="contact-action"
                @click="openMap(contactInfo.address)"
              >
                查看地图
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="contactInfo.website" class="website-section">
          <h4>相关链接</h4>
          <div class="website-links">
            <a 
              :href="contactInfo.website" 
              target="_blank" 
              class="website-link"
            >
              <i class="icon">🌐</i>
              官方网站
            </a>
          </div>
        </div>
        
        <div v-if="contactInfo.socialLinks && contactInfo.socialLinks.length > 0" class="social-section">
          <h4>社交媒体</h4>
          <div class="social-links">
            <a 
              v-for="link in contactInfo.socialLinks" 
              :key="link.platform"
              :href="link.url" 
              target="_blank" 
              class="social-link"
            >
              <i :class="getSocialIcon(link.platform)"></i>
              {{ link.platform }}
            </a>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">关闭</button>
        <button class="btn btn-primary" @click="shareContact">分享联系方式</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    contactInfo: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    
    callPhone(phone) {
      if (process.client && typeof window !== 'undefined') {
        window.location.href = `tel:${phone}`
      }
    },
    
    sendEmail(email) {
      if (process.client && typeof window !== 'undefined') {
        window.location.href = `mailto:${email}`
      }
    },
    
    copyWechat(wechat) {
      if (process.client && typeof window !== 'undefined' && navigator.clipboard) {
        navigator.clipboard.writeText(wechat).then(() => {
          this.$toast.success('微信号已复制到剪贴板')
        }).catch(() => {
          this.fallbackCopy(wechat)
        })
      } else {
        this.fallbackCopy(wechat)
      }
    },
    
    fallbackCopy(text) {
      if (process.client && typeof window !== 'undefined') {
        const textArea = document.createElement('textarea')
        textArea.value = text
        document.body.appendChild(textArea)
        textArea.select()
        try {
          document.execCommand('copy')
          this.$toast.success('微信号已复制到剪贴板')
        } catch (err) {
          this.$toast.error('复制失败')
        }
        document.body.removeChild(textArea)
      }
    },
    
    openMap(address) {
      if (process.client && typeof window !== 'undefined') {
        const encodedAddress = encodeURIComponent(address)
        window.open(`https://maps.google.com/maps?q=${encodedAddress}`, '_blank')
      }
    },
    
    getSocialIcon(platform) {
      const iconMap = {
        '微信': 'icon-wechat',
        '微博': 'icon-weibo',
        'QQ': 'icon-qq',
        'LinkedIn': 'icon-linkedin',
        'Twitter': 'icon-twitter',
        'Facebook': 'icon-facebook',
        'Instagram': 'icon-instagram'
      }
      return iconMap[platform] || 'icon-link'
    },
    
    shareContact() {
      if (process.client && typeof window !== 'undefined') {
        const shareData = {
          title: `${this.contactInfo.name || '联系人'}的联系方式`,
          text: `姓名：${this.contactInfo.name || '未知'}\n电话：${this.contactInfo.phone || '未提供'}\n邮箱：${this.contactInfo.email || '未提供'}`,
          url: window.location.href
        }
        
        if (navigator.share) {
          navigator.share(shareData).catch(err => {
            console.log('分享失败:', err)
            this.fallbackShare(shareData)
          })
        } else {
          this.fallbackShare(shareData)
        }
      }
    },
    
    fallbackShare(shareData) {
      if (process.client && typeof window !== 'undefined') {
        const text = `${shareData.title}\n${shareData.text}\n${shareData.url}`
        if (navigator.clipboard) {
          navigator.clipboard.writeText(text).then(() => {
            this.$toast.success('联系方式已复制到剪贴板')
          }).catch(() => {
            this.$toast.error('分享失败')
          })
        } else {
          this.$toast.error('当前浏览器不支持分享功能')
        }
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.contact-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e6f7ff;
  border-radius: 50%;
  flex-shrink: 0;
}

.contact-details {
  flex: 1;
}

.contact-details h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
}

.contact-value {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  word-break: break-all;
}

.contact-action {
  background: #1890ff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.contact-action:hover {
  background: #40a9ff;
}

.website-section,
.social-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.website-section h4,
.social-section h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.website-links,
.social-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.website-link,
.social-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
  font-size: 14px;
  transition: background-color 0.3s;
}

.website-link:hover,
.social-link:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
  }
  
  .contact-item {
    flex-direction: column;
    text-align: center;
  }
  
  .contact-icon {
    align-self: center;
  }
}
</style>
