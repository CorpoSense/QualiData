<template>
  <div class="dashboard">
    <div class="columns">
      <!-- Stats Cards -->
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Total Projects</p>
          <p class="title is-1">{{ stats.projects }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Total Datasets</p>
          <p class="title is-1">{{ stats.datasets }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Rows Processed</p>
          <p class="title is-1">{{ formatNumber(stats.rows) }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Storage Used</p>
          <p class="title is-1">{{ formatBytes(stats.storage) }}</p>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="box mb-5">
      <h2 class="title is-4">Quick Actions</h2>
      <div class="buttons">
        <b-button type="is-primary" icon-left="plus" @click="$router.push('/projects/new')">
          New Project
        </b-button>
        <b-button type="is-info" icon-left="upload" @click="showImportModal = true">
          Import Data
        </b-button>
        <b-button type="is-success" icon-left="robot" @click="$router.push('/assistant')">
          AI Assistant
        </b-button>
      </div>
    </div>

    <!-- API Usage -->
    <div class="box mb-5">
      <RateLimitStatus />
    </div>

    <!-- Recent Projects -->
    <div class="box">
      <div class="is-flex is-justify-content-space-between is-align-items-center mb-4">
        <h2 class="title is-4 mb-0">Recent Projects</h2>
        <b-button tag="router-link" to="/projects" size="is-small" type="is-text">
          View All
        </b-button>
      </div>

      <div v-if="loading" class="has-text-centered py-6">
        <b-icon icon="loading" size="is-large" spin></b-icon>
      </div>

      <div v-else-if="projects.length === 0" class="has-text-centered py-6">
        <p class="has-text-grey">No projects yet</p>
        <b-button type="is-primary" class="mt-3" @click="$router.push('/projects/new')">
          Create Your First Project
        </b-button>
      </div>

      <div v-else class="columns is-multiline">
        <div v-for="project in projects" :key="project.id" class="column is-4">
          <div class="box project-card" @click="$router.push(`/projects/${project.id}`)">
            <h3 class="title is-5 mb-2">{{ project.name }}</h3>
            <p class="has-text-grey is-size-7 mb-3">
              {{ project.description || 'No description' }}
            </p>
            <div class="is-flex is-justify-content-space-between is-size-7 has-text-grey">
              <span>
                <b-icon icon="database" size="is-small"></b-icon>
                {{ project.row_count || 0 }} rows
              </span>
              <span>{{ formatDate(project.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <b-modal v-model="showImportModal" :has-modal-card="true">
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Import Data</p>
          <button class="delete" @click="showImportModal = false"></button>
        </header>
        <section class="modal-card-body">
          <b-field label="Select Project">
            <b-select v-model="importForm.projectId" expanded placeholder="Choose project">
              <option v-for="p in projects" :key="p.id" :value="p.id">
                {{ p.name }}
              </option>
            </b-select>
          </b-field>

          <b-field label="Upload File">
            <b-upload v-model="importForm.file" drag-drop expanded>
              <section class="section">
                <div class="content has-text-centered">
                  <p><b-icon icon="upload" size="is-large"></b-icon></p>
                  <p>Drop your file here or click to upload</p>
                  <p class="is-size-7 has-text-grey">Supported: CSV, Excel, JSON</p>
                </div>
              </section>
            </b-upload>
          </b-field>

          <b-field label="Dataset Name">
            <b-input v-model="importForm.name" placeholder="My Dataset"></b-input>
          </b-field>
        </section>
        <footer class="modal-card-foot">
          <b-button type="is-primary" :loading="importing" @click="handleImport">
            Import
          </b-button>
          <b-button @click="showImportModal = false">Cancel</b-button>
        </footer>
      </div>
    </b-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RateLimitStatus from '@/components/RateLimitStatus.vue'

const router = useRouter()
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  // Calculate stats from projects
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
