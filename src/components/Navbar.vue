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
      <li class="nav-item">
        <a href="#" class="nav-link">Home</a>
        <!-- <router-link class="nav-link" to="/">Home</router-link> -->
      </li>
      <li class="nav-item"><a href="#features" class="nav-link">Features</a></li>
      <li class="nav-item"><a href="#pricing" class="nav-link">Pricing</a></li>
      <li class="nav-item mt-2 mt-lg-0">
        <router-link class="btn btn-primary btn-sm rounded-pill px-4" to="/login">Sign In</router-link>
      </li>
    </ul>

    <!-- Authenticated Nav Links -->
    <ul v-else class="navbar-nav ms-auto align-items-lg-center gap-2 gap-lg-3">
      <li class="nav-item"><router-link class="nav-link" to="/dashboard">Dashboard</router-link></li>

      <!-- Projects Dropdown -->
      <li class="nav-item dropdown projects-dropdown" :class="{ show: projectsOpen }" @mouseenter="onProjectsEnter" @mouseleave="onProjectsLeave">
        <button
          class="nav-link dropdown-toggle no-background"
          :class="{ show: projectsOpen }"
          @click="toggleProjects"
          aria-haspopup="true"
          :aria-expanded="projectsOpen"
        >
          <i class="bi bi-folder me-1"></i>Projects
        </button>
        <ul class="dropdown-menu projects-dropdown-menu" :class="{ show: projectsOpen }">
          <li>
            <router-link class="dropdown-item" to="/projects" @click="closeProjects">
              <i class="bi bi-folder2-open me-2"></i>All Projects
            </router-link>
          </li>
          <li><hr class="dropdown-divider"></li>

          <!-- Loading state -->
          <li v-if="navLoading" class="dropdown-item-text text-center py-2">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </li>

          <!-- Empty state -->
          <li v-else-if="navProjects.length === 0" class="dropdown-item-text">
            <span class="dropdown-text-muted">No projects yet</span>
          </li>

          <!-- Projects list -->
          <template v-else>
            <li
              v-for="project in navProjects"
              :key="project.id"
              class="dropdown-submenu"
              @mouseenter="onSubmenuEnter(project.id)"
              @mouseleave="onSubmenuLeave"
            >
              <router-link
                class="dropdown-item dropdown-item-wrapper d-flex align-items-center justify-content-between"
                :to="`/projects/${project.id}`"
                @click="closeProjects"
              >
                <span class="text-truncate" style="max-width: 160px;">
                  <i class="bi bi-folder2 me-2"></i>{{ project.name }}
                </span>
                <span class="badge bg-light text-dark ms-1">{{ project.datasets_count || 0 }}</span>
              </router-link>

              <!-- Submenu for datasets -->
              <ul class="dropdown-menu submenu" :class="{ show: activeSubmenu === project.id }">
                <li>
                  <router-link
                    class="dropdown-item"
                    :to="`/projects/${project.id}`"
                    @click="closeProjects"
                  >
                    <i class="bi bi-folder2-open me-2"></i>Project Details
                  </router-link>
                </li>
                <li v-if="project.datasets_count > 0"><hr class="dropdown-divider"></li>

                <!-- Datasets loading -->
                <li v-if="submenuLoading === project.id" class="dropdown-item-text text-center py-2">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </li>

                <!-- Datasets list -->
                <template v-else-if="(projectDatasets[project.id] || []).length > 0">
                  <li v-for="ds in projectDatasets[project.id]" :key="ds.id">
                    <router-link
                      class="dropdown-item"
                      :to="`/projects/${project.id}/dataset/${ds.id}`"
                      @click="closeProjects"
                    >
                      <i class="bi bi-table me-2"></i>
                      <span class="text-truncate" style="max-width: 180px; display: inline-block; vertical-align: middle;">{{ ds.name }}</span>
                    </router-link>
                  </li>
                </template>

                <!-- No datasets -->
                <li v-else-if="submenuLoading !== project.id" class="dropdown-item-text">
                  <span class="dropdown-text-muted">No datasets</span>
                </li>
              </ul>
            </li>
          </template>
        </ul>
      </li>

      <li class="nav-item"><router-link class="nav-link" to="/agents">AI Agents</router-link></li>
      <li class="nav-item" v-if="canManageUsers(user)"><router-link class="nav-link" to="/admin/users">Users</router-link></li>

      <!-- Notifications -->
      <li class="nav-item">
        <button class="nav-link position-relative no-background" @click="$emit('show-notifications')">
          <i class="bi bi-bell fs-5"></i>
          <span v-if="unreadCount > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 10px;">
            {{ unreadCount > 9 ? '9+' : unreadCount }}
          </span>
        </button>
      </li>

      <!-- User Dropdown -->
      <li class="nav-item">
        <div class="dropdown">
          <button class="nav-link d-flex align-items-center gap-2 dropdown-toggle no-background" data-bs-toggle="dropdown">
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
import { ref, watch } from 'vue'
import { canManageUsers } from '@/composables/useUser'
import { useProjectsNav } from '@/composables/useProjectsNav'

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

const { projects: navProjects, loading: navLoading, fetchProjects, fetchDatasets } = useProjectsNav()

const projectsOpen = ref(false)
const activeSubmenu = ref(null)
const submenuLoading = ref(null)
const projectDatasets = ref({})

let hoverTimeout = null

function toggleProjects() {
  projectsOpen.value = !projectsOpen.value
  if (projectsOpen.value) {
    fetchProjects()
  }
}

function closeProjects() {
  projectsOpen.value = false
  activeSubmenu.value = null
}

function onProjectsEnter() {
  clearTimeout(hoverTimeout)
}

function onProjectsLeave() {
  hoverTimeout = setTimeout(() => {
    closeProjects()
  }, 150)
}

async function onSubmenuEnter(projectId) {
  activeSubmenu.value = projectId
  if (!projectDatasets.value[projectId]) {
    submenuLoading.value = projectId
    const datasets = await fetchDatasets(projectId)
    projectDatasets.value[projectId] = datasets
    submenuLoading.value = null
  }
}

function onSubmenuLeave() {
  activeSubmenu.value = null
}
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

.no-background {
  background: none;
  border: none;
  cursor: pointer;
}

/* Projects dropdown */
.projects-dropdown-menu {
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  padding: 0.5rem 0;
  overflow: visible;
}

.projects-dropdown-menu .dropdown-item {
  padding: 0.45rem 1rem;
  font-size: 0.875rem;
  border-radius: 4px;
  margin: 1px 0.375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.projects-dropdown-menu .dropdown-item:hover,
.projects-dropdown-menu .dropdown-item:focus {
  background-color: rgba(79, 70, 229, 0.06);
  color: var(--primary-color);
}

.projects-dropdown-menu .dropdown-item.router-link-active {
  background-color: rgba(79, 70, 229, 0.1);
  color: var(--primary-color);
  font-weight: 600;
}

.dropdown-text-muted {
  color: #94a3b8;
  font-size: 0.8125rem;
  padding: 0.5rem 1rem;
  display: block;
}

/* Submenu */
.dropdown-submenu {
  position: relative;
}

.dropdown-submenu > .dropdown-menu.submenu {
  display: none;
  position: absolute;
  left: 100%;
  top: -6px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  padding: 0.5rem 0;
  z-index: 1050;
  overflow: visible;
}

.dropdown-submenu > .dropdown-menu.submenu.show {
  display: block;
}

.dropdown-submenu > .dropdown-menu.submenu .dropdown-item {
  padding: 0.45rem 1rem;
  font-size: 0.8125rem;
  border-radius: 4px;
  margin: 1px 0.375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-submenu > .dropdown-menu.submenu .dropdown-item:hover,
.dropdown-submenu > .dropdown-menu.submenu .dropdown-item:focus {
  background-color: rgba(79, 70, 229, 0.06);
  color: var(--primary-color);
}

.dropdown-submenu > .dropdown-menu.submenu .dropdown-item.router-link-active {
  background-color: rgba(79, 70, 229, 0.1);
  color: var(--primary-color);
  font-weight: 600;
}

/* Badge styling */
.projects-dropdown-menu .badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.2em 0.5em;
}

/* Responsive: stack submenus on small screens */
@media (max-width: 991.98px) {
  .dropdown-submenu > .dropdown-menu.submenu {
    position: static;
    left: auto;
    top: auto;
    box-shadow: none;
    border: none;
    margin-left: 1rem;
    padding-left: 0.5rem;
    border-left: 2px solid rgba(79, 70, 229, 0.2);
    min-width: 0;
  }

  .projects-dropdown-menu {
    border: none;
    box-shadow: none;
    border-radius: 0;
    padding: 0;
  }

  .projects-dropdown-menu .dropdown-item {
    margin: 0;
    border-radius: 0;
  }
}
</style>
