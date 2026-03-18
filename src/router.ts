import { createWebHistory, createRouter } from 'vue-router'
import { getApiUrl } from '@/utils/api'
import { isAdmin } from '@/composables/useUser'
import { useDebugStore } from '@/stores/debug'

import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import Projects from '@/views/Projects.vue'
import ProjectDetail from '@/views/ProjectDetail.vue'
import DataViewer from '@/views/DataViewer.vue'
import Assistant from '@/views/Assistant.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import ResetPassword from '@/views/ResetPassword.vue'
import OAuthCallback from '@/views/OAuthCallback.vue'
import Pricing from '@/views/Pricing.vue'
import Profile from '@/views/Profile.vue'
import Users from '@/views/admin/Users.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/pricing', component: Pricing },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/projects', component: Projects, meta: { requiresAuth: true } },
  { path: '/projects/:id', component: ProjectDetail, meta: { requiresAuth: true } },
  { path: '/projects/:id/dataset/:datasetId', component: DataViewer, meta: { requiresAuth: true } },
  { path: '/assistant', component: Assistant, meta: { requiresAuth: true } },
  { path: '/forgot-password', component: ForgotPassword },
  { path: '/reset-password', component: ResetPassword },
  { path: '/oauth/callback/:provider', component: OAuthCallback },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/agents', component: () => import('@/views/AgentManager.vue'), meta: { requiresAuth: true } },
  { path: '/admin/users', component: Users, meta: { requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard to check auth
router.beforeEach(async (to, _from, next) => {
  const debugStore = useDebugStore()
  
  // Auto-login in debug mode if no token
  if (debugStore.isDebug && !localStorage.getItem('token') && to.path !== '/debug-login') {
    try {
      const res = await fetch(`${getApiUrl()}/api/auth/debug-login`, { method: 'POST' })
      if (res.ok) {
        const data = await res.json()
        localStorage.setItem('token', data.access_token)
      }
    } catch (e) {
      console.error('Debug login failed:', e)
    }
  }
  
  // Auto-redirect to dashboard in debug mode if on login page
  if (debugStore.isDebug && to.path === '/login') {
    next('/dashboard')
    return
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const token = localStorage.getItem('token')
  
  if (requiresAuth && !token) {
    next('/login')
  } else if (token && to.path === '/login') {
    next('/dashboard')
  } else if (requiresAdmin && token) {
    // Check if user is admin
    try {
      const res = await fetch(`${getApiUrl()}/api/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const user = await res.json()
        if (isAdmin(user)) {
          next()
        } else {
          next('/dashboard')
        }
      } else {
        next('/dashboard')
      }
    } catch (e) {
      next('/dashboard')
    }
  } else {
    next()
  }
})

export default router
