<template>
  <div class="project-detail">
    <!-- Header -->
    <div class="is-flex is-justify-content-space-between is-align-items-center mb-5">
      <div>
        <b-button tag="router-link" to="/projects" icon-left="arrow-left" class="mb-3">
          Back to Projects
        </b-button>
        <h1 class="title is-3 mb-1">{{ project?.name }}</h1>
        <p class="has-text-grey">{{ project?.description || 'No description' }}</p>
      </div>
      <div class="buttons">
        <b-button type="is-primary" icon-left="upload" @click="showImportModal = true">
          Import Data
        </b-button>
        <b-button type="is-success" icon-left="robot" @click="showAssistantModal = true">
          AI Assistant
        </b-button>
      </div>
    </div>

    <!-- Stats -->
    <div class="columns mb-5">
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Datasets</p>
          <p class="title">{{ datasets.length }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Total Rows</p>
          <p class="title">{{ formatNumber(project?.row_count || 0) }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Storage</p>
          <p class="title">{{ formatBytes(project?.storage_bytes || 0) }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered">
          <p class="heading">Last Updated</p>
          <p class="title is-5">{{ formatDate(project?.updated_at) }}</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <b-tabs v-model="activeTab" type="is-boxed">
      <b-tab-item label="Datasets">
        <!-- Datasets List -->
        <div v-if="loading" class="has-text-centered py-6">
          <b-icon icon="loading" size="is-large" spin></b-icon>
        </div>
        <div v-else-if="datasets.length === 0" class="box has-text-centered py-6">
          <b-icon icon="database-outline" size="is-large" class="has-text-grey-light mb-4"></b-icon>
          <p class="has-text-grey mb-4">No datasets yet</p>
          <b-button type="is-primary" @click="showImportModal = true">
            Import Your First Dataset
          </b-button>
        </div>
        <div v-else class="columns is-multiline">
          <div v-for="dataset in datasets" :key="dataset.id" class="column is-4">
            <div class="box dataset-card" @click="selectDataset(dataset)">
              <div class="is-flex is-justify-content-space-between is-align-items-start mb-2">
                <h3 class="title is-6 mb-0">{{ dataset.name }}</h3>
                <b-dropdown position="is-bottom-right" @click.stop>
                  <b-button icon-left="dots-vertical" size="is-small" slot="trigger"></b-button>
                  <b-dropdown-item @click="previewDataset(dataset)">Preview</b-dropdown-item>
                  <b-dropdown-item @click="exportDataset(dataset)">Export</b-dropdown-item>
                  <b-dropdown-item @click="profileDataset(dataset)" class="has-text-info">Profile</b-dropdown-item>
                  <b-dropdown-item @click="deleteDataset(dataset)" class="has-text-danger">Delete</b-dropdown-item>
                </b-dropdown>
              </div>
              <p class="is-size-7 has-text-grey mb-2">{{ dataset.description || 'No description' }}</p>
              <div class="is-flex is-justify-content-space-between is-size-7 has-text-grey">
                <span><b-icon icon="table" size="is-small"></b-icon> {{ dataset.row_count }} rows</span>
                <span>{{ dataset.file_type?.toUpperCase() }}</span>
              </div>
            </div>
          </div>
        </div>
      </b-tab-item>

      <b-tab-item label="Operations">
        <div class="box">
          <h3 class="title is-5 mb-4">Operation History</h3>
          <div v-if="operations.length === 0" class="has-text-centered py-4 has-text-grey">
            No operations yet
          </div>
          <timeline v-else>
            <timeline-item 
              v-for="op in operations" 
              :key="op.id"
              :color="op.is_undone ? 'grey' : 'green'"
            >
              <div class="is-flex is-justify-content-space-between">
                <div>
                  <strong>{{ op.operation_type }}</strong>
                  <p class="is-size-7 has-text-grey">{{ formatDate(op.created_at) }}</p>
                </div>
                <b-tag v-if="op.is_undone" type="is-light">Undone</b-tag>
              </div>
            </timeline-item>
          </timeline>
        </div>
      </b-tab-item>
    </b-tabs>

    <!-- Import Modal -->
    <b-modal v-model="showImportModal" :has-modal-card="true">
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Import Data</p>
          <button class="delete" @click="showImportModal = false"></button>
        </header>
        <section class="modal-card-body">
          <b-field label="Dataset Name">
            <b-input v-model="importForm.name" placeholder="My Dataset"></b-input>
          </b-field>
          <b-field label="Upload File">
            <b-upload v-model="importForm.file" drag-drop expanded>
              <section class="section">
                <div class="content has-text-centered">
                  <p><b-icon icon="upload" size="is-large"></b-icon></p>
                  <p>Drop file here or click to upload</p>
                  <p class="is-size-7 has-text-grey">CSV, Excel, JSON</p>
                </div>
              </section>
            </b-upload>
          </b-field>
        </section>
        <footer class="modal-card-footer">
          <b-button type="is-primary" :loading="importing" @click="handleImport">Import</b-button>
          <b-button @click="showImportModal = false">Cancel</b-button>
        </footer>
      </div>
    </b-modal>

    <!-- Preview Modal -->
    <b-modal v-model="showPreviewModal" :has-modal-card="true" :width="'90%'">
      <div class="modal-card" style="width: 90%">
        <header class="modal-card-head">
          <p class="modal-card-title">{{ selectedDataset?.name }} - Preview</p>
          <button class="delete" @click="showPreviewModal = false"></button>
        </header>
        <section class="modal-card-body">
          <b-field label="Rows to Show">
            <b-select v-model="previewLimit">
              <option :value="10">10 rows</option>
              <option :value="25">25 rows</option>
              <option :value="50">50 rows</option>
              <option :value="100">100 rows</option>
            </b-select>
          </b-field>
          <b-table :data="previewData" :columns="previewColumns" :per-page="previewLimit" paginated></b-table>
        </section>
      </div>
    </b-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const projectId = route.params.id
const loading = ref(true)
const activeTab = ref(0)
const project = ref(null)
const datasets = ref([])
const operations = ref([])
const showImportModal = ref(false)
const showPreviewModal = ref(false)
const showAssistantModal = ref(false)
const importing = ref(false)
const selectedDataset = ref(null)
const previewLimit = ref(10)
const previewData = ref([])

const importForm = reactive({
  name: '',
  file: null
})

const previewColumns = computed(() => {
  if (previewData.value.length === 0) return []
  return Object.keys(previewData.value[0]).map(key => ({
    field: key,
    label: key
  }))
})

onMounted(async () => {
  await fetchProject()
  await fetchDatasets()
  loading.value = false
})

async function fetchProject() {
  try {
    const res = await fetch(`${apiUrl}/api/projects/${projectId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      project.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchDatasets() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      datasets.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

async function handleImport() {
  if (!importForm.file) return
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', importForm.file)
    formData.append('project_id', projectId)
    if (importForm.name) formData.append('name', importForm.name)

    const res = await fetch(`${apiUrl}/api/datasets/import`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      showImportModal.value = false
      importForm.name = ''
      importForm.file = null
      await fetchDatasets()
    }
  } catch (e) {
    console.error(e)
  } finally {
    importing.value = false
  }
}

async function previewDataset(dataset) {
  selectedDataset.value = dataset
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${dataset.id}/preview?limit=${previewLimit.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      previewData.value = data.preview_data || []
      showPreviewModal.value = true
    }
  } catch (e) {
    console.error(e)
  }
}

async function deleteDataset(dataset) {
  try {
    await fetch(`${apiUrl}/api/datasets/${dataset.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    await fetchDatasets()
  } catch (e) {
    console.error(e)
  }
}

function exportDataset(dataset) {
  window.open(`${apiUrl}/api/datasets/${dataset.id}/export?format=csv`, '_blank')
}

function selectDataset(dataset) {
  selectedDataset.value = dataset
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
.dataset-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.dataset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
