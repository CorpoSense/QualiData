<template>
  <div class="data-viewer">
    <!-- Operations Toolbar -->
    <div class="card mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2">
            <!-- Per-page selector -->
<select v-model="limit" class="form-select form-select-sm" style="width: auto;">
  <option v-for="opt in limitOptions" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
</select>
            <span class="text-muted ms-3">{{ totalRows }} total rows</span>
            <BButton size="sm" variant="outline-secondary" @click="refreshData">
              <i class="bi bi-arrow-clockwise me-1"></i> Refresh
            </BButton>
          </div>
          
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <BFormInput v-model="searchQuery" size="sm" placeholder="Search..." style="width: 150px;"></BFormInput>
            <BButton size="sm" variant="info" @click="showProfile = true">
              <i class="bi bi-bar-chart me-1"></i> Profile
            </BButton>
            <BButton size="sm" variant="success" @click="showCompare = true">
              <i class="bi bi-columns-gap me-1"></i> Compare
            </BButton>
            <BButton size="sm" variant="secondary" @click="showHistory = !showHistory">
              <i class="bi bi-clock-history me-1"></i> History
            </BButton>
            <BButton size="sm" variant="warning" outline @click="showClipboardImport = true">
              <i class="bi bi-clipboard me-1"></i> Paste
            </BButton>
            <BButton size="sm" variant="warning" outline @click="copyToClipboard">
              <i class="bi bi-clipboard-check me-1"></i> Copy
            </BButton>
          </div>
        </div>

        <!-- Operation Buttons -->
        <div class="d-flex flex-wrap gap-2 align-items-center">
          <BDropdown text="Missing Values" size="sm">
            <BDropdownItem @click="applyOperation('fillna', { method: 'drop' })">
              <i class="bi bi-trash me-2"></i>Drop rows with nulls
            </BDropdownItem>
            <BDropdownItem @click="showFillnaModal = true">
              <i class="bi bi-pencil me-2"></i>Fill with value...
            </BDropdownItem>
            <BDropdownItem @click="applyOperation('fillna', { method: 'forward' })">
              <i class="bi bi-arrow-down me-2"></i>Forward fill
            </BDropdownItem>
            <BDropdownItem @click="applyOperation('fillna', { method: 'backward' })">
              <i class="bi bi-arrow-up me-2"></i>Backward fill
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="String Ops" size="sm">
            <BDropdownItem @click="applyStringOp('strip')">
              <i class="bi bi-type me-2"></i>Trim whitespace
            </BDropdownItem>
            <BDropdownItem @click="applyStringOp('lower')">
              <i class="bi bi-type me-2"></i>Lowercase
            </BDropdownItem>
            <BDropdownItem @click="applyStringOp('upper')">
              <i class="bi bi-type me-2"></i>Uppercase
            </BDropdownItem>
            <BDropdownItem @click="applyStringOp('title')">
              <i class="bi bi-type me-2"></i>Title case
            </BDropdownItem>
            <BDropdownItem @click="applyStringOp('capitalize')">
              <i class="bi bi-type me-2"></i>Capitalize
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Date Ops" size="sm">
            <BDropdownItem @click="applyDatetimeOp('parse-datetime')">
              <i class="bi bi-calendar me-2"></i>Parse datetime
            </BDropdownItem>
            <BDropdownItem @click="applyDatetimeOp('extract-year')">
              <i class="bi bi-calendar3 me-2"></i>Extract year
            </BDropdownItem>
            <BDropdownItem @click="applyDatetimeOp('extract-month')">
              <i class="bi bi-calendar3 me-2"></i>Extract month
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Numeric Ops" size="sm">
            <BDropdownItem @click="applyNumericOp('round')">
              <i class="bi bi-123 me-2"></i>Round numbers
            </BDropdownItem>
            <BDropdownItem @click="applyNumericOp('normalize')">
              <i class="bi bi-percent me-2"></i>Normalize
            </BDropdownItem>
            <BDropdownItem @click="applyNumericOp('outliers')">
              <i class="bi bi-exclamation-triangle me-2"></i>Handle outliers
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Structure" size="sm">
            <BDropdownItem @click="applyStructuralOp('rename')" :disabled="selectedColumns.length !== 1">
              <i class="bi bi-pencil-square me-2"></i>Rename column
              <span v-if="selectedColumns.length !== 1" class="text-muted small ms-2">(select 1)</span>
            </BDropdownItem>
            <BDropdownItem @click="applyStructuralOp('drop')">
              <i class="bi bi-trash me-2"></i>Drop column
            </BDropdownItem>
            <BDropdownItem @click="applyStructuralOp('astype')">
              <i class="bi bi-arrow-left-right me-2"></i>Change type
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Dedupe" size="sm">
            <BDropdownItem @click="applyDedup('duplicates')">
              <i class="bi bi-copy me-2"></i>Remove duplicates
            </BDropdownItem>
            <BDropdownItem @click="applyDedup('fuzzy')">
              <i class="bi bi-search me-2"></i>Fuzzy match
            </BDropdownItem>
          </BDropdown>

          <BButton size="sm" variant="primary" :disabled="selectedColumns.length === 0" @click="showAiModal = true">
            <i class="bi bi-stars me-1"></i> AI Clean
          </BButton>

          <div class="ms-auto d-flex gap-1">
            <BButton size="sm" variant="outline-secondary" :disabled="!canUndo" @click="undo">
              <i class="bi bi-arrow-counterclockwise"></i>
            </BButton>
            <BButton size="sm" variant="outline-secondary" :disabled="!canRedo" @click="redo">
              <i class="bi bi-arrow-clockwise"></i>
            </BButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Selection Bar - click columns in table to select -->
    <div class="d-flex gap-2 mb-3 flex-wrap align-items-center">
      <BBadge variant="secondary" pill>{{ data.length }} rows</BBadge>
      <BBadge variant="secondary" pill>{{ columns.length }} columns</BBadge>
      <BBadge variant="warning" pill>{{ nullCount }} nulls</BBadge>
      
      <!-- Selected columns display -->
      <BBadge v-if="selectedColumns.length > 0" variant="info" pill class="ms-2">
        <i class="bi bi-check2-square me-1"></i>
        {{ selectedColumns.length === 1 ? `1 column: ${selectedColumns[0]}` : `${selectedColumns.length} columns selected` }}
      </BBadge>
      <BButton size="sm" variant="outline-secondary" @click="selectedColumns = columns.map(c => c.field)">
        Select All
      </BButton>
      <BButton v-if="selectedColumns.length > 0" size="sm" variant="outline-secondary" @click="selectedColumns = []">
        Clear
      </BButton>
      <span v-else class="text-muted small ms-2">
        <i class="bi bi-info-circle me-1"></i>Click column headers to select
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Data Table -->
    <div v-else class="card">
      <!-- Custom DataTable (no pagination - handled below) -->
      <DataTable
        :items="data"
        :fields="tableFields"
        :selected-columns="selectedColumns"
        @row-clicked="onRowClicked"
        @head-clicked="onHeadClicked"
      />

      <!-- Pagination Footer -->
      <div class="d-flex justify-content-between align-items-center mt-3">
        <small class="text-muted">
          Showing {{ startRow }} - {{ endRow }} of {{ totalRows }}
        </small>
        <div class="d-flex align-items-center gap-2">
          <button 
            class="btn btn-sm btn-outline-secondary" 
            :disabled="page <= 1"
            @click="goToPrev"
          >
            ← Prev
          </button>
                    <span class="text-muted">Page {{ page }} of {{ totalPages }}</span>
          <button 
            class="btn btn-sm btn-outline-secondary" 
            :disabled="page >= totalPages"
            @click="goToNext"
          >
            Next →
          </button>
        </div>
      </div>
    </div>

    <!-- Profile Modal -->
    <BModal v-model="showProfile" title="Data Profile" size="lg">
      <div v-if="profileData">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="card">
              <div class="card-body text-center">
                <h3>{{ profileData.total_rows || 0 }}</h3>
                <p class="text-muted mb-0">Total Rows</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card">
              <div class="card-body text-center">
                <h3>{{ profileData.total_columns || 0 }}</h3>
                <p class="text-muted mb-0">Columns</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card">
              <div class="card-body text-center">
                <h3>{{ nullCount }}</h3>
                <p class="text-muted mb-0">Null Values</p>
              </div>
            </div>
          </div>
        </div>
        <div class="mt-4">
          <h5>Column Profiles</h5>
          <div v-for="col in profileData.columns" :key="col.name" class="mb-3">
            <div class="d-flex justify-content-between mb-1">
              <strong>{{ col.name }}</strong>
              <span class="text-muted">{{ col.dtype }}</span>
            </div>
            <div class="progress" style="height: 6px;">
              <div class="progress-bar" :style="{ width: (col.null_count / profileData.total_rows * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <BButton @click="showProfile = false">Close</BButton>
      </template>
    </BModal>

    <!-- AI Clean Modal -->
    <BModal v-model="showAiModal" title="AI Clean" @ok="applyAiClean">
      <div class="alert alert-info">
        <i class="bi bi-info-circle me-2"></i>
        <strong>Selected {{ selectedColumns.length === 1 ? 'column' : 'columns' }}:</strong> 
        {{ selectedColumns.length === 1 ? selectedColumns[0] : selectedColumns.join(', ') }}
      </div>
      <BFormGroup label="Instruction">
        <BFormTextarea v-model="aiInstruction" placeholder="e.g., Extract the email domain, Convert to title case"></BFormTextarea>
      </BFormGroup>
      <template #footer>
        <BButton @click="showAiModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" @click="applyAiClean">Apply</BButton>
      </template>
    </BModal>

    <!-- Clipboard Import Modal -->
    <BModal v-model="showClipboardImport" title="Import from Clipboard">
      <BFormGroup label="Dataset Name">
        <BFormInput v-model="clipboardDatasetName" placeholder="My Dataset"></BFormInput>
      </BFormGroup>
      <BFormGroup label="CSV Data">
        <template #label>
          <div class="d-flex justify-content-between align-items-center">
            <span>CSV Data</span>
            <BButton size="sm" @click="pasteFromClipboard">
              <i class="bi bi-clipboard me-1"></i> Paste from Clipboard
            </BButton>
          </div>
        </template>
        <BFormTextarea v-model="clipboardData" :rows="10" placeholder="Paste your CSV data here..."></BFormTextarea>
      </BFormGroup>
      <template #footer>
        <BButton @click="showClipboardImport = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" @click="importFromClipboard">Import</BButton>
      </template>
    </BModal>

    <!-- Fill NA Modal -->
    <BModal v-model="showFillnaModal" title="Fill Missing Values">
      <BFormGroup label="Fill Value">
        <BFormInput v-model="fillValue" placeholder="Enter value to fill"></BFormInput>
      </BFormGroup>
      <template #footer>
        <BButton @click="showFillnaModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" @click="applyOperation('fillna', { method: 'constant', fill_value: fillValue })">Apply</BButton>
      </template>
    </BModal>

    <!-- Compare Modal -->
    <BModal v-model="showCompare" title="Compare Operations" size="lg">
      <p class="text-muted">Compare data before and after a cleaning operation.</p>
      
      <BFormGroup label="Select Operation" class="mb-3">
        <BFormSelect v-model="compareOpId" :options="operationOptions"></BFormSelect>
      </BFormGroup>

      <!-- Comparison Results -->
      <div v-if="comparisonResult" class="comparison-results">
        <!-- Summary Cards -->
        <div class="row g-2 mb-3">
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0 text-success">{{ comparisonResult.changes_summary?.columns_added?.length || 0 }}</h4>
                <small class="text-muted">Columns Added</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0 text-danger">{{ comparisonResult.changes_summary?.columns_removed?.length || 0 }}</h4>
                <small class="text-muted">Columns Removed</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0 text-warning">{{ comparisonResult.changes_summary?.columns_renamed?.length || 0 }}</h4>
                <small class="text-muted">Columns Changed</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0" :class="comparisonResult.changes_summary?.rows_changed > 0 ? 'text-success' : comparisonResult.changes_summary?.rows_changed < 0 ? 'text-danger' : ''">
                  {{ comparisonResult.changes_summary?.rows_changed || 0 }}
                </h4>
                <small class="text-muted">Rows Changed</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Columns Added -->
        <div v-if="comparisonResult.changes_summary?.columns_added?.length" class="mb-3">
          <h6 class="text-success"><i class="bi bi-plus-circle me-1"></i>Columns Added</h6>
          <div class="d-flex flex-wrap gap-1">
            <BBadge v-for="col in comparisonResult.changes_summary.columns_added" :key="col" variant="success">
              {{ col }}
            </BBadge>
          </div>
        </div>

        <!-- Columns Removed -->
        <div v-if="comparisonResult.changes_summary?.columns_removed?.length" class="mb-3">
          <h6 class="text-danger"><i class="bi bi-dash-circle me-1"></i>Columns Removed</h6>
          <div class="d-flex flex-wrap gap-1">
            <BBadge v-for="col in comparisonResult.changes_summary.columns_removed" :key="col" variant="danger">
              {{ col }}
            </BBadge>
          </div>
        </div>

        <!-- Columns Changed -->
        <div v-if="comparisonResult.changes_summary?.columns_renamed?.length" class="mb-3">
          <h6 class="text-warning"><i class="bi bi-pencil me-1"></i>Columns Changed</h6>
          <div class="d-flex flex-wrap gap-1">
            <BBadge v-for="col in comparisonResult.changes_summary.columns_renamed" :key="col.from" variant="warning">
              {{ col.from }} → {{ col.to }}
            </BBadge>
          </div>
        </div>

        <!-- Column Details -->
        <div class="row">
          <div class="col-6">
            <h6>Before ({{ comparisonResult.before_columns?.length || 0 }} columns)</h6>
            <ul class="list-group" style="max-height: 200px; overflow-y: auto;">
              <li v-for="col in comparisonResult.before_columns" :key="col.name" class="list-group-item py-1 small">
                {{ col.name }}
              </li>
            </ul>
          </div>
          <div class="col-6">
            <h6>After ({{ comparisonResult.after_columns?.length || 0 }} columns)</h6>
            <ul class="list-group" style="max-height: 200px; overflow-y: auto;">
              <li v-for="col in comparisonResult.after_columns" :key="col.name" class="list-group-item py-1 small">
                {{ col.name }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-else-if="comparing" class="text-center py-4">
        <div class="spinner-border text-primary"></div>
        <p class="mt-2 text-muted">Loading comparison...</p>
      </div>

      <div v-else class="text-center py-4 text-muted">
        <i class="bi bi-arrow-left-right fs-1"></i>
        <p>Select an operation and click Compare</p>
      </div>

      <template #footer>
        <BButton @click="showCompare = false">Close</BButton>
        <BButton variant="primary" :loading="comparing" :disabled="!compareOpId" @click="loadComparison">
          Compare
        </BButton>
      </template>
    </BModal>

    <!-- History Sidebar -->
    <div v-if="showHistory" class="history-sidebar">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0"><i class="bi bi-clock-history me-2"></i>Operation History</h6>
        <BButton size="sm" variant="outline-secondary" @click="showHistory = false">
          <i class="bi bi-x-lg"></i>
        </BButton>
      </div>
      
      <div v-if="operations.length === 0" class="text-muted text-center py-4">
        <i class="bi bi-inbox fs-4"></i>
        <p class="small mb-0">No operations yet</p>
      </div>
      
      <div v-else class="operation-list" style="max-height: 70vh; overflow-y: auto;">
        <div v-for="op in operations" :key="op.id" class="card mb-2">
          <div class="card-body py-2 px-3">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <span class="badge" :class="op.is_undone ? 'bg-secondary' : 'bg-primary'">
                  {{ op.operation_type }}
                </span>
                <small class="text-muted d-block mt-1">
                  {{ formatDate(op.created_at) }}
                </small>
              </div>
              <BButton v-if="!op.is_undone" size="sm" variant="outline-warning" @click="undoOperation(op.id)">
                Undo
              </BButton>
            </div>
            <div v-if="op.operation_params" class="mt-2">
              <small class="text-muted">{{ formatOperationParams(op.operation_params) }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { BButton, BFormSelect, BFormInput, BFormTextarea, BFormGroup, BBadge, BModal, BDropdown, BDropdownItem } from 'bootstrap-vue-next'
import DataTable from '../components/DataTable.vue'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const datasetId = computed(() => route.params.datasetId)

const apiUrl = getApiUrl()
const toast = useToast()

const loading = ref(true)
const dataset = ref(null)
const data = ref([])
const columns = ref([])
const operations = ref([])
const limit = ref(10)
const page = ref(1)
const totalRows = ref(0)

// Pagination computed properties
const startRow = computed(() => Math.min((page.value - 1) * limit.value + 1, totalRows.value))
const endRow = computed(() => Math.min(page.value * limit.value, totalRows.value))

const searchQuery = ref('')
const showProfile = ref(false)
const showCompare = ref(false)
const showHistory = ref(false)
const showClipboardImport = ref(false)
const showFillnaModal = ref(false)
const showAiModal = ref(false)
const profileData = ref(null)
const comparing = ref(false)
const compareOpId = ref(null)
const comparisonResult = ref(null)
const nullCount = ref(0)
const selectedColumns = ref([])  // Selected columns (click on table headers)
const selectedRows = ref([])  // Selected rows

// Computed fields for BTable - disable sorting to allow column selection
const tableFields = computed(() => {
  return columns.value.map(col => ({
    key: col.field,
    label: col.label,
    sortable: false
  }))
})

// Selected row keys for BTable
const selectedRowKeys = computed(() => {
  return selectedRows.value.map(row => row._index ?? JSON.stringify(row))
})
const showColumnSelector = ref(false)
const fillValue = ref('')
const canUndo = ref(false)
const canRedo = ref(false)
const operating = ref(false)
const aiInstruction = ref('')
const clipboardData = ref('')
const clipboardDatasetName = ref('')

const limitOptions = [
  { value: 10, text: '10 rows' },
  { value: 25, text: '25 rows' },
  { value: 50, text: '50 rows' },
  { value: 100, text: '100 rows' },
  { value: 250, text: '250 rows' },
  { value: 500, text: '500 rows' }
]

const totalPages = computed(() => Math.ceil(totalRows.value / limit.value))

function nextPage() {
  if (page.value < totalPages.value) {
    page.value++
    refreshData()
  }
}

function goToPage(p) {
  if (p < 1) return
  const maxPage = Math.ceil(totalRows / limit.value)
  if (p > maxPage) return
  page.value = p
  tableKey.value++
  refreshData()
}

const columnOptions = computed(() => columns.value.map(c => ({ value: c.field, text: c.label })))

// Toggle column selection (click on table header)
function toggleColumnSelection(field) {
  const idx = selectedColumns.value.indexOf(field)
  if (idx === -1) {
    selectedColumns.value.push(field)
  } else {
    selectedColumns.value.splice(idx, 1)
  }
}

// Handle BTable row selection
function onRowSelected(rows) {
  selectedRows.value = rows
}

// Handle DataTable row click
function onRowClicked({ item, index }) {
  // Toggle selection or handle as needed
  const idx = selectedRows.value.findIndex(r => JSON.stringify(r) === JSON.stringify(item))
  if (idx >= 0) {
    selectedRows.value.splice(idx, 1)
  } else {
    selectedRows.value.push(item)
  }
}

// Handle DataTable pagination
function goToPrev() {
  if (page.value > 1) {
    page.value--
    refreshData()
  }
}

function goToNext() {
  const maxPage = Math.ceil(totalRows.value / limit.value)
  if (page.value < maxPage) {
    page.value++
    refreshData()
  }
}

// Handle DataTable page change - just refresh data (v-model updates page)
function onPageChange(newPage) {
  refreshData()
}

// Handle DataTable header click (for future sorting)
function onHeadClicked(field) {
  // Toggle column selection when clicking column header
  toggleColumnSelection(field.key || field.field)
}

// Check if single-column only operation (like rename)
function isSingleColumnOnly(operation) {
  return ['rename'].includes(operation)
}

const operationOptions = computed(() => operations.value.map(op => ({ value: op.id, text: `${op.operation_type} - ${formatDate(op.created_at)}` })))

// Data from API (already paginated by server)
const paginatedData = computed(() => {
  // Data from API is already limited, no need to slice again
  return data.value
})

// Filtered data (search) applied on top of paginated data
const filteredData = computed(() => {
  if (!searchQuery.value) return paginatedData.value
  const q = searchQuery.value.toLowerCase()
  return paginatedData.value.filter(row => Object.values(row).some(val => String(val).toLowerCase().includes(q)))
})

onMounted(async () => { await refreshData() })

// Watch limit changes - reset to first page and refresh
watch(limit, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    page.value = 1
    refreshData()
  }
})

// Watch for compare modal
watch(showCompare, (val) => {
  if (!val) {
    comparisonResult.value = null
    compareOpId.value = null
  }
})


async function refreshData() {
  loading.value = true
  try {
    // Fetch paginated data from API
    const [previewRes, opsRes] = await Promise.all([
      fetch(`${apiUrl}/api/datasets/${datasetId.value}/preview?limit=${limit.value}&page=${page.value}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      }),
      fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
    ])
    
    if (previewRes.ok) {
      const preview = await previewRes.json()
      data.value = preview.preview_data || []
      columns.value = (preview.columns || []).map(col => ({ field: col.name, label: col.name }))
      dataset.value = preview
      totalRows.value = preview.row_count || 0
      // Don't overwrite page value - it's managed by goToNext/goToPrev
    }
    
    if (opsRes.ok) operations.value = await opsRes.json()
    
    const profileRes = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (profileRes.ok) {
      profileData.value = await profileRes.json()
      nullCount.value = profileData.value.columns?.reduce((sum, c) => sum + c.null_count, 0) || 0
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadComparison() {
  if (!compareOpId.value) return
  comparing.value = true
  comparisonResult.value = null
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/compare/${compareOpId.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      comparisonResult.value = await res.json()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to load comparison')
    }
  } catch (e) { 
    console.error(e)
    toast.error('Failed to load comparison')
  }
  finally { comparing.value = false }
}

function handleRowClick(row) { console.log('Row clicked:', row) }
function handleCellClick(row, col) { console.log('Cell clicked:', row, col) }

async function applyOperation(endpoint, params) {
  if (!selectedColumns.value || selectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  const col = selectedColumns.value[0]
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ column: col, ...params })
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false; showFillnaModal.value = false }
}

async function applyStringOp(operation) {
  if (!selectedColumns.value || selectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/string-operations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ columns: selectedColumns.value, operation })
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}
async function applyDatetimeOp(operation) {
  if (!selectedColumns.value || selectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/datetime-operations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ columns: selectedColumns.value, operation })
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}
async function applyStructuralOp(operation) {
  if (operation === 'rename') {
    // Rename is single-column only
    if (selectedColumns.value.length !== 1) {
      toast.warning('Select exactly 1 column to rename'); return
    }
    const newName = prompt('Enter new column name:')
    if (!newName) return
    const col = selectedColumns.value[0]
    await applyOperation('structural', { operation, column: col, new_name: newName })
  } else if (operation === 'astype') {
    if (!selectedColumns.value || selectedColumns.value.length === 0) {
      toast.warning('No columns selected'); return
    }
    const dtype = prompt('Enter new type (int, float, str, bool):')
    if (!dtype) return
    operating.value = true
    try {
      const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/structural`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ operation, columns: selectedColumns.value, dtype })
      })
      if (res.ok) { 
        const data = await res.json()
        toast.success(data.message || 'Operation applied successfully')
        await refreshData() 
      }
      else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
    } catch (e) { toast.error(e.message) }
    finally { operating.value = false }
  } else if (operation === 'drop') {
    if (!selectedColumns.value || selectedColumns.value.length === 0) {
      toast.warning('No columns selected'); return
    }
    if (!confirm(`Are you sure you want to delete ${selectedColumns.value.length} columns?`)) return
    operating.value = true
    try {
      const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/structural`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ operation, columns: selectedColumns.value })
      })
      if (res.ok) { 
        const data = await res.json()
        toast.success(data.message || 'Operation applied successfully')
        await refreshData() 
        selectedColumns.value = []
      }
      else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
    } catch (e) { toast.error(e.message) }
    finally { operating.value = false }
  }
}
async function applyNumericOp(operation) {
  if (!selectedColumns.value || selectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/numeric`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ columns: selectedColumns.value, operation })
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}
async function applyDedup(type) { await applyOperation(type === 'duplicates' ? 'remove-duplicates' : 'fuzzy-dedupe', {}) }

async function undo() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/undo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { toast.success('Undo successful'); await refreshData() }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function redo() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/redo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { toast.success('Redo successful'); await refreshData() }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function applyAiClean() {
  if (!selectedColumns.value || selectedColumns.value.length === 0) {
    toast.warning('No column selected'); return
  }
  if (!aiInstruction.value) return
  // Send columns (array) for multiple, column (string) for single
  const payload = selectedColumns.value.length === 1
    ? { column: selectedColumns.value[0], instruction: aiInstruction.value, batch_size: 10 }
    : { columns: selectedColumns.value, instruction: aiInstruction.value, batch_size: 10 }
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/ai-clean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(payload)
    })
    if (res.ok) { toast.success('AI cleaning applied'); showAiModal.value = false; await refreshData() }
    else { const err = await res.json(); toast.error(err.detail || 'AI cleaning failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText()
    clipboardData.value = text
    toast.success('Pasted from clipboard')
  } catch (e) { 
    toast.error('Failed to paste: ' + e.message + '. Make sure you are using HTTPS.') 
  }
}

async function importFromClipboard() {
  if (!clipboardData.value.trim()) return
  operating.value = true
  try {
    const blob = new Blob([clipboardData.value], { type: 'text/csv' })
    const file = new File([blob], 'clipboard.csv', { type: 'text/csv' })
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', route.params.id)
    if (clipboardDatasetName.value) formData.append('name', clipboardDatasetName.value)
    
    const res = await fetch(`${apiUrl}/api/datasets/import`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { toast.success('Data imported successfully'); showClipboardImport.value = false; clipboardData.value = ''; await refreshData() }
    else throw new Error('Import failed')
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function copyToClipboard() {
  if (!data.value || data.value.length === 0) { toast.warning('No data to copy'); return }
  try {
    const headers = Object.keys(data.value[0])
    const csvRows = [headers.join(','), ...data.value.map(row => headers.map(h => {
      const val = row[h]
      if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) return `"${val.replace(/"/g, '""')}"`
      return val ?? ''
    }).join(','))]
    await navigator.clipboard.writeText(csvRows.join('\n'))
    toast.success('Data copied to clipboard')
  } catch (e) { toast.error('Failed to copy: ' + e.message + '. Make sure you are using HTTPS.') }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatOperationParams(params) {
  if (!params) return ''
  try {
    const p = typeof params === 'string' ? JSON.parse(params) : params
    const parts = []
    if (p.column) parts.push(`column: ${p.column}`)
    if (p.columns) parts.push(`columns: ${p.columns.join(', ')}`)
    if (p.operation) parts.push(`op: ${p.operation}`)
    if (p.method) parts.push(`method: ${p.method}`)
    if (p.new_name) parts.push(`→ ${p.new_name}`)
    return parts.join(' | ')
  } catch {
    return ''
  }
}

async function undoOperation(opId) {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/undo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ operation_id: opId })
    })
    if (res.ok) {
      toast.success('Operation undone')
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to undo')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}
</script>

<style scoped>
.data-viewer {
  background: #f8f9fa;
  min-height: 100vh;
}
.history-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 350px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 10px rgba(0,0,0,0.1);
  z-index: 99999 !important;
  overflow-y: auto;
  padding-top: 60px;
}
</style>
