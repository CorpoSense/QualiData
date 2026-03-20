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
              <p class="text-muted small mb-3">Scanning your data for quality issues.</p>

              <!-- Analysis checklist -->
              <div class="list-group list-group-flush mb-3">
                <div v-for="check in analysisChecks" :key="check.label" class="list-group-item d-flex align-items-center py-2 px-2">
                  <span v-if="check.status === 'pending'" class="text-muted me-2"><i class="bi bi-circle"></i></span>
                  <span v-else-if="check.status === 'running'" class="text-primary me-2"><i class="bi bi-arrow-repeat spin"></i></span>
                  <span v-else-if="check.status === 'done'" class="text-success me-2"><i class="bi bi-check-circle-fill"></i></span>
                  <span class="small" :class="check.status === 'pending' ? 'text-muted' : ''">{{ check.label }}</span>
                  <span v-if="check.result" class="ms-auto small text-muted">{{ check.result }}</span>
                </div>
              </div>

              <!-- Start button -->
              <BButton v-if="!analysisDone" variant="primary" class="w-100" :loading="analyzing" :disabled="analyzing" @click="analyzeData">
                <i class="bi bi-search me-1"></i> {{ analyzing ? 'Analyzing…' : 'Start Analysis' }}
              </BButton>

              <!-- Results summary -->
              <div v-if="analysisDone" class="mt-3">
                <div class="alert" :class="issues.length ? 'alert-warning' : 'alert-success'" py-2>
                  <i class="bi me-1" :class="issues.length ? 'bi-exclamation-triangle' : 'bi-check-circle'"></i>
                  <strong>{{ issues.length ? `${issues.length} issue(s) found` : 'No issues found!' }}</strong>
                  <small class="d-block text-muted">
                    {{ issues.length ? 'Click "Fix →" on each issue or continue to the clean step.' : 'Your data looks clean. You can go back to select a different dataset.' }}
                  </small>
                </div>
                <div class="d-flex gap-2 mt-2">
                  <BButton size="sm" variant="outline-secondary" @click="currentStep = 0">← Back</BButton>
                  <BButton v-if="issues.length" size="sm" variant="success" @click="currentStep = 2">
                    Continue to Clean →
                  </BButton>
                </div>
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
const analysisDone = ref(false)
const issues = ref([])
const analysisChecks = ref([
  { label: 'Check for missing values', status: 'pending', result: '' },
  { label: 'Check for duplicates', status: 'pending', result: '' },
  { label: 'Check for JSON columns', status: 'pending', result: '' },
  { label: 'Check column types', status: 'pending', result: '' },
])

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
  analysisDone.value = false
  analysisChecks.value.forEach(c => { c.status = 'pending'; c.result = '' })
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
  analysisDone.value = false
  issues.value = []
  pendingOps.value = []

  // Reset checks
  analysisChecks.value.forEach(c => { c.status = 'pending'; c.result = '' })

  try {
    const res = await fetch(`${apiUrl}/api/datasets/${selectedDataset.value}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (!res.ok) { toast.error('Failed to analyze'); return }
    const profile = await res.json()
    const found = []

    // Check 1: Missing values
    analysisChecks.value[0].status = 'running'
    await sleep(300)
    if (profile.columns) {
      const nullCols = profile.columns.filter(c => c.null_count > 0)
      if (nullCols.length) {
        analysisChecks.value[0].result = `${nullCols.length} column(s) with nulls`
        for (const col of nullCols) {
          const pct = Math.round(col.null_percent || 0)
          found.push({
            title: `Missing values in "${col.name}"`,
            description: `${col.null_count} nulls (${pct}%)`,
            alertClass: pct > 50 ? 'danger' : pct > 10 ? 'warning' : 'info',
            icon: 'bi-exclamation-triangle',
            operation: 'fillna', column: col.name,
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
      } else {
        analysisChecks.value[0].result = 'No nulls ✓'
      }
    }
    analysisChecks.value[0].status = 'done'

    // Check 2: Duplicates
    analysisChecks.value[1].status = 'running'
    await sleep(300)
    // Detect duplicates from the loaded data
    if (data.value.length > 0) {
      const seen = new Set()
      let dupes = 0
      for (const row of data.value) {
        const key = JSON.stringify(row)
        if (seen.has(key)) dupes++
        else seen.add(key)
      }
      if (dupes > 0) {
        analysisChecks.value[1].result = `${dupes} found`
        found.push({
          title: 'Duplicate rows',
          description: `${dupes} duplicate(s) in current page`,
          alertClass: 'warning', icon: 'bi-files',
          operation: 'remove-duplicates', column: null,
          params: {}, options: null,
        })
      } else {
        analysisChecks.value[1].result = 'None ✓'
      }
    } else {
      analysisChecks.value[1].result = 'Skipped (no data)'
    }
    analysisChecks.value[1].status = 'done'

    // Check 3: JSON columns
    analysisChecks.value[2].status = 'running'
    await sleep(300)
    if (profile.columns) {
      const jsonCols = profile.columns.filter(c =>
        c.dtype === 'object' && c.sample_values?.some(v => typeof v === 'string' && v.trim().startsWith('{'))
      )
      if (jsonCols.length) {
        analysisChecks.value[2].result = `${jsonCols.length} column(s)`
        for (const col of jsonCols) {
          found.push({
            title: `JSON in "${col.name}"`,
            description: 'Extract values from JSON strings',
            alertClass: 'info', icon: 'bi-braces',
            operation: 'extract-json', column: col.name,
            params: { key: '' },
            options: [{ key: 'key', label: 'Key to extract', type: 'text', placeholder: 'e.g. country' }],
          })
        }
      } else {
        analysisChecks.value[2].result = 'None found'
      }
    }
    analysisChecks.value[2].status = 'done'

    // Check 4: Column types
    analysisChecks.value[3].status = 'running'
    await sleep(200)
    analysisChecks.value[3].result = `${profile.columns?.length || 0} columns analyzed`
    analysisChecks.value[3].status = 'done'

    issues.value = found
    pendingOps.value = found.map(f => ({
      label: f.title, description: f.description,
      operation: f.operation, column: f.column,
      params: { ...f.params }, options: f.options, applied: false,
    }))
    analysisDone.value = true

  } catch (e) { toast.error(e.message) }
  finally { analyzing.value = false }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

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
.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
