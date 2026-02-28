import { createMemoryHistory, createRouter } from 'vue-router'

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

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard },
  { path: '/projects', component: Projects },
  { path: '/projects/:id', component: ProjectDetail },
  { path: '/projects/:id/dataset/:datasetId', component: DataViewer },
  { path: '/assistant', component: Assistant },
  { path: '/forgot-password', component: ForgotPassword },
  { path: '/reset-password', component: ResetPassword },
  { path: '/oauth/callback/:provider', component: OAuthCallback },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

// Navigation guard to check auth
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  
  if (!token && to.path !== '/' && to.path !== '/login') {
    next('/login')
  } else if (token && to.path === '/login') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
