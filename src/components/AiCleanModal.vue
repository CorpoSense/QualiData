<template>
  <BModal
    v-model="isOpen"
    :title="modalTitle"
    size="lg"
    no-close-on-backdrop
    @hide="onClose"
  >
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-2">Loading agent configuration…</p>
    </div>
    <div v-else-if="error" class="text-center py-4 text-danger">
      <i class="bi bi-exclamation-triangle fs-1 d-block mb-2"></i>
      <p>{{ error }}</p>
      <BButton size="sm" variant="outline-primary" @click="loadAgentConfig">Retry</BButton>
    </div>
    <div v-else>
      <!-- Tab Navigation -->
      <ul class="nav nav-pills mb-3">
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: activeTab === 'simple' }"
            @click="activeTab = 'simple'"
          >
            <i class="bi bi-lightning me-1"></i> Simple
          </button>
        </li>
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: activeTab === 'advanced' }"
            @click="activeTab = 'advanced'"
          >
            <i class="bi bi-gear me-1"></i> Advanced
          </button>
        </li>
      </ul>

      <!-- Simple Tab -->
      <div v-if="activeTab === 'simple'">
        <!-- Info Alert -->
        <div class="alert alert-secondary mb-3">
          <i class="bi bi-info-circle me-1"></i>
          <strong>{{ type === 'structural' ? 'For column-level changes:' : 'For row-level changes:' }}</strong>
          {{ type === 'structural' ? 'rename columns, drop columns, add new columns, or change column types.' : 'fill/derive values, fix typos, standardize formats, categorize data.' }}
          <template v-if="type === 'structural'">
            For filling/deriving values, use <em>AI Data Clean</em> instead.
          </template>
          <template v-else>
            For renaming/dropping columns, use <em>AI Structural Clean</em> instead.
          </template>
        </div>

        <!-- Selected Columns -->
        <div class="alert alert-info mb-3">
          <i class="bi bi-info-circle me-2"></i>
          <strong>Selected {{ selectedColumns.length === 1 ? 'column' : 'columns' }}:</strong>
          {{ selectedColumns.length === 1 ? selectedColumns[0] : selectedColumns.join(', ') }}
        </div>

        <!-- Agent Selection -->
        <BFormGroup label="AI Agent *" label-for="simple-agent">
          <BFormSelect id="simple-agent" v-model="selectedAgentId" :options="agentOptions" size="sm"></BFormSelect>
        </BFormGroup>

        <!-- Instruction -->
        <BFormGroup label="Instruction" label-for="simple-instruction" class="mt-2">
          <BFormTextarea
            id="simple-instruction"
            v-model="instruction"
            :placeholder="instructionPlaceholder"
            rows="3"
          ></BFormTextarea>
        </BFormGroup>

        <!-- Batch Options (Data type only) -->
        <div v-if="type === 'data'" class="mt-3">
          <div class="form-check mb-2">
            <input class="form-check-input" type="checkbox" v-model="batchProcessAll" id="batch-process-all">
            <label class="form-check-label" for="batch-process-all">Process all rows</label>
          </div>
          <div v-if="batchProcessAll" class="row g-2">
            <div class="col-4">
              <BFormGroup label="Batch size" label-for="batch-size" label-size="sm">
                <BFormInput id="batch-size" v-model.number="batchSize" type="number" min="1" max="100" size="sm"></BFormInput>
              </BFormGroup>
            </div>
            <div class="col-4">
              <BFormGroup label="Delay (seconds)" label-for="batch-delay" label-size="sm">
                <BFormInput id="batch-delay" v-model.number="batchDelay" type="number" min="0" max="60" step="0.5" size="sm"></BFormInput>
              </BFormGroup>
            </div>
            <div class="col-4">
              <BFormGroup label="Start from row" label-for="batch-start" label-size="sm">
                <BFormInput id="batch-start" v-model.number="batchStartRow" type="number" min="0" size="sm"></BFormInput>
              </BFormGroup>
            </div>
          </div>
          <div v-if="batchProcessAll && totalRows > 100" class="alert alert-warning py-2 mt-2">
            <i class="bi bi-exclamation-triangle me-1"></i>
            Large dataset ({{ totalRows }} rows). This will make ~{{ estimatedCalls }} AI calls.
          </div>
        </div>
      </div>

      <!-- Advanced Tab -->
      <div v-if="activeTab === 'advanced'">
        <!-- Agent Info -->
        <div v-if="agentConfig" class="alert alert-info py-2 mb-3">
          <div class="d-flex align-items-center gap-2">
            <i class="bi bi-robot fs-4"></i>
            <div>
              <strong>{{ agentConfig.agent_name }}</strong>
              <small class="d-block text-muted">{{ agentConfig.provider }} / {{ agentConfig.model }}</small>
            </div>
          </div>
        </div>

        <!-- Agent Selection (if not already selected) -->
        <BFormGroup v-if="!selectedAgentId" label="AI Agent *" label-for="advanced-agent" class="mb-3">
          <BFormSelect id="advanced-agent" v-model="selectedAgentId" :options="agentOptions" size="sm"></BFormSelect>
        </BFormGroup>

        <!-- Prompt Presets -->
        <div class="mb-3">
          <label class="form-label fw-bold small">Quick Presets</label>
          <div class="d-flex flex-wrap gap-2">
            <button
              v-for="preset in promptPresets"
              :key="preset.id"
              class="btn btn-sm"
              :class="selectedPreset === preset.id ? 'btn-primary' : 'btn-outline-secondary'"
              @click="applyPreset(preset)"
            >
              <i class="bi me-1" :class="preset.icon"></i>
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
            {{ promptPresets.find(p => p.id === selectedPreset)?.description }}
          </small>
        </div>

        <!-- System Prompt -->
        <div class="mb-3">
          <label class="form-label fw-bold small">
            System Prompt
            <span v-if="selectedPreset" class="badge bg-light text-dark ms-1">
              {{ promptPresets.find(p => p.id === selectedPreset)?.label }}
            </span>
          </label>
          <BFormTextarea
            v-model="systemPrompt"
            rows="3"
            size="sm"
            placeholder="System prompt for the AI agent…"
          ></BFormTextarea>
        </div>

        <!-- User Prompt -->
        <div class="mb-3">
          <label class="form-label fw-bold small">
            Additional Instructions <span class="text-muted fw-normal">(optional)</span>
          </label>
          <BFormTextarea
            v-model="userPrompt"
            rows="2"
            size="sm"
            :placeholder="advancedPlaceholder"
          ></BFormTextarea>
        </div>

        <!-- Available Operations -->
        <div class="mb-2">
          <label class="form-label fw-bold small">Available Operations</label>
          <div class="d-flex flex-wrap gap-1">
            <span
              v-for="op in availableOperations"
              :key="op.operation"
              class="badge bg-light text-dark"
              :title="op.description"
            >
              {{ op.label }}
            </span>
          </div>
        </div>

        <!-- Rows & Options -->
        <div class="row g-2 mt-1">
          <div class="col-6">
            <BFormGroup label="Rows for context" label-size="sm">
              <BFormSelect v-model="rowsForContext" :options="limitOptions" size="sm"></BFormSelect>
            </BFormGroup>
          </div>
          <div class="col-6">
            <BFormGroup label=" " label-size="sm">
              <div class="form-check mt-1">
                <input class="form-check-input" type="checkbox" v-model="includeDescription" id="include-desc">
                <label class="form-check-label small" for="include-desc">Include dataset description</label>
              </div>
            </BFormGroup>
          </div>
        </div>
      </div>

      <!-- Batch Progress (Data type only) -->
      <div v-if="type === 'data' && batchProgress" class="mt-3">
        <div class="d-flex justify-content-between mb-1">
          <small>
            {{ batchProgress.status === 'error' ? 'Completed with errors' : batchProgress.status === 'done' ? 'Done' : 'Processing…' }}
          </small>
          <small>{{ batchProgress.percentage }}% ({{ batchProgress.completed }}/{{ batchProgress.total }} batches)</small>
        </div>
        <div class="progress" style="height: 20px;">
          <div
            class="progress-bar progress-bar-striped"
            :class="progressBarClass"
            :style="{ width: batchProgress.percentage + '%' }"
            role="progressbar"
          >
            {{ batchProgress.percentage }}%
          </div>
        </div>
        <small v-if="batchProgress.failed > 0" class="text-danger">
          {{ batchProgress.failed }} batch(es) failed
        </small>
      </div>
    </div>

    <template #footer>
      <BButton
        v-if="!operating && !batchProgress"
        variant="outline-secondary"
        @click="onClose"
      >
        Cancel
      </BButton>
      <BButton
        v-if="!operating && !batchProgress"
        variant="primary"
        :disabled="!canApply"
        @click="onApply"
      >
        <i class="bi bi-magic me-1"></i> Apply
      </BButton>
      <BButton
        v-if="operating"
        variant="outline-secondary"
        disabled
      >
        <i class="bi bi-hourglass-split me-1"></i> Processing…
      </BButton>
      <BButton
        v-if="!operating && batchProgress && (batchProgress.status === 'done' || batchProgress.status === 'error')"
        variant="primary"
        @click="onClose"
      >
        Close
      </BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { BModal, BFormGroup, BFormSelect, BFormTextarea, BFormInput, BButton } from 'bootstrap-vue-next'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  type: { type: String, required: true, validator: v => ['structural', 'data'].includes(v) },
  selectedColumns: { type: Array, default: () => [] },
  agentOptions: { type: Array, default: () => [] },
  totalRows: { type: Number, default: 0 },
  operating: { type: Boolean, default: false },
  batchProgress: { type: Object, default: null },
  fuzzyContext: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue', 'apply', 'close'])

// State
const activeTab = ref('simple')
const loading = ref(false)
const error = ref('')
const agentConfig = ref(null)
const selectedAgentId = ref(null)
const instruction = ref('')
const systemPrompt = ref('')
const userPrompt = ref('')
const selectedPreset = ref(null)
const rowsForContext = ref(10)
const includeDescription = ref(false)
const batchProcessAll = ref(false)
const batchSize = ref(10)
const batchDelay = ref(3)
const batchStartRow = ref(0)

// Computed
const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const modalTitle = computed(() => {
  return props.type === 'structural' ? 'AI Structural Clean' : 'AI Data Clean'
})

const instructionPlaceholder = computed(() => {
  return props.type === 'structural'
    ? 'e.g., Rename columns to snake_case, Convert column types appropriately'
    : 'e.g., Fill country based on city, Standardize phone numbers, Categorize product types'
})

const advancedPlaceholder = computed(() => {
  return props.type === 'structural'
    ? 'Add specific instructions for structural changes, e.g., "Rename all columns to lowercase"…'
    : 'Add specific instructions for this analysis, e.g., "Focus on the email column" or "Ignore the ID column"…'
})

const canApply = computed(() => {
  return selectedAgentId.value && instruction.value.trim()
})

const estimatedCalls = computed(() => {
  if (!batchProcessAll.value) return 0
  const remaining = props.totalRows - batchStartRow.value
  return Math.max(1, Math.ceil(remaining / batchSize.value))
})

const progressBarClass = computed(() => {
  if (!props.batchProgress) return ''
  const p = props.batchProgress
  if (p.status === 'done') return 'bg-info'
  if (p.status === 'error') return 'bg-danger'
  if (p.failed > 0) return 'bg-warning'
  return 'bg-success'
})

const promptPresets = computed(() => {
  if (props.type === 'structural') {
    return [
      {
        id: 'quality',
        label: 'Quality',
        icon: 'bi-shield-check',
        description: 'Focus on data quality and consistency',
        system_prompt: 'You are a data quality expert. Focus on identifying and fixing structural issues in the dataset. Ensure column names are consistent, data types are appropriate, and the schema is clean.',
        user_prompt: ''
      },
      {
        id: 'formatting',
        label: 'Formatting',
        icon: 'bi-type',
        description: 'Standardize column names and types',
        system_prompt: 'You are a data formatting specialist. Focus on standardizing column names (e.g., snake_case), ensuring appropriate data types, and maintaining consistent naming conventions.',
        user_prompt: ''
      }
    ]
  } else {
    return [
      {
        id: 'quality',
        label: 'Quality',
        icon: 'bi-shield-check',
        description: 'Focus on data quality and consistency',
        system_prompt: 'You are a data quality expert. Focus on identifying and fixing data quality issues including missing values, inconsistencies, and errors. Ensure data is clean and reliable.',
        user_prompt: ''
      },
      {
        id: 'formatting',
        label: 'Formatting',
        icon: 'bi-type',
        description: 'Standardize formats and values',
        system_prompt: 'You are a data formatting specialist. Focus on standardizing data formats (phone numbers, dates, addresses), fixing typos, and ensuring consistent value representations.',
        user_prompt: ''
      },
      {
        id: 'enrichment',
        label: 'Enrichment',
        icon: 'bi-stars',
        description: 'Fill missing values and derive new data',
        system_prompt: 'You are a data enrichment specialist. Focus on filling missing values based on available context, deriving new columns from existing data, and enhancing the dataset with inferred information.',
        user_prompt: ''
      }
    ]
  }
})

const availableOperations = computed(() => {
  if (props.type === 'structural') {
    return [
      { operation: 'rename', label: 'Rename columns', description: 'Change column names' },
      { operation: 'drop', label: 'Drop columns', description: 'Remove columns' },
      { operation: 'add', label: 'Add columns', description: 'Create new columns' },
      { operation: 'astype', label: 'Change types', description: 'Convert column data types' }
    ]
  } else {
    return [
      { operation: 'fillna', label: 'Fill missing', description: 'Fill null values' },
      { operation: 'find-replace', label: 'Find & Replace', description: 'Replace values' },
      { operation: 'string-operations', label: 'String ops', description: 'Text transformations' },
      { operation: 'extract-json', label: 'Extract JSON', description: 'Parse JSON values' }
    ]
  }
})

const limitOptions = [
  { value: 10, text: '10 rows' },
  { value: 25, text: '25 rows' },
  { value: 50, text: '50 rows' },
  { value: 100, text: '100 rows' }
]

// Methods
function applyPreset(preset) {
  selectedPreset.value = preset.id
  systemPrompt.value = preset.system_prompt
  userPrompt.value = preset.user_prompt
}

async function loadAgentConfig() {
  if (!selectedAgentId.value) return
  loading.value = true
  error.value = ''
  try {
    const apiUrl = import.meta.env.VITE_API_URL || ''
    const res = await fetch(`${apiUrl}/api/assistant/ai-suggest/preflight`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ agent_id: selectedAgentId.value })
    })
    if (res.ok) {
      agentConfig.value = await res.json()
      systemPrompt.value = agentConfig.value.system_prompt || ''
    } else {
      const err = await res.json().catch(() => ({}))
      error.value = err.detail || `Failed to load agent configuration (${res.status})`
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function onApply() {
  const payload = {
    agentId: selectedAgentId.value,
    instruction: instruction.value,
    systemPrompt: systemPrompt.value || undefined,
    userPrompt: userPrompt.value || undefined,
    preset: selectedPreset.value || undefined,
    rowsForContext: rowsForContext.value,
    includeDescription: includeDescription.value
  }
  if (props.type === 'data' && batchProcessAll.value) {
    payload.batchProcessAll = true
    payload.batchSize = batchSize.value
    payload.batchDelay = batchDelay.value
    payload.batchStartRow = batchStartRow.value
  }
  emit('apply', payload)
}

function onClose() {
  emit('close')
  emit('update:modelValue', false)
}

// Watch for agent changes
watch(selectedAgentId, (newVal) => {
  if (newVal) {
    loadAgentConfig()
  }
})

// Reset state when modal opens
watch(() => props.modelValue, (val) => {
  if (val) {
    activeTab.value = 'simple'
    selectedAgentId.value = null
    instruction.value = ''
    systemPrompt.value = ''
    userPrompt.value = ''
    selectedPreset.value = null
    rowsForContext.value = 10
    includeDescription.value = false
    batchProcessAll.value = false
    batchSize.value = 10
    batchDelay.value = 3
    batchStartRow.value = 0
    agentConfig.value = null
    error.value = ''
    
    // Pre-fill with fuzzy matching context if provided
    if (props.fuzzyContext) {
      const ctx = props.fuzzyContext
      const uniqueList = ctx.uniqueValues?.map(v => `${v.value} (${v.frequency})`).join(', ') || ''
      const clusterList = ctx.clusters?.map((c, i) => `Group ${i + 1}: ${c.values.join(' → ')}`).join('\n') || ''
      
      instruction.value = `Help me decide which values to keep for fuzzy matching on column "${ctx.column}".\n\nUnique values: ${uniqueList}\n\nClusters found:\n${clusterList}\n\nPlease recommend which values to merge based on frequency and similarity. Return a mapping of which values should be merged to which target value.`
    }
  }
})
</script>
