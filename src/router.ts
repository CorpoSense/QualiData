import { createMemoryHistory, createRouter } from 'vue-router'

import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import Projects from '@/views/Projects.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard },
  { path: '/projects', component: Projects },
  { path: '/projects/:id', component: { template: '<div class="section"><h1 class="title">Project Details</h1><p>Coming soon...</p></div>' } },
  { path: '/assistant', component: { template: '<div class="section"><h1 class="title">AI Assistant</h1><p>Coming soon...</p></div>' } },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

// Navigation guard to check auth
router.beforeEach((to, from, next) => {
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
