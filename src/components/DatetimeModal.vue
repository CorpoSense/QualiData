<template>
  <BModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="Datetime Operations"
    size="lg"
    @show="onModalOpen"
    @hide="onCancel"
  >
    <!-- Info Banner -->
    <div class="alert alert-info py-2 mb-3">
      <i class="bi bi-info-circle me-1"></i>
      Apply datetime operations to <strong>{{ selectedColumns.length }}</strong> column(s).
      Choose an operation and configure error handling.
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

    <!-- Operation Selector -->
    <BFormGroup label="Operation" label-size="sm" class="mb-3">
      <BFormSelect
        v-model="operation"
        size="sm"
        :options="operationOptions"
      ></BFormSelect>
    </BFormGroup>

    <!-- Input Format (only for parse_datetime) -->
    <BFormGroup v-if="operation === 'parse_datetime'" label="Input Format" label-size="sm" class="mb-2">
      <BFormInput
        v-model="inputFormat"
        size="sm"
        placeholder="e.g. %Y-%m-%d, %d/%m/%Y (leave empty for auto-detect)"
      ></BFormInput>
      <small class="text-muted">Python strptime format. Leave empty to auto-detect.</small>
    </BFormGroup>

    <!-- Output Format (only for parse_datetime) -->
    <BFormGroup v-if="operation === 'parse_datetime'" label="Output Format" label-size="sm" class="mb-2">
      <BFormInput
        v-model="outputFormat"
        size="sm"
        placeholder="e.g. %Y-%m-%d, %d/%m/%Y %H:%M:%S"
      ></BFormInput>
      <small class="text-muted">Python strftime format for the output.</small>
    </BFormGroup>

    <!-- Error Handling -->
    <BFormGroup label="Error Handling" label-size="sm" class="mb-2">
      <BFormSelect
        v-model="errorHandling"
        size="sm"
        :options="errorHandlingOptions"
      ></BFormSelect>
      <small class="text-muted">How to handle values that cannot be parsed.</small>
    </BFormGroup>

    <!-- Fallback Value (only shown when error_handling = fallback) -->
    <BFormGroup v-if="errorHandling === 'fallback'" label="Fallback Value" label-size="sm" class="mb-3">
      <BFormInput
        v-model="fallbackValue"
        size="sm"
        placeholder="e.g. 1970-01-01"
      ></BFormInput>
      <small class="text-muted">Values that fail parsing will be replaced with this value.</small>
    </BFormGroup>

    <!-- Create New Column -->
    <div class="form-check mb-3">
      <input
        class="form-check-input"
        type="checkbox"
        v-model="createNewColumn"
        :disabled="selectedColumns.length > 1"
        id="dt-create-new-column"
      >
      <label class="form-check-label small" for="dt-create-new-column">
        Create new column
        <small v-if="selectedColumns.length > 1" class="text-muted">(not available in batch mode)</small>
      </label>
    </div>
    <div v-if="createNewColumn" class="ms-4 mb-3">
      <BFormGroup label="New column name" label-size="sm">
        <BFormInput
          v-model="newColumnName"
          size="sm"
          :placeholder="defaultNewColumnPlaceholder"
        ></BFormInput>
      </BFormGroup>
    </div>

    <!-- Live JS Preview -->
    <div v-if="previewRows.length" class="mb-3">
      <label class="form-label fw-bold small">Preview (first {{ previewRows.length }} rows):</label>

      <!-- Warning Notice -->
      <div v-if="parseErrorCount > 0" class="alert alert-warning py-1 px-2 mb-2 small">
        <i class="bi bi-exclamation-triangle me-1"></i>
        {{ parseErrorCount }} value(s) cannot be parsed with the current settings.
        <span v-if="errorHandling === 'coerce'">They will be set to null.</span>
        <span v-else-if="errorHandling === 'fallback'">They will be set to the fallback value.</span>
        <span v-else-if="errorHandling === 'raise'">The operation will fail.</span>
      </div>

      <div class="bg-light p-2 rounded" style="max-height: 200px; overflow-y: auto;">
        <table class="table table-sm table-bordered mb-0 small" style="font-size: 0.8rem;">
          <thead class="table-light">
            <tr>
              <th style="width: 45%;">Before</th>
              <th style="width: 45%;">After</th>
              <th style="width: 10%;">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, ri) in previewRows" :key="ri">
              <td class="text-muted">{{ row.before }}</td>
              <td :class="{ 'text-danger': row.isError, 'text-success': row.changed && !row.isError }">
                {{ row.after }}
              </td>
              <td>
                <span v-if="row.isError" class="badge bg-danger">Error</span>
                <span v-else-if="row.changed" class="badge bg-success">Changed</span>
                <span v-else class="badge bg-secondary">Same</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
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
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import advancedFormat from 'dayjs/plugin/advancedFormat'

dayjs.extend(customParseFormat)
dayjs.extend(advancedFormat)

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  selectedColumns: { type: Array, default: () => [] },
  operating: { type: Boolean, default: false },
  data: { type: Array, default: () => [] }, // current page data for preview
  defaultOperation: { type: String, default: 'parse_datetime' },
})

const emit = defineEmits(['update:modelValue', 'apply'])

// Local state
const operation = ref('parse_datetime')
const inputFormat = ref('')
const outputFormat = ref('')
const errorHandling = ref('coerce')
const fallbackValue = ref('')
const createNewColumn = ref(false)
const newColumnName = ref('')
const previewRows = ref([])
const parseErrorCount = ref(0)

// Operation options
const operationOptions = [
  { value: 'parse_datetime', text: 'Parse datetime' },
  { value: 'extract_year', text: 'Extract year' },
  { value: 'extract_month', text: 'Extract month' },
  { value: 'extract_day', text: 'Extract day' },
  { value: 'extract_weekday', text: 'Extract weekday' },
]

// Error handling options
const errorHandlingOptions = [
  { value: 'coerce', text: 'Set to null (coerce)' },
  { value: 'fallback', text: 'Replace with fallback value' },
  { value: 'raise', text: 'Fail operation on error' },
]

// Default new column name
const defaultNewColumnPlaceholder = computed(() => {
  const col = props.selectedColumns[0] || 'column'
  switch (operation.value) {
    case 'parse_datetime': return `${col}_parsed`
    case 'extract_year': return `${col}_year`
    case 'extract_month': return `${col}_month`
    case 'extract_day': return `${col}_day`
    case 'extract_weekday': return `${col}_weekday`
    default: return `${col}_result`
  }
})

// Whether the Apply button should be enabled
const canApply = computed(() => {
  if (props.operating) return false
  if (createNewColumn.value && !newColumnName.value.trim()) return false
  if (errorHandling.value === 'fallback' && !fallbackValue.value && parseErrorCount.value > 0) return false
  return true
})

// Python strptime format → dayjs format mapping
function pythonToDayjsFormat(fmt) {
  if (!fmt) return ''
  return fmt
    .replace('%Y', 'YYYY')
    .replace('%m', 'MM')
    .replace('%d', 'DD')
    .replace('%H', 'HH')
    .replace('%M', 'mm')
    .replace('%S', 'ss')
}

// Compute preview
function computePreview() {
  previewRows.value = []
  parseErrorCount.value = 0

  if (!props.data.length || !props.selectedColumns.length) return

  const col = props.selectedColumns[0]
  const sampleSize = Math.min(10, props.data.length)
  const samples = props.data.slice(0, sampleSize)

  const jsInputFormat = inputFormat.value ? pythonToDayjsFormat(inputFormat.value) : null
  const jsOutputFormat = outputFormat.value ? pythonToDayjsFormat(outputFormat.value) : null

  for (const row of samples) {
    const before = String(row[col] ?? '')
    let after = before
    let changed = false
    let isError = false

    try {
      let parsed
      if (jsInputFormat) {
        parsed = dayjs(before, jsInputFormat)
      } else {
        parsed = dayjs(before)
      }

      if (!parsed.isValid()) {
        isError = true
        after = errorHandling.value === 'fallback' ? fallbackValue.value : '(null)'
        changed = true
      } else {
        if (operation.value === 'parse_datetime') {
          const fmt = jsOutputFormat || 'YYYY-MM-DD HH:mm:ss'
          after = parsed.format(fmt)
        } else if (operation.value === 'extract_year') {
          after = String(parsed.year())
        } else if (operation.value === 'extract_month') {
          after = String(parsed.month() + 1)
        } else if (operation.value === 'extract_day') {
          after = String(parsed.date())
        } else if (operation.value === 'extract_weekday') {
          after = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][parsed.day()]
        }
        changed = after !== before
      }
    } catch (e) {
      isError = true
      after = errorHandling.value === 'fallback' ? fallbackValue.value : '(null)'
      changed = true
    }

    if (isError) parseErrorCount.value++
    previewRows.value.push({ before, after, changed, isError })
  }
}

// Debounce preview
let previewTimer = null
function debouncedPreview() {
  clearTimeout(previewTimer)
  previewTimer = setTimeout(computePreview, 300)
}

// Watch for changes that should trigger preview refresh
watch(operation, debouncedPreview)
watch(inputFormat, debouncedPreview)
watch(outputFormat, debouncedPreview)
watch(errorHandling, debouncedPreview)
watch(fallbackValue, debouncedPreview)
watch(createNewColumn, debouncedPreview)
watch(newColumnName, debouncedPreview)

// Reset state when modal opens
function onModalOpen() {
  operation.value = props.defaultOperation || 'parse_datetime'
  inputFormat.value = ''
  outputFormat.value = ''
  errorHandling.value = 'coerce'
  fallbackValue.value = ''
  createNewColumn.value = false
  newColumnName.value = ''
  previewRows.value = []
  parseErrorCount.value = 0
  computePreview()
}

function onCancel() {
  emit('update:modelValue', false)
}

function onApply() {
  if (!canApply.value) return
  const payload = {
    operation: operation.value,
    error_handling: errorHandling.value,
  }
  if (errorHandling.value === 'fallback') payload.fallback_value = fallbackValue.value
  if (createNewColumn.value && newColumnName.value.trim()) payload.new_column = newColumnName.value.trim()
  if (operation.value === 'parse_datetime') {
    if (inputFormat.value.trim()) payload.input_format = inputFormat.value.trim()
    if (outputFormat.value.trim()) payload.output_format = outputFormat.value.trim()
  }
  emit('apply', payload)
  emit('update:modelValue', false)
}
</script>

<style scoped>
.table-sm td, .table-sm th {
  padding: 0.2rem 0.4rem;
}
</style>
