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
        <BButton variant="success" @click="$router.push(`/assistant?project=${projectId}`)">
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
            <DatasetCard 
              :dataset="dataset"
              @click="viewDataset(dataset)"
            >
              <template #actions>
                <BDropdownItem @click="previewDataset(dataset)">Preview</BDropdownItem>
                <BDropdownItem @click="openRenameModal(dataset)">Rename</BDropdownItem>
                <BDropdownItem @click="exportDataset(dataset)">Export</BDropdownItem>
                <BDropdownItem @click="profileDataset(dataset)" variant="info">Profile</BDropdownItem>
                <BDropdownItem @click="deleteDataset(dataset)" variant="danger">Delete</BDropdownItem>
              </template>
            </DatasetCard>
          </div>
        </div>
        <!-- Datasets pagination -->
        <div v-if="datasetTotal > datasetPageSize" class="d-flex justify-content-center mt-3">
          <BPagination
            v-model="datasetPage"
            :total-rows="datasetTotal"
            :per-page="datasetPageSize"
            @update:model-value="fetchDatasets"
          ></BPagination>
        </div>
      </BTab>

      <BTab title="Operations">
        <div class="card">
          <div class="card-body p-0">
            <div v-if="operations.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-clock-history" style="font-size: 3rem;"></i>
              <p class="mt-3 mb-0">No operations yet</p>
              <p class="small">Operations will appear here after you clean or transform data</p>
            </div>
            <div v-else class="operations-list">
              <div 
                v-for="op in operations" 
                :key="op.id"
                class="operation-item"
              >
                <div class="d-flex align-items-center gap-3">
                  <div class="operation-icon" :class="getOperationClass(op.operation_type)">
                    <i :class="getOperationIcon(op.operation_type)"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <strong>{{ formatOperationType(op.operation_type) }}</strong>
                      <span v-if="op.dataset_name" class="badge bg-light text-dark">{{ op.dataset_name }}</span>
                    </div>
                    <p class="small text-muted mb-0">{{ formatDate(op.created_at) }}</p>
                  </div>
                  <BBadge v-if="op.is_undone" variant="secondary">Undone</BBadge>
                  <BBadge v-else variant="success">Done</BBadge>
                  <button class="btn btn-sm btn-outline-secondary border-0 py-0 px-1" @click="showOpDetails(op)" title="View details">
                    <i class="bi bi-info-circle"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </BTab>
    </BTabs>

    <!-- Import Modal -->
    <BModal
      v-model="showImportModal"
      :has-modal-card="true"
      title="Import Data"
      size="lg"
      no-header-close
    >
      <div class="p-3">
        <!-- Tabs -->
        <ul class="nav nav-pills mb-3">
          <li class="nav-item">
            <button class="nav-link" :class="{ active: importTab === 'file' }" @click="importTab = 'file'">
              <i class="bi bi-file-earmark-arrow-up me-1"></i> File
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: importTab === 'database' }" @click="importTab = 'database'">
              <i class="bi bi-database me-1"></i> Database
            </button>
          </li>
        </ul>

        <!-- File Import -->
        <div v-if="importTab === 'file'">
          <BFormGroup label="Dataset Name">
            <BFormInput v-model="importForm.name" placeholder="My Dataset"></BFormInput>
          </BFormGroup>
          <BFormGroup label="Upload File" class="mt-3">
            <BFormFile v-model="importForm.file" accept=".csv,.tsv,.txt,.xlsx,.xls" drop-placeholder="Drop file here"></BFormFile>
            <small class="text-muted">CSV, Excel</small>
          </BFormGroup>

          <!-- Import Options -->
          <div class="mt-3 p-3 border rounded">
            <div class="fw-bold mb-2">Import Options</div>
            <div class="mb-2">
              <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" id="autoMode" :value="true" v-model="importForm.autoDetect">
                <label class="form-check-label" for="autoMode">Auto (recommended)</label>
              </div>
              <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" id="manualMode" :value="false" v-model="importForm.autoDetect">
                <label class="form-check-label" for="manualMode">Manual</label>
              </div>
            </div>

            <div v-if="importForm.autoDetect === false" class="mt-2 ps-2 border-start">
              <div class="mb-2">
                <label class="form-label">Has Header:</label>
                <div class="form-check">
                  <input class="form-check-input" type="radio" id="hasHeaderYes" :value="true" v-model="importForm.hasHeader">
                  <label class="form-check-label" for="hasHeaderYes">Yes</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="radio" id="hasHeaderNo" :value="false" v-model="importForm.hasHeader">
                  <label class="form-check-label" for="hasHeaderNo">No</label>
                </div>
              </div>
              <div class="mt-2">
                <label class="form-label">Delimiter:</label>
                <select class="form-select" v-model="importForm.delimiter">
                  <option value=",">Comma (,)</option>
                  <option value=";">Semicolon (;)</option>
                  <option value="	">Tab</option>
                  <option value="|">Pipe (|)</option>
                </select>
              </div>
            </div>
          </div>
          <div class="mt-3 text-end">
            <BButton variant="primary" :loading="importing" :disabled="!importForm.name || !importForm.file" @click="handleImport">
              <i class="bi bi-upload me-1"></i> Import
            </BButton>
          </div>
        </div>

        <!-- Database Import -->
        <div v-if="importTab === 'database'">
          <BFormGroup label="Dataset Name">
            <BFormInput v-model="dbImportForm.name" placeholder="My Dataset"></BFormInput>
          </BFormGroup>
          <div class="row g-2 mt-1">
            <div class="col-4">
              <BFormGroup label="Database Type" label-size="sm">
                <BFormSelect v-model="dbImportForm.db_type" :options="dbTypeOptions" size="sm"></BFormSelect>
              </BFormGroup>
            </div>
            <div class="col-5">
              <BFormGroup label="Host" label-size="sm">
                <BFormInput v-model="dbImportForm.host" size="sm" placeholder="localhost"></BFormInput>
              </BFormGroup>
            </div>
            <div class="col-3">
              <BFormGroup label="Port" label-size="sm">
                <BFormInput v-model.number="dbImportForm.port" type="number" size="sm"></BFormInput>
              </BFormGroup>
            </div>
          </div>
          <div class="row g-2 mt-1">
            <div class="col-6">
              <BFormGroup label="Database" label-size="sm">
                <BFormInput v-model="dbImportForm.database" size="sm" placeholder="mydb"></BFormInput>
              </BFormGroup>
            </div>
            <div class="col-6">
              <BFormGroup label="Username" label-size="sm">
                <BFormInput v-model="dbImportForm.username" size="sm" placeholder="user"></BFormInput>
              </BFormGroup>
            </div>
          </div>
          <BFormGroup label="Password" label-size="sm" class="mt-1">
            <BFormInput v-model="dbImportForm.password" type="password" size="sm"></BFormInput>
          </BFormGroup>
          <BFormGroup v-if="dbImportForm.db_type === 'postgresql'" label="SSL Mode" label-size="sm" class="mt-1">
            <BFormSelect v-model="dbImportForm.sslmode" :options="sslmodeOptions" size="sm"></BFormSelect>
          </BFormGroup>

          <!-- Saved connections -->
          <div class="d-flex gap-2 mt-2">
            <BButton size="sm" variant="outline-success" @click="saveDbConnection" :disabled="!dbImportForm.host || !dbImportForm.database">
              <i class="bi bi-save me-1"></i> Save
            </BButton>
            <BFormSelect v-if="savedConnections.length" v-model="selectedConnection" :options="savedConnectionOptions" size="sm" style="max-width: 200px;" @update:model-value="loadSavedConnection"></BFormSelect>
            <BButton v-if="selectedConnection" size="sm" variant="outline-danger" @click="deleteSavedConnection">
              <i class="bi bi-trash"></i>
            </BButton>
          </div>

          <!-- Test Connection -->
          <div class="d-flex gap-2 mt-2">
            <BButton size="sm" variant="outline-primary" :loading="dbTesting" @click="testDbConnection">
              <i class="bi bi-plug me-1"></i> Test Connection
            </BButton>
            <span v-if="dbTestResult" :class="dbTestResult.success ? 'text-success' : 'text-danger'" class="small align-self-center">
              <i class="bi me-1" :class="dbTestResult.success ? 'bi-check-circle' : 'bi-x-circle'"></i>
              {{ dbTestResult.message }}
            </span>
          </div>

          <!-- Table Selection -->
          <div v-if="dbTables.length" class="mt-3">
            <BFormGroup label="Select Table" label-size="sm">
              <BFormSelect v-model="dbImportForm.table" :options="dbTableOptions" size="sm"></BFormSelect>
            </BFormGroup>
          </div>

          <div class="mt-3 text-end">
            <BButton variant="primary" :loading="importing" :disabled="!dbImportForm.name || !dbImportForm.table" @click="handleDbImport">
              <i class="bi bi-download me-1"></i> Import
            </BButton>
          </div>
        </div>
      </div>
      <template #footer><span></span></template>
    </BModal>

    <!-- Rename Dataset Modal -->
    <BModal v-model="showRenameModal" title="Rename Dataset">
      <BFormGroup label="Name" label-for="rename-ds-name">
        <BFormInput id="rename-ds-name" v-model="renameDatasetName" required></BFormInput>
      </BFormGroup>
      <BFormGroup label="Description" label-for="rename-ds-desc">
        <BFormTextarea id="rename-ds-desc" v-model="renameDatasetDesc" rows="2"></BFormTextarea>
      </BFormGroup>
      <template #footer>
        <BButton @click="showRenameModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="renamingDataset" @click="renameDataset">Save</BButton>
      </template>
    </BModal>

    <!-- Profile Modal -->
    <BModal v-model="showProfileModal" title="Data Profile" size="lg">
      <div v-if="profileLoading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading profile…</p>
      </div>
      <div v-else-if="profileData">
        <div class="row g-3">
          <div v-for="col in profileData.columns" :key="col.name" class="col-md-6">
            <div class="card h-100">
              <div class="card-body py-2 px-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <strong class="small">{{ col.name }}</strong>
                  <span class="badge bg-light text-dark">{{ col.dtype }}</span>
                </div>
                <div class="small text-muted">
                  <span v-if="col.null_count > 0" class="text-danger me-2">
                    {{ col.null_count }} nulls ({{ col.null_percent }}%)
                  </span>
                  <span>{{ col.unique_count }} unique</span>
                  <span class="ms-2">Quality: {{ col.quality_score }}%</span>
                </div>
                <div v-if="col.stats?.top_values?.length" class="mt-1">
                  <small class="text-muted">Top: </small>
                  <small v-for="(v, i) in col.stats.top_values.slice(0, 3)" :key="i" class="badge bg-light text-dark me-1">{{ v.value }} ({{ v.count }})</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <BButton variant="primary" @click="showProfileModal = false">Close</BButton>
      </template>
    </BModal>

    <!-- Export Modal -->
    <BModal v-model="showExportModal" title="Export Dataset">
      <BFormGroup label="Format" label-for="export-format">
        <BFormSelect id="export-format" v-model="exportFormat" :options="[
          { value: 'csv', text: 'CSV (.csv)' },
          { value: 'json', text: 'JSON (.json)' },
          { value: 'tsv', text: 'TSV (.tsv)' },
          { value: 'excel', text: 'Excel (.xlsx)' },
        ]"></BFormSelect>
      </BFormGroup>
      <BFormGroup label="Rows" label-for="export-limit" class="mt-2">
        <BFormSelect id="export-limit" v-model="exportLimit" :options="[
          { value: 0, text: 'All rows' },
          { value: 10, text: 'First 10' },
          { value: 50, text: 'First 50' },
          { value: 100, text: 'First 100' },
          { value: 500, text: 'First 500' },
          { value: 1000, text: 'First 1000' },
        ]"></BFormSelect>
      </BFormGroup>
      <template #footer>
        <BButton @click="showExportModal = false">Cancel</BButton>
        <BButton variant="primary" @click="downloadExport">
          <i class="bi bi-download me-1"></i> Download
        </BButton>
      </template>
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

    <!-- Operation Details Modal -->
    <BModal v-model="showOpDetailsModal" title="Operation Details" size="md">
      <div v-if="selectedOp">
        <div class="mb-3">
          <span class="badge" :class="selectedOp.is_undone ? 'bg-secondary' : 'bg-primary'">
            {{ selectedOp.operation_type }}
          </span>
          <span v-if="selectedOp.is_undone" class="badge bg-warning text-dark ms-1">Undone</span>
          <span v-if="selectedOp.dataset_name" class="badge bg-light text-dark ms-1">{{ selectedOp.dataset_name }}</span>
        </div>
        <div class="mb-2">
          <small class="text-muted">Date</small>
          <div>{{ formatDate(selectedOp.created_at) }}</div>
        </div>
        <div class="mb-2">
          <small class="text-muted">ID</small>
          <div><code class="small">{{ selectedOp.id }}</code></div>
        </div>
        <div v-if="selectedOp.operation_params">
          <small class="text-muted">Parameters</small>
          <pre class="bg-light p-2 rounded small mb-0" style="max-height: 200px; overflow-y: auto;">{{ formatOpParamsPretty(selectedOp.operation_params) }}</pre>
        </div>
      </div>
      <template #footer>
        <BButton variant="primary" @click="showOpDetailsModal = false">Close</BButton>
      </template>
    </BModal>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { BButton, BTab, BTabs, BDropdown, BDropdownItem, BBadge, BModal, BFormGroup, BFormInput, BFormTextarea, BFormFile, BFormSelect, BTable } from 'bootstrap-vue-next'
import DatasetCard from '@/components/DatasetCard.vue'

const route = useRoute()
const router = useRouter()
const apiUrl = getApiUrl()
const toast = useToast()

const projectId = route.params.id
const loading = ref(true)
const activeTab = ref(0)
const project = ref(null)
const operations = ref([])
const showImportModal = ref(false)
watch(showImportModal, (val) => {
  if (!val) {
    importForm.name = ''
    importForm.file = null
    importTab.value = 'file'
    dbImportForm.name = ''
    dbImportForm.table = ''
    dbTables.value = []
    dbTestResult.value = null
  }
})
const showPreviewModal = ref(false)
const showRenameModal = ref(false)
const showExportModal = ref(false)
const exportFormat = ref('csv')
const exportLimit = ref(0)
const showProfileModal = ref(false)
const profileData = ref(null)
const profileLoading = ref(false)
const showOpDetailsModal = ref(false)
const selectedOp = ref(null)
const renameDatasetId = ref(null)
const renameDatasetName = ref('')
const renameDatasetDesc = ref('')
const renamingDataset = ref(false)
const importTab = ref('file')
const importing = ref(false)
const dbTesting = ref(false)
const dbTestResult = ref(null)
const dbTables = ref([])

// Saved connections (localStorage)
const savedConnections = ref(JSON.parse(localStorage.getItem('dbConnections') || '[]'))
const selectedConnection = ref(null)

const savedConnectionOptions = computed(() => [
  { value: null, text: 'Load connection…' },
  ...savedConnections.value.map((c, i) => ({ value: i, text: `${c.name} (${c.db_type})` }))
])

function saveDbConnection() {
  const name = dbImportForm.name || `${dbImportForm.db_type}@${dbImportForm.host}`
  const conn = {
    name,
    db_type: dbImportForm.db_type,
    host: dbImportForm.host,
    port: dbImportForm.port,
    database: dbImportForm.database,
    username: dbImportForm.username,
    sslmode: dbImportForm.sslmode,
  }
  savedConnections.value.push(conn)
  localStorage.setItem('dbConnections', JSON.stringify(savedConnections.value))
  toast.success('Connection saved')
}

function loadSavedConnection(index) {
  if (index === null || index === undefined) return
  const conn = savedConnections.value[index]
  if (!conn) return
  Object.assign(dbImportForm, { ...conn, password: '', table: '' })
  dbTables.value = []
  dbTestResult.value = null
}

function deleteSavedConnection() {
  if (selectedConnection.value === null) return
  savedConnections.value.splice(selectedConnection.value, 1)
  localStorage.setItem('dbConnections', JSON.stringify(savedConnections.value))
  selectedConnection.value = null
}

const dbTypeOptions = [
  { value: 'postgresql', text: 'PostgreSQL' },
  { value: 'mysql', text: 'MySQL' },
  { value: 'sqlite', text: 'SQLite' },
  { value: 'oracle', text: 'Oracle' },
  { value: 'mssql', text: 'SQL Server' },
]

const sslmodeOptions = [
  { value: '', text: 'None' },
  { value: 'disable', text: 'Disable' },
  { value: 'allow', text: 'Allow' },
  { value: 'prefer', text: 'Prefer' },
  { value: 'require', text: 'Require' },
  { value: 'verify-ca', text: 'Verify CA' },
  { value: 'verify-full', text: 'Verify Full' },
]

const dbImportForm = reactive({
  name: '',
  db_type: 'postgresql',
  host: 'localhost',
  port: 5432,
  database: '',
  username: '',
  password: '',
  sslmode: 'require',
  table: '',
})

const dbTableOptions = computed(() => [
  { value: '', text: 'Select table…', disabled: true },
  ...dbTables.value.map(t => ({ value: t, text: t }))
])

// Update port when db_type changes
watch(() => dbImportForm.db_type, (type) => {
  const defaultPorts = { postgresql: 5432, mysql: 3306, sqlite: 0, oracle: 1521, mssql: 1433 }
  dbImportForm.port = defaultPorts[type] || 5432
  if (type === 'sqlite') dbImportForm.host = ''
})
const showAssistantModal = ref(false)
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
  file: null,
  autoDetect: true,
  hasHeader: true,
  delimiter: ','
})

const autoModeOptions = [
  { value: true, text: 'Auto (recommended)' },
  { value: false, text: 'Manual' }
]

const headerOptions = [
  { value: true, text: 'Yes' },
  { value: false, text: 'No' }
]

const delimiterOptions = [
  { value: ',', text: 'Comma (,)' },
  { value: ';', text: 'Semicolon (;)' },
  { value: '\t', text: 'Tab' },
  { value: '|', text: 'Pipe (|)' }
]

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
  await fetchOperations() // Load operations on mount
  loading.value = false

  // Auto-open import modal if navigated from dashboard "Import Data" shortcut
  if (route.query.import === 'true') {
    showImportModal.value = true
    router.replace({ query: {} })
  }
})

// Watch for tab changes to refresh operations when Operations tab is active
watch(activeTab, async (newTab) => {
  if (newTab === 1) { // Operations tab
    // Already loaded in onMounted, but refresh to get latest
    operations.value = [] 
    await fetchOperations()
  }
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

const datasets = ref([])
const datasetTotal = ref(0)
const datasetPage = ref(1)
const datasetPageSize = ref(12)

async function fetchDatasets() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets?project_id=${projectId}&page=${datasetPage.value}&page_size=${datasetPageSize.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      datasets.value = data.datasets || data || []
      datasetTotal.value = data.total || datasets.value.length
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchOperations() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const datasets = await res.json()
      // Get operations for each dataset
      const allOps = []
      for (const ds of datasets) {
        const opsRes = await fetch(`${apiUrl}/api/datasets/${ds.id}/operations`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        if (opsRes.ok) {
          const ops = await opsRes.json()
          allOps.push(...ops.map(op => ({ ...op, dataset_name: ds.name })))
        }
      }
      // Sort by date descending
      allOps.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      operations.value = allOps
    }
  } catch (e) {
    console.error(e)
  }
}

function handleFileSelect() {
  const file = importForm.file
  if (!file) return
  
  // Preview disabled - import goes directly to backend
  importPreviewHeaders.value = []
  importPreview.value = []
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

async function testDbConnection() {
  dbTesting.value = true
  dbTestResult.value = null
  dbTables.value = []
  dbImportForm.table = ''
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(dbImportForm)
    })
    if (res.ok) {
      dbTestResult.value = { success: true, message: 'Connected!' }
      await fetchDbTables()
    } else {
      const err = await res.json()
      dbTestResult.value = { success: false, message: err.detail || 'Connection failed' }
    }
  } catch (e) {
    dbTestResult.value = { success: false, message: e.message }
  } finally {
    dbTesting.value = false
  }
}

async function fetchDbTables() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db/tables`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(dbImportForm)
    })
    if (res.ok) {
      const data = await res.json()
      dbTables.value = data.tables || []
    }
  } catch { /* silent */ }
}

async function handleDbImport() {
  if (!dbImportForm.name || !dbImportForm.table) return
  importing.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ ...dbImportForm, project_id: projectId })
    })
    if (res.ok) {
      const data = await res.json()
      showImportModal.value = false
      dbTables.value = []
      dbTestResult.value = null
      await fetchDatasets()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Import failed')
    }
  } catch (e) {
    toast.error(e.message)
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

function openRenameModal(dataset) {
  renameDatasetId.value = dataset.id
  renameDatasetName.value = dataset.name
  renameDatasetDesc.value = dataset.description || ''
  showRenameModal.value = true
}

async function renameDataset() {
  if (!renameDatasetName.value.trim()) return
  renamingDataset.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${renameDatasetId.value}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ name: renameDatasetName.value, description: renameDatasetDesc.value })
    })
    if (res.ok) {
      showRenameModal.value = false
      await fetchDatasets()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to rename')
    }
  } catch (e) { toast.error(e.message) }
  finally { renamingDataset.value = false }
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
  selectedDataset.value = dataset
  exportFormat.value = 'csv'
  exportLimit.value = 0
  showExportModal.value = true
}

function downloadExport() {
  if (!selectedDataset.value) return
  const params = new URLSearchParams({ format: exportFormat.value })
  if (exportLimit.value > 0) params.set('limit', exportLimit.value)

  // Use fetch with auth header instead of window.open (which doesn't send auth)
  fetch(`${apiUrl}/api/datasets/${selectedDataset.value.id}/export?${params}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
    .then(res => {
      if (!res.ok) throw new Error(`Export failed (${res.status})`)
      const disposition = res.headers.get('Content-Disposition') || ''
      const match = disposition.match(/filename="(.+?)"/)
      const filename = match ? match[1] : `export.${exportFormat.value}`
      return res.blob().then(blob => ({ blob, filename }))
    })
    .then(({ blob, filename }) => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    })
    .catch(e => { toast.error(e.message) })

  showExportModal.value = false
}

function viewDataset(dataset) {
  router.push(`/projects/${projectId}/dataset/${dataset.id}`)
}

function profileDataset(dataset) {
  selectedDataset.value = dataset
  fetchDatasetProfile(dataset.id)
}

async function fetchDatasetProfile(dsId) {
  profileLoading.value = true
  profileData.value = null
  showProfileModal.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${dsId}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      profileData.value = await res.json()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to load profile')
    }
  } catch (e) { toast.error(e.message) }
  finally { profileLoading.value = false }
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

function showOpDetails(op) {
  selectedOp.value = op
  showOpDetailsModal.value = true
}

function formatOpParamsPretty(params) {
  if (!params) return ''
  try {
    return JSON.stringify(params, null, 2)
  } catch { return String(params) }
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

/* Operations List */
.operations-list {
  display: flex;
  flex-direction: column;
}

.operation-item {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background 0.2s ease;
}

.operation-item:last-child {
  border-bottom: none;
}

.operation-item:hover {
  background: rgba(79, 70, 229, 0.03);
}

.operation-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.operation-icon.bg-primary { background: rgba(79, 70, 229, 0.1); }
.operation-icon.bg-success { background: rgba(34, 197, 94, 0.1); }
.operation-icon.bg-warning { background: rgba(249, 115, 22, 0.1); }
.operation-icon.bg-danger { background: rgba(239, 68, 68, 0.1); }
.operation-icon.bg-info { background: rgba(6, 182, 212, 0.1); }
.operation-icon.bg-secondary { background: rgba(107, 114, 128, 0.1); }
</style>
