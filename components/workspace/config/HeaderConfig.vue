<template>
  <div class="module-config header-config">
    <div class="config-section">
      <h4 class="section-title">基础信息</h4>
      
      <p class="info-note">
        <i class="icon-info"></i>
        姓名、职位、部门等基础信息将自动从企业微信同步
      </p>
      
      <ImageUpload
        v-model="localData.companyLogo"
        label="公司Logo"
        hint="建议尺寸：200x200px，支持透明背景PNG"
        @change="emitChange"
      />
      
      <TextInput
        v-model="localData.companyName"
        label="公司名称"
        placeholder="XX科技有限公司"
        @input="emitChange"
      />
      
      <TextInput
        v-model="localData.slogan"
        label="Slogan标语"
        placeholder="专业、创新、值得信赖"
        hint="可选，显示在名片顶部"
        @input="emitChange"
      />
    </div>
    
    <div class="config-section">
      <h4 class="section-title">联系方式显示</h4>
      
      <p class="section-desc">选择要在名片头部显示的联系方式</p>
      
      <div class="contact-toggles">
        <label
          v-for="contact in contactFields"
          :key="contact.key"
          class="toggle-item"
        >
          <input
            v-model="localData.contactVisibility[contact.key]"
            type="checkbox"
            @change="emitChange"
          />
          <i :class="contact.icon"></i>
          <span>{{ contact.label }}</span>
        </label>
      </div>
    </div>
    
    <div class="config-section">
      <h4 class="section-title">样式设置</h4>
      
      <div class="form-group">
        <label class="form-label">背景样式</label>
        <div class="bg-options">
          <label class="radio-option">
            <input
              v-model="localData.backgroundStyle"
              type="radio"
              value="solid"
              @change="emitChange"
            />
            <span>纯色背景</span>
          </label>
          <label class="radio-option">
            <input
              v-model="localData.backgroundStyle"
              type="radio"
              value="translucent"
              @change="emitChange"
            />
            <span>半透明</span>
          </label>
          <label class="radio-option">
            <input
              v-model="localData.backgroundStyle"
              type="radio"
              value="gradient"
              @change="emitChange"
            />
            <span>渐变</span>
          </label>
        </div>
      </div>
      
      <ColorPicker
        v-model="localData.backgroundColor"
        label="背景颜色"
        @change="emitChange"
      />
      
      <div class="form-group">
        <label class="form-label">文字大小</label>
        <div class="typography-settings">
          <div class="size-item">
            <span class="size-label">姓名</span>
            <select v-model="localData.typography.nameSize" @change="emitChange">
              <option value="lg">大</option>
              <option value="xl">特大</option>
              <option value="2xl">超大</option>
            </select>
          </div>
          <div class="size-item">
            <span class="size-label">公司</span>
            <select v-model="localData.typography.companySize" @change="emitChange">
              <option value="md">中</option>
              <option value="lg">大</option>
              <option value="xl">特大</option>
            </select>
          </div>
          <div class="size-item">
            <span class="size-label">职位</span>
            <select v-model="localData.typography.titleSize" @change="emitChange">
              <option value="sm">小</option>
              <option value="md">中</option>
              <option value="lg">大</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label class="form-label">
          <input
            v-model="localData.showCompanyLogo"
            type="checkbox"
            @change="emitChange"
          />
          显示公司Logo
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import TextInput from '../form/TextInput.vue'
import ImageUpload from '../form/ImageUpload.vue'
import ColorPicker from '../form/ColorPicker.vue'
import debounceMixin from './debounce-mixin'

export default {
  name: 'HeaderConfig',
  
  mixins: [debounceMixin],
  
  components: {
    TextInput,
    ImageUpload,
    ColorPicker
  },
  
  props: {
    data: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      localData: this._smartClone ? this._smartClone(this.data) : { ...this.data },
      
      contactFields: [
        { key: 'mobile', label: '手机号', icon: 'icon-phone' },
        { key: 'wechat', label: '微信', icon: 'icon-wechat' },
        { key: 'email', label: '邮箱', icon: 'icon-email' },
        { key: 'phone', label: '座机', icon: 'icon-telephone' },
        { key: 'address', label: '地址', icon: 'icon-location' },
        { key: 'website', label: '官网', icon: 'icon-globe' }
      ]
    }
  },
  
  // watch 已由 debounce-mixin 提供
  
  methods: {
    // emitChange 方法现在由 debounce-mixin 提供
  }
}
</script>

<style scoped>
.module-config {
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
}

.config-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #e0e0e0;
}

.config-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 16px 0;
}

.section-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.info-note {
  padding: 12px 16px;
  background: rgba(0, 123, 255, 0.1);
  border-left: 3px solid #007bff;
  border-radius: 6px;
  font-size: 13px;
  color: #1a1a2e;
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.contact-toggles {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.toggle-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-item:hover {
  border-color: #00ffaa;
  background: rgba(0, 255, 170, 0.05);
}

.toggle-item input[type="checkbox"] {
  margin: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.bg-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
}

.typography-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.size-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.size-label {
  font-size: 14px;
  color: #1a1a2e;
}

.size-item select {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}
</style>

