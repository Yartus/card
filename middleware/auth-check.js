/**
 * 认证检查中间件
 * 处理不同页面的认证需求
 */

export default function ({ route, redirect, $auth }) {
  // 公开页面路径
  const publicPaths = [
    '/',
    '/card-preview',
    '/privacy-policy',
    '/terms-of-service'
  ]
  
  // 素材库公开页面（动态路由）
  const isAssetLibraryPublic = /^\/assets\/[^/]+$/.test(route.path)
  
  // 名片公开页面（动态路由）
  const isCardPublic = /^\/card\/[^/]+\/[^/]+$/.test(route.path)
  
  // 卡片预览公开页面（动态路由）
  const isCardPreviewPublic = /^\/card-preview\/[^/]+\/[^/]+$/.test(route.path)
  
  // 管理页面路径
  const isAdminPath = route.path.startsWith('/admin')
  
  // 登录页面
  const isLoginPath = route.path === '/login'
  
  // 如果是公开页面，直接允许访问
  if (publicPaths.includes(route.path) || isAssetLibraryPublic || isCardPublic || isCardPreviewPublic) {
    return
  }
  
  // 如果是登录页面且用户已登录，重定向到管理后台
  if (isLoginPath && $auth.loggedIn) {
    return redirect('/admin')
  }
  
  // 如果是管理页面且用户未登录，重定向到登录页
  if (isAdminPath && !$auth.loggedIn) {
    return redirect('/login')
  }
}
