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

              <!-- AI Agent toggle -->
              <div class="form-check form-switch mt-3 mb-2">
                <input class="form-check-input" type="checkbox" v-model="useAiAgent" id="use-ai-toggle">
                <label class="form-check-label" for="use-ai-toggle">
                  <i class="bi bi-magic me-1"></i> Use AI Agent
                </label>
              </div>

              <div v-if="useAiAgent" class="border rounded p-3 mb-3 bg-light">
                <BFormGroup label="AI Agent *" label-for="assist-agent" label-size="sm">
                  <BFormSelect id="assist-agent" v-model="assistAgentId" :options="assistAgentOptions" size="sm"></BFormSelect>
                </BFormGroup>
                <BFormGroup label="Rows for context" label-for="assist-rows" label-size="sm" class="mt-2">
                  <BFormSelect id="assist-rows" v-model="assistRows" :options="limitOptions" size="sm"></BFormSelect>
                </BFormGroup>
                <div class="form-check mt-2">
                  <input class="form-check-input" type="checkbox" v-model="assistIncludeDesc" id="assist-desc">
                  <label class="form-check-label small" for="assist-desc">Include dataset description</label>
                </div>
              </div>

              <BButton variant="primary" class="mt-2 w-100" :disabled="!selectedDataset || (useAiAgent && !assistAgentId) || aiAnalyzing" @click="startAnalysis">
                <template v-if="aiAnalyzing">
                  <i class="bi bi-arrow-repeat spin me-1"></i>{{ aiAnalysisStage }}
                </template>
                <template v-else>
                  {{ useAiAgent ? 'Configure & Start AI Analysis' : 'Next → Analyze' }}
                </template>
              </BButton>

              <!-- AI progress stages -->
              <div v-if="useAiAgent && aiAnalyzing" class="mt-3">
                <div v-for="(stage, i) in aiStages" :key="i" class="d-flex align-items-center gap-2 mb-1">
                  <span v-if="stage.status === 'pending'" class="text-muted"><i class="bi bi-circle small"></i></span>
                  <span v-else-if="stage.status === 'running'" class="text-primary"><i class="bi bi-arrow-repeat spin small"></i></span>
                  <span v-else-if="stage.status === 'done'" class="text-success"><i class="bi bi-check-circle-fill small"></i></span>
                  <span v-else-if="stage.status === 'error'" class="text-danger"><i class="bi bi-x-circle-fill small"></i></span>
                  <small :class="stage.status === 'pending' ? 'text-muted' : ''">{{ stage.label }}</small>
                </div>
              </div>

              <!-- AI error details -->
              <div v-if="aiError" class="alert alert-danger mt-3 py-2">
                <i class="bi bi-exclamation-triangle me-1"></i>
                <strong>AI Analysis Failed</strong>
                <small class="d-block mt-1">{{ aiError }}</small>
                <BButton size="sm" variant="outline-danger" class="mt-2" @click="aiError = ''; aiStages.forEach(s => s.status = 'pending')">
                  Try Again
                </BButton>
              </div>
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
              <p class="text-muted small">
                {{ useAiAgent ? 'AI suggestions. Accept, tweak, or skip each one.' : 'Apply operations. Undo any step if needed.' }}
              </p>

              <!-- AI mode: show AI suggestions -->
              <template v-if="useAiAgent">
                <div v-for="(sug, i) in aiSuggestions" :key="'ai-'+i" class="card mb-2" :class="{ 'border-primary': activeOpIndex === i, 'opacity-50': !sug.accepted }">
                  <div class="card-body py-2 px-3">
                    <div class="d-flex justify-content-between align-items-start">
                      <div>
                        <div class="d-flex align-items-center gap-1 mb-1">
                          <input class="form-check-input" type="checkbox" v-model="sug.accepted" :disabled="sug.applied">
                          <span class="badge" :class="sug.applied ? 'bg-success' : 'bg-primary'">{{ sug.operation }}</span>
                          <small v-if="sug.column" class="text-muted">{{ sug.column }}</small>
                        </div>
                        <small class="text-muted d-block">{{ sug.reasoning }}</small>
                      </div>
                      <div class="d-flex gap-1">
                        <BButton v-if="sug.applied" size="sm" variant="outline-warning" @click="undoAiOp(i)" title="Undo">
                          <i class="bi bi-arrow-counterclockwise"></i>
                        </BButton>
                        <BButton v-if="!sug.applied && sug.accepted" size="sm" variant="outline-primary" @click="activeOpIndex = activeOpIndex === i ? null : i">
                          {{ activeOpIndex === i ? 'Hide' : 'Options' }}
                        </BButton>
                        <BButton v-if="!sug.applied && sug.accepted && activeOpIndex === i" size="sm" variant="primary" @click="applyAiOp(i)">
                          Apply
                        </BButton>
                      </div>
                    </div>
                    <div v-if="activeOpIndex === i && !sug.applied && sug.params" class="mt-2">
                      <div v-for="(val, key) in sug.params" :key="key" class="mb-1">
                        <label class="form-label small mb-0">{{ key }}</label>
                        <BFormInput v-model="sug.params[key]" size="sm" :placeholder="String(val)"></BFormInput>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="!aiSuggestions.length" class="text-muted text-center py-3 small">No AI suggestions.</div>
              </template>

              <!-- Manual mode: show pendingOps -->
              <template v-else>
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
              </template>

              <div class="d-flex gap-2 mt-2">
                <BButton v-if="useAiAgent && aiSuggestions.some(s => s.accepted && !s.applied)" size="sm" variant="primary" @click="applyAllAiSuggested">
                  <i class="bi bi-lightning me-1"></i> Apply All Accepted
                </BButton>
                <BButton variant="success" size="sm" :disabled="!currentAppliedCount" @click="currentStep = 3">
                  Review →
                </BButton>
              </div>
            </div>

            <!-- Step 3: Review -->
            <div v-if="currentStep === 3">
              <div class="alert alert-success py-2">
                <i class="bi bi-check-circle me-1"></i>
                <strong>{{ currentAppliedCount }} operation(s) applied.</strong>
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

      <!-- AI Pre-flight Modal -->
      <BModal v-model="showAiPreflight" title="AI Analysis Configuration" size="lg" no-close-on-backdrop>
        <div v-if="preflightLoading" class="text-center py-4">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted mt-2">Loading agent configuration…</p>
        </div>
        <div v-else-if="!preflight" class="text-center py-4 text-danger">
          <i class="bi bi-exclamation-triangle fs-1 d-block mb-2"></i>
          <p>Failed to load agent configuration. Please try again.</p>
          <BButton size="sm" variant="outline-primary" @click="openAiPreflight">Retry</BButton>
        </div>
        <div v-else>
          <!-- Agent Info -->
          <div class="alert alert-info py-2 mb-3">
            <div class="d-flex align-items-center gap-2">
              <i class="bi bi-robot fs-4"></i>
              <div>
                <strong>{{ preflight.agent_name }}</strong>
                <small class="d-block text-muted">{{ preflight.provider }} / {{ preflight.model }}</small>
              </div>
            </div>
          </div>

          <!-- Prompt Presets -->
          <div class="mb-3">
            <label class="form-label fw-bold small">Quick Presets</label>
            <div class="d-flex flex-wrap gap-2">
              <button
                v-for="preset in preflight.prompt_presets"
                :key="preset.id"
                class="btn btn-sm"
                :class="selectedPreset === preset.id ? 'btn-primary' : 'btn-outline-secondary'"
                @click="applyPreset(preset)"
              >
                <i class="bi me-1" :class="preset.id === 'quality' ? 'bi-shield-check' : preset.id === 'formatting' ? 'bi-type' : 'bi-stars'"></i>
                {{ preset.label }}
              </button>
              <button
                class="btn btn-sm"
                :class="selectedPreset === null ? 'btn-primary' : 'btn-outline-secondary'"
                @click="selectedPreset = null"
              >
                <i class="bi bi-pencil me-1"></i> Custom
              </button>
            </div>
            <small v-if="selectedPreset" class="text-muted d-block mt-1">
              {{ preflight.prompt_presets.find(p => p.id === selectedPreset)?.description }}
            </small>
          </div>

          <!-- System Prompt -->
          <div class="mb-3">
            <label class="form-label fw-bold small">System Prompt
              <span v-if="selectedPreset" class="badge bg-light text-dark ms-1">{{ preflight.prompt_presets.find(p => p.id === selectedPreset)?.label }}</span>
            </label>
            <BFormTextarea
              v-model="preflightSystemPrompt"
              rows="3"
              size="sm"
              placeholder="System prompt for the AI agent…"
            ></BFormTextarea>
          </div>

          <!-- User Prompt -->
          <div class="mb-3">
            <label class="form-label fw-bold small">Additional Instructions <span class="text-muted fw-normal">(optional)</span></label>
            <BFormTextarea
              v-model="preflightUserPrompt"
              rows="2"
              size="sm"
              placeholder="Add specific instructions for this analysis, e.g. 'Focus on the email column' or 'Ignore the ID column'…"
            ></BFormTextarea>
          </div>

          <!-- Available Operations -->
          <div class="mb-2">
            <label class="form-label fw-bold small">Available Operations</label>
            <div class="d-flex flex-wrap gap-1">
              <span v-for="op in preflight.available_operations" :key="op.operation" class="badge bg-light text-dark" :title="op.description">
                {{ op.label }}
              </span>
            </div>
          </div>

          <!-- Rows & Options -->
          <div class="row g-2 mt-1">
            <div class="col-6">
              <BFormGroup label="Rows for context" label-size="sm">
                <BFormSelect v-model="assistRows" :options="limitOptions" size="sm"></BFormSelect>
              </BFormGroup>
            </div>
            <div class="col-6">
              <BFormGroup label=" " label-size="sm">
                <div class="form-check mt-1">
                  <input class="form-check-input" type="checkbox" v-model="assistIncludeDesc" id="preflight-desc">
                  <label class="form-check-label small" for="preflight-desc">Include dataset description</label>
                </div>
              </BFormGroup>
            </div>
          </div>
        </div>
        <template #footer>
          <BButton variant="outline-secondary" @click="showAiPreflight = false">Cancel</BButton>
          <BButton variant="primary" :loading="aiAnalyzing" @click="runAiAnalysisFromPreflight">
            <i class="bi bi-magic me-1"></i> Start Analysis
          </BButton>
        </template>
      </BModal>

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
import { useRoute } from 'vue-router'
import { getApiUrl } from '@/utils/api'
import { useToast } from '@/composables/useToast'
import DataTable from '@/components/DataTable.vue'
import { BFormGroup, BFormSelect, BFormInput, BFormTextarea, BButton, BAlert, BModal } from 'bootstrap-vue-next'

const apiUrl = getApiUrl()
const route = useRoute()
const toast = useToast()

const steps = ['Select', 'Analyze', 'Clean', 'Review']
const currentStep = ref(0)

// AI Agent mode
const useAiAgent = ref(false)
const assistAgentId = ref(null)
const assistAgents = ref([])
const assistRows = ref(10)
const assistIncludeDesc = ref(false)
const aiSuggestions = ref([])
const aiAnalyzing = ref(false)
const aiAnalysisStage = ref('')
const aiError = ref('')
const aiStages = ref([
  { label: 'Preparing data context', status: 'pending' },
  { label: 'Connecting to AI agent', status: 'pending' },
  { label: 'Analyzing and generating suggestions', status: 'pending' },
  { label: 'Processing response', status: 'pending' },
])
const showAiPreflight = ref(false)
const preflightLoading = ref(false)
const preflight = ref(null)
const preflightSystemPrompt = ref('')
const preflightUserPrompt = ref('')
const selectedPreset = ref(null)

const limitOptions = [
  { value: 10, text: '10 rows' },
  { value: 25, text: '25 rows' },
  { value: 50, text: '50 rows' },
  { value: 100, text: '100 rows' },
]

const assistAgentOptions = computed(() => [
  { value: null, text: 'Select agent…', disabled: true },
  ...assistAgents.value.map(a => ({ value: a.id, text: `${a.name} (${a.provider}/${a.model})` }))
])

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
  { label: 'Check for empty strings', status: 'pending', result: '' },
  { label: 'Check column types', status: 'pending', result: '' },
])

// Clean
const pendingOps = ref([])
const activeOpIndex = ref(null)

const appliedCount = computed(() => pendingOps.value.filter(o => o.applied).length)
const currentAppliedCount = computed(() => useAiAgent.value ? aiSuggestions.value.filter(s => s.accepted && s.applied).length : pendingOps.value.filter(o => o.applied).length)

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
    if (res.ok) {
      projects.value = (await res.json()).projects || []
      // Auto-select project from query param
      const pid = route.query.project
      if (pid && projects.value.some(p => p.id === pid)) {
        selectedProject.value = pid
        await onProjectChange()
      }
    }
  } catch { /* silent */ }
}

async function fetchAgents() {
  try {
    const res = await fetch(`${apiUrl}/api/agents/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) assistAgents.value = await res.json() || []
  } catch { /* silent */ }
}

fetchAgents()

function startAnalysis() {
  if (useAiAgent.value) {
    openAiPreflight()
  } else {
    currentStep.value = 1
  }
}

async function openAiPreflight() {
  showAiPreflight.value = true
  preflightLoading.value = true
  preflight.value = null
  selectedPreset.value = null
  preflightSystemPrompt.value = ''
  preflightUserPrompt.value = ''
  try {
    const res = await fetch(`${apiUrl}/api/assistant/ai-suggest/preflight`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ agent_id: assistAgentId.value })
    })
    if (res.ok) {
      preflight.value = await res.json()
      preflightSystemPrompt.value = preflight.value.system_prompt
    } else {
      const err = await res.json().catch(() => ({}))
      toast.error(err.detail || `Failed to load agent configuration (${res.status})`)
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    preflightLoading.value = false
  }
}

function applyPreset(preset) {
  selectedPreset.value = preset.id
  preflightSystemPrompt.value = preset.system_prompt
  preflightUserPrompt.value = preset.user_prompt
}

async function runAiAnalysisFromPreflight() {
  showAiPreflight.value = false
  await runAiAnalysis(preflightSystemPrompt.value, preflightUserPrompt.value)
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
    if (res.ok) {
      const data = await res.json()
      datasets.value = data.datasets || data || []
    }
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
  const canGoToStep2 = selectedDataset.value && (issues.value.length > 0 || aiSuggestions.value.length > 0)
  const canGoToStep3 = currentAppliedCount.value > 0
  if (i <= currentStep.value || (i === 1 && selectedDataset.value) || (i === 2 && canGoToStep2) || (i === 3 && canGoToStep3)) {
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
          const isNumeric = col.dtype && (col.dtype.includes('int') || col.dtype.includes('float'))

          const methodChoices = [
            { value: 'constant', text: 'Custom value' },
            { value: 'drop', text: 'Drop rows' },
            { value: 'forward', text: 'Forward fill' },
            { value: 'backward', text: 'Backward fill' },
          ]
          if (isNumeric) {
            methodChoices.push(
              { value: 'mean', text: 'Mean (numeric)' },
              { value: 'median', text: 'Median (numeric)' },
            )
          }
          methodChoices.push({ value: 'mode', text: 'Mode (most frequent)' })

          found.push({
            title: `Missing values in "${col.name}"`,
            description: `${col.null_count} nulls (${pct}%)${isNumeric ? ' [numeric]' : ''}`,
            alertClass: pct > 50 ? 'danger' : pct > 10 ? 'warning' : 'info',
            icon: 'bi-exclamation-triangle',
            operation: 'fillna', column: col.name,
            params: { method: isNumeric ? 'mean' : 'constant', fill_value: '' },
            options: [
              { key: 'method', label: 'Method', type: 'select', choices: methodChoices },
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

    // Check 4: Empty strings (suggests find-replace)
    analysisChecks.value[3].status = 'running'
    await sleep(300)
    if (data.value.length > 0 && profile.columns) {
      const stringCols = profile.columns.filter(c => c.dtype === 'object')
      let emptyCount = 0
      for (const col of stringCols) {
        const empties = data.value.filter(row => {
          const val = row[col.name]
          return val !== null && val !== undefined && String(val).trim() === ''
        }).length
        if (empties > 0) {
          emptyCount++
          found.push({
            title: `Empty strings in "${col.name}"`,
            description: `${empties} empty string(s) — replace with value`,
            alertClass: 'info', icon: 'bi-type',
            operation: 'find-replace', column: col.name,
            params: { find: '', replace: '', regex: false, case_sensitive: true },
            options: [
              { key: 'find', label: 'Find (empty string)', type: 'text', placeholder: 'Leave empty to match ""' },
              { key: 'replace', label: 'Replace with', type: 'text', placeholder: 'e.g. N/A' },
            ]
          })
        }
      }
      analysisChecks.value[3].result = emptyCount ? `${emptyCount} column(s)` : 'None found'
    } else {
      analysisChecks.value[3].result = 'Skipped'
    }
    analysisChecks.value[3].status = 'done'

    // Check 5: Column types
    analysisChecks.value[4].status = 'running'
    await sleep(200)
    analysisChecks.value[4].result = `${profile.columns?.length || 0} columns analyzed`
    analysisChecks.value[4].status = 'done'

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

async function runAiAnalysis(systemPrompt, userPrompt) {
  aiAnalyzing.value = true
  aiError.value = ''
  aiSuggestions.value = []
  aiStages.value.forEach(s => s.status = 'pending')

  try {
    // Stage 1: Prepare
    aiStages.value[0].status = 'running'
    aiAnalysisStage.value = 'Preparing data…'
    await sleep(200)
    aiStages.value[0].status = 'done'

    // Stage 2: Connect
    aiStages.value[1].status = 'running'
    aiAnalysisStage.value = 'Connecting to AI…'

    // Stage 3+4: Actual API call
    aiStages.value[2].status = 'running'
    aiAnalysisStage.value = 'Analyzing…'

    const res = await fetch(`${apiUrl}/api/assistant/ai-suggest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({
        dataset_id: selectedDataset.value,
        agent_id: assistAgentId.value,
        rows: assistRows.value,
        include_description: assistIncludeDesc.value,
        system_prompt: systemPrompt || undefined,
        user_prompt: userPrompt || undefined,
      })
    })

    aiStages.value[1].status = 'done'
    aiStages.value[2].status = 'done'

    if (!res.ok) {
      let errMsg = `HTTP ${res.status}`
      try { const err = await res.json(); errMsg = err.detail || errMsg } catch { /* keep default */ }
      aiStages.value[3].status = 'error'
      aiError.value = errMsg
      return
    }

    aiStages.value[3].status = 'running'
    aiAnalysisStage.value = 'Processing…'
    const data = await res.json()

    aiSuggestions.value = (data.suggestions || []).map(s => ({
      ...s,
      params: { ...(s.params || {}) },
      accepted: true,
      applied: false,
    }))
    aiStages.value[3].status = 'done'

    if (!aiSuggestions.value.length) {
      aiError.value = 'AI returned no suggestions. Try different settings or a different agent.'
      return
    }

    currentStep.value = 2
  } catch (e) {
    aiStages.value.forEach(s => { if (s.status === 'running') s.status = 'error' })
    aiError.value = e.message || 'Connection failed'
  } finally {
    aiAnalyzing.value = false
    aiAnalysisStage.value = ''
  }
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
  } else if (op.operation === 'find-replace') {
    endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/find-replace`
    body = { columns: [op.column], ...op.params }
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

async function applyAiOp(index) {
  const sug = aiSuggestions.value[index]
  if (!sug || !sug.accepted) return

  const auth = { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` }
  const ops = { 'fillna': 'fillna', 'remove-duplicates': 'remove-duplicates', 'extract-json': 'extract-json', 'find-replace': 'find-replace', 'string-operations': 'string-operations' }
  const endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/${ops[sug.operation] || sug.operation}`

  let body = { ...sug.params }
  if (sug.column) body.column = sug.column
  if (sug.operation === 'fillna' && sug.column) body.columns = [sug.column]
  if (sug.operation === 'find-replace' && sug.column) body.columns = [sug.column]

  try {
    const res = await fetch(endpoint, { method: 'POST', headers: auth, body: JSON.stringify(body) })
    if (res.ok) {
      sug.applied = true
      activeOpIndex.value = null
      toast.success(`Applied: ${sug.operation}`)
      await loadData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed')
    }
  } catch (e) { toast.error(e.message) }
}

async function undoAiOp(index) {
  const sug = aiSuggestions.value[index]
  if (!sug?.applied) return
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${selectedDataset.value}/operations/undo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({})
    })
    if (res.ok) {
      sug.applied = false
      toast.success('Undone')
      await loadData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Undo failed')
    }
  } catch (e) { toast.error(e.message) }
}

async function applyAllAiSuggested() {
  for (let i = 0; i < aiSuggestions.value.length; i++) {
    if (aiSuggestions.value[i].accepted && !aiSuggestions.value[i].applied) {
      await applyAiOp(i)
    }
  }
}

async function resetAll() {
  const items = useAiAgent.value ? aiSuggestions.value : pendingOps.value
  const applied = items.filter(o => o.applied)
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
  aiSuggestions.value = []
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
