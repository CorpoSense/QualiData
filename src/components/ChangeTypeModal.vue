<template>
  <BModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="Change Column Type"
    size="lg"
    @show="onModalOpen"
    @hide="onCancel"
  >
    <!-- Info Banner -->
    <div class="alert alert-info py-2 mb-3">
      <i class="bi bi-info-circle me-1"></i>
      Change the data type of <strong>{{ selectedColumns.length }}</strong> column(s).
      Auto-detect suggests the best type based on your data.
    </div>

    <!-- Column Selection -->
    <BFormGroup label="Columns" label-size="sm" class="mb-3">
      <div class="d-flex flex-wrap gap-1">
        <BBadge
          v-for="col in selectedColumns"
          :key="col"
          variant="info"
          pill
        >{{ col }}</BBadge>
      </div>
    </BFormGroup>

    <!-- Target Type Selector -->
    <BFormGroup label="Target Type" label-size="sm" class="mb-3">
      <BFormSelect
        v-model="targetType"
        size="sm"
        :options="typeOptions"
      ></BFormSelect>
      <!-- Suggested type hint -->
      <div v-if="suggestedType && targetType !== suggestedType" class="mt-1">
        <small class="text-muted">
          <i class="bi bi-lightbulb me-1"></i>
          Suggested: <strong>{{ suggestedType }}</strong> ({{ suggestedConfidence }}% confidence)
          <BButton size="sm" variant="link" class="p-0 ms-1" @click="targetType = suggestedType">Apply suggestion</BButton>
        </small>
      </div>
      <div v-if="suggestedType && targetType === suggestedType" class="mt-1">
        <small class="text-success">
          <i class="bi bi-check-circle me-1"></i>
          This matches the auto-detected type ({{ suggestedConfidence }}% confidence)
        </small>
      </div>
    </BFormGroup>

    <!-- Type Mismatch Feedback -->
    <div v-if="typeMismatchFeedback" class="alert alert-warning py-2 mb-3">
      <i class="bi bi-exclamation-triangle me-1"></i>
      {{ typeMismatchFeedback }}
    </div>

    <!-- Error Handling -->
    <BFormGroup label="Error Handling" label-size="sm" class="mb-2">
      <BFormSelect
        v-model="errorHandling"
        size="sm"
        :options="errorHandlingOptions"
      ></BFormSelect>
      <small class="text-muted">
        How to handle values that cannot be converted to the target type.
      </small>
    </BFormGroup>

    <!-- Fallback Value (only shown when error_handling = fallback) -->
    <BFormGroup v-if="errorHandling === 'fallback'" label="Fallback Value" label-size="sm" class="mb-3">
      <BFormInput
        v-model="fallbackValue"
        size="sm"
        :placeholder="fallbackPlaceholder"
      ></BFormInput>
      <small class="text-muted">Values that fail conversion will be replaced with this value.</small>
    </BFormGroup>

    <!-- Preview Section -->
    <div v-if="previewLoading" class="text-center py-3 mb-3">
      <div class="spinner-border spinner-border-sm text-primary me-1"></div>
      <small class="text-muted">Loading preview...</small>
    </div>

    <div v-else-if="previewData.length" class="mb-3">
      <label class="form-label fw-bold small">Preview</label>

      <!-- Data Loss Warnings -->
      <div v-for="(warning, i) in dataLossWarnings" :key="'w-' + i" class="alert alert-warning py-1 px-2 mb-1 small">
        <i class="bi bi-exclamation-triangle me-1"></i>{{ warning }}
      </div>

      <!-- Error Summary -->
      <div v-if="totalErrorCount > 0" class="alert alert-danger py-1 px-2 mb-2 small">
        <i class="bi bi-x-circle me-1"></i>
        {{ totalErrorCount }} value(s) cannot be converted to {{ targetType }}
        <span v-if="errorHandling === 'coerce'">and will become null</span>
        <span v-else-if="errorHandling === 'fallback'">and will be replaced with fallback value</span>
        <span v-else-if="errorHandling === 'raise'">— the operation will fail</span>
      </div>

      <!-- Before/After Table -->
      <div
        v-for="colPreview in previewData"
        :key="colPreview.column"
        class="mb-2"
      >
        <small class="fw-bold text-muted">{{ colPreview.column }} ({{ colPreview.current_type }} → {{ colPreview.target_type }})</small>
        <table class="table table-sm table-bordered mb-0 small" style="font-size: 0.8rem;">
          <thead class="table-light">
            <tr>
              <th style="width: 40%;">Before</th>
              <th style="width: 40%;">After</th>
              <th style="width: 20%;">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, ri) in colPreview.preview" :key="ri">
              <td :class="{ 'text-muted': row.before === null }">{{ row.before ?? '(null)' }}</td>
              <td :class="{ 'text-muted': row.after === null, 'text-danger': row.error, 'text-success': row.changed && !row.error }">
                {{ row.after ?? '(null)' }}
              </td>
              <td>
                <span v-if="row.error" class="badge bg-danger">Error</span>
                <span v-else-if="row.changed" class="badge bg-success">Changed</span>
                <span v-else class="badge bg-secondary">Same</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="previewError" class="alert alert-danger py-2 mb-3 small">
      <i class="bi bi-x-circle me-1"></i>{{ previewError }}
    </div>

    <div v-else-if="targetType && !previewLoading" class="text-center py-2 mb-3">
      <small class="text-muted">Select a target type to see preview</small>
    </div>

    <template #footer>
      <BButton variant="outline-secondary" @click="onCancel">Cancel</BButton>
      <BButton
        variant="primary"
        :loading="operating"
        :disabled="!canApply"
        @click="onApply"
      >
        <i class="bi bi-check-lg me-1"></i> Apply
      </BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { BModal, BButton, BFormGroup, BFormSelect, BFormInput, BBadge } from 'bootstrap-vue-next'
import { getApiUrl } from '@/utils/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  selectedColumns: { type: Array, default: () => [] },
  datasetId: { type: String, default: '' },
  operating: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'apply'])

const toast = useToast()
const apiUrl = getApiUrl()

// Local state
const targetType = ref('')
const errorHandling = ref('coerce')
const fallbackValue = ref('')
const suggestedType = ref('')
const suggestedConfidence = ref(0)
const detectionResults = ref([])
const previewData = ref([])
const previewLoading = ref(false)
const previewError = ref('')
const dataLossWarnings = ref([])

// Type options for dropdown
const typeOptions = [
  { value: '', text: 'Select a type...' },
  { value: 'string', text: 'String (text)' },
  { value: 'integer', text: 'Integer (whole numbers)' },
  { value: 'float', text: 'Float (decimal numbers)' },
  { value: 'boolean', text: 'Boolean (true/false)' },
  { value: 'datetime', text: 'Datetime (date/time)' },
  { value: 'category', text: 'Category (categorical)' },
]

// Error handling options
const errorHandlingOptions = [
  { value: 'coerce', text: 'Set to null (coerce)' },
  { value: 'fallback', text: 'Replace with fallback value' },
  { value: 'raise', text: 'Fail operation on error' },
]

// Fallback value placeholder based on target type
const fallbackPlaceholder = computed(() => {
  switch (targetType.value) {
    case 'integer': return 'e.g. 0'
    case 'float': return 'e.g. 0.0'
    case 'boolean': return 'e.g. false'
    case 'datetime': return 'e.g. 1970-01-01'
    case 'string': return 'e.g. N/A'
    default: return 'Enter fallback value'
  }
})

// Total error count across all columns
const totalErrorCount = computed(() => {
  return previewData.value.reduce((sum, col) => sum + (col.total_errors || 0), 0)
})

// Whether the Apply button should be enabled
const canApply = computed(() => {
  if (!targetType.value) return false
  if (props.operating) return false
  if (errorHandling.value === 'raise' && totalErrorCount.value > 0) return false
  if (errorHandling.value === 'fallback' && !fallbackValue.value && totalErrorCount.value > 0) return false
  return true
})

// Type mismatch feedback — warn when user selects a type that doesn't match detected data
const typeMismatchFeedback = computed(() => {
  if (!targetType.value || !detectionResults.value.length) return ''
  const mismatches = []
  for (const det of detectionResults.value) {
    const suggested = det.suggested_type
    const scores = det.type_scores || {}
    const targetScore = scores[targetType.value] ?? 0
    if (targetScore < 0.5 && suggested !== targetType.value) {
      mismatches.push(
        `${det.column}: data looks like "${suggested}" (${Math.round((scores[suggested] || 0) * 100)}%), not "${targetType.value}" (${Math.round(targetScore * 100)}%)`
      )
    }
  }
  if (mismatches.length === 0) return ''
  return 'Potential mismatch: ' + mismatches.join('; ')
})

// Fetch type detection when modal opens
async function fetchDetection() {
  if (!props.selectedColumns.length || !props.datasetId) return
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/detect-type`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ columns: props.selectedColumns }),
    })
    if (res.ok) {
      const data = await res.json()
      detectionResults.value = data.columns || []
      // Use first column's suggestion as default
      if (detectionResults.value.length > 0) {
        const first = detectionResults.value[0]
        suggestedType.value = first.suggested_type
        suggestedConfidence.value = Math.round((first.confidence || 0) * 100)
        // Auto-select suggested type if all columns agree
        const allAgree = detectionResults.value.every(d => d.suggested_type === first.suggested_type)
        if (allAgree) {
          targetType.value = first.suggested_type
        }
      }
    } else {
      const err = await res.json()
      console.warn('Type detection failed:', err.detail)
    }
  } catch (e) {
    console.warn('Type detection error:', e.message)
  }
}

// Fetch preview when target type or error handling changes
async function fetchPreview() {
  if (!targetType.value || !props.selectedColumns.length || !props.datasetId) {
    previewData.value = []
    dataLossWarnings.value = []
    previewError.value = ''
    return
  }

  previewLoading.value = true
  previewError.value = ''
  try {
    const body = {
      columns: props.selectedColumns,
      target_type: targetType.value,
      error_handling: errorHandling.value,
      sample_rows: 10,
    }
    if (errorHandling.value === 'fallback' && fallbackValue.value) {
      body.fallback_value = fallbackValue.value
    }
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations/change-type-preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(body),
    })
    if (res.ok) {
      const data = await res.json()
      previewData.value = data.columns || []
      // Aggregate data loss warnings
      const allWarnings = []
      for (const col of previewData.value) {
        if (col.data_loss_warnings) {
          allWarnings.push(...col.data_loss_warnings)
        }
      }
      dataLossWarnings.value = [...new Set(allWarnings)]
    } else {
      const err = await res.json()
      previewError.value = err.detail || 'Preview failed'
      previewData.value = []
      dataLossWarnings.value = []
    }
  } catch (e) {
    previewError.value = e.message
    previewData.value = []
    dataLossWarnings.value = []
  } finally {
    previewLoading.value = false
  }
}

// Debounce timer for preview fetch
let previewTimer = null

// Watch for changes that should trigger preview refresh
watch(targetType, () => {
  clearTimeout(previewTimer)
  previewTimer = setTimeout(fetchPreview, 300)
})

watch(errorHandling, () => {
  clearTimeout(previewTimer)
  previewTimer = setTimeout(fetchPreview, 300)
})

watch(fallbackValue, () => {
  if (errorHandling.value === 'fallback') {
    clearTimeout(previewTimer)
    previewTimer = setTimeout(fetchPreview, 500)
  }
})

// Reset state when modal opens
function onModalOpen() {
  targetType.value = ''
  errorHandling.value = 'coerce'
  fallbackValue.value = ''
  suggestedType.value = ''
  suggestedConfidence.value = 0
  detectionResults.value = []
  previewData.value = []
  previewLoading.value = false
  previewError.value = ''
  dataLossWarnings.value = []
  fetchDetection()
}

function onCancel() {
  emit('update:modelValue', false)
}

function onApply() {
  if (!canApply.value) return
  emit('apply', {
    column: props.selectedColumns[0],
    targetType: targetType.value,
    errorHandling: errorHandling.value,
    fallbackValue: errorHandling.value === 'fallback' ? fallbackValue.value : null,
  })
  emit('update:modelValue', false)
}
</script>

<style scoped>
.table-sm td, .table-sm th {
  padding: 0.2rem 0.4rem;
}
</style>
