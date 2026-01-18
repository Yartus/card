/**
 * WeCard 框架定义配置
 * 
 * 这是服务商层的框架定义，所有租户共享
 * 服务商更新框架代码后，所有租户自动受益
 * 
 * 架构设计原则：
 * - 服务商维护：组件代码、框架Schema、默认配置
 * - 租户维护：框架实例、自定义标题、内容数据
 * - 分离关注点：框架逻辑与内容数据解耦
 */

/**
 * 框架分类定义
 */
export const FRAMEWORK_CATEGORIES = {
  display: {
    label: '内容展示',
    icon: '🖼',
    order: 1,
    description: '图片、视频等媒体内容展示'
  },
  content: {
    label: '文本内容',
    icon: '📝',
    order: 2,
    description: '文章、介绍等文本内容'
  },
  credentials: {
    label: '信任背书',
    icon: '🏆',
    order: 3,
    description: '客户Logo、资质证书等'
  },
  timeline: {
    label: '时间线',
    icon: '⏱',
    order: 4,
    description: '发展历程、里程碑'
  },
  social: {
    label: '社交媒体',
    icon: '🔗',
    order: 5,
    description: '社交平台链接'
  }
}

/**
 * 所有可用框架的定义
 * 
 * 每个框架包含：
 * - 基础信息：id、版本、名称、描述
 * - 组件映射：Vue组件文件、配置组件文件
 * - 数据Schema：定义数据结构和验证规则
 * - 默认数据：新建时的初始值
 * - 套餐限制：不同套餐的功能限制
 */
export const FRAMEWORK_DEFINITIONS = {
  /**
   * 通用网格框架
   * 支持多种模式的网格展示
   */
  StandardGrid: {
    id: 'StandardGrid',
    version: '1.1.0',
    name: '通用网格框架',
    icon: '🏢',
    description: '支持图标、图片、Logo、文本四种展示模式',
    category: 'display',
    
    component: 'StandardGrid.vue',
    configComponent: 'StandardGridConfig.vue',
    
    dataSchema: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          default: '网格展示',
          description: '模块标题'
        },
        subtitle: {
          type: 'string',
          default: '',
          description: '副标题'
        },
        mode: {
          type: 'string',
          enum: ['icon', 'image', 'logo', 'text'],
          default: 'image',
          description: '展示模式'
        },
        columns: {
          type: 'number',
          default: 2,
          min: 2,
          max: 3,
          description: '网格列数（2-3列）'
        },
        items: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              // icon模式
              icon: { type: 'string' },
              // image/logo模式
              src: { type: 'string' },
              image: { type: 'string' },
              logo: { type: 'string' },
              alt: { type: 'string' },
              // text模式
              content: { type: 'string' },
              // 通用
              title: { type: 'string' },
              name: { type: 'string' },
              description: { type: 'string' },
              subtitle: { type: 'string' },
              link: { type: 'string' }
            }
          }
        }
      }
    },
    
    defaultData: {
      title: '网格展示',
      subtitle: '',
      mode: 'image',
      columns: 2,
      items: []
    },
    
    planLimits: {
      free: { max_items: 8 },
      paid: { max_items: 30 },
      enterprise: { max_items: 100 }
    },
    
    previewImage: '/assets/previews/standard-grid.png'
  },

  /**
   * 信任背书框架
   * 展示客户Logo、合作伙伴、资质证书
   */
  TrustCredentials: {
    id: 'TrustCredentials',
    version: '1.0.0',
    name: '信任背书框架',
    icon: '🤝',
    description: '展示客户Logo、合作伙伴、资质证书',
    category: 'credentials',
    
    component: 'TrustCredentials.vue',
    configComponent: 'TrustCredentialsConfig.vue',
    
    dataSchema: {
      type: 'object',
      properties: {
        credentials: {
          type: 'array',
          description: '资质证书列表',
          items: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                required: true,
                description: '证书ID'
              },
              image: {
                type: 'string',
                required: true,
                description: '证书图片URL'
              },
              title: {
                type: 'string',
                required: true,
                description: '证书名称'
              },
              issuer: {
                type: 'string',
                description: '颁发机构'
              },
              date: {
                type: 'string',
                description: '获得时间'
              }
            }
          }
        },
        logos: {
          type: 'array',
          description: '客户/合作伙伴Logo列表',
          items: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                required: true,
                description: '客户/合作伙伴名称'
              },
              logo: {
                type: 'string',
                required: true,
                description: 'Logo图片URL'
              },
              url: {
                type: 'string',
                description: '官网链接（可选）'
              }
            }
          }
        },
        layout: {
          type: 'string',
          enum: ['grid', 'carousel'],
          default: 'grid',
          description: '布局样式'
        },
        showDate: {
          type: 'boolean',
          default: true,
          description: '是否显示获得时间'
        },
        enableZoom: {
          type: 'boolean',
          default: true,
          description: '是否支持点击放大'
        },
        uniform_shape: {
          type: 'string',
          enum: ['rect', 'circle', 'square'],
          default: 'rect',
          description: 'Logo统一形状'
        },
        aspect_ratio: {
          type: 'string',
          enum: ['4:3', '16:9', '1:1'],
          default: '4:3',
          description: 'Logo宽高比'
        },
        carousel: {
          type: 'object',
          description: '轮播配置',
          properties: {
            autoplay: {
              type: 'boolean',
              default: true
            },
            speed_ms: {
              type: 'number',
              default: 3000,
              min: 1000,
              max: 10000
            },
            gap_px: {
              type: 'number',
              default: 12,
              min: 0,
              max: 50
            },
            loop: {
              type: 'boolean',
              default: true
            }
          }
        }
      }
    },
    
    defaultData: {
      credentials: [],
      logos: [],
      layout: 'grid',
      showDate: true,
      enableZoom: true,
      uniform_shape: 'rect',
      aspect_ratio: '4:3',
      carousel: {
        autoplay: true,
        speed_ms: 3000,
        gap_px: 12,
        loop: true
      }
    },
    
    planLimits: {
      free: { max_logos: 8 },
      paid: { max_logos: 30 },
      enterprise: { max_logos: 100 }
    },
    
    previewImage: '/assets/previews/trust-credentials.png'
  },

  /**
   * 企业时间线框架
   * 展示企业发展历程、里程碑事件
   */
  Timeline: {
    id: 'Timeline',
    version: '1.0.0',
    name: '企业时间线框架',
    icon: '⏱',
    description: '展示企业发展历程、里程碑事件',
    category: 'timeline',
    
    component: 'Timeline.vue',
    configComponent: 'TimelineConfig.vue',
    
    dataSchema: {
      type: 'object',
      properties: {
        layout: {
          type: 'string',
          enum: ['alternate', 'left', 'right'],
          default: 'alternate',
          description: '布局方式：左右交错/左对齐/右对齐'
        },
        line_style: {
          type: 'string',
          enum: ['solid', 'dashed', 'dotted'],
          default: 'dashed',
          description: '时间线样式'
        },
        events: {
          type: 'array',
          description: '事件列表',
          items: {
            type: 'object',
            properties: {
              date: {
                type: 'string',
                required: true,
                pattern: '^\\d{4}-\\d{2}$',
                description: '日期（YYYY-MM格式）'
              },
              icon: {
                type: 'string',
                default: 'milestone',
                description: '事件图标'
              },
              title: {
                type: 'string',
                required: true,
                maxLength: 50,
                description: '事件标题'
              },
              description: {
                type: 'string',
                maxLength: 200,
                description: '事件描述'
              }
            }
          }
        }
      }
    },
    
    defaultData: {
      layout: 'alternate',
      line_style: 'dashed',
      events: []
    },
    
    planLimits: {
      free: { max_events: 4 },
      paid: { max_events: 12 },
      enterprise: { max_events: 30 }
    },
    
    previewImage: '/assets/previews/timeline.png'
  },

  /**
   * 企业简介框架
   * 展示公司介绍、企业文化等文本内容
   */
  CompanyIntro: {
    id: 'CompanyIntro',
    version: '1.1.0',
    name: '企业简介框架',
    icon: '🏢',
    description: '展示公司介绍、企业文化、核心价值观',
    category: 'content',
    
    component: 'CompanyIntro.vue',
    configComponent: 'CompanyIntroConfig.vue',
    
    dataSchema: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          default: '企业简介',
          description: '模块标题'
        },
        mode: {
          type: 'string',
          enum: ['simple', 'rich'],
          default: 'simple',
          description: '内容模式'
        },
        // 简洁模式
        content: {
          type: 'string',
          maxLength: 1000,
          description: '企业简介内容（简洁模式）'
        },
        // 丰富模式
        subtitle: {
          type: 'string',
          description: '副标题（丰富模式）'
        },
        summary: {
          type: 'string',
          maxLength: 800,
          description: '主要内容（丰富模式）'
        },
        points: {
          type: 'array',
          description: '核心要点列表（丰富模式）',
          items: { type: 'string' }
        },
        // 配图
        showImage: {
          type: 'boolean',
          default: false,
          description: '是否显示配图'
        },
        imagePosition: {
          type: 'string',
          enum: ['top', 'float-left', 'float-right'],
          default: 'top',
          description: '配图位置（顶部横图、左上角浮动、右上角浮动）'
        },
        image: {
          type: 'string',
          description: '配图URL'
        },
        // 数据亮点
        showHighlights: {
          type: 'boolean',
          default: false,
          description: '是否显示数据亮点'
        },
        highlightsColumns: {
          type: 'number',
          default: 2,
          min: 2,
          max: 3,
          description: '数据亮点列数（2-3列）'
        },
        highlights: {
          type: 'array',
          description: '核心数据亮点',
          items: {
            type: 'object',
            properties: {
              icon: { type: 'string' },
              iconType: { type: 'string', enum: ['emoji', 'css', 'svg', 'lottie'] },
              label: { type: 'string', required: true },
              value: { type: 'string', required: true }
            }
          }
        }
      }
    },
    
    defaultData: {
      title: '企业简介',
      mode: 'simple',
      content: '',
      subtitle: '',
      summary: '',
      points: [],
      showImage: false,
      imagePosition: 'top',
      image: '',
      showHighlights: false,
      highlightsColumns: 2,
      highlights: []
    },
    
    planLimits: {
      free: { max_length: 500, max_highlights: 3 },
      paid: { max_length: 1000, max_highlights: 8 },
      enterprise: { max_length: 2000, max_highlights: 15 }
    },
    
    previewImage: '/assets/previews/company-intro.png'
  },

  /**
   * Logo墙框架
   * 展示合作伙伴、客户Logo等
   */
  LogoWall: {
    id: 'LogoWall',
    version: '1.1.0',
    name: 'Logo墙框架',
    icon: '🎯',
    description: '展示合作伙伴Logo，支持横向滚动动画',
    category: 'display',
    
    component: 'LogoWall.vue',
    configComponent: 'LogoWallConfig.vue',
    
    dataSchema: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          default: '合作客户',
          description: '模块标题'
        },
        logos: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string', required: true },
              src: { type: 'string', required: true },
              name: { type: 'string' }
            }
          }
        },
        scrollSpeed: {
          type: 'number',
          default: 2.5,
          min: 1.5,
          max: 5,
          description: '滚动速度系数（秒/个Logo），数值越小越快'
        },
        perLogoDisplay: {
          type: 'number',
          default: null,
          description: '（已废弃，兼容旧配置）每个Logo显示时长'
        },
        duration: {
          type: 'number',
          default: null,
          description: '（已废弃，兼容旧配置）滚动动画时长'
        },
        pauseOnHover: {
          type: 'boolean',
          default: true,
          description: '鼠标悬停时暂停'
        },
        gap: {
          type: 'number',
          default: 28,
          min: 20,
          max: 48,
          description: 'Logo间距（px，最小20px避免过密）'
        },
        defaultStyle: {
          type: 'string',
          default: 'grayscale',
          enum: ['grayscale', 'color', 'dim'],
          description: '默认样式'
        }
      }
    },
    
    defaultData: {
      title: '合作客户',
      logos: [],
      scrollSpeed: 2.5, // 滚动速度系数（适中）
      pauseOnHover: true,
      gap: 28,
      defaultStyle: 'grayscale'
    },
    
    planLimits: {
      free: { max_logos: 8 },
      paid: { max_logos: 20 },
      enterprise: { max_logos: 30 }
    },
    
    previewImage: '/assets/previews/logo-wall.png'
  },

  /**
   * 视频展示框架
   * 支持外部视频链接和本地视频上传
   */
  VideoShowcase: {
    id: 'VideoShowcase',
    version: '2.0.0',
    name: '多媒体展示框架',
    icon: '🎬',
    description: '支持视频、图文交替、图片网格三种展示模式',
    category: 'display',
    
    component: 'VideoShowcase.vue',
    configComponent: 'VideoShowcaseConfig.vue',
    
    dataSchema: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          default: '多媒体展示',
          description: '模块标题'
        },
        subtitle: {
          type: 'string',
          description: '模块副标题'
        },
        mode: {
          type: 'string',
          enum: ['video', 'text-image-alt', 'image-grid'],
          default: 'video',
          description: '展示模式：视频/图文交替/图片网格'
        },
        grid_columns: {
          type: 'number',
          default: 2,
          min: 1,
          max: 3,
          description: '网格列数（仅视频和图片网格模式）'
        },
        videos: {
          type: 'array',
          description: '视频列表（仅视频模式）',
          items: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                required: true
              },
              type: {
                type: 'string',
                enum: ['external', 'local'],
                default: 'external',
                description: '视频类型：外部链接或本地上传'
              },
              url: {
                type: 'string',
                required: true,
                description: '视频URL或嵌入代码'
              },
              title: {
                type: 'string',
                required: true,
                maxLength: 100,
                description: '视频标题'
              },
              description: {
                type: 'string',
                maxLength: 200,
                description: '视频描述'
              },
              thumbnail: {
                type: 'string',
                description: '封面图URL'
              },
              duration: {
                type: 'string',
                description: '视频时长（如 3:45）'
              }
            }
          }
        },
        content: {
          type: 'object',
          description: '图文内容（图文交替和图片网格模式）',
          properties: {
            blocks: {
              type: 'array',
              description: '内容块列表（支持文字和图片混合排序）',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string', required: true },
                  type: { type: 'string', enum: ['text', 'image'], required: true },
                  text: { type: 'string', description: '文字内容（type=text时）' },
                  src: { type: 'string', description: '图片URL（type=image时）' },
                  caption: { type: 'string', description: '图片说明（type=image时）' }
                }
              }
            }
          }
        }
      }
    },
    
    defaultData: {
      title: '多媒体展示',
      subtitle: '',
      mode: 'video',
      grid_columns: 2,
      videos: [],
      content: {
        blocks: []
      }
    },
    
    planLimits: {
      free: {
        max_videos: 0,  // 🔒 不支持视频模式，只能使用图文模式
        max_images: 5,
        allow_local_upload: false,
        max_video_size_mb: 0
      },
      trial: {
        max_videos: 1,  // 🎬 只能添加1个视频
        max_images: 8,
        allow_local_upload: true,
        max_video_size_mb: 20
      },
      pro: {
        max_videos: 1,  // 🎬 只能添加1个视频
        max_images: 10,
        allow_local_upload: true,
        max_video_size_mb: 30
      },
      enterprise: {
        max_videos: 2,  // 🎬🎬 可以添加2个视频
        max_images: 20,
        allow_local_upload: true,
        max_video_size_mb: 50
      }
    },
    
    previewImage: '/assets/previews/video-showcase.png'
  },

  /**
   * 网店直达框架
   * 展示企业网店链接，支持多种平台：
   * - 电商平台：天猫、京东、拼多多、1688、淘宝等（APP唤醒，支持自定义平台）
   * - 微信生态：微信小程序、微信小店（小程序唤醒）
   */
  ShopDirect: {
    id: 'ShopDirect',
    version: '1.0.0',
    name: '网店直达',
    icon: '🛒',
    description: '展示企业网店链接，支持多种电商平台APP唤醒（天猫/京东/拼多多/1688/淘宝等），以及微信小程序/小店唤醒',
    category: 'social',
    
    component: 'ShopDirect.vue',
    configComponent: 'ShopDirectConfig.vue',
    
    dataSchema: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          default: '网店直达',
          description: '模块标题'
        },
        subtitle: {
          type: 'string',
          default: '',
          description: '模块副标题'
        },
        shops: {
          type: 'array',
          description: '网店列表',
          items: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                required: true,
                description: '网店ID'
              },
              name: {
                type: 'string',
                required: true,
                description: '网店名称'
              },
              platform: {
                type: 'string',
                enum: ['tmall', 'jd', 'pdd', '1688', 'taobao', 'miniprogram', 'wechat_shop', 'custom'],
                default: 'tmall',
                description: '平台类型（支持：tmall/jd/pdd/1688/taobao/miniprogram/wechat_shop/custom）'
              },
              platformName: {
                type: 'string',
                description: '自定义平台名称（当platform为custom时必填）'
              },
              image: {
                type: 'string',
                required: true,
                description: '横版展示图片URL'
              },
              // 电商平台字段
              appScheme: {
                type: 'string',
                description: 'APP唤醒链接（scheme，用于天猫/京东/拼多多/1688/淘宝/自定义）'
              },
              webUrl: {
                type: 'string',
                description: 'H5备用链接（APP未安装时降级使用）'
              },
              // 小程序/小店字段
              appId: {
                type: 'string',
                description: '小程序AppID（用于微信小程序/小店）'
              },
              path: {
                type: 'string',
                description: '小程序页面路径（可选）'
              },
              urlScheme: {
                type: 'string',
                description: 'URL Scheme（用于小程序外部唤醒，格式：weixin://dl/business/?t=TOKEN）'
              },
              qrCode: {
                type: 'string',
                description: '小程序码图片URL（降级方案）'
              },
              enabled: {
                type: 'boolean',
                default: true,
                description: '是否启用'
              }
            }
          }
        }
      }
    },
    
    defaultData: {
      title: '网店直达',
      subtitle: '点击进入我们的官方店铺',
      shops: []
    },
    
    planLimits: {
      free: { max_shops: 2 },
      trial: { max_shops: 2 },
      paid: { max_shops: 3 },
      enterprise: { max_shops: 3 }
    },
    
    previewImage: '/assets/previews/shop-direct.png'
  },

  /**
   * 注释：以下框架已被 StandardGrid 替代，暂时保留定义但不在ModuleLibrary中展示
   * - ProductGallery: 图片展示可使用 StandardGrid (mode='image')
   * - EnvironmentShowcase: 环境展示可使用 StandardGrid (mode='image')
   * 
   * 如需启用，请在 ModuleLibrary.vue 中取消注释
   */
}

/**
 * 获取框架定义
 * @param {string} frameworkType - 框架类型ID
 * @returns {object|null} 框架定义对象
 */
export function getFrameworkDefinition(frameworkType) {
  // 直接匹配
  if (FRAMEWORK_DEFINITIONS[frameworkType]) {
    return FRAMEWORK_DEFINITIONS[frameworkType]
  }
  
  // 向后兼容：检查legacyId映射
  const legacyMatch = Object.values(FRAMEWORK_DEFINITIONS).find(
    def => def.legacyId === frameworkType
  )
  
  return legacyMatch || null
}

/**
 * 获取框架的默认数据
 * @param {string} frameworkType - 框架类型ID
 * @returns {object} 默认数据（深拷贝）
 */
export function getFrameworkDefaultData(frameworkType) {
  const definition = FRAMEWORK_DEFINITIONS[frameworkType]
  if (!definition) {
    return {}
  }
  return JSON.parse(JSON.stringify(definition.defaultData))
}

/**
 * 按分类获取框架列表
 * @returns {object} 按分类组织的框架列表
 */
export function getFrameworksByCategory() {
  const result = {}
  
  Object.keys(FRAMEWORK_CATEGORIES).forEach(categoryId => {
    result[categoryId] = {
      ...FRAMEWORK_CATEGORIES[categoryId],
      frameworks: []
    }
  })
  
  Object.values(FRAMEWORK_DEFINITIONS).forEach(framework => {
    if (result[framework.category]) {
      result[framework.category].frameworks.push(framework)
    }
  })
  
  return result
}

/**
 * 验证模块数据是否符合Schema
 * @param {string} frameworkType - 框架类型
 * @param {object} data - 要验证的数据
 * @returns {object} { valid: boolean, errors: array }
 */
export function validateFrameworkData(frameworkType, data) {
  const definition = FRAMEWORK_DEFINITIONS[frameworkType]
  if (!definition) {
    return {
      valid: false,
      errors: [`Unknown framework type: ${frameworkType}`]
    }
  }
  
  // 简单验证（生产环境应使用 ajv 等专业库）
  const errors = []
  const schema = definition.dataSchema
  
  // TODO: 实现完整的Schema验证
  // 这里只做基础检查
  if (!data || typeof data !== 'object') {
    errors.push('Data must be an object')
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 检查套餐限制
 * @param {string} frameworkType - 框架类型
 * @param {string} planType - 套餐类型 (free/paid/enterprise)
 * @param {object} data - 数据对象
 * @returns {object} { allowed: boolean, message: string }
 */
export function checkPlanLimits(frameworkType, planType, data) {
  const definition = FRAMEWORK_DEFINITIONS[frameworkType]
  if (!definition || !definition.planLimits) {
    return { allowed: true }
  }
  
  const limits = definition.planLimits[planType]
  if (!limits) {
    return { allowed: true }
  }
  
  // 检查各种限制
  if (limits.max_items && data.items && data.items.length > limits.max_items) {
    return {
      allowed: false,
      message: `${definition.name}在${planType}套餐下最多支持${limits.max_items}个项目`
    }
  }
  
  if (limits.max_events && data.events && data.events.length > limits.max_events) {
    return {
      allowed: false,
      message: `${definition.name}在${planType}套餐下最多支持${limits.max_events}个事件`
    }
  }
  
  if (limits.max_shops && data.shops && data.shops.length > limits.max_shops) {
    return {
      allowed: false,
      message: `${definition.name}在${planType}套餐下最多支持${limits.max_shops}个网店`
    }
  }
  
  // 可以添加更多限制检查...
  
  return { allowed: true }
}

export default {
  FRAMEWORK_DEFINITIONS,
  FRAMEWORK_CATEGORIES,
  getFrameworkDefinition,
  getFrameworkDefaultData,
  getFrameworksByCategory,
  validateFrameworkData,
  checkPlanLimits
}

