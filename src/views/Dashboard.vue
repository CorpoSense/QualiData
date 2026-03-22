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
            <BButton variant="outline-primary" class="rounded-pill px-4" @click="importData">
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
          <h2 class="h5 fw-bold mb-4">Operation Stats</h2>
          <div v-if="opStats" class="row g-2">
            <div class="col-6">
              <div class="text-center p-2 bg-light rounded">
                <div class="h4 fw-bold text-primary mb-0">{{ opStats.total }}</div>
                <small class="text-muted">Total Ops</small>
              </div>
            </div>
            <div class="col-6">
              <div class="text-center p-2 bg-light rounded">
                <div class="h4 fw-bold text-success mb-0">{{ opStats.ai_operations }}</div>
                <small class="text-muted">AI Ops</small>
              </div>
            </div>
            <div class="col-6">
              <div class="text-center p-2 bg-light rounded">
                <div class="h4 fw-bold mb-0">{{ opStats.active }}</div>
                <small class="text-muted">Active</small>
              </div>
            </div>
            <div class="col-6">
              <div class="text-center p-2 bg-light rounded">
                <div class="h4 fw-bold text-secondary mb-0">{{ opStats.undone }}</div>
                <small class="text-muted">Undone</small>
              </div>
            </div>
          </div>
          <div v-if="opStats?.top_types?.length" class="mt-3">
            <small class="text-muted fw-bold">Most Used:</small>
            <div v-for="t in opStats.top_types" :key="t.type" class="d-flex justify-content-between small mt-1">
              <span>{{ formatOpType(t.type) }}</span>
              <span class="badge bg-light text-dark">{{ t.count }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-8">
        <!-- Recent Projects -->
        <div class="recent-projects-card mb-4">
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

        <!-- Recent Operations -->
        <div class="recent-operations-card">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="h5 fw-bold mb-0">Recent Operations</h2>
            <span v-if="operations.length > 0" class="small text-muted">{{ operations.length }} operations</span>
          </div>

          <div v-if="operationsLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-else-if="operations.length === 0" class="text-center py-5">
            <i class="bi bi-clock-history text-secondary" style="font-size: 3rem;"></i>
            <p class="text-secondary mt-3">No operations yet</p>
            <p class="small text-muted">Operations will appear here after you clean or transform data</p>
          </div>

          <div v-else class="operations-list">
            <div 
              v-for="op in operations" 
              :key="op.id"
              class="operation-item"
              @click="goToDataset(op)"
            >
              <div class="d-flex align-items-center gap-3">
                <div class="operation-icon" :class="getOperationClass(op.operation_type)">
                  <i :class="getOperationIcon(op.operation_type)"></i>
                </div>
                <div class="flex-grow-1">
                  <h6 class="fw-bold mb-1">{{ formatOperationType(op.operation_type) }}</h6>
                  <p class="small text-secondary mb-0">{{ op.dataset_name }} · {{ formatDate(op.created_at) }}</p>
                </div>
                <span class="badge" :class="op.is_undone ? 'bg-secondary' : 'bg-success'" style="font-size: 10px;">
                  {{ op.is_undone ? 'Undone' : 'Done' }}
                </span>
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
import { useRouter } from 'vue-router'
import { getApiUrl } from '@/utils/api'

const router = useRouter()
const apiUrl = getApiUrl()
const stats = ref({ projects: 0, datasets: 0, rows: 0, storage: 0 })
const opStats = ref(null)
const projects = ref([])
const operations = ref([])
const loading = ref(true)
const operationsLoading = ref(true)
function importData() {
  if (projects.value.length === 0) {
    router.push('/projects')
    return
  }
  // Projects are fetched from API; find the most recent by created_at
  const sorted = [...projects.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  router.push(`/projects/${sorted[0].id}?import=true`)
}

onMounted(async () => {
  await Promise.all([fetchStats(), fetchOpStats(), fetchProjects(), fetchOperations()])
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

async function fetchOpStats() {
  try {
    const res = await fetch(`${apiUrl}/api/operations/stats`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) opStats.value = await res.json()
  } catch { /* silent */ }
}

function formatOpType(type) {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

async function fetchOperations() {
  try {
    const res = await fetch(`${apiUrl}/api/operations/recent?limit=10`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      operations.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    operationsLoading.value = false
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

function goToDataset(op) {
  if (op.project_id && op.dataset_id) {
    router.push(`/projects/${op.project_id}/dataset/${op.dataset_id}`)
  }
}

function getOperationClass(opType) {
  const classes = {
    'fillna': 'bg-success',
    'drop_duplicates': 'bg-warning',
    'rename': 'bg-info',
    'remove_columns': 'bg-danger',
    'add_column': 'bg-primary',
    'reorder_columns': 'bg-secondary',
    'deduplicate': 'bg-warning',
    'ai_clean': 'bg-primary',
  }
  return classes[opType] || 'bg-secondary'
}

function getOperationIcon(opType) {
  const icons = {
    'fillna': 'bi bi-droplet',
    'drop_duplicates': 'bi bi-copy',
    'rename': 'bi bi-pencil',
    'remove_columns': 'bi bi-trash',
    'add_column': 'bi bi-plus-circle',
    'reorder_columns': 'bi bi-arrow-left-right',
    'deduplicate': 'bi bi-copy',
    'ai_clean': 'bi bi-stars',
  }
  return icons[opType] || 'bi bi-gear'
}

function formatOperationType(opType) {
  if (!opType) return 'Unknown'
  return opType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
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

/* Recent Operations */
.recent-operations-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.operations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.operation-item {
  padding: 1rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.operation-item:hover {
  background: rgba(79, 70, 229, 0.05);
  border-color: rgba(79, 70, 229, 0.1);
}

.operation-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.operation-icon.bg-primary { background: rgba(79, 70, 229, 0.1); }
.operation-icon.bg-success { background: rgba(34, 197, 94, 0.1); }
.operation-icon.bg-warning { background: rgba(249, 115, 22, 0.1); }
.operation-icon.bg-danger { background: rgba(239, 68, 68, 0.1); }
.operation-icon.bg-info { background: rgba(6, 182, 212, 0.1); }
.operation-icon.bg-secondary { background: rgba(107, 114, 128, 0.1); }
</style>
