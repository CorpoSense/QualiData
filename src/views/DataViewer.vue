<template>
  <div class="data-viewer">
    <!-- Operations Toolbar -->
    <div class="box mb-3">
      <div class="is-flex is-justify-content-space-between is-align-items-center mb-3">
        <div class="is-flex is-align-items-center">
          <b-field class="mb-0 mr-3">
            <b-select v-model="limit" size="is-small">
              <option :value="25">25 rows</option>
              <option :value="50">50 rows</option>
              <option :value="100">100 rows</option>
            </b-select>
          </b-field>
          <b-button size="is-small" @click="refreshData" icon-left="refresh">Refresh</b-button>
        </div>
        
        <div class="is-flex is-align-items-center">
          <b-field class="mb-0 mr-2">
            <b-input v-model="searchQuery" size="is-small" placeholder="Search..." icon="magnify"></b-input>
          </b-field>
          <b-button size="is-small" type="is-info" @click="showProfile = true" icon-left="chart-bar">
            Profile
          </b-button>
          <b-button size="is-small" type="is-success" @click="showCompare = true" icon-left="compare">
            Compare
          </b-button>
          <b-button size="is-small" type="is-warning" outlined @click="showClipboardImport = true" icon-left="content-paste">
            Paste
          </b-button>
          <b-button size="is-small" type="is-warning" outlined @click="copyToClipboard" icon-left="content-copy">
            Copy
          </b-button>
        </div>
      </div>

      <!-- Operation Buttons -->
      <div class="operations-bar">
        <b-dropdown>
          <button class="button is-small" slot="trigger">
            <b-icon icon="eraser"></b-icon>
            <span>Missing Values</span>
            <b-icon icon="menu-down"></b-icon>
          </button>
          <b-dropdown-item @click="applyOperation('fillna', { method: 'drop' })">
            <b-icon icon="trash-can-outline" size="is-small"></b-icon>
            Drop rows with nulls
          </b-dropdown-item>
          <b-dropdown-item @click="showFillnaModal = true">
            <b-icon icon="pencil-outline" size="is-small"></b-icon>
            Fill with value...
          </b-dropdown-item>
          <b-dropdown-item @click="applyOperation('fillna', { method: 'forward' })">
            <b-icon icon="arrow-down" size="is-small"></b-icon>
            Forward fill
          </b-dropdown-item>
          <b-dropdown-item @click="applyOperation('fillna', { method: 'backward' })">
            <b-icon icon="arrow-up" size="is-small"></b-icon>
            Backward fill
          </b-dropdown-item>
        </b-dropdown>

        <b-dropdown>
          <button class="button is-small" slot="trigger">
            <b-icon icon="format-text"></b-icon>
            <span>String Ops</span>
            <b-icon icon="menu-down"></b-icon>
          </button>
          <b-dropdown-item @click="applyStringOp('strip')">
            <b-icon icon="format-clear" size="is-small"></b-icon>
            Trim whitespace
          </b-dropdown-item>
          <b-dropdown-item @click="applyStringOp('lower')">
            <b-icon icon="format-letter-case-lower" size="is-small"></b-icon>
            Lowercase
          </b-dropdown-item>
          <b-dropdown-item @click="applyStringOp('upper')">
            <b-icon icon="format-letter-case-upper" size="is-small"></b-icon>
            Uppercase
          </b-dropdown-item>
          <b-dropdown-item @click="applyStringOp('title')">
            <b-icon icon="format-letter-case" size="is-small"></b-icon>
            Title case
          </b-dropdown-item>
          <b-dropdown-item @click="applyStringOp('capitalize')">
            <b-icon icon="format-letter-spacing" size="is-small"></b-icon>
            Capitalize
          </b-dropdown-item>
        </b-dropdown>

        <b-dropdown>
          <button class="button is-small" slot="trigger">
            <b-icon icon="calendar"></b-icon>
            <span>Date Ops</span>
            <b-icon icon="menu-down"></b-icon>
          </button>
          <b-dropdown-item @click="applyDatetimeOp('parse-datetime')">
            <b-icon icon="calendar-clock" size="is-small"></b-icon>
            Parse datetime
          </b-dropdown-item>
          <b-dropdown-item @click="applyDatetimeOp('extract-year')">
            <b-icon icon="calendar-blank" size="is-small"></b-icon>
            Extract year
          </b-dropdown-item>
          <b-dropdown-item @click="applyDatetimeOp('extract-month')">
            <b-icon icon="calendar-month" size="is-small"></b-icon>
            Extract month
          </b-dropdown-item>
          <b-dropdown-item @click="applyDatetimeOp('extract-day')">
            <b-icon icon="calendar-blank-outline" size="is-small"></b-icon>
            Extract day
          </b-dropdown-item>
        </b-dropdown>

        <b-dropdown>
          <button class="button is-small" slot="trigger">
            <b-icon icon="content-copy"></b-icon>
            <span>Structure</span>
            <b-icon icon="menu-down"></b-icon>
          </button>
          <b-dropdown-item @click="applyStructuralOp('fix-case')">
            <b-icon icon="format-letter-case" size="is-small"></b-icon>
            Fix case errors
          </b-dropdown-item>
          <b-dropdown-item @click="applyStructuralOp('trim-whitespace')">
            <b-icon icon="format-clear" size="is-small"></b-icon>
            Trim whitespace
          </b-dropdown-item>
          <b-dropdown-item @click="applyStructuralOp('fix-typos')">
            <b-icon icon="spellcheck" size="is-small"></b-icon>
            Fix typos
          </b-dropdown-item>
          <b-dropdown-item @click="applyStructuralOp('standardize-values')">
            <b-icon icon="format-list-bulleted" size="is-small"></b-icon>
            Standardize values
          </b-dropdown-item>
        </b-dropdown>

        <b-button size="is-small" type="is-primary" @click="showAiModal = true" icon-left="robot">
          AI Clean
        </b-button>

        <div class="is-flex is-align-items-center ml-auto">
          <b-button size="is-small" type="is-warning" :disabled="!canUndo" @click="undo" icon-left="undo">
            Undo
          </b-button>
          <b-button size="is-small" type="is-warning" :disabled="!canRedo" @click="redo" icon-left="redo">
            Redo
          </b-button>
        </div>
      </div>
    </div>

    <!-- Column Selection -->
    <div v-if="selectedColumn" class="notification is-info is-light mb-3 py-2">
      <b-icon icon="table-column"></b-icon>
      <span class="ml-2">Operating on column: <strong>{{ selectedColumn }}</strong></span>
      <b-button class="is-small is-light ml-2" @click="selectedColumn = null">Clear</b-button>
    </div>

    <!-- Data Table -->
    <div class="box table-container">
      <div v-if="loading" class="has-text-centered py-6">
        <b-icon icon="loading" size="is-large" spin></b-icon>
      </div>
      
      <b-table
        v-else
        :data="filteredData"
        :columns="columns"
        :per-page="limit"
        paginated
        sticky-header
        :height="'500px'"
        :narrowed="true"
        :loading="loading"
        @click="handleCellClick"
      >
        <template #empty>
          <div class="has-text-centered py-4">
            <p class="has-text-grey">No data available</p>
          </div>
        </template>
      </b-table>
    </div>

    <!-- Summary Stats -->
    <div class="columns mt-3">
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Total Rows</p>
          <p class="title is-5">{{ dataset?.row_count || 0 }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Columns</p>
          <p class="title is-5">{{ columns.length }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Null Values</p>
          <p class="title is-5">{{ nullCount }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Duplicates</p>
          <p class="title is-5">{{ duplicateCount }}</p>
        </div>
      </div>
    </div>

    <!-- Profile Modal -->
    <b-modal v-model="showProfile" :has-modal-card="true" :width="'80%'">
      <div class="modal-card" style="width: 80%">
        <header class="modal-card-head">
          <p class="modal-card-title">Column Profile</p>
          <button class="delete" @click="showProfile = false"></button>
        </header>
        <section class="modal-card-body">
          <div v-if="profileData" class="columns is-multiline">
            <div v-for="col in profileData.columns" :key="col.name" class="column is-4">
              <div class="box">
                <h4 class="title is-6">{{ col.name }}</h4>
                <p><strong>Type:</strong> {{ col.dtype }}</p>
                <p><strong>Nulls:</strong> {{ col.null_count }} ({{ col.null_pct }}%)</p>
                <p><strong>Unique:</strong> {{ col.unique_count }}</p>
                <div v-if="col.type === 'numeric'">
                  <p><strong>Min:</strong> {{ col.min }}</p>
                  <p><strong>Max:</strong> {{ col.max }}</p>
                  <p><strong>Mean:</strong> {{ col.mean?.toFixed(2) }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </b-modal>

    <!-- Compare Modal -->
    <b-modal v-model="showCompare" :has-modal-card="true">
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Compare Operations</p>
          <button class="delete" @click="showCompare = false"></button>
        </header>
        <section class="modal-card-body">
          <b-field label="Select Operation">
            <b-select v-model="compareOpId" expanded>
              <option v-for="op in operations" :key="op.id" :value="op.id">
                {{ op.operation_type }} - {{ formatDate(op.created_at) }}
              </option>
            </b-select>
          </b-field>
          <b-button type="is-primary" :loading="comparing" @click="loadComparison">Compare</b-button>
        </section>
      </div>
    </b-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

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
const duplicateCount = ref(0)
const selectedColumn = ref(null)
const fillValue = ref('')
const canUndo = ref(false)
const canRedo = ref(false)
const operating = ref(false)
const aiInstruction = ref('')
const clipboardData = ref('')
const clipboardDatasetName = ref('')

const filteredData = computed(() => {
  if (!searchQuery.value) return data.value
  const q = searchQuery.value.toLowerCase()
  return data.value.filter(row => 
    Object.values(row).some(val => String(val).toLowerCase().includes(q))
  )
})

onMounted(async () => {
  await refreshData()
})

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
      columns.value = (preview.columns || []).map(col => ({
        field: col.name,
        label: col.name
      }))
      dataset.value = preview
    }
    
    if (opsRes.ok) {
      operations.value = await opsRes.json()
    }
    
    // Fetch profile
    const profileRes = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (profileRes.ok) {
      profileData.value = await profileRes.json()
      nullCount.value = profileData.value.columns?.reduce((sum, c) => sum + c.null_count, 0) || 0
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
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
      // Show comparison in a new view or modal
      console.log('Comparison:', comparison)
    }
  } catch (e) {
    console.error(e)
  } finally {
    comparing.value = false
  }
}

function handleCellClick(row) {
  // Could open cell editor
}

async function applyOperation(endpoint, params) {
  const col = selectedColumn.value || columns.value[0]?.name
  if (!col) return
  
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ column: col, ...params })
    })
    
    if (res.ok) {
      showToast('Operation applied successfully', 'is-success')
      await refreshData()
    } else {
      const err = await res.json()
      showToast(err.detail || 'Operation failed', 'is-danger')
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

async function applyStringOp(operation) {
  const col = selectedColumn.value || columns.value[0]?.name
  if (!col) return
  
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/string-operations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ column: col, operation })
    })
    
    if (res.ok) {
      showToast('String operation applied', 'is-success')
      await refreshData()
    } else {
      const err = await res.json()
      showToast(err.detail || 'Operation failed', 'is-danger')
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

async function applyDatetimeOp(operation) {
  const col = selectedColumn.value || columns.value[0]?.name
  if (!col) return
  
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/datetime-operations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ column: col, operation })
    })
    
    if (res.ok) {
      showToast('Datetime operation applied', 'is-success')
      await refreshData()
    } else {
      const err = await res.json()
      showToast(err.detail || 'Operation failed', 'is-danger')
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

async function applyStructuralOp(operation) {
  const col = selectedColumn.value || columns.value[0]?.name
  if (!col) return
  
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/structural`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ column: col, operation })
    })
    
    if (res.ok) {
      showToast('Structural operation applied', 'is-success')
      await refreshData()
    } else {
      const err = await res.json()
      showToast(err.detail || 'Operation failed', 'is-danger')
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

async function undo() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/undo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      showToast('Undo successful', 'is-success')
      await refreshData()
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

async function redo() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/redo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      showToast('Redo successful', 'is-success')
      await refreshData()
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

function showToast(message, type) {
  // Buefy toast will be available globally
  if (typeof window !== 'undefined' && window.$buefy) {
    window.$buefy.toast.open({ message, type })
  } else {
    alert(message)
  }
}

async function applyAiClean() {
  const col = selectedColumn.value || columns.value[0]?.name
  if (!col || !aiInstruction.value) return
  
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/ai-clean`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ 
        column: col, 
        instruction: aiInstruction.value,
        batch_size: 10
      })
    })
    
    if (res.ok) {
      showToast('AI cleaning applied', 'is-success')
      showAiModal.value = false
      await refreshData()
    } else {
      const err = await res.json()
      showToast(err.detail || 'AI cleaning failed', 'is-danger')
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

async function importFromClipboard() {
  if (!clipboardData.value.trim()) return
  
  operating.value = true
  try {
    // Create a blob from the clipboard data
    const blob = new Blob([clipboardData.value], { type: 'text/csv' })
    const file = new File([blob], 'clipboard.csv', { type: 'text/csv' })
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', props.projectId || 1) // Would need to pass projectId
    if (clipboardDatasetName.value) {
      formData.append('name', clipboardDatasetName.value)
    }
    
    const res = await fetch(`${apiUrl}/api/datasets/import`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (res.ok) {
      showToast('Data imported successfully', 'is-success')
      showClipboardImport.value = false
      clipboardData.value = ''
      clipboardDatasetName.value = ''
      await refreshData()
    } else {
      throw new Error('Import failed')
    }
  } catch (e) {
    showToast(e.message, 'is-danger')
  } finally {
    operating.value = false
  }
}

async function copyToClipboard() {
  if (!data.value || data.value.length === 0) {
    showToast('No data to copy', 'is-warning')
    return
  }
  
  try {
    // Convert data to CSV format
    const headers = Object.keys(data.value[0])
    const csvRows = [
      headers.join(','),
      ...data.value.map(row => 
        headers.map(header => {
          const val = row[header]
          // Escape quotes and wrap in quotes if contains comma
          if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
            return `"${val.replace(/"/g, '""')}"`
          }
          return val ?? ''
        }).join(',')
      )
    ]
    
    await navigator.clipboard.writeText(csvRows.join('\n'))
    showToast('Data copied to clipboard', 'is-success')
  } catch (e) {
    showToast('Failed to copy: ' + e.message, 'is-danger')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}
</script>

<!-- FillNA Modal -->
<b-modal v-model="showFillnaModal" :has-modal-card="true">
  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">Fill Missing Values</p>
      <button class="delete" @click="showFillnaModal = false"></button>
    </header>
    <section class="modal-card-body">
      <b-field label="Column">
        <b-select v-model="selectedColumn" expanded>
          <option v-for="col in columns" :key="col.field" :value="col.field">
            {{ col.label }}
          </option>
        </b-select>
      </b-field>
      <b-field label="Fill Value">
        <b-input v-model="fillValue" placeholder="Enter value or leave empty for empty string"></b-input>
      </b-field>
    </section>
    <footer class="modal-card-foot">
      <b-button type="is-primary" :loading="operating" @click="applyOperation('fillna', { method: 'constant', fill_value: fillValue })">
        Fill
      </b-button>
      <b-button @click="showFillnaModal = false">Cancel</b-button>
    </footer>
  </div>
</b-modal>

<!-- Clipboard Import Modal -->
<b-modal v-model="showClipboardImport" :has-modal-card="true">
  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">Import from Clipboard</p>
      <button class="delete" @click="showClipboardImport = false"></button>
    </header>
    <section class="modal-card-body">
      <b-field label="Paste CSV Data">
        <b-input 
          v-model="clipboardData" 
          type="textarea" 
          placeholder="Paste your CSV data here..."
          :rows="10"
        ></b-input>
      </b-field>
      <b-field label="Dataset Name">
        <b-input v-model="clipboardDatasetName" placeholder="My Dataset"></b-input>
      </b-field>
    </section>
    <footer class="modal-card-foot">
      <b-button type="is-primary" :loading="operating" @click="importFromClipboard">
        Import
      </b-button>
      <b-button @click="showClipboardImport = false">Cancel</b-button>
    </footer>
  </div>
</b-modal>

<!-- AI Clean Modal -->
<b-modal v-model="showAiModal" :has-modal-card="true">
  <div class="modal-card">
    <header class="modal-card-head">
      <p class="modal-card-title">AI-Powered Cleaning</p>
      <button class="delete" @click="showAiModal = false"></button>
    </header>
    <section class="modal-card-body">
      <b-field label="Column">
        <b-select v-model="selectedColumn" expanded>
          <option v-for="col in columns" :key="col.field" :value="col.field">
            {{ col.label }}
          </option>
        </b-select>
      </b-field>
      <b-field label="Instruction">
        <b-input v-model="aiInstruction" type="textarea" placeholder="Describe what you want the AI to do..."></b-input>
      </b-field>
    </section>
    <footer class="modal-card-foot">
      <b-button type="is-primary" :loading="operating" @click="applyAiClean">
        Apply AI Cleaning
      </b-button>
      <b-button @click="showAiModal = false">Cancel</b-button>
    </footer>
  </div>
</b-modal>

<style scoped>
.table-container {
  overflow: auto;
}

.operations-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.operations-bar .button {
  height: auto;
  padding: 0.25em 0.75em;
}
</style>
