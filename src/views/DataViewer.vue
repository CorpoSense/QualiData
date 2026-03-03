<template>
  <div class="data-viewer">
    <!-- Operations Toolbar -->
    <div class="card mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2">
            <BFormSelect v-model="limit" :options="limitOptions" size="sm" style="width: auto;"></BFormSelect>
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
            <BDropdownItem @click="applyStructuralOp('rename')">
              <i class="bi bi-pencil-square me-2"></i>Rename column
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

          <BButton size="sm" variant="primary" @click="showAiModal = true">
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

    <!-- Stats Bar -->
    <div class="d-flex gap-3 mb-3 flex-wrap">
      <BBadge variant="secondary" pill>{{ data.length }} rows</BBadge>
      <BBadge variant="secondary" pill>{{ columns.length }} columns</BBadge>
      <BBadge variant="warning" pill>{{ nullCount }} nulls</BBadge>
      <BBadge v-if="selectedColumn" variant="info" pill>
        Selected: {{ selectedColumn }}
      </BBadge>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Data Table -->
    <div v-else class="card">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th v-for="col in columns" :key="col.field" @click="selectedColumn = col.field" style="cursor: pointer;">
                {{ col.label }}
                <i v-if="selectedColumn === col.field" class="bi bi-check-circle-fill text-primary"></i>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in filteredData" :key="idx" @click="handleRowClick(row)">
              <td v-for="col in columns" :key="col.field" @click.stop="handleCellClick(row, col)">
                {{ row[col.field] }}
              </td>
            </tr>
          </tbody>
        </table>
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
      <BFormGroup label="Column">
        <BFormSelect v-model="selectedColumn" :options="columnOptions"></BFormSelect>
      </BFormGroup>
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
    <BModal v-model="showCompare" title="Compare Operations">
      <p class="text-muted">Compare current data with a previous operation.</p>
      <BFormGroup label="Select Operation">
        <BFormSelect v-model="compareOpId" :options="operationOptions"></BFormSelect>
      </BFormGroup>
      <template #footer>
        <BButton @click="showCompare = false">Cancel</BButton>
        <BButton variant="primary" :loading="comparing" @click="loadComparison">Compare</BButton>
      </template>
    </BModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { BButton, BFormSelect, BFormInput, BFormTextarea, BFormGroup, BBadge, BModal, BDropdown, BDropdownItem } from 'bootstrap-vue-next'

const props = defineProps({
  datasetId: { type: Number, required: true }
})

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(true)
const dataset = ref(null)
const data = ref([])
const columns = ref([])
const operations = ref([])
const limit = ref(25)
const searchQuery = ref('')
const showProfile = ref(false)
const showCompare = ref(false)
const showClipboardImport = ref(false)
const showFillnaModal = ref(false)
const showAiModal = ref(false)
const profileData = ref(null)
const comparing = ref(false)
const compareOpId = ref(null)
const nullCount = ref(0)
const selectedColumn = ref(null)
const fillValue = ref('')
const canUndo = ref(false)
const canRedo = ref(false)
const operating = ref(false)
const aiInstruction = ref('')
const clipboardData = ref('')
const clipboardDatasetName = ref('')

const limitOptions = [
  { value: 25, text: '25 rows' },
  { value: 50, text: '50 rows' },
  { value: 100, text: '100 rows' }
]

const columnOptions = computed(() => columns.value.map(c => ({ value: c.field, text: c.label })))

const operationOptions = computed(() => operations.value.map(op => ({ value: op.id, text: `${op.operation_type} - ${formatDate(op.created_at)}` })))

const filteredData = computed(() => {
  if (!searchQuery.value) return data.value
  const q = searchQuery.value.toLowerCase()
  return data.value.filter(row => Object.values(row).some(val => String(val).toLowerCase().includes(q)))
})

onMounted(async () => { await refreshData() })
watch(limit, refreshData)

async function refreshData() {
  loading.value = true
  try {
    const [previewRes, opsRes] = await Promise.all([
      fetch(`${apiUrl}/api/datasets/${props.datasetId}/preview?limit=${limit.value}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      }),
      fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
    ])
    
    if (previewRes.ok) {
      const preview = await previewRes.json()
      data.value = preview.preview_data || []
      columns.value = (preview.columns || []).map(col => ({ field: col.name, label: col.name }))
      dataset.value = preview
    }
    
    if (opsRes.ok) operations.value = await opsRes.json()
    
    const profileRes = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/profile`, {
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
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/compare/${compareOpId.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const comparison = await res.json()
      console.log('Comparison:', comparison)
    }
  } catch (e) { console.error(e) }
  finally { comparing.value = false }
}

function handleRowClick(row) { console.log('Row clicked:', row) }
function handleCellClick(row, col) { console.log('Cell clicked:', row, col) }

async function applyOperation(endpoint, params) {
  const col = selectedColumn.value || columns.value[0]?.field
  if (!col) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ column: col, ...params })
    })
    if (res.ok) { alert('Operation applied successfully'); await refreshData() }
    else { const err = await res.json(); alert(err.detail || 'Operation failed') }
  } catch (e) { alert(e.message) }
  finally { operating.value = false; showFillnaModal.value = false }
}

async function applyStringOp(operation) { await applyOperation('string-operations', { operation }) }
async function applyDatetimeOp(operation) { await applyOperation('datetime-operations', { operation }) }
async function applyStructuralOp(operation) { await applyOperation('structural', { operation }) }
async function applyNumericOp(operation) { await applyOperation('numeric', { operation }) }
async function applyDedup(type) { await applyOperation(type === 'duplicates' ? 'remove-duplicates' : 'fuzzy-dedupe', {}) }

async function undo() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/undo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { alert('Undo successful'); await refreshData() }
  } catch (e) { alert(e.message) }
  finally { operating.value = false }
}

async function redo() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/redo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { alert('Redo successful'); await refreshData() }
  } catch (e) { alert(e.message) }
  finally { operating.value = false }
}

async function applyAiClean() {
  const col = selectedColumn.value || columns.value[0]?.field
  if (!col || !aiInstruction.value) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/ai-clean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ column: col, instruction: aiInstruction.value, batch_size: 10 })
    })
    if (res.ok) { alert('AI cleaning applied'); showAiModal.value = false; await refreshData() }
    else { const err = await res.json(); alert(err.detail || 'AI cleaning failed') }
  } catch (e) { alert(e.message) }
  finally { operating.value = false }
}

async function importFromClipboard() {
  if (!clipboardData.value.trim()) return
  operating.value = true
  try {
    const blob = new Blob([clipboardData.value], { type: 'text/csv' })
    const file = new File([blob], 'clipboard.csv', { type: 'text/csv' })
    const formData = new FormData()
    formData.append('file', file)
    if (clipboardDatasetName.value) formData.append('name', clipboardDatasetName.value)
    
    const res = await fetch(`${apiUrl}/api/datasets/import`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { alert('Data imported successfully'); showClipboardImport.value = false; clipboardData.value = ''; await refreshData() }
    else throw new Error('Import failed')
  } catch (e) { alert(e.message) }
  finally { operating.value = false }
}

async function copyToClipboard() {
  if (!data.value || data.value.length === 0) { alert('No data to copy'); return }
  try {
    const headers = Object.keys(data.value[0])
    const csvRows = [headers.join(','), ...data.value.map(row => headers.map(h => {
      const val = row[h]
      if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) return `"${val.replace(/"/g, '""')}"`
      return val ?? ''
    }).join(','))]
    await navigator.clipboard.writeText(csvRows.join('\n'))
    alert('Data copied to clipboard')
  } catch (e) { alert('Failed to copy: ' + e.message) }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}
</script>

<style scoped>
.data-viewer {
  background: #f8f9fa;
  min-height: 100vh;
}
</style>
