<template>
  <div class="project-detail">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-5">
      <div>
        <BButton variant="link" @click="$router.push('/projects')" class="mb-3 ps-0">
          <i class="bi bi-arrow-left me-2"></i>Back to Projects
        </BButton>
        <h1 class="h3 mb-1">{{ project?.name }}</h1>
        <p class="text-muted">{{ project?.description || 'No description' }}</p>
      </div>
      <div class="d-flex gap-2">
        <BButton variant="primary" @click="showImportModal = true">
          <i class="bi bi-upload me-2"></i>Import Data
        </BButton>
        <BButton variant="success" @click="showAssistantModal = true">
          <i class="bi bi-robot me-2"></i>AI Assistant
        </BButton>
      </div>
    </div>

    <!-- Stats -->
    <div class="row mb-5">
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Datasets</p>
            <p class="h3 mb-0">{{ datasets.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Total Rows</p>
            <p class="h3 mb-0">{{ formatNumber(project?.row_count || 0) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Storage</p>
            <p class="h3 mb-0">{{ formatBytes(project?.storage_bytes || 0) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Last Updated</p>
            <p class="h5 mb-0">{{ formatDate(project?.updated_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <BTabs v-model="activeTab" nav-style="box">
      <BTab title="Datasets">
        <!-- Datasets List -->
        <div v-if="loading" class="text-center py-6">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="datasets.length === 0" class="card text-center py-6">
          <div class="card-body">
            <i class="bi bi-database text-muted mb-4" style="font-size: 3rem;"></i>
            <p class="text-muted mb-4">No datasets yet</p>
            <BButton variant="primary" @click="showImportModal = true">
              Import Your First Dataset
            </BButton>
          </div>
        </div>
        <div v-else class="row">
          <div v-for="dataset in datasets" :key="dataset.id" class="col-md-4 mb-3">
              <div class="card dataset-card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h3 class="h6 mb-0">{{ dataset.name }}</h3>
                  <BDropdown text="Actions" variant="outline-secondary" size="sm">
                    <BDropdownItem @click="viewDataset(dataset)">View Data</BDropdownItem>
                    <BDropdownItem @click="previewDataset(dataset)">Preview</BDropdownItem>
                    <BDropdownItem @click="exportDataset(dataset)">Export</BDropdownItem>
                    <BDropdownItem @click="profileDataset(dataset)" variant="info">Profile</BDropdownItem>
                    <BDropdownItem @click="deleteDataset(dataset)" variant="danger">Delete</BDropdownItem>
                  </BDropdown>
                </div>
                <p class="small text-muted mb-2">{{ dataset.description || 'No description' }}</p>
                <div class="d-flex justify-content-between small text-muted">
                  <span><i class="bi bi-table me-1"></i> {{ dataset.row_count }} rows</span>
                  <span>{{ dataset.file_type?.toUpperCase() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </BTab>

      <BTab title="Operations">
        <div class="card">
          <div class="card-body">
            <h3 class="h5 mb-4">Operation History</h3>
            <div v-if="operations.length === 0" class="text-center py-4 text-muted">
              No operations yet
            </div>
            <div v-else class="list-group list-group-flush">
              <div 
                v-for="op in operations" 
                :key="op.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <div>
                  <strong>{{ op.operation_type }}</strong>
                  <p class="small text-muted mb-0">{{ formatDate(op.created_at) }}</p>
                </div>
                <BBadge v-if="op.is_undone" variant="light">Undone</BBadge>
              </div>
            </div>
          </div>
        </div>
      </BTab>
    </BTabs>

    <!-- Import Modal -->
    <BModal v-model="showImportModal" :has-modal-card="true" ok-title="Import" @ok="handleImport" :cancel-title="null">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Import Data</h5>
            <button type="button" class="btn-close" @click="showImportModal = false"></button>
          </div>
          <div class="modal-body">
            <BFormGroup label="Dataset Name">
              <BFormInput v-model="importForm.name" placeholder="My Dataset"></BFormInput>
            </BFormGroup>
            <BFormGroup label="Upload File" class="mt-3">
              <BFormFile v-model="importForm.file" accept=".csv,.tsv,.txt,.xlsx,.xls" drop-placeholder="Drop file here"></BFormFile>
              <small class="text-muted">CSV, Excel</small>
            </BFormGroup>
            
            <!-- Import Options -->
            <div class="mt-3 p-3 bg-light rounded">
              <h6>Import Options</h6>
              <BFormGroup label="Mode">
                <BFormRadioGroup v-model="importForm.autoDetect" :options="[{value: true, text: 'Auto (recommended)'}, {value: false, text: 'Manual'}]"></BFormRadioGroup>
              </BFormGroup>
              
              <!-- Manual options -->
              <div v-if="importForm.autoDetect === false">
                <BFormGroup label="Has Header" class="mt-2">
                  <BFormRadioGroup v-model="importForm.hasHeader" :options="[{value: true, text: 'Yes'}, {value: false, text: 'No'}]"></BFormRadioGroup>
                </BFormGroup>
                <BFormGroup label="Delimiter" class="mt-2">
                  <BFormSelect v-model="importForm.delimiter" :options="[{value: ',', text: 'Comma (,)'}, {value: ';', text: 'Semicolon (;)'}, {value: '\\t', text: 'Tab'}, {value: '|', text: 'Pipe (|)'}]"></BFormSelect>
                </BFormGroup>
              </div>
            </div>
          </div>
        </div>
      </div>
    </BModal>

    <!-- Preview Modal -->
    <BModal v-model="showPreviewModal" :has-modal-card="true" size="xl">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedDataset?.name }} - Preview</h5>
            <button type="button" class="btn-close" @click="showPreviewModal = false"></button>
          </div>
          <div class="modal-body">
            <BFormGroup label="Rows to Show">
              <BFormSelect v-model="previewLimit" :options="previewLimitOptions"></BFormSelect>
            </BFormGroup>
            <BTable :items="previewData" :fields="previewColumns" :per-page="previewLimit" bordered striped hover></BTable>
          </div>
        </div>
      </div>
    </BModal>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BButton, BTab, BTabs, BDropdown, BDropdownItem, BBadge, BModal, BFormGroup, BFormInput, BFormFile, BFormSelect, BTable } from 'bootstrap-vue-next'

const route = useRoute()
const router = useRouter()
const apiUrl = getApiUrl()

const projectId = route.params.id
const loading = ref(true)
const activeTab = ref(0)
const project = ref(null)
const datasets = ref([])
const operations = ref([])
const showImportModal = ref(false)
watch(showImportModal, (val) => {
  if (!val) {
    importForm.name = ''
    importForm.file = null
  }
})
const showPreviewModal = ref(false)
const showAssistantModal = ref(false)
const importing = ref(false)
const selectedDataset = ref(null)
const previewLimit = ref(10)
const previewData = ref([])

const previewLimitOptions = [
  { value: 10, text: '10 rows' },
  { value: 25, text: '25 rows' },
  { value: 50, text: '50 rows' },
  { value: 100, text: '100 rows' }
]

const importForm = reactive({
  name: '',
  file: null
})

const previewColumns = computed(() => {
  if (previewData.value.length === 0) return []
  return Object.keys(previewData.value[0]).map(key => ({
    key: key,
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

function handleFileSelect() {
  const file = importForm.file
  if (!file) return
  
  Papa.parse(file, {
    complete: function(results) {
      if (results.data && results.data.length > 0) {
        // Filter out empty rows
        const filtered = results.data.filter(row => row.some(cell => cell && cell.trim()))
        if (filtered.length > 0) {
          importPreviewHeaders.value = filtered[0]
          importPreview.value = filtered.slice(1)
        }
      }
    },
    error: function(err) {
      console.error('Parse error:', err)
    }
  })
}

async function confirmImport() {
  handleImport()
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

function viewDataset(dataset) {
  router.push(`/projects/${projectId}/dataset/${dataset.id}`)
}

function profileDataset(dataset) {
  console.log('Profile dataset:', dataset)
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
