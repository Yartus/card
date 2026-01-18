/**
 * WeCard 框架数据迁移工具
 * 
 * 处理框架版本升级时的数据迁移
 * 确保租户配置在框架更新后仍然兼容
 */

import { FRAMEWORK_DEFINITIONS, getFrameworkDefinition } from '@/config/framework-definitions'

/**
 * 比较版本号
 * @param {string} v1 - 版本号1
 * @param {string} v2 - 版本号2
 * @returns {number} -1: v1<v2, 0: v1=v2, 1: v1>v2
 */
export function compareVersions(v1, v2) {
  const parts1 = v1.split('.').map(Number)
  const parts2 = v2.split('.').map(Number)
  
  for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
    const p1 = parts1[i] || 0
    const p2 = parts2[i] || 0
    
    if (p1 < p2) return -1
    if (p1 > p2) return 1
  }
  
  return 0
}

/**
 * 迁移单个模块数据
 * @param {object} module - 模块配置对象
 * @returns {object} 迁移后的模块配置
 */
export function migrateModule(module) {
  const definition = getFrameworkDefinition(module.framework_type)
  
  if (!definition) {
    console.warn(`Unknown framework type: ${module.framework_type}, skipping migration`)
    return module
  }
  
  const currentVersion = definition.version
  const moduleVersion = module.framework_version || '1.0.0'
  
  // 如果版本一致，无需迁移
  if (compareVersions(moduleVersion, currentVersion) === 0) {
    return module
  }
  
  // 执行迁移
  const migrated = {
    ...module,
    framework_version: currentVersion
  }
  
  // 根据框架类型和版本执行特定迁移
  if (module.framework_type === 'ProductService') {
    migrated.data = migrateProductService(module.data, moduleVersion, currentVersion)
  } else if (module.framework_type === 'StandardGrid') {
    migrated.data = migrateStandardGrid(module.data, moduleVersion, currentVersion)
  } else if (module.framework_type === 'Timeline') {
    migrated.data = migrateTimeline(module.data, moduleVersion, currentVersion)
  }
  // ... 其他框架类型的迁移
  
  return migrated
}

/**
 * ProductService 数据迁移
 */
function migrateProductService(data, fromVersion, toVersion) {
  let migrated = { ...data }
  
  // 示例：从 1.0.0 升级到 1.1.0，添加了 grid_columns 字段
  if (compareVersions(fromVersion, '1.1.0') < 0 && compareVersions(toVersion, '1.1.0') >= 0) {
    if (!migrated.grid_columns) {
      migrated.grid_columns = 3 // 默认值
    }
  }
  
  // 示例：从 1.1.0 升级到 1.2.0，重构了 items 结构
  if (compareVersions(fromVersion, '1.2.0') < 0 && compareVersions(toVersion, '1.2.0') >= 0) {
    if (migrated.items) {
      migrated.items = migrated.items.map(item => {
        // 如果旧版本有某个字段，转换为新格式
        return {
          ...item,
          // 新增字段的默认值
          link: item.link || ''
        }
      })
    }
  }
  
  return migrated
}

/**
 * StandardGrid 数据迁移
 */
function migrateStandardGrid(data, fromVersion, toVersion) {
  let migrated = { ...data }
  
  // 添加迁移逻辑...
  
  return migrated
}

/**
 * Timeline 数据迁移
 */
function migrateTimeline(data, fromVersion, toVersion) {
  let migrated = { ...data }
  
  // 添加迁移逻辑...
  
  return migrated
}

/**
 * 迁移整个租户配置
 * @param {object} config - 租户配置对象
 * @returns {object} 迁移后的配置
 */
export function migrateConfig(config) {
  if (!config || !config.modules) {
    return config
  }
  
  const migrated = {
    ...config,
    modules: config.modules.map(migrateModule),
    // 更新配置版本号
    version: config.version || '1.0',
    migrated_at: new Date().toISOString()
  }
  
  return migrated
}

/**
 * 验证模块数据完整性
 * @param {object} module - 模块对象
 * @returns {object} { valid: boolean, errors: array, warnings: array }
 */
export function validateModule(module) {
  const errors = []
  const warnings = []
  
  // 检查必填字段
  if (!module.framework_type) {
    errors.push('Missing framework_type')
  }
  
  if (!module.id) {
    errors.push('Missing module id')
  }
  
  if (typeof module.sort_order !== 'number') {
    errors.push('Invalid sort_order')
  }
  
  // 检查框架是否存在
  const definition = getFrameworkDefinition(module.framework_type)
  if (!definition) {
    errors.push(`Unknown framework type: ${module.framework_type}`)
    return { valid: false, errors, warnings }
  }
  
  // 检查版本
  if (module.framework_version) {
    const currentVersion = definition.version
    if (compareVersions(module.framework_version, currentVersion) < 0) {
      warnings.push(`Module ${module.id} uses old version ${module.framework_version}, current is ${currentVersion}`)
    }
  } else {
    warnings.push(`Module ${module.id} missing framework_version`)
  }
  
  // 检查数据结构
  if (!module.data || typeof module.data !== 'object') {
    errors.push('Invalid or missing data object')
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  }
}

/**
 * 批量验证配置
 * @param {object} config - 租户配置
 * @returns {object} 验证结果
 */
export function validateConfig(config) {
  const results = {
    valid: true,
    errors: [],
    warnings: [],
    modules: []
  }
  
  if (!config) {
    results.valid = false
    results.errors.push('Config is null or undefined')
    return results
  }
  
  if (!config.modules || !Array.isArray(config.modules)) {
    results.valid = false
    results.errors.push('Config.modules is not an array')
    return results
  }
  
  // 验证每个模块
  config.modules.forEach((module, index) => {
    const moduleResult = validateModule(module)
    
    results.modules.push({
      index,
      id: module.id,
      ...moduleResult
    })
    
    if (!moduleResult.valid) {
      results.valid = false
      results.errors.push(...moduleResult.errors.map(err => 
        `Module ${index} (${module.id || 'unknown'}): ${err}`
      ))
    }
    
    results.warnings.push(...moduleResult.warnings)
  })
  
  // 检查模块ID唯一性
  const ids = config.modules.map(m => m.id).filter(Boolean)
  const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index)
  if (duplicates.length > 0) {
    results.valid = false
    results.errors.push(`Duplicate module IDs: ${duplicates.join(', ')}`)
  }
  
  // 检查sort_order连续性
  const sortOrders = config.modules.map(m => m.sort_order).filter(n => typeof n === 'number')
  if (sortOrders.length > 0) {
    const sorted = [...sortOrders].sort((a, b) => a - b)
    let hasGaps = false
    for (let i = 1; i < sorted.length; i++) {
      if (sorted[i] - sorted[i - 1] > 1) {
        hasGaps = true
        break
      }
    }
    if (hasGaps) {
      results.warnings.push('sort_order has gaps, consider normalizing')
    }
  }
  
  return results
}

/**
 * 标准化 sort_order（重新从0开始编号）
 * @param {object} config - 租户配置
 * @returns {object} 标准化后的配置
 */
export function normalizeSortOrder(config) {
  if (!config || !config.modules) {
    return config
  }
  
  const sorted = [...config.modules].sort((a, b) => 
    (a.sort_order || 0) - (b.sort_order || 0)
  )
  
  sorted.forEach((module, index) => {
    module.sort_order = index
  })
  
  return {
    ...config,
    modules: sorted
  }
}

/**
 * 生成唯一模块ID
 * @returns {string} UUID格式的ID
 */
export function generateModuleId() {
  return `module-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 克隆模块（用于复制功能）
 * @param {object} module - 源模块
 * @returns {object} 新模块（新ID，deep copy data）
 */
export function cloneModule(module) {
  return {
    ...module,
    id: generateModuleId(),
    data: JSON.parse(JSON.stringify(module.data))
  }
}

/**
 * 合并默认值到模块数据
 * @param {string} frameworkType - 框架类型
 * @param {object} data - 用户数据
 * @returns {object} 合并后的数据
 */
export function mergeDefaults(frameworkType, data) {
  const definition = getFrameworkDefinition(frameworkType)
  if (!definition) {
    return data
  }
  
  const defaults = definition.defaultData || {}
  
  // 深度合并（简单实现，生产环境应使用 lodash.merge）
  function deepMerge(target, source) {
    const result = { ...target }
    
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = deepMerge(target[key] || {}, source[key])
      } else if (!(key in result)) {
        result[key] = source[key]
      }
    }
    
    return result
  }
  
  return deepMerge(data || {}, defaults)
}

export default {
  compareVersions,
  migrateModule,
  migrateConfig,
  validateModule,
  validateConfig,
  normalizeSortOrder,
  generateModuleId,
  cloneModule,
  mergeDefaults
}

