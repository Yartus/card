import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _7db8e91b = () => interopDefault(import('../pages/admin/index.vue' /* webpackChunkName: "pages/admin/index" */))
const _2276005c = () => interopDefault(import('../pages/card-preview.vue' /* webpackChunkName: "pages/card-preview" */))
const _1812646c = () => interopDefault(import('../pages/card-preview/_tenantId/_memberId.vue' /* webpackChunkName: "pages/card-preview/_tenantId/_memberId" */))
const _796883b2 = () => interopDefault(import('../pages/login.vue' /* webpackChunkName: "pages/login" */))
const _fead49c4 = () => interopDefault(import('../pages/privacy-policy.vue' /* webpackChunkName: "pages/privacy-policy" */))
const _05719a0c = () => interopDefault(import('../pages/terms-of-service.vue' /* webpackChunkName: "pages/terms-of-service" */))
const _e10e87ec = () => interopDefault(import('../pages/admin/assets.vue' /* webpackChunkName: "pages/admin/assets" */))
const _fc36c388 = () => interopDefault(import('../pages/admin/frameworks.vue' /* webpackChunkName: "pages/admin/frameworks" */))
const _454afb0e = () => interopDefault(import('../pages/admin/test-center.vue' /* webpackChunkName: "pages/admin/test-center" */))
const _ef842e9a = () => interopDefault(import('../pages/wecom/card.vue' /* webpackChunkName: "pages/wecom/card" */))
const _0c0fefc8 = () => interopDefault(import('../pages/wecom/install.vue' /* webpackChunkName: "pages/wecom/install" */))
const _1f16eac6 = () => interopDefault(import('../pages/wecom/settings.vue' /* webpackChunkName: "pages/wecom/settings" */))
const _4f06b882 = () => interopDefault(import('../pages/wecom/workspace.vue' /* webpackChunkName: "pages/wecom/workspace" */))
const _a07e3eca = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))
const _18d452dc = () => interopDefault(import('../pages/admin/tenant/_id.vue' /* webpackChunkName: "pages/admin/tenant/_id" */))
const _3063a226 = () => interopDefault(import('../pages/assets/_tenant_id.vue' /* webpackChunkName: "pages/assets/_tenant_id" */))

const emptyFn = () => {}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: '/',
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
    path: "/admin",
    component: _7db8e91b,
    name: "admin"
  }, {
    path: "/card-preview",
    component: _2276005c,
    name: "card-preview",
    children: [{
      path: ":tenantId?/:memberId?",
      component: _1812646c,
      name: "card-preview-tenantId-memberId"
    }]
  }, {
    path: "/login",
    component: _796883b2,
    name: "login"
  }, {
    path: "/privacy-policy",
    component: _fead49c4,
    name: "privacy-policy"
  }, {
    path: "/terms-of-service",
    component: _05719a0c,
    name: "terms-of-service"
  }, {
    path: "/admin/assets",
    component: _e10e87ec,
    name: "admin-assets"
  }, {
    path: "/admin/frameworks",
    component: _fc36c388,
    name: "admin-frameworks"
  }, {
    path: "/admin/test-center",
    component: _454afb0e,
    name: "admin-test-center"
  }, {
    path: "/wecom/card",
    component: _ef842e9a,
    name: "wecom-card"
  }, {
    path: "/wecom/install",
    component: _0c0fefc8,
    name: "wecom-install"
  }, {
    path: "/wecom/settings",
    component: _1f16eac6,
    name: "wecom-settings"
  }, {
    path: "/wecom/workspace",
    component: _4f06b882,
    name: "wecom-workspace"
  }, {
    path: "/",
    component: _a07e3eca,
    name: "index"
  }, {
    path: "/admin/tenant/:id?",
    component: _18d452dc,
    name: "admin-tenant-id"
  }, {
    path: "/assets/:tenant_id?",
    component: _3063a226,
    name: "assets-tenant_id"
  }],

  fallback: false
}

export function createRouter (ssrContext, config) {
  const base = (config._app && config._app.basePath) || routerOptions.base
  const router = new Router({ ...routerOptions, base  })

  // TODO: remove in Nuxt 3
  const originalPush = router.push
  router.push = function push (location, onComplete = emptyFn, onAbort) {
    return originalPush.call(this, location, onComplete, onAbort)
  }

  const resolve = router.resolve.bind(router)
  router.resolve = (to, current, append) => {
    if (typeof to === 'string') {
      to = normalizeURL(to)
    }
    return resolve(to, current, append)
  }

  return router
}
