<template>
  <div class="config-area">
    <!-- 头部 -->
    <div class="config-header">
      <h3 class="config-title">
        <span class="icon">⚙️</span>
        配置区域
      </h3>
      <div class="config-stats">
        <span class="stat-badge">{{ modules.length }}个模块</span>
        <span class="stat-badge enabled">{{ enabledCount }}已启用</span>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="modules.length === 0" class="empty-config">
      <div class="empty-content">
        <span class="empty-icon">👈</span>
        <h4>从左侧添加模块</h4>
        <p>拖拽或点击添加按钮</p>
        <p class="tip">💡 提示：同一框架可以添加多次</p>
      </div>
    </div>

    <!-- 模块列表（可拖拽） -->
    <draggable
      v-else
      v-model="modulesLocal"
      class="module-list"
      handle=".drag-handle"
      :animation="200"
      @end="onDragEnd"
    >
      <div
        v-for="module in modulesLocal"
        :key="module.id"
        :class="['module-item', { disabled: !module.enabled }]"
      >
        <!-- 模块头部 -->
        <div class="module-header">
          <button class="drag-handle" title="拖拽排序">
            <span class="icon">⋮⋮</span>
          </button>
          
          <span class="module-icon">{{ getFrameworkIcon(module.framework_type) }}</span>
          
          <div class="module-title-wrapper">
            <input
              v-model="module.custom_title"
              class="module-title-input"
              @blur="updateModule(module)"
              @keyup.enter="$event.target.blur()"
            />
            <span class="framework-type">{{ module.framework_type }}</span>
          </div>
          
          <div class="module-actions">
            <button
              class="action-btn"
              :class="{ active: module.enabled }"
              @click="toggleEnabled(module.id)"
              :title="module.enabled ? '禁用' : '启用'"
            >
              <span class="icon">{{ module.enabled ? '👁' : '👁‍🗨' }}</span>
            </button>
            
            <button
              class="action-btn"
              @click="duplicateModule(module.id)"
              title="复制"
            >
              <span class="icon">📋</span>
            </button>
            
            <button
              class="action-btn delete"
              @click="deleteModule(module.id)"
              title="删除"
            >
              <span class="icon">🗑</span>
            </button>
            
            <button
              class="action-btn expand"
              @click="toggleExpand(module.id)"
            >
              <span class="icon">{{ isExpanded(module.id) ? '▲' : '▼' }}</span>
            </button>
          </div>
        </div>

        <!-- 模块配置表单（可展开） -->
        <transition name="expand">
          <div v-if="isExpanded(module.id)" class="module-config">
            <!-- 使用 v-show 而非 v-if，减少重复渲染 -->
            <component
              v-show="getConfigComponent(module.framework_type)"
              :is="getConfigComponent(module.framework_type)"
              :key="module.id"
              :data="module.data"
              :plan-limit="getModulePlanLimit(module.framework_type)"
              @change="handleConfigChange(module.id, $event)"
            />
            
            <div v-if="!getConfigComponent(module.framework_type)" class="config-placeholder">
              <p>🚧 {{ getFrameworkName(module.framework_type) }} 配置表单开发中...</p>
              
              <!-- 临时：显示当前数据 -->
              <details class="data-preview">
                <summary>查看当前数据</summary>
                <pre>{{ JSON.stringify(module.data, null, 2) }}</pre>
              </details>
            </div>
          </div>
        </transition>
      </div>
    </draggable>

    <!-- 底部操作 -->
    <div v-if="modules.length > 0" class="config-footer">
      <button class="footer-btn" @click="collapseAll">
        <span class="icon">⬆</span>
        全部收起
      </button>
      <button class="footer-btn" @click="expandAll">
        <span class="icon">⬇</span>
        全部展开
      </button>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import draggable from 'vuedraggable'
import { getFrameworkDefinition } from '@/config/framework-definitions'

// 同步导入配置组件（确保组件立即可用）
import TimelineConfig from './config/TimelineConfig.vue'
import TrustCredentialsConfig from './config/TrustCredentialsConfig.vue'
import HeaderConfig from './config/HeaderConfig.vue'
import StandardGridConfig from './config/StandardGridConfig.vue'
import LogoWallConfig from './config/LogoWallConfig.vue'
import CompanyIntroConfig from './config/CompanyIntroConfig.vue'
import VideoShowcaseConfig from './config/VideoShowcaseConfig.vue'
import ShopDirectConfig from './config/ShopDirectConfig.vue'

const configComponents = {
  'Timeline': TimelineConfig,
  'TrustCredentials': TrustCredentialsConfig,
  'Header': HeaderConfig,
  'StandardGrid': StandardGridConfig,
  'LogoWall': LogoWallConfig,
  'CompanyIntro': CompanyIntroConfig,
  'VideoShowcase': VideoShowcaseConfig,
  'ShopDirect': ShopDirectConfig
}

export default {
  name: 'ConfigArea',
  
  components: {
    draggable
  },
  
  data() {
    return {
      // 改用对象存储展开状态，Vue 2 可以正确检测对象的变化
      expandedModules: {},
      loadedConfigComponents: {},
      // 添加渲染状态控制，防止同时渲染过多组件
      renderingModuleId: null
    }
  },
  
  watch: {
    modules: {
      handler(newModules) {
        // 当添加新模块时，自动展开它
        if (newModules.length > 0) {
          const lastModule = newModules[newModules.length - 1]
          if (lastModule && !this.expandedModules[lastModule.id]) {
            // 使用 nextTick 延迟展开，让 DOM 先渲染完成
            this.$nextTick(() => {
              this.$set(this.expandedModules, lastModule.id, true)
              console.log('✅ 自动展开新模块:', lastModule.custom_title)
            })
          }
        }
      },
      immediate: false
    }
  },
  
  computed: {
    ...mapState('workspace', ['modules', 'tenantInfo']),
    ...mapGetters('workspace', ['enabledModuleCount']),
    
    modulesLocal: {
      get() {
        return this.modules
      },
      set(value) {
        this.updateModuleOrder(value)
      }
    },
    
    enabledCount() {
      return this.modules.filter(m => m.enabled).length
    }
  },
  
  methods: {
    ...mapActions('workspace', [
      'updateModule',
      'deleteModule',
      'toggleModuleEnabled',
      'updateModuleOrder',
      'duplicateModule',
      'updateModuleData'
    ]),
    
    getFrameworkIcon(frameworkType) {
      const definition = getFrameworkDefinition(frameworkType)
      return definition?.icon || '📦'
    },
    
    getFrameworkName(frameworkType) {
      const definition = getFrameworkDefinition(frameworkType)
      return definition?.name || frameworkType
    },
    
    getConfigComponent(frameworkType) {
      // 直接返回配置组件（同步导入）
      const component = configComponents[frameworkType]
      if (component) {
        console.log(`✅ 配置组件可用: ${frameworkType}`)
        return component
      } else {
        console.warn(`⚠️ 未找到配置组件: ${frameworkType}`)
        return null
      }
    },
    
    getModulePlanLimit(frameworkType) {
      const definition = getFrameworkDefinition(frameworkType)
      const plan = this.tenantInfo?.plan || 'free'
      return definition?.planLimits?.[plan] || null
    },
    
    handleConfigChange(moduleId, newData) {
      this.updateModuleData({
        id: moduleId,
        data: newData
      })
    },
    
    toggleEnabled(id) {
      this.toggleModuleEnabled(id)
    },
    
    onDragEnd() {
      // 拖拽结束后自动保存顺序
      this.$toast?.success('排序已更新')
    },
    
    isExpanded(id) {
      return !!this.expandedModules[id]
    },
    
    toggleExpand(id) {
      const isCurrentlyExpanded = this.expandedModules[id]
      
      // 如果是展开操作，使用 requestAnimationFrame 优化性能
      if (!isCurrentlyExpanded) {
        // 先标记正在渲染
        this.renderingModuleId = id
        
        // 使用 nextTick 确保 DOM 更新后再展开
        this.$nextTick(() => {
          requestAnimationFrame(() => {
            this.$set(this.expandedModules, id, true)
            
            // 渲染完成后清除标记
            setTimeout(() => {
              this.renderingModuleId = null
            }, 100)
          })
        })
      } else {
        // 折叠操作直接执行
        this.$set(this.expandedModules, id, false)
      }
    },
    
    expandAll() {
      this.modules.forEach(m => {
        this.$set(this.expandedModules, m.id, true)
      })
    },
    
    collapseAll() {
      // 清空所有展开状态
      this.expandedModules = {}
    }
  }
}
</script>

<style scoped>
.config-area {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 头部 */
.config-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.config-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-stats {
  display: flex;
  gap: 8px;
}

.stat-badge {
  font-size: 12px;
  color: #8c8c8c;
  background: #f5f5f5;
  padding: 4px 10px;
  border-radius: 10px;
}

.stat-badge.enabled {
  background: #e6f7ff;
  color: #1890ff;
}

/* 空状态 */
.empty-config {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.empty-content {
  text-align: center;
  color: #8c8c8c;
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.empty-content h4 {
  font-size: 18px;
  color: #262626;
  margin: 0 0 8px 0;
}

.empty-content p {
  font-size: 14px;
  margin: 4px 0;
}

.tip {
  color: #fa8c16 !important;
  margin-top: 16px !important;
}

/* 模块列表 */
.module-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.module-item {
  background: white;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.module-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.module-item.disabled {
  opacity: 0.6;
}

/* 模块头部 */
.module-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
}

.drag-handle {
  cursor: grab;
  background: none;
  border: none;
  padding: 0;
  color: #bfbfbf;
  font-size: 16px;
  display: flex;
  align-items: center;
}

.drag-handle:active {
  cursor: grabbing;
}

.drag-handle:hover {
  color: #1890ff;
}

.module-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.module-title-wrapper {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.module-title-input {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  border: 1px solid transparent;
  background: transparent;
  padding: 4px 8px;
  border-radius: 4px;
  outline: none;
  width: 100%;
}

.module-title-input:hover {
  border-color: #d9d9d9;
}

.module-title-input:focus {
  border-color: #1890ff;
  background: white;
}

.framework-type {
  font-size: 11px;
  color: #8c8c8c;
  font-weight: normal;
}

.module-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #595959;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #f5f5f5;
}

.action-btn.active {
  color: #52c41a;
}

.action-btn.delete:hover {
  background: #fff2e8;
  color: #ff4d4f;
}

/* 模块配置 */
.module-config {
  border-top: 1px solid #f0f0f0;
  padding: 16px;
  background: #fafafa;
}

/* 展开/收起动画 */
.expand-enter-active, .expand-leave-active {
  transition: all 0.3s ease;
  max-height: 2000px;
  overflow: hidden;
}

.expand-enter, .expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding: 0 16px;
}

.config-placeholder {
  text-align: center;
  padding: 20px;
  color: #8c8c8c;
}

.config-placeholder p {
  margin: 4px 0;
  font-size: 14px;
}

.config-placeholder .small {
  font-size: 12px;
}

.data-preview {
  margin-top: 16px;
  text-align: left;
}

.data-preview summary {
  cursor: pointer;
  font-size: 12px;
  color: #1890ff;
  padding: 8px;
  border-radius: 4px;
}

.data-preview summary:hover {
  background: #e6f7ff;
}

.data-preview pre {
  margin-top: 8px;
  padding: 12px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 11px;
  overflow-x: auto;
  max-height: 300px;
}

/* 底部操作 */
.config-footer {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  background: #fafafa;
}

.footer-btn {
  flex: 1;
  padding: 8px 16px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  color: #595959;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.footer-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

/* 滚动条 */
.module-list::-webkit-scrollbar {
  width: 6px;
}

.module-list::-webkit-scrollbar-track {
  background: transparent;
}

.module-list::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}
</style>

