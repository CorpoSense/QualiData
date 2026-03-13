<template>
  <div class="dashboard">
    <!-- Welcome Section -->
    <div class="welcome-section mb-5">
      <h1 class="h3 fw-bold">Welcome back!</h1>
      <p class="text-secondary">Here's what's happening with your data today.</p>
    </div>

    <!-- Stats Cards -->
    <div class="row g-4 mb-5">
      <div class="col-6 col-lg-3">
        <div class="stat-card h-100">
          <div class="stat-icon" style="background: rgba(79, 70, 229, 0.1);">
            <i class="bi bi-folder text-primary"></i>
          </div>
          <div class="stat-content">
            <p class="text-secondary small mb-1">Total Projects</p>
            <p class="h3 fw-bold mb-0">{{ stats.projects }}</p>
          </div>
        </div>
      </div>
      <div class="col-6 col-lg-3">
        <div class="stat-card h-100">
          <div class="stat-icon" style="background: rgba(34, 197, 94, 0.1);">
            <i class="bi bi-database text-success"></i>
          </div>
          <div class="stat-content">
            <p class="text-secondary small mb-1">Total Datasets</p>
            <p class="h3 fw-bold mb-0">{{ stats.datasets }}</p>
          </div>
        </div>
      </div>
      <div class="col-6 col-lg-3">
        <div class="stat-card h-100">
          <div class="stat-icon" style="background: rgba(249, 115, 22, 0.1);">
            <i class="bi bi-table text-warning"></i>
          </div>
          <div class="stat-content">
            <p class="text-secondary small mb-1">Rows Processed</p>
            <p class="h3 fw-bold mb-0">{{ formatNumber(stats.rows) }}</p>
          </div>
        </div>
      </div>
      <div class="col-6 col-lg-3">
        <div class="stat-card h-100">
          <div class="stat-icon" style="background: rgba(236, 72, 153, 0.1);">
            <i class="bi bi-hdd text-danger"></i>
          </div>
          <div class="stat-content">
            <p class="text-secondary small mb-1">Storage Used</p>
            <p class="h3 fw-bold mb-0">{{ formatBytes(stats.storage) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row g-4 mb-5">
      <div class="col-12">
        <div class="quick-actions-card">
          <h2 class="h5 fw-bold mb-4">Quick Actions</h2>
          <div class="d-flex flex-wrap gap-3">
            <BButton variant="primary" class="rounded-pill px-4" @click="$router.push('/projects')">
              <i class="bi bi-plus-lg me-2"></i>New Project
            </BButton>
            <BButton variant="outline-primary" class="rounded-pill px-4" @click="showImportModal = true">
              <i class="bi bi-upload me-2"></i>Import Data
            </BButton>
            <BButton variant="outline-primary" class="rounded-pill px-4" @click="$router.push('/assistant')">
              <i class="bi bi-robot me-2"></i>AI Assistant
            </BButton>
          </div>
        </div>
      </div>
    </div>

    <!-- API Usage & Recent Projects -->
    <div class="row g-4">
      <div class="col-lg-4">
        <div class="api-card h-100">
          <h2 class="h5 fw-bold mb-4">API Usage</h2>
          <RateLimitStatus />
        </div>
      </div>
      <div class="col-lg-8">
        <div class="recent-projects-card">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="h5 fw-bold mb-0">Recent Projects</h2>
            <router-link to="/projects" class="small">View All <i class="bi bi-arrow-right"></i></router-link>
          </div>

          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-else-if="projects.length === 0" class="text-center py-5">
            <i class="bi bi-folder-plus text-secondary" style="font-size: 3rem;"></i>
            <p class="text-secondary mt-3">No projects yet</p>
            <BButton variant="primary" class="mt-2 rounded-pill" @click="$router.push('/projects')">
              Create Your First Project
            </BButton>
          </div>

          <div v-else class="projects-list">
            <div 
              v-for="project in projects.slice(0, 5)" 
              :key="project.id"
              class="project-item"
              @click="$router.push(`/projects/${project.id}`)"
            >
              <div class="d-flex align-items-center gap-3">
                <div class="project-icon">
                  <i class="bi bi-folder-fill text-warning"></i>
                </div>
                <div class="flex-grow-1">
                  <h6 class="fw-bold mb-1">{{ project.name }}</h6>
                  <p class="small text-secondary mb-0">{{ project.datasets_count || 0 }} datasets · {{ formatDate(project.created_at) }}</p>
                </div>
                <i class="bi bi-chevron-right text-secondary"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getApiUrl } from '@/utils/api'
import RateLimitStatus from '@/components/RateLimitStatus.vue'

const apiUrl = getApiUrl()
const stats = ref({ projects: 0, datasets: 0, rows: 0, storage: 0 })
const projects = ref([])
const loading = ref(true)
const showImportModal = ref(false)

onMounted(async () => {
  await fetchStats()
  await fetchProjects()
})

async function fetchStats() {
  try {
    const res = await fetch(`${apiUrl}/api/projects`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      stats.value.projects = data.projects?.length || 0
      let totalDatasets = 0
      let totalRows = 0
      let totalStorage = 0
      for (const p of data.projects || []) {
        totalDatasets += p.datasets_count || 0
        totalRows += p.total_rows || 0
        totalStorage += p.storage_bytes || 0
      }
      stats.value.datasets = totalDatasets
      stats.value.rows = totalRows
      stats.value.storage = totalStorage
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchProjects() {
  try {
    const res = await fetch(`${apiUrl}/api/projects`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      projects.value = data.projects || []
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.welcome-section {
  padding: 1.5rem 0;
}

/* Stat Cards */
.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

/* Quick Actions */
.quick-actions-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* API Card */
.api-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Recent Projects */
.recent-projects-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.project-item {
  padding: 1rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.project-item:hover {
  background: rgba(79, 70, 229, 0.05);
  border-color: rgba(79, 70, 229, 0.1);
}

.project-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(249, 192, 11, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}
</style>
