<template>
  <div class="assistant-page p-3">
    <div class="row g-3">
      <!-- Left: Wizard Steps -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h2 class="h5 mb-3"><i class="bi bi-magic me-2"></i>AI Cleaning Assistant</h2>

            <!-- Steps -->
            <ul class="nav nav-pills nav-fill mb-3" role="tablist">
              <li v-for="(step, i) in steps" :key="i" class="nav-item">
                <button class="nav-link" :class="{ active: currentStep === i, 'bg-success text-white': i < currentStep }" @click="goToStep(i)">
                  {{ i + 1 }}. {{ step }}
                </button>
              </li>
            </ul>

            <!-- Step 0: Select Data -->
            <div v-if="currentStep === 0">
              <BFormGroup label="Project">
                <BFormSelect v-model="selectedProject" :options="projectOptions" @update:model-value="onProjectChange"></BFormSelect>
              </BFormGroup>
              <BFormGroup v-if="selectedProject" label="Dataset" class="mt-2">
                <BFormSelect v-model="selectedDataset" :options="datasetOptions" @update:model-value="onDatasetChange"></BFormSelect>
              </BFormGroup>
              <BButton variant="primary" class="mt-3 w-100" :disabled="!selectedDataset" @click="currentStep = 1">
                Next → Analyze
              </BButton>
            </div>

            <!-- Step 1: Analyze -->
            <div v-if="currentStep === 1">
              <p class="text-muted small">Scan data for quality issues.</p>
              <BButton variant="primary" class="w-100" :loading="analyzing" @click="analyzeData">
                <i class="bi bi-search me-1"></i> Analyze Data
              </BButton>
              <div v-if="issues.length" class="mt-3">
                <div v-for="(issue, i) in issues" :key="i" class="alert py-2 px-3 mb-2" :class="'alert-' + issue.alertClass">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <i class="bi me-1" :class="issue.icon"></i>
                      <strong class="small">{{ issue.title }}</strong>
                      <small class="d-block text-muted">{{ issue.description }}</small>
                    </div>
                    <BButton size="sm" variant="outline-primary" @click="startClean(i)">Fix →</BButton>
                  </div>
                </div>
                <BButton variant="success" size="sm" class="w-100 mt-2" @click="currentStep = 2">
                  Continue to Clean →
                </BButton>
              </div>
            </div>

            <!-- Step 2: Clean -->
            <div v-if="currentStep === 2">
              <p class="text-muted small">Apply operations. Undo any step if needed.</p>
              <div v-for="(op, i) in pendingOps" :key="i" class="card mb-2" :class="{ 'border-primary': activeOpIndex === i }">
                <div class="card-body py-2 px-3">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <span class="badge" :class="op.applied ? 'bg-success' : 'bg-light text-dark'">{{ op.label }}</span>
                      <small class="text-muted d-block">{{ op.description }}</small>
                    </div>
                    <div class="d-flex gap-1">
                      <BButton v-if="op.applied" size="sm" variant="outline-warning" @click="undoOp(i)" title="Undo">
                        <i class="bi bi-arrow-counterclockwise"></i>
                      </BButton>
                      <BButton v-if="!op.applied" size="sm" variant="outline-primary" @click="activeOpIndex = activeOpIndex === i ? null : i">
                        {{ activeOpIndex === i ? 'Hide' : 'Options' }}
                      </BButton>
                      <BButton v-if="!op.applied && activeOpIndex === i" size="sm" variant="primary" @click="applyOp(i)">
                        Apply
                      </BButton>
                    </div>
                  </div>
                  <!-- Options -->
                  <div v-if="activeOpIndex === i && !op.applied && op.options" class="mt-2">
                    <div v-for="opt in op.options" :key="opt.key" class="mb-1">
                      <label class="form-label small mb-0">{{ opt.label }}</label>
                      <BFormSelect v-if="opt.type === 'select'" v-model="op.params[opt.key]" :options="opt.choices" size="sm"></BFormSelect>
                      <BFormInput v-else v-model="op.params[opt.key]" size="sm" :type="opt.type || 'text'" :placeholder="opt.placeholder"></BFormInput>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="!pendingOps.length" class="text-muted text-center py-3 small">No issues found — nothing to clean!</div>
              <BButton variant="success" size="sm" class="w-100 mt-2" :disabled="!pendingOps.some(o => o.applied)" @click="currentStep = 3">
                Review Results →
              </BButton>
            </div>

            <!-- Step 3: Review -->
            <div v-if="currentStep === 3">
              <div class="alert alert-success py-2">
                <i class="bi bi-check-circle me-1"></i>
                <strong>{{ appliedCount }} operation(s) applied.</strong>
              </div>
              <div class="d-grid gap-2">
                <BButton size="sm" variant="outline-warning" @click="resetAll">
                  <i class="bi bi-arrow-counterclockwise me-1"></i> Undo All & Restart
                </BButton>
                <BButton size="sm" variant="outline-secondary" @click="currentStep = 2">
                  ← Back to Clean
                </BButton>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Data Table (always visible) -->
      <div class="col-md-8">
        <div v-if="!selectedDataset" class="card">
          <div class="card-body text-center text-muted py-5">
            <i class="bi bi-table fs-1 d-block mb-2"></i>
            Select a project and dataset to begin.
          </div>
        </div>
        <div v-else>
          <div class="d-flex justify-content-between align-items-center mb-2">
            <small class="text-muted">{{ data.length }} rows (page {{ page }})</small>
            <div class="d-flex gap-1">
              <button class="btn btn-sm btn-outline-secondary" :disabled="page <= 1" @click="page--; loadData()">← Prev</button>
              <button class="btn btn-sm btn-outline-secondary" @click="page++; loadData()">Next →</button>
            </div>
          </div>
          <DataTable
            :items="data"
            :fields="tableFields"
            :selected-columns="[]"
            @row-clicked="() => {}"
            @head-clicked="() => {}"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getApiUrl } from '@/utils/api'
import { useToast } from '@/composables/useToast'
import DataTable from '@/components/DataTable.vue'
import { BFormGroup, BFormSelect, BFormInput, BButton, BAlert } from 'bootstrap-vue-next'

const apiUrl = getApiUrl()
const toast = useToast()

const steps = ['Select', 'Analyze', 'Clean', 'Review']
const currentStep = ref(0)

// Data selection
const projects = ref([])
const datasets = ref([])
const selectedProject = ref(null)
const selectedDataset = ref(null)
const columns = ref([])

// Data table
const data = ref([])
const page = ref(1)
const limit = ref(20)
const totalRows = ref(0)

// Analysis
const analyzing = ref(false)
const issues = ref([])

// Clean
const pendingOps = ref([])
const activeOpIndex = ref(null)

const appliedCount = computed(() => pendingOps.value.filter(o => o.applied).length)

const projectOptions = computed(() => [
  { value: null, text: 'Select project…', disabled: true },
  ...projects.value.map(p => ({ value: p.id, text: p.name }))
])

const datasetOptions = computed(() => [
  { value: null, text: 'Select dataset…', disabled: true },
  ...datasets.value.map(d => ({ value: d.id, text: d.name }))
])

const tableFields = computed(() => columns.value.map(c => ({ key: c.name, label: c.name })))

// Init
fetchProjects()

async function fetchProjects() {
  try {
    const res = await fetch(`${apiUrl}/api/projects?page=1&page_size=100`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) projects.value = (await res.json()).projects || []
  } catch { /* silent */ }
}

async function onProjectChange() {
  datasets.value = []
  selectedDataset.value = null
  columns.value = []
  data.value = []
  try {
    const res = await fetch(`${apiUrl}/api/datasets?project_id=${selectedProject.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) datasets.value = await res.json()
  } catch { /* silent */ }
}

async function onDatasetChange() {
  columns.value = []
  data.value = []
  page.value = 1
  issues.value = []
  pendingOps.value = []
  currentStep.value = 1
  await loadData()
}

async function loadData() {
  if (!selectedDataset.value) return
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${selectedDataset.value}/preview?limit=${limit.value}&page=${page.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const preview = await res.json()
      data.value = preview.preview_data || []
      columns.value = (preview.columns || []).map(c => ({ name: c.name }))
      totalRows.value = preview.row_count || 0
    }
  } catch { /* silent */ }
}

function goToStep(i) {
  if (i <= currentStep.value || (i === 1 && selectedDataset.value) || (i === 2 && issues.value.length) || (i === 3 && appliedCount.value > 0)) {
    currentStep.value = i
  }
}

async function analyzeData() {
  analyzing.value = true
  issues.value = []
  pendingOps.value = []
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${selectedDataset.value}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!res.ok) { toast.error('Failed to analyze'); return }
    const profile = await res.json()
    const found = []

    // Missing values
    if (profile.null_counts) {
      for (const [col, count] of Object.entries(profile.null_counts)) {
        if (count > 0) {
          const pct = Math.round((count / (profile.row_count || 1)) * 100)
          found.push({
            title: `Missing values in "${col}"`,
            description: `${count} nulls (${pct}%)`,
            alertClass: pct > 50 ? 'danger' : pct > 10 ? 'warning' : 'info',
            icon: 'bi-exclamation-triangle',
            operation: 'fillna',
            column: col,
            params: { method: 'constant', fill_value: '' },
            options: [
              { key: 'method', label: 'Method', type: 'select', choices: [
                { value: 'constant', text: 'Custom value' },
                { value: 'drop', text: 'Drop rows' },
                { value: 'forward', text: 'Forward fill' },
                { value: 'backward', text: 'Backward fill' },
              ]},
              { key: 'fill_value', label: 'Value (if constant)', type: 'text', placeholder: 'e.g. N/A' },
            ]
          })
        }
      }
    }

    // Duplicates
    if (profile.duplicate_rows > 0) {
      found.push({
        title: 'Duplicate rows',
        description: `${profile.duplicate_rows} duplicate(s)`,
        alertClass: 'warning',
        icon: 'bi-files',
        operation: 'remove-duplicates',
        column: null,
        params: {},
        options: null,
      })
    }

    // JSON columns
    if (profile.columns) {
      for (const col of profile.columns) {
        if (col.dtype === 'object' && col.sample_values?.some(v => typeof v === 'string' && v.startsWith('{'))) {
          found.push({
            title: `JSON in "${col.name}"`,
            description: 'Extract values from JSON strings',
            alertClass: 'info',
            icon: 'bi-braces',
            operation: 'extract-json',
            column: col.name,
            params: { key: '' },
            options: [{ key: 'key', label: 'Key to extract', type: 'text', placeholder: 'e.g. country' }],
          })
        }
      }
    }

    issues.value = found
    pendingOps.value = found.map(f => ({
      label: f.title,
      description: f.description,
      operation: f.operation,
      column: f.column,
      params: { ...f.params },
      options: f.options,
      applied: false,
    }))
  } catch (e) { toast.error(e.message) }
  finally { analyzing.value = false }
}

function startClean(issueIndex) {
  currentStep.value = 2
  activeOpIndex.value = issueIndex
}

async function applyOp(index) {
  const op = pendingOps.value[index]
  if (!op) return
  const auth = { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` }
  let endpoint, body

  if (op.operation === 'fillna') {
    endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/fillna`
    body = { columns: op.column ? [op.column] : undefined, ...op.params }
  } else if (op.operation === 'remove-duplicates') {
    endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/remove-duplicates`
    body = {}
  } else if (op.operation === 'extract-json') {
    endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/extract-json`
    body = { column: op.column, key: op.params.key }
  } else {
    toast.warning(`Unknown: ${op.operation}`)
    return
  }

  try {
    const res = await fetch(endpoint, { method: 'POST', headers: auth, body: JSON.stringify(body) })
    if (res.ok) {
      op.applied = true
      activeOpIndex.value = null
      toast.success(`Applied: ${op.label}`)
      await loadData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed')
    }
  } catch (e) { toast.error(e.message) }
}

async function undoOp(index) {
  const op = pendingOps.value[index]
  if (!op?.applied) return
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${selectedDataset.value}/operations/undo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({})
    })
    if (res.ok) {
      op.applied = false
      toast.success('Undone')
      await loadData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Undo failed')
    }
  } catch (e) { toast.error(e.message) }
}

async function resetAll() {
  const applied = pendingOps.value.filter(o => o.applied)
  for (let i = applied.length - 1; i >= 0; i--) {
    try {
      await fetch(`${apiUrl}/api/datasets/${selectedDataset.value}/operations/undo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({})
      })
    } catch { /* continue */ }
  }
  currentStep.value = 1
  issues.value = []
  pendingOps.value = []
  await loadData()
  toast.success('All undone')
}
</script>

<style scoped>
.assistant-page {
  background: #f8f9fa;
  min-height: 100vh;
}
</style>
