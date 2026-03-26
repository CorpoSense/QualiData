<template>
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
          <li class="nav-item"><a href="#features" class="nav-link">Features</a></li>
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
          <li class="nav-item" v-if="canManageUsers(user)"><router-link class="nav-link" to="/admin/users">Users</router-link></li>
          
          <!-- Notifications -->
          <li class="nav-item">
            <button class="nav-link position-relative" @click="$emit('show-notifications')" style="background: none; border: none; cursor: pointer;">
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
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item text-danger" href="#" @click.prevent="$emit('logout')"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
              </ul>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { canManageUsers } from '@/composables/useUser'

defineProps({
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: null
  },
  unreadCount: {
    type: Number,
    default: 0
  }
})

defineEmits(['show-notifications', 'logout'])
</script>

<style scoped>
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
</style>
