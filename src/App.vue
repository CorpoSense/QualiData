<template>
  <div id="app">
    <BOrchestrator />
    
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg fixed-top" :class="isAuthenticated ? 'navbar-auth' : 'navbar-public'">
      <div class="container">
        <router-link class="navbar-brand fw-bold d-flex align-items-center gap-2" to="/">
          <div class="brand-icon rounded d-flex align-items-center justify-content-center">
            <i class="bi bi-stars text-white"></i>
          </div>
          <span class="d-none d-sm-inline">MasterDataCleaner</span>
        </router-link>
        
        <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <!-- Public Nav Links -->
          <ul v-if="!isAuthenticated" class="navbar-nav ms-auto align-items-lg-center gap-2 gap-lg-4">
            <li class="nav-item"><router-link class="nav-link" to="/">Home</router-link></li>
            <li class="nav-item"><a href="#pricing" class="nav-link">Pricing</a></li>
            <li class="nav-item mt-2 mt-lg-0">
              <router-link class="btn btn-primary btn-sm rounded-pill px-4" to="/login">Sign In</router-link>
            </li>
          </ul>
          
          <!-- Authenticated Nav Links -->
          <ul v-else class="navbar-nav ms-auto align-items-lg-center gap-2 gap-lg-3">
            <li class="nav-item"><router-link class="nav-link" to="/dashboard">Dashboard</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/projects">Projects</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/agents">AI Agents</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/agents">AI Agents</router-link></li>
            <li class="nav-item" v-if="canManageUsers(user)"><router-link class="nav-link" to="/admin/users">Users</router-link></li>
            
            <!-- Notifications -->
            <li class="nav-item">
              <button class="nav-link position-relative" @click="showNotifications = true" style="background: none; border: none; cursor: pointer;">
                <i class="bi bi-bell fs-5"></i>
                <span v-if="unreadCount > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 10px;">
                  {{ unreadCount > 9 ? '9+' : unreadCount }}
                </span>
              </button>
            </li>
            
            <!-- User Dropdown -->
            <li class="nav-item">
              <div class="dropdown">
                <button class="nav-link d-flex align-items-center gap-2 dropdown-toggle" data-bs-toggle="dropdown" style="background: none; border: none; cursor: pointer;">
                  <div class="user-avatar rounded-circle d-flex align-items-center justify-content-center">
                    <i class="bi bi-person text-white fs-6"></i>
                  </div>
                  <span class="d-none d-lg-inline text-truncate" style="max-width: 150px;">{{ user?.email }}</span>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li><router-link class="dropdown-item" to="/profile"><i class="bi bi-person me-2"></i>Profile</router-link></li>
                  <li v-if="canManageUsers(user)"><router-link class="dropdown-item" to="/admin/users"><i class="bi bi-people me-2"></i>User Management</router-link></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item text-danger" href="#" @click.prevent="logout"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
                </ul>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="main-content" :class="{ 'with-navbar': true }">
      <div class="container py-4">
        <router-view />
      </div>
    </div>

    <!-- Notifications Offcanvas -->
    <div class="offcanvas offcanvas-end" :class="{ show: showNotifications }" tabindex="-1" v-if="showNotifications">
      <div class="offcanvas-header">
        <h5 class="offcanvas-title">Notifications</h5>
        <button type="button" class="btn-close" @click="showNotifications = false"></button>
      </div>
      <div class="offcanvas-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <button class="btn btn-link btn-sm p-0" @click="markAllRead">Mark all read</button>
        </div>
        <div v-if="notifications.length === 0" class="text-center text-muted py-4">
          No notifications
        </div>
        <div v-else>
          <div 
            v-for="notif in notifications" 
            :key="notif.id"
            class="alert mb-3"
            :class="`alert-${getNotificationType(notif.type)}`"
          >
            <button type="button" class="btn-close" @click="deleteNotification(notif.id)"></button>
            <strong>{{ notif.title }}</strong>
            <p class="mb-0 small">{{ notif.message }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Backdrop for offcanvas -->
    <div v-if="showNotifications" class="position-fixed top-0 start-0 w-100 h-100" style="z-index: 1040; background: rgba(0,0,0,0.5);" @click="showNotifications = false"></div>
  </div>
  
  <!-- Toast Notifications -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 9999">
    <div v-for="toast in toasts" :key="toast.id" class="toast show" role="alert">
      <div :class="'alert-' + toast.variant" class="alert mb-1 py-2" role="alert">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { useToast } from './composables/useToast'
const { toasts } = useToast()

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getApiUrl } from '@/utils/api'
import { canManageUsers } from '@/composables/useUser'
import { BOrchestrator } from 'bootstrap-vue-next'

const router = useRouter()

const isAuthenticated = ref(false)
const user = ref(null)
const notifications = ref([])
const unreadCount = ref(0)
const showNotifications = ref(false)

const apiUrl = getApiUrl()

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    isAuthenticated.value = true
    await fetchUser()
    await fetchNotifications()
  }
})

async function fetchUser() {
  try {
    const res = await fetch(`${apiUrl}/api/auth/me`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      user.value = await res.json()
    } else {
      logout()
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchNotifications() {
  try {
    const res = await fetch(`${apiUrl}/api/notifications`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      notifications.value = data.notifications
      unreadCount.value = data.unread_count
    }
  } catch (e) {
    console.error(e)
  }
}

function logout() {
  localStorage.removeItem('token')
  isAuthenticated.value = false
  user.value = null
  router.push('/login')
}

function getNotificationType(type) {
  const map = { 'info': 'info', 'success': 'success', 'warning': 'warning', 'error': 'danger' }
  return map[type] || 'info'
}

async function markAllRead() {
  try {
    await fetch(`${apiUrl}/api/notifications/read-all`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    await fetchNotifications()
  } catch (e) {
    console.error(e)
  }
}

async function deleteNotification(id) {
  try {
    await fetch(`${apiUrl}/api/notifications/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    await fetchNotifications()
  } catch (e) {
    console.error(e)
  }
}
</script>

<style>
/* Navbar Styles */
.navbar {
  padding: 0.75rem 0;
  transition: all 0.3s ease;
}

.navbar-public {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.navbar-auth {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.brand-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

.navbar .nav-link {
  font-weight: 500;
  color: #475569 !important;
  transition: color 0.2s ease;
  padding: 0.5rem 1rem !important;
}

.navbar .nav-link:hover,
.navbar .nav-link.router-link-active {
  color: var(--primary-color) !important;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

/* Main Content */
.main-content {
  padding-top: 80px;
  min-height: 100vh;
  background: var(--bg-color);
}

.main-content.with-navbar {
  padding-top: 70px;
}

body {
  background-color: var(--bg-color);
}
</style>
