<template>
  <div id="app">
    <!-- Public Navbar (when not authenticated) -->
    <nav v-if="!isAuthenticated" class="navbar navbar-light bg-white border-bottom mb-4">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">MasterDataCleaner</router-link>
        <div class="navbar-nav ms-auto flex-row gap-2">
          <router-link class="nav-link" to="/">Home</router-link>
          <router-link class="nav-link" to="/pricing">Pricing</router-link>
          <router-link class="btn btn-primary btn-sm" to="/login">Sign In</router-link>
        </div>
      </div>
    </nav>

    <!-- Authenticated Navbar -->
    <nav v-if="isAuthenticated" class="navbar navbar-dark bg-dark fixed-top">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">MasterDataCleaner</router-link>
        <div class="navbar-nav flex-row gap-3">
          <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
          <router-link class="nav-link" to="/projects">Projects</router-link>
          <router-link v-if="user?.role === 'admin'" class="nav-link" to="/admin/users">User Management</router-link>
        </div>
        <div class="navbar-nav flex-row gap-2 ms-auto align-items-center">
          <button class="btn btn-outline-light btn-sm position-relative" @click="showNotifications = true">
            <i class="bi bi-bell"></i>
            <span v-if="unreadCount > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              {{ unreadCount }}
            </span>
          </button>
          <div class="dropdown">
            <button class="btn btn-outline-light btn-sm dropdown-toggle" data-bs-toggle="dropdown">
              <i class="bi bi-person me-1"></i>
              {{ user?.email }}
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
              <li><router-link v-if="user?.role === 'admin'" class="dropdown-item" to="/admin/users">User Management</router-link></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item" href="#" @click.prevent="logout">Logout</a></li>
            </ul>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="container mt-4" :class="{ 'pt-5': isAuthenticated }">
      <router-view />
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
    <div v-if="showNotifications" class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50" style="z-index: 1040;" @click="showNotifications = false"></div>
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
body {
  background-color: #f8f9fa;
}
</style>
