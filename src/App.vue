<template>
  <div id="app">
    <!-- Navbar -->
    <b-navbar v-if="isAuthenticated" type="is-dark" :fixed-top="true">
      <template #brand>
        <b-navbar-item tag="router-link" :to="{ path: '/' }">
          <span class="has-text-weight-bold is-size-5">MasterDataCleaner</span>
        </b-navbar-item>
      </template>

      <template #start>
        <b-navbar-item tag="router-link" :to="{ path: '/dashboard' }">
          Dashboard
        </b-navbar-item>
        <b-navbar-item tag="router-link" :to="{ path: '/projects' }">
          Projects
        </b-navbar-item>
      </template>

      <template #end>
        <b-navbar-item tag="div">
          <div class="buttons">
            <b-button size="is-small" @click="showNotifications = true">
              <b-icon icon="bell"></b-icon>
              <span v-if="unreadCount > 0" class="tag is-danger is-rounded ml-1">{{ unreadCount }}</span>
            </b-button>
            <b-dropdown position="is-bottom-right">
              <a class="navbar-item" slot="trigger">
                <b-icon icon="account"></b-icon>
                <span>{{ user?.email }}</span>
              </a>
              <b-dropdown-item @click="logout">Logout</b-dropdown-item>
            </b-dropdown>
          </div>
        </b-navbar-item>
      </template>
    </b-navbar>

    <!-- Main Content -->
    <section class="section" :class="{ 'mt-6': isAuthenticated }">
      <router-view />
    </section>

    <!-- Notifications Panel -->
    <b-sidebar v-model="showNotifications" position="fixed" type="is-dark" :fullheight="true" :overlay="true">
      <div class="p-4">
        <div class="is-flex is-justify-content-space-between is-align-items-center mb-4">
          <h3 class="title is-4">Notifications</h3>
          <b-button size="is-small" @click="markAllRead">Mark all read</b-button>
        </div>
        <div v-if="notifications.length === 0" class="has-text-centered has-text-grey">
          No notifications
        </div>
        <div v-else>
          <div 
            v-for="notif in notifications" 
            :key="notif.id"
            class="notification mb-3"
            :class="getNotificationClass(notif.type)"
          >
            <button class="delete" @click="deleteNotification(notif.id)"></button>
            <strong>{{ notif.title }}</strong>
            <p>{{ notif.message }}</p>
          </div>
        </div>
      </div>
    </b-sidebar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isAuthenticated = ref(false)
const user = ref(null)
const notifications = ref([])
const unreadCount = ref(0)
const showNotifications = ref(false)

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

function getNotificationClass(type) {
  return {
    'is-info': type === 'info',
    'is-success': type === 'success',
    'is-warning': type === 'warning',
    'is-danger': type === 'error'
  }
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
.mt-6 {
  margin-top: 3rem !important;
}
</style>
