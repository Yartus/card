const isDev = process.env.NODE_ENV !== 'production'

export default {
  server: {
    host: process.env.NUXT_HOST || '127.0.0.1',
    port: process.env.NUXT_PORT || 3000,
    timing: false
  },

  watchers: {
    webpack: {
      aggregateTimeout: isDev ? 400 : 600,
      poll: false,
      ignored: /node_modules/
    },
    chokidar: {
      ignoreInitial: true
    }
  },

  // Global page headers
  head: {
    title: 'WeCard - 企业智能名片系统',
    htmlAttrs: {
      lang: 'zh-CN'
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'WeCard企业智能名片系统，集成企业微信，提供专业的数字名片解决方案' },
      { name: 'format-detection', content: 'telephone=no' },
      // 微信分享优化
      { property: 'og:type', content: 'website' },
      { property: 'og:title', content: 'WeCard - 企业智能名片系统' },
      { property: 'og:description', content: 'WeCard企业智能名片系统，集成企业微信，提供专业的数字名片解决方案' },
      { property: 'og:image', content: '/images/og-image.jpg' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
      { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true }
    ]
  },

  // Global CSS
  css: [
    '~/assets/css/main.scss',
    '~/assets/css/icons.scss',
    '~/assets/css/icon-font.css',
    '~/assets/css/wecard-enhanced.css'
  ],

  // Plugins to run before rendering page
  plugins: [
    '~/plugins/axios.js',
    '~/plugins/toast.js',
    '~/plugins/provider-auth.js',  // ✅ 服务商后台认证
    '~/plugins/wecom-auth.js',     // ✅ 企微OAuth认证
    { src: '~/plugins/lottie.js', mode: 'client' }
  ],

  // Auto import components
  components: true,

  // Modules for dev and build (recommended)
  // buildModules: [
  //   '@nuxtjs/eslint-module'
  // ],

  // Modules
  modules: [
    '@nuxtjs/axios',
    // '@nuxtjs/auth-next',  // ❌ 暂时禁用，使用自定义认证
    '@nuxtjs/toast'
  ],

  // Axios module configuration
  axios: {
    baseURL: process.env.API_BASE_URL || '/',
    browserBaseURL: process.env.BROWSER_BASE_URL || '/',
    proxy: false
  },

  // Auth module configuration (已禁用，使用自定义认证)
  // auth: {
  //   strategies: {
  //     local: {
  //       token: {
  //         property: 'access_token',
  //         global: true,
  //         required: false,
  //         type: 'Bearer',
  //         maxAge: 86400 * 30
  //       },
  //       refreshToken: false,
  //       user: {
  //         property: 'user',
  //         autoFetch: false
  //       },
  //       endpoints: {
  //         login: { url: '/api/auth/login', method: 'post' },
  //         logout: { url: '/api/auth/logout', method: 'post' },
  //         user: false
  //       }
  //     }
  //   },
  //   redirect: {
  //     login: '/login',
  //     logout: '/',
  //     callback: '/login',
  //     home: '/admin'
  //   },
  //   watchLoggedIn: false,
  //   rewriteRedirects: false
  // },

  // Toast module configuration
  toast: {
    position: 'top-right',
    duration: 3000,
    keepOnHover: true,
    singleton: true,
    theme: 'outline',
    iconPack: 'fontawesome'
  },

  // Router configuration
  router: {
    middleware: ['auth-check']
  },

  // Server middleware
  serverMiddleware: [
    { path: '/api', handler: '~/api/index.js' }
  ],

  // Build Configuration
  build: {
    extractCSS: !isDev,
    parallel: false,
    cache: !isDev,
    terser: {
      parallel: false
    },
    // 优化构建
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all'
          },
          lottie: {
            test: /[\\/]node_modules[\\/]lottie-web[\\/]/,
            name: 'lottie',
            chunks: 'all'
          }
        }
      }
    },
    
    // 扩展webpack配置
    extend(config, { isDev, isClient }) {
      // 开发环境下的配置（已移除编译期 ESLint）
      
      // 处理Lottie动画文件
      config.module.rules.push({
        test: /\.json$/,
        include: /assets\/animations/,
        type: 'javascript/auto'
      })
    },
    
    // PostCSS配置
    postcss: {
      plugins: { 
        tailwindcss: {}, 
        autoprefixer: {} 
      },
      preset: { 
        stage: 1 
      }
    }
  },

  // 环境变量
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
    BASE_URL: process.env.BASE_URL || 'http://localhost:3000',
    WECHAT_APP_ID: process.env.WECHAT_APP_ID || '',
    WECOM_CORP_ID: process.env.WECOM_CORP_ID || ''
  },

  // 生成配置
  generate: {
    // 预渲染路由
    routes: [
      '/',
      '/card-preview',
      '/privacy-policy',
      '/terms-of-service'
    ],
    
    // 生成配置
    fallback: true,
    exclude: [
      /^\/admin/,
      /^\/api/
    ]
  },

  // PWA配置（暂时禁用以排查SSR问题）
  // pwa: {
  //   meta: {
  //     title: 'WeCard',
  //     author: 'WeCard Team',
  //     description: 'WeCard企业智能名片系统',
  //     theme_color: '#1890FF',
  //     lang: 'zh-CN'
  //   },
  //   manifest: {
  //     name: 'WeCard企业智能名片',
  //     short_name: 'WeCard',
  //     description: 'WeCard企业智能名片系统',
  //     theme_color: '#1890FF',
  //     background_color: '#ffffff',
  //     display: 'standalone',
  //     start_url: '/',
  //     icons: [
  //       {
  //         src: '/icon-192x192.png',
  //         sizes: '192x192',
  //         type: 'image/png'
  //       },
  //       {
  //         src: '/icon-512x512.png',
  //         sizes: '512x512',
  //         type: 'image/png'
  //       }
  //     ]
  //   }
  // },

  // 性能优化
  render: {
    // 启用HTTP/2推送
    http2: {
      push: true,
      pushAssets: (req, res, publicPath, preloadFiles) => {
        return preloadFiles
          .filter(f => f.asType === 'script' && f.file === 'runtime.js')
          .map(f => `<${publicPath}${f.file}>; rel=preload; as=${f.asType}`)
      }
    },
    
    // 资源提示
    resourceHints: !isDev,
    
    // 压缩
    compressor: {
      threshold: 0
    }
  },

  // 加载指示器
  loading: {
    color: '#1890FF',
    height: '3px',
    continuous: true
  },

  // 错误页面
  error: '~/layouts/error.vue'
}