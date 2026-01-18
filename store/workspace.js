/**
 * Workspace Store Module
 * 管理租户配置工作台的状态
 */

import { 
  getFrameworkDefaultData,
  getFrameworkDefinition 
} from '@/config/framework-definitions'

import {
  generateModuleId,
  validateConfig,
  normalizeSortOrder,
  cloneModule
} from '@/utils/framework-migration'

export const state = () => ({
  // 当前租户信息
  tenantInfo: null,
  
  // 模块配置列表
  modules: [],
  
  // Header配置
  header: {
    background_style: 'solid',
    slogan: '',
    show_company_logo: true,
    contact_visibility: {
      mobile: true,
      wechat: true,
      email: true,
      phone: false,
      address: false,
      website: true
    }
  },
  
  // 主题
  theme: 'tech',
  
  // 状态标志
  isDirty: false,          // 是否有未保存的更改
  isSaving: false,         // 是否正在保存
  isLoading: false,        // 是否正在加载
  
  // 错误信息
  error: null,
  
  // 配置版本
  version: '1.0'
})

export const getters = {
  // 已启用的模块（按sort_order排序）
  enabledModules: (state) => {
    return state.modules
      .filter(m => m.enabled)
      .sort((a, b) => a.sort_order - b.sort_order)
  },
  
  // 模块总数
  moduleCount: (state) => {
    return state.modules.length
  },
  
  // 已启用模块数
  enabledModuleCount: (state, getters) => {
    return getters.enabledModules.length
  },
  
  // 根据ID获取模块
  getModuleById: (state) => (id) => {
    return state.modules.find(m => m.id === id)
  },
  
  // 预览数据（转换为WecardOptimized所需格式）
  previewData: (state, getters) => {
    // 辅助函数：将驼峰命名转换为下划线命名
    const toSnakeCase = (str) => {
      return str
        .replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
        .replace(/^_/, '') // 移除开头的下划线
    }
    
    // ✅ 生成默认头像（使用姓名首字母）
    const getDefaultAvatar = (name) => {
      const names = (name || '张三').split(' ')
      const initials = names.length >= 2 
        ? names[0].charAt(0) + names[1].charAt(0)
        : (name || '张').charAt(0)
      return `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect fill="#667eea" width="200" height="200"/><text x="50%" y="50%" font-size="80" fill="white" text-anchor="middle" dominant-baseline="central" font-family="Arial">${initials}</text></svg>`)}`
    }
    
    return {
      basic_info: {
        name: '张三', // ✅ 预览用模拟姓名
        title: '产品经理', // ✅ 预览用模拟职位
        department: '产品部', // ✅ 预览用模拟部门
        company: state.tenantInfo?.name || '示例公司', // ✅ 公司简称
        company_logo: state.tenantInfo?.logo || '',
        avatar: getDefaultAvatar('张三'), // ✅ 预览用模拟头像
        slogan: state.header?.slogan || '以白为底，科技为线' // ✅ 预览用模拟slogan
      },
      contact_info: {
        mobile: '138****0000',
        email: 'contact@example.com',
        wechat: 'wechat_id'
      },
      header: state.header,
      // 🔧 修复：改为数组格式，支持同类型模块多次添加
      // 所有启用的模块都会在 modules_list 中，支持多个同类型模块
      modules_list: getters.enabledModules.map(module => ({
        id: module.id,
        type: module.framework_type,
        type_snake: toSnakeCase(module.framework_type),
        enabled: true,
        title: module.custom_title,
        sort_order: module.sort_order,
        data: module.data
      })),
      // 保留旧的对象格式（向后兼容，但仅在 modules_list 为空时使用）
      // 注意：如果 modules_list 存在且有数据，则 modules 对象应为空，避免重复渲染
      // 只有当 modules_list 为空时，才生成 modules 对象用于旧版兼容
      modules: (getters.enabledModules.length === 0) ? {} : {},
      theme: state.theme
    }
  },
  
  // 配置是否有效
  isConfigValid: (state) => {
    const validation = validateConfig({
      version: state.version,
      header: state.header,
      modules: state.modules,
      theme: state.theme
    })
    return validation.valid
  },
  
  // 配置验证错误
  configErrors: (state) => {
    const validation = validateConfig({
      version: state.version,
      header: state.header,
      modules: state.modules,
      theme: state.theme
    })
    return validation.errors
  }
}

export const mutations = {
  // 设置租户信息
  SET_TENANT_INFO(state, tenantInfo) {
    state.tenantInfo = tenantInfo
  },
  
  // 设置加载状态
  SET_LOADING(state, loading) {
    state.isLoading = loading
  },
  
  // 设置保存状态
  SET_SAVING(state, saving) {
    state.isSaving = saving
  },
  
  // 设置错误
  SET_ERROR(state, error) {
    state.error = error
  },
  
  // 清除错误
  CLEAR_ERROR(state) {
    state.error = null
  },
  
  // 设置整个配置
  SET_CONFIG(state, config) {
    state.modules = config.modules || []
    state.header = config.header || state.header
    state.theme = config.theme || 'tech'
    state.version = config.version || '1.0'
    state.isDirty = false
  },
  
  // 添加模块
  ADD_MODULE(state, module) {
    state.modules.push(module)
    state.isDirty = true
  },
  
  // 更新模块
  UPDATE_MODULE(state, { id, updates }) {
    const index = state.modules.findIndex(m => m.id === id)
    if (index !== -1) {
      state.modules.splice(index, 1, {
        ...state.modules[index],
        ...updates
      })
      state.isDirty = true
    }
  },
  
  // 更新模块数据（用于配置表单）
  UPDATE_MODULE_DATA(state, { id, data }) {
    const index = state.modules.findIndex(m => m.id === id)
    if (index !== -1) {
      // ✅ 深拷贝断开引用，防止"在 mutation 之外修改 Vuex"崩溃
      state.modules[index].data = JSON.parse(JSON.stringify(data))
      state.isDirty = true
    }
  },
  
  // 删除模块
  DELETE_MODULE(state, id) {
    const index = state.modules.findIndex(m => m.id === id)
    if (index !== -1) {
      state.modules.splice(index, 1)
      // 重新标准化sort_order
      state.modules.forEach((m, i) => {
        m.sort_order = i
      })
      state.isDirty = true
    }
  },
  
  // 更新模块列表（用于拖拽排序）
  SET_MODULES(state, modules) {
    state.modules = modules
    // 更新sort_order
    modules.forEach((m, index) => {
      m.sort_order = index
    })
    state.isDirty = true
  },
  
  // 切换模块启用状态
  TOGGLE_MODULE_ENABLED(state, id) {
    const module = state.modules.find(m => m.id === id)
    if (module) {
      module.enabled = !module.enabled
      state.isDirty = true
    }
  },
  
  // 更新Header配置
  UPDATE_HEADER(state, headerConfig) {
    state.header = {
      ...state.header,
      ...headerConfig
    }
    state.isDirty = true
  },
  
  // 更新主题
  SET_THEME(state, theme) {
    state.theme = theme
    state.isDirty = true
  },
  
  // 标记为已保存
  MARK_SAVED(state) {
    state.isDirty = false
  },
  
  // 重置状态
  RESET_STATE(state) {
    state.modules = []
    state.header = {
      background_style: 'solid',
      slogan: '',
      show_company_logo: true,
      contact_visibility: {
        mobile: true,
        wechat: true,
        email: true,
        phone: false,
        address: false,
        website: true
      }
    }
    state.theme = 'tech'
    state.isDirty = false
    state.error = null
  }
}

export const actions = {
  // 加载租户配置（使用JWT认证）
  async loadConfig({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      console.log('📡 开始加载workspace配置...')
      
      // 获取token
      const token = this.$wecomAuth.getToken()
      if (!token) {
        throw new Error('未找到认证token')
      }
      
      console.log('✅ Token已获取，发送请求...')
      
      // JWT token通过axios拦截器自动添加，但这里显式传递确保万无一失
      const { data } = await this.$axios.get(`/api/v1/wecom/tenant/workspace`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      console.log('✅ 配置加载成功:', {
        tenant: data.tenant_info?.name,
        modules: data.config?.modules?.length || 0
      })
      
      commit('SET_TENANT_INFO', data.tenant_info)
      commit('SET_CONFIG', data.config || {})
      
      return data
    } catch (error) {
      console.error('❌ 加载配置失败:', error)
      console.error('错误详情:', error.response?.data)
      commit('SET_ERROR', error.response?.data?.error || error.response?.data?.message || error.message || '加载配置失败')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 保存配置（使用JWT认证）
  async saveConfig({ state, commit, getters }) {
    // 验证配置
    if (!getters.isConfigValid) {
      const errors = getters.configErrors
      commit('SET_ERROR', `配置验证失败：${errors.join(', ')}`)
      return false
    }
    
    commit('SET_SAVING', true)
    commit('CLEAR_ERROR')
    
    try {
      const config = {
        version: state.version,
        header: state.header,
        modules: state.modules,
        theme: state.theme
      }
      
      console.log('💾 开始保存配置:', {
        模块数量: state.modules.length,
        主题: state.theme
      })
      
      // 确保有JWT token
      const token = this.$wecomAuth.getToken()
      if (!token) {
        throw new Error('未找到认证token，请重新登录')
      }
      
      console.log('✅ Token已获取，长度:', token.length)
      
      // JWT token通过axios拦截器自动添加到headers，但这里显式传递确保万无一失
      const { data } = await this.$axios.put(
        `/api/v1/wecom/tenant/workspace`,
        { config },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      console.log('✅ 保存成功:', data)
      commit('MARK_SAVED')
      
      return data
    } catch (error) {
      console.error('❌ 保存配置失败:', error)
      console.error('错误详情:', error.response?.data)
      commit('SET_ERROR', error.response?.data?.error || error.response?.data?.message || error.message || '保存配置失败')
      throw error
    } finally {
      commit('SET_SAVING', false)
    }
  },
  
  // 添加模块
  addModule({ commit, state }, frameworkType) {
    const definition = getFrameworkDefinition(frameworkType)
    
    if (!definition) {
      console.error(`Unknown framework type: ${frameworkType}`)
      return
    }
    
    const newModule = {
      id: generateModuleId(),
      framework_type: frameworkType,
      framework_version: definition.version,
      enabled: true,
      sort_order: state.modules.length,
      custom_title: definition.name,
      data: getFrameworkDefaultData(frameworkType)
    }
    
    commit('ADD_MODULE', newModule)
    
    return newModule
  },
  
  // 复制模块
  duplicateModule({ commit, state }, id) {
    const module = state.modules.find(m => m.id === id)
    if (!module) {
      console.error(`Module ${id} not found`)
      return
    }
    
    const duplicated = cloneModule(module)
    duplicated.custom_title = `${module.custom_title} (副本)`
    duplicated.sort_order = state.modules.length
    
    commit('ADD_MODULE', duplicated)
    
    return duplicated
  },
  
  // 更新模块数据
  updateModule({ commit }, { id, updates }) {
    commit('UPDATE_MODULE', { id, updates })
  },
  
  // 更新模块配置数据（用于配置表单）
  updateModuleData({ commit }, { id, data }) {
    commit('UPDATE_MODULE_DATA', { id, data })
  },
  
  // 删除模块
  deleteModule({ commit }, id) {
    commit('DELETE_MODULE', id)
  },
  
  // 切换模块启用状态
  toggleModuleEnabled({ commit }, id) {
    commit('TOGGLE_MODULE_ENABLED', id)
  },
  
  // 更新模块排序（拖拽后）
  updateModuleOrder({ commit }, modules) {
    commit('SET_MODULES', modules)
  },
  
  // 更新Header
  updateHeader({ commit }, headerConfig) {
    commit('UPDATE_HEADER', headerConfig)
  },
  
  // 切换主题
  setTheme({ commit }, theme) {
    commit('SET_THEME', theme)
  },
  
  // 重置配置
  resetConfig({ commit }) {
    if (confirm('确定要重置所有配置吗？此操作不可恢复。')) {
      commit('RESET_STATE')
    }
  }
}

