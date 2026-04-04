<template>
  <div class="pivot-table-container">
    <!-- Configuration Sidebar (Collapsible) -->
    <div class="pivot-sidebar" :class="{ collapsed: !showSidebar }">
      <div class="sidebar-header">
        <h6 class="mb-0">
        <BButton size="sm" variant="link" @click="showSidebar = !showSidebar" class="px-0">
          <i :class="showSidebar ? 'bi bi-chevron-left' : 'bi bi-chevron-right'"></i>
        </BButton>
          <span v-show="showSidebar" class="p-2">
              Configuration
          </span>
        </h6>
      </div>

      <div v-if="showSidebar" class="sidebar-content">

        <!-- Action Buttons -->
        <div class="config-section mt-2">
          <BButton
            variant="outline-secondary"
            size="sm"
            class="w-50"
            @click="resetToDefaults"
          >
            <i class="bi bi-arrow-counterclockwise me-1"></i>Reset
          </BButton>          
          <BButton
            variant="primary"
            size="sm"
            class="w-50"
            @click="applyPivot"
            :loading="loading"
            :disabled="!canApply"
          >
            <i class="bi bi-play-fill me-1"></i>Apply
          </BButton>
        </div>

        <!-- Auto-Reload -->
        <div class="config-section">
          <div class="form-check form-switch">
            <input
              class="form-check-input"
              type="checkbox"
              v-model="config.autoReload"
              id="auto-reload"
            >
            <label class="form-check-label small" for="auto-reload">
              Auto-reload
            </label>
          </div>
        </div>        

        <!-- Include Nulls -->
        <div class="config-section">
          <div class="form-check form-switch">
            <input
              class="form-check-input"
              type="checkbox"
              v-model="config.includeNulls"
              id="include-nulls"
            >
            <label class="form-check-label small" for="include-nulls">
              Include null values
            </label>
          </div>
        </div>
                
        <!-- Available Columns (Drag Source) -->
        <div class="config-section">
          <label class="form-label small fw-bold">
            <i class="bi bi-columns me-1"></i>Available Columns
          </label>
          <div class="available-columns">
            <div
              v-for="col in availableColumns"
              :key="col.field"
              class="column-item"
              draggable="true"
              @dragstart="onDragStart($event, col.field, 'available')"
              :title="col.label || col.field"
            >
              <i class="bi bi-grip-vertical me-1 text-muted"></i>
              {{ col.label || col.field }}
            </div>
            <div v-if="availableColumns.length === 0" class="text-muted small">
              All columns assigned
            </div>
          </div>
        </div>
        
        <!-- Index Columns (Rows) -->
        <div class="config-section">
          <label class="form-label small fw-bold">
            <i class="bi bi-list-ul me-1"></i>Index Columns (Rows)
          </label>
          <div class="column-drop-zone" @drop="onDropIndex" @dragover.prevent>
            <div
              v-for="col in config.indexColumns"
              :key="col"
              class="column-tag"
              draggable="true"
              @dragstart="onDragStart($event, col, 'index')"
            >
              {{ col }}
              <button class="btn-close btn-close-sm ms-1" @click="removeIndexColumn(col)"></button>
            </div>
            <div v-if="config.indexColumns.length === 0" class="text-muted small">
              Drag columns here
            </div>
          </div>
        </div>

        <!-- Column Columns (Columns) -->
        <div class="config-section">
          <label class="form-label small fw-bold">
            <i class="bi bi-layout-three-columns me-1"></i>Column Columns
          </label>
          <div class="column-drop-zone" @drop="onDropColumn" @dragover.prevent>
            <div
              v-for="col in config.columnColumns"
              :key="col"
              class="column-tag"
              draggable="true"
              @dragstart="onDragStart($event, col, 'column')"
            >
              {{ col }}
              <button class="btn-close btn-close-sm ms-1" @click="removeColumnColumn(col)"></button>
            </div>
            <div v-if="config.columnColumns.length === 0" class="text-muted small">
              Drag columns here
            </div>
          </div>
        </div>

        <!-- Value Column -->
        <div class="config-section">
          <label class="form-label small fw-bold">
            <i class="bi bi-calculator me-1"></i>Value Column
          </label>
          <BFormSelect v-model="config.valueColumn" size="sm" :options="valueColumnOptions">
            <template #first>
              <option value="">Select column...</option>
            </template>
          </BFormSelect>
        </div>

        <!-- Aggregation Functions -->
        <div class="config-section">
          <label class="form-label small fw-bold">
            <i class="bi bi-bar-chart me-1"></i>Aggregation
          </label>
          <div class="d-flex flex-wrap gap-1">
            <div v-for="agg in aggregationOptions" :key="agg.value" class="form-check form-check-inline">
              <input
                class="form-check-input"
                type="radio"
                :id="'agg-' + agg.value"
                :value="agg.value"
                v-model="config.aggfunc"
              >
              <label class="form-check-label small" :for="'agg-' + agg.value">
                {{ agg.text }}
              </label>
            </div>
          </div>
        </div>

        <!-- Binning Options -->
        <div class="config-section">
          <div class="form-check form-switch mb-2">
            <input
              class="form-check-input"
              type="checkbox"
              v-model="config.binContinuous"
              id="bin-continuous"
            >
            <label class="form-check-label small" for="bin-continuous">
              Bin continuous columns
            </label>
          </div>

          <div v-if="config.binContinuous">
            <label class="form-label small">Bins: {{ config.bins }}</label>
            <BFormInput
              v-model.number="config.bins"
              type="range"
              min="2"
              max="20"
              step="1"
              size="sm"
            />
            <div class="d-flex justify-content-between small text-muted">
              <span>2</span>
              <span>20</span>
            </div>

            <label class="form-label small mt-2">Strategy</label>
            <BFormSelect v-model="config.binningStrategy" size="sm">
              <option value="equal_width">Equal Width</option>
              <option value="equal_freq">Equal Frequency</option>
            </BFormSelect>
          </div>
        </div>

        <!-- Unique Threshold -->
        <div class="config-section">
          <label class="form-label small fw-bold">
            Unique Threshold: {{ config.uniqueThreshold }}
          </label>
          <BFormInput
            v-model.number="config.uniqueThreshold"
            type="range"
            min="5"
            max="100"
            step="5"
            size="sm"
          />
          <div class="d-flex justify-content-between small text-muted">
            <span>5</span>
            <span>100</span>
          </div>
          <small class="text-muted">
            Max unique values to consider as categorical
          </small>
        </div>

      </div>
    </div>

    <!-- Pivot Display Area -->
    <div class="pivot-display">
      <!-- Loading Overlay -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Creating pivot table...</p>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="alert alert-danger m-3">
        <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
      </div>

      <!-- Pivot Table -->
      <div v-if="pivotData && !loading" class="pivot-content">
        <!-- Summary Stats -->
        <div class="pivot-summary mb-3 p-2 bg-light rounded">
          <div class="d-flex flex-wrap gap-3 align-items-center">
            <span class="badge bg-primary">
              {{ pivotData.summary.total_rows }} rows
            </span>
            <span class="badge bg-primary">
              {{ pivotData.summary.total_columns }} columns
            </span>
            <span class="badge bg-secondary">
              {{ pivotData.summary.aggregation }}
            </span>
            <span v-if="pivotData.summary.binned_columns.length" class="badge bg-info">
              Binned: {{ pivotData.summary.binned_columns.join(', ') }}
            </span>
          </div>
        </div>

        <!-- Export Buttons -->
        <div class="d-flex gap-2 mb-3">
          <BButton size="sm" variant="outline-secondary" @click="exportCSV">
            <i class="bi bi-download me-1"></i>CSV
          </BButton>
          <BButton size="sm" variant="outline-secondary" @click="copyAsMarkdown">
            <i class="bi bi-clipboard me-1"></i>Markdown
          </BButton>
          <BButton size="sm" variant="outline-secondary" @click="copyAsJSON">
            <i class="bi bi-braces me-1"></i>JSON
          </BButton>
        </div>

        <!-- Table -->
        <div class="table-responsive">
          <table class="table table-bordered table-sm pivot-table">
            <thead>
              <tr>
                <th v-for="col in pivotData.columns" :key="col" class="text-nowrap">
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in pivotData.pivot" :key="idx">
                <td v-for="col in pivotData.columns" :key="col">
                  {{ formatValue(row[col]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!pivotData && !loading && !error" class="text-center text-muted py-5">
        <i class="bi bi-table fs-1"></i>
        <p class="mt-2">Configure and apply to create a pivot table</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { BButton, BFormSelect, BFormInput } from 'bootstrap-vue-next'
import { useToast } from '@/composables/useToast'
import { getApiUrl } from '@/utils/api'

const props = defineProps({
  datasetId: {
    type: String,
    required: true
  },
  columns: {
    type: Array,
    default: () => []
  },
  selectedColumns: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

const toast = useToast()
const apiUrl = getApiUrl()

// State
const loading = ref(false)
const error = ref(null)
const pivotData = ref(null)
const showSidebar = ref(true)
const columnTypes = ref({ categorical: [], continuous: [], datetime: [] })

// Configuration
const defaultConfig = {
  indexColumns: [],
  columnColumns: [],
  valueColumn: '',
  aggfunc: 'count',
  binContinuous: true,
  bins: 10,
  binningStrategy: 'equal_width',
  includeNulls: false,
  uniqueThreshold: 20,
  autoReload: false
}

const config = ref({ ...defaultConfig })

// Computed
const aggregationOptions = [
  { value: 'count', text: 'Count' },
  { value: 'sum', text: 'Sum' },
  { value: 'mean', text: 'Mean' },
  { value: 'median', text: 'Median' },
  { value: 'min', text: 'Min' },
  { value: 'max', text: 'Max' },
  { value: 'std', text: 'Std' }
]

const valueColumnOptions = computed(() => {
  return props.columns.map(col => ({
    value: col.field,
    text: col.label || col.field
  }))
})

const availableColumns = computed(() => {
  return props.columns.filter(col => {
    const field = col.field
    return !config.value.indexColumns.includes(field) && 
           !config.value.columnColumns.includes(field)
  })
})

const canApply = computed(() => {
  return (
    config.value.indexColumns.length > 0 &&
    config.value.columnColumns.length > 0 &&
    config.value.valueColumn
  )
})

// Debounce timer for auto-reload
let applyDebounceTimer = null

function debouncedApply() {
  if (applyDebounceTimer) {
    clearTimeout(applyDebounceTimer)
  }
  applyDebounceTimer = setTimeout(() => {
    applyPivot(true) // true = silent mode (no toast)
    applyDebounceTimer = null
  }, 300)
}

// Methods
function onDragStart(event, column, source) {
  event.dataTransfer.setData('text/plain', JSON.stringify({ column, source }))
  event.dataTransfer.effectAllowed = 'move'
}

function onDropIndex(event) {
  event.preventDefault()
  try {
    const data = JSON.parse(event.dataTransfer.getData('text/plain'))
    if (data.column && !config.value.indexColumns.includes(data.column)) {
      config.value.indexColumns.push(data.column)
      // Remove from other zones
      config.value.columnColumns = config.value.columnColumns.filter(c => c !== data.column)
    }
  } catch (e) {
    // Ignore
  }
}

function onDropColumn(event) {
  event.preventDefault()
  try {
    const data = JSON.parse(event.dataTransfer.getData('text/plain'))
    if (data.column && !config.value.columnColumns.includes(data.column)) {
      config.value.columnColumns.push(data.column)
      // Remove from other zones
      config.value.indexColumns = config.value.indexColumns.filter(c => c !== data.column)
    }
  } catch (e) {
    // Ignore
  }
}

function removeIndexColumn(column) {
  config.value.indexColumns = config.value.indexColumns.filter(c => c !== column)
}

function removeColumnColumn(column) {
  config.value.columnColumns = config.value.columnColumns.filter(c => c !== column)
}

async function fetchColumnTypes() {
  try {
    const res = await fetch(
      `${apiUrl}/api/datasets/${props.datasetId}/pivot/columns?unique_threshold=${config.value.uniqueThreshold}`,
      {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      }
    )
    if (res.ok) {
      columnTypes.value = await res.json()
    }
  } catch (e) {
    // Silent fail
  }
}

async function applyPivot(silent = false) {
  if (!canApply.value) return

  loading.value = true
  error.value = null

  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/pivot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        index_columns: config.value.indexColumns,
        column_columns: config.value.columnColumns,
        value_column: config.value.valueColumn,
        aggfunc: config.value.aggfunc,
        bin_continuous: config.value.binContinuous,
        bins: config.value.bins,
        binning_strategy: config.value.binningStrategy,
        include_nulls: config.value.includeNulls,
        unique_threshold: config.value.uniqueThreshold
      })
    })

    if (res.ok) {
      pivotData.value = await res.json()
      if (!silent) {
        toast.success('Pivot table created')
      }
    } else {
      const err = await res.json()
      error.value = err.detail || 'Failed to create pivot table'
      if (!silent) {
        toast.error(error.value)
      }
    }
  } catch (e) {
    error.value = e.message
    if (!silent) {
      toast.error(e.message)
    }
  } finally {
    loading.value = false
  }
}

function resetToDefaults() {
  config.value = { ...defaultConfig }
  pivotData.value = null
  error.value = null
}

function formatValue(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value : value.toFixed(2)
  }
  return String(value)
}

function exportCSV() {
  if (!pivotData.value) return

  const headers = pivotData.value.columns
  const rows = pivotData.value.pivot.map(row =>
    headers.map(h => {
      const val = row[h]
      if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
        return `"${val.replace(/"/g, '""')}"`
      }
      return val ?? ''
    }).join(',')
  )

  const csv = [headers.join(','), ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'pivot-table.csv'
  a.click()
  URL.revokeObjectURL(url)
  toast.success('CSV exported')
}

function copyAsMarkdown() {
  if (!pivotData.value) return

  const headers = pivotData.value.columns
  const headerRow = '| ' + headers.join(' | ') + ' |'
  const separatorRow = '| ' + headers.map(() => '---').join(' | ') + ' |'
  const dataRows = pivotData.value.pivot.map(row =>
    '| ' + headers.map(h => formatValue(row[h])).join(' | ') + ' |'
  )

  const markdown = [headerRow, separatorRow, ...dataRows].join('\n')
  navigator.clipboard.writeText(markdown)
  toast.success('Copied as Markdown')
}

function copyAsJSON() {
  if (!pivotData.value) return

  const json = JSON.stringify(pivotData.value.pivot, null, 2)
  navigator.clipboard.writeText(json)
  toast.success('Copied as JSON')
}

// Watch for auto-reload with config changes
watch(
  () => props.selectedColumns,
  (newCols) => {
    if (newCols.length > 0) {
      // Auto-populate with selected columns (only when not already set)
      if (newCols.length >= 2) {
        config.value.indexColumns = [newCols[0]]
        config.value.columnColumns = [newCols[1]]
        if (newCols.length >= 3 && !config.value.valueColumn) {
          config.value.valueColumn = newCols[2]
        }
      }
      // Trigger auto-reload if enabled
      if (config.value.autoReload && canApply.value) {
        debouncedApply()
      }
    }
  },
  { immediate: true }
)

// Deep watcher for config changes - triggers auto-reload
watch(
  () => config.value,
  (newConfig, oldConfig) => {
    if (!config.value.autoReload) return
    if (!canApply.value) return
    
    // Check if any significant config changed
    const significantChanges = [
      newConfig.indexColumns,
      newConfig.columnColumns,
      newConfig.valueColumn,
      newConfig.aggfunc,
      newConfig.binContinuous,
      newConfig.bins,
      newConfig.binningStrategy,
      newConfig.includeNulls
    ]
    
    // Trigger auto-reload
    debouncedApply()
  },
  { deep: true }
)

// Watch for dataset changes (e.g., after cleaning operations)
watch(
  () => props.datasetId,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      // Dataset changed, reload if auto-reload is enabled
      if (config.value.autoReload && canApply.value) {
        debouncedApply()
      }
    }
  }
)

// Initial load
onMounted(() => {
  fetchColumnTypes()
  // Pre-populate with selected columns if available
  if (props.selectedColumns.length >= 2) {
    config.value.indexColumns = [props.selectedColumns[0]]
    config.value.columnColumns = [props.selectedColumns[1]]
    if (props.selectedColumns.length >= 3) {
      config.value.valueColumn = props.selectedColumns[2]
    }
  }
})
</script>

<style scoped>
.pivot-table-container {
  display: flex;
  height: 100%;
  min-height: 400px;
}

.pivot-sidebar {
  width: 280px;
  min-width: 280px;
  border-right: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  transition: width 0.2s, min-width 0.2s;
}

.pivot-sidebar.collapsed {
  width: 40px;
  min-width: 40px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.config-section {
  margin-bottom: 16px;
}

.column-drop-zone {
  min-height: 60px;
  border: 2px dashed #cbd5e1;
  border-radius: 6px;
  padding: 8px;
  background: white;
  transition: border-color 0.2s;
}

.column-drop-zone:hover {
  border-color: #3b82f6;
}

.column-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background: #e0e7ff;
  border-radius: 4px;
  font-size: 0.85rem;
  margin: 2px;
  cursor: grab;
}

.column-tag:active {
  cursor: grabbing;
}

.pivot-display {
  flex: 1;
  overflow: auto;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.pivot-content {
  padding: 16px;
}

.pivot-summary {
  font-size: 0.9rem;
}

.pivot-table {
  font-size: 0.85rem;
}

.pivot-table th {
  background: #f1f5f9;
  font-weight: 600;
  white-space: nowrap;
}

.pivot-table td {
  white-space: nowrap;
}

.available-columns {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.column-item {
  display: flex;
  align-items: center;
  padding: 6px 10px;
  font-size: 0.85rem;
  cursor: grab;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.15s;
}

.column-item:last-child {
  border-bottom: none;
}

.column-item:hover {
  background: #f1f5f9;
}

.column-item:active {
  cursor: grabbing;
  background: #e2e8f0;
}

.column-item i {
  font-size: 0.75rem;
}
</style>
