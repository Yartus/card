/**
 * 图片上传限制配置
 * 
 * 支持租户级别的自定义配置
 * 平台型应用 - 不同租户可以有不同的限制
 */

/**
 * 默认限制配置
 */
const DEFAULT_LIMITS = {
  MAX_IMAGES: 20,                // 最大图片数量
  MAX_BATCH_UPLOAD: 10,          // 单次批量上传最大数量
  UPLOAD_COOLDOWN: 2000,         // 上传冷却时间（毫秒）
  MAX_FILE_SIZE: 500 * 1024,     // 单个文件最大大小（字节）
  
  ALLOWED_MIME_TYPES: [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/svg+xml',
    'image/webp'
  ],
  
  ALLOWED_EXTENSIONS: [
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.svg',
    '.webp'
  ]
}

/**
 * 租户自定义配置
 * 
 * 格式：
 * {
 *   [tenantId]: {
 *     MAX_IMAGES: number,
 *     MAX_BATCH_UPLOAD: number,
 *     // ... 其他可覆盖的配置
 *   }
 * }
 * 
 * 示例：
 * {
 *   'tenant_vip_001': {
 *     MAX_IMAGES: 50,           // VIP租户可上传50张
 *     MAX_FILE_SIZE: 1024 * 1024 // 1MB
 *   },
 *   'tenant_basic_001': {
 *     MAX_IMAGES: 10            // 基础版租户只能10张
 *   }
 * }
 */
const TENANT_LIMITS = {
  // 租户配置会从后端API获取，这里作为fallback
  // 或者在构建时注入
}

/**
 * 获取租户的上传限制配置
 * @param {string} tenantId - 租户ID
 * @returns {Object} 合并后的配置
 */
export function getUploadLimits(tenantId = null) {
  // 1. 从Vuex store获取租户配置（如果有）
  if (typeof window !== 'undefined' && window.$nuxt?.$store) {
    const storeLimits = window.$nuxt.$store.state.tenant?.uploadLimits
    if (storeLimits) {
      return { ...DEFAULT_LIMITS, ...storeLimits }
    }
  }
  
  // 2. 从租户配置中获取
  if (tenantId && TENANT_LIMITS[tenantId]) {
    return { ...DEFAULT_LIMITS, ...TENANT_LIMITS[tenantId] }
  }
  
  // 3. 返回默认配置
  return { ...DEFAULT_LIMITS }
}

/**
 * 设置租户的上传限制（运行时动态设置）
 * @param {string} tenantId - 租户ID
 * @param {Object} limits - 限制配置
 */
export function setTenantLimits(tenantId, limits) {
  if (!tenantId) {
    console.warn('setTenantLimits: tenantId is required')
    return
  }
  
  TENANT_LIMITS[tenantId] = { ...limits }
  
  // 如果有Vuex store，也更新到store中
  if (typeof window !== 'undefined' && window.$nuxt?.$store) {
    window.$nuxt.$store.commit('tenant/setUploadLimits', limits)
  }
}

/**
 * 从后端API加载租户配置
 * @param {Object} axios - axios实例
 * @param {string} tenantId - 租户ID
 * @returns {Promise<Object>} 租户限制配置
 */
export async function loadTenantLimitsFromAPI(axios, tenantId) {
  try {
    const response = await axios.get(`/api/v1/tenant/${tenantId}/upload-limits`)
    if (response.data && response.data.success) {
      const limits = response.data.limits
      setTenantLimits(tenantId, limits)
      return limits
    }
  } catch (error) {
    console.warn('Failed to load tenant upload limits, using defaults:', error.message)
  }
  return DEFAULT_LIMITS
}

/**
 * 验证配置值是否合法
 * @param {Object} limits - 要验证的配置
 * @returns {Object} 验证后的配置
 */
export function validateLimits(limits) {
  const validated = { ...limits }
  
  // 确保数值在合理范围内
  if (validated.MAX_IMAGES) {
    validated.MAX_IMAGES = Math.max(1, Math.min(100, validated.MAX_IMAGES))
  }
  
  if (validated.MAX_BATCH_UPLOAD) {
    validated.MAX_BATCH_UPLOAD = Math.max(1, Math.min(50, validated.MAX_BATCH_UPLOAD))
  }
  
  if (validated.UPLOAD_COOLDOWN) {
    validated.UPLOAD_COOLDOWN = Math.max(0, Math.min(10000, validated.UPLOAD_COOLDOWN))
  }
  
  if (validated.MAX_FILE_SIZE) {
    validated.MAX_FILE_SIZE = Math.max(100 * 1024, Math.min(10 * 1024 * 1024, validated.MAX_FILE_SIZE))
  }
  
  return validated
}

// 导出默认配置
export { DEFAULT_LIMITS }

// 默认导出获取函数
export default getUploadLimits

