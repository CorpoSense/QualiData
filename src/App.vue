<template>
  <div id="app">
    <BOrchestrator />
    
    <!-- Navbar -->
    <Navbar
      :is-authenticated="isAuthenticated"
      :user="currentUser"
      :unread-count="unreadCount"
      @show-notifications="showNotifications = true"
      @logout="logout"
    />

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

import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getApiUrl } from '@/utils/api'
import { canManageUsers, currentUser } from '@/composables/useUser'
import { BOrchestrator } from 'bootstrap-vue-next'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()

const isAuthenticated = ref(false)
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

// Watch for changes in currentUser to update isAuthenticated
watch(currentUser, (newUser) => {
  isAuthenticated.value = !!newUser
})

async function fetchUser() {
  try {
    const res = await fetch(`${apiUrl}/api/auth/me`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      currentUser.value = await res.json()
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
  currentUser.value = null
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
