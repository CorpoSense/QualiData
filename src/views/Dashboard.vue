<template>
  <div class="dashboard">
    <div class="row">
      <!-- Stats Cards -->
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Total Projects</p>
            <p class="h1 mb-0">{{ stats.projects }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Total Datasets</p>
            <p class="h1 mb-0">{{ stats.datasets }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Rows Processed</p>
            <p class="h1 mb-0">{{ formatNumber(stats.rows) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Storage Used</p>
            <p class="h1 mb-0">{{ formatBytes(stats.storage) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card mb-5">
      <div class="card-body">
        <h2 class="h4 mb-3">Quick Actions</h2>
        <div class="d-flex gap-2">
          <BButton variant="primary" @click="$router.push('/projects/new')">
            <i class="bi bi-plus-lg me-2"></i>New Project
          </BButton>
          <BButton variant="info" @click="showImportModal = true">
            <i class="bi bi-upload me-2"></i>Import Data
          </BButton>
          <BButton variant="success" @click="$router.push('/assistant')">
            <i class="bi bi-robot me-2"></i>AI Assistant
          </BButton>
        </div>
      </div>
    </div>

    <!-- API Usage -->
    <div class="card mb-5">
      <div class="card-body">
        <RateLimitStatus />
      </div>
    </div>

    <!-- Recent Projects -->
    <div class="card">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="h4 mb-0">Recent Projects</h2>
          <router-link to="/projects" class="small">View All</router-link>
        </div>

        <div v-if="loading" class="text-center py-6">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="projects.length === 0" class="text-center py-6">
          <p class="text-muted">No projects yet</p>
          <BButton variant="primary" class="mt-3" @click="$router.push('/projects/new')">
            Create Your First Project
          </BButton>
        </div>

        <div v-else class="row">
          <div v-for="project in projects" :key="project.id" class="col-md-4 mb-3">
            <div class="card project-card" @click="$router.push(`/projects/${project.id}`)">
              <div class="card-body">
                <h3 class="h5 mb-2">{{ project.name }}</h3>
                <p class="text-muted small mb-3">
                  {{ project.description || 'No description' }}
                </p>
                <div class="d-flex justify-content-between small text-muted">
                  <span>
                    <i class="bi bi-database me-1"></i>
                    {{ project.row_count || 0 }} rows
                  </span>
                  <span>{{ formatDate(project.updated_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <BModal v-model="showImportModal" :has-modal-card="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Import Data</h5>
            <button type="button" class="btn-close" @click="showImportModal = false"></button>
          </div>
          <div class="modal-body">
            <BFormGroup label="Select Project">
              <BFormSelect v-model="importForm.projectId" :options="projectOptions"></BFormSelect>
            </BFormGroup>

            <BFormGroup label="Upload File" class="mt-3">
              <BFormFile v-model="importForm.file" drop-placeholder="Drop your file here"></BFormFile>
              <small class="text-muted">Supported: CSV, Excel, JSON</small>
            </BFormGroup>

            <BFormGroup label="Dataset Name" class="mt-3">
              <BFormInput v-model="importForm.name" placeholder="My Dataset"></BFormInput>
            </BFormGroup>
          </div>
          <div class="modal-footer">
            <BButton variant="primary" :loading="importing" @click="handleImport">
              Import
            </BButton>
            <BButton @click="showImportModal = false">Cancel</BButton>
          </div>
        </div>
      </div>
    </BModal>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { BButton, BModal, BFormGroup, BFormSelect, BFormFile, BFormInput } from 'bootstrap-vue-next'
import RateLimitStatus from '@/components/RateLimitStatus.vue'

const router = useRouter()
const apiUrl = getApiUrl()

const loading = ref(true)
const projects = ref([])
const stats = ref({ projects: 0, datasets: 0, rows: 0, storage: 0 })
const showImportModal = ref(false)
const importing = ref(false)
const importForm = reactive({
  projectId: null,
  file: null,
  name: ''
})

const projectOptions = computed(() => 
  projects.value.map(p => ({ value: p.id, text: p.name }))
)

onMounted(async () => {
  await fetchProjects()
  await fetchStats()
  loading.value = false
})

async function fetchProjects() {
  try {
    const res = await fetch(`${apiUrl}/api/projects?page=1&page_size=6`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      projects.value = data.projects
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchStats() {
  stats.value.projects = projects.value.length
  stats.value.datasets = projects.value.reduce((sum, p) => sum + (p.datasets?.length || 0), 0)
  stats.value.rows = projects.value.reduce((sum, p) => sum + (p.row_count || 0), 0)
  stats.value.storage = projects.value.reduce((sum, p) => sum + (p.storage_bytes || 0), 0)
}

async function handleImport() {
  if (!importForm.file || !importForm.projectId) return

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', importForm.file)
    formData.append('project_id', importForm.projectId)
    if (importForm.name) {
      formData.append('name', importForm.name)
    }

    const res = await fetch(`${apiUrl}/api/datasets/import`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })

    if (res.ok) {
      showImportModal.value = false
      router.push(`/projects/${importForm.projectId}`)
    } else {
      throw new Error('Import failed')
    }
  } catch (e) {
    console.error(e)
  } finally {
    importing.value = false
  }
}

function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}
</script>

<style scoped>
.project-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
