<template>
  <BModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="`Value Mapping — ${column}`"
    size="lg"
    @show="onModalOpen"
  >
    <div class="value-mapping-modal">
      <!-- Info -->
      <p class="text-muted small mb-3">
        <i class="bi bi-info-circle me-1"></i>
        Map values in "<strong>{{ column }}</strong>" to new values.
        Each rule is applied in order. First match wins.
      </p>

      <!-- Mapping Rules -->
      <BFormGroup label="Mapping Rules" label-size="sm" class="mb-3">
        <div
          v-for="(rule, index) in mappingRules"
          :key="index"
          class="d-flex align-items-center gap-2 mb-2"
        >
          <BFormInput
            v-model="rule.from_value"
            placeholder="From value"
            size="sm"
            style="flex: 2"
            @blur="validateRegex(index)"
          />
          <span class="text-muted">→</span>
          <BFormInput
            v-model="rule.to_value"
            placeholder="To value"
            size="sm"
            style="flex: 2"
          />
          <BFormCheckbox
            v-model="rule.is_regex"
            title="Toggle regex mode"
          />
          <span class="small text-muted" :title="rule.is_regex ? 'Regex mode' : 'Exact match'">
            {{ rule.is_regex ? 'RegEx' : 'Exact' }}
          </span>
          <template v-if="rule.is_regex">
            <BFormCheckbox
              v-model="rule.case_sensitive"
              title="Case sensitive"
            />
            <span class="small text-muted">Aa</span>
          </template>
          <BButton
            variant="outline-danger"
            size="sm"
            :disabled="mappingRules.length <= 1"
            @click="removeRule(index)"
          >
            <i class="bi bi-x"></i>
          </BButton>
          <span v-if="regexErrors[index]" class="text-danger small">
            {{ regexErrors[index] }}
          </span>
        </div>

        <div class="d-flex gap-2 mt-2">
          <BButton variant="outline-primary" size="sm" @click="addRule">
            <i class="bi bi-plus me-1"></i>Add Rule
          </BButton>
          <BButton variant="outline-secondary" size="sm" @click="showJsonImport = !showJsonImport">
            <i class="bi bi-code-slash me-1"></i>Import JSON
          </BButton>
          <BButton variant="outline-danger" size="sm" @click="clearAll">
            <i class="bi bi-trash me-1"></i>Clear All
          </BButton>
        </div>

        <!-- JSON Import -->
        <div v-if="showJsonImport" class="mt-2">
          <textarea
            v-model="jsonImportText"
            class="form-control form-control-sm"
            rows="3"
            placeholder='{"old_value": "new_value", ...}'
          ></textarea>
          <BButton variant="primary" size="sm" class="mt-1" @click="importJson(jsonImportText)">
            Import
          </BButton>
        </div>
      </BFormGroup>

      <!-- Unique Values -->
      <BFormGroup v-if="uniqueValues.length > 0" label="Unique Values (click to add)" label-size="sm" class="mb-3">
        <div class="d-flex flex-wrap gap-1">
          <BBadge
            v-for="val in uniqueValues"
            :key="val"
            variant="light"
            pill
            class="cursor-pointer"
            @click="addFromUniqueValue(val)"
          >
            {{ val }}
          </BBadge>
        </div>
      </BFormGroup>

      <!-- Missing Values -->
      <BFormGroup label="Missing Values" label-size="sm" class="mb-3">
        <div class="d-flex align-items-center gap-2">
          <BFormSelect
            v-model="missingValueAction"
            :options="missingValueOptions"
            size="sm"
            style="width: auto"
          />
          <BFormInput
            v-if="showFillInput"
            v-model="missingValueFill"
            placeholder="Fill value"
            size="sm"
            style="flex: 1"
          />
        </div>
      </BFormGroup>

      <!-- Default Value -->
      <BFormGroup label="Default for unmatched" label-size="sm" class="mb-3">
        <BFormInput
          v-model="defaultValue"
          placeholder="Leave empty to keep unmatched values unchanged"
          size="sm"
        />
      </BFormGroup>

      <!-- Preview -->
      <BFormGroup v-if="previewResults.length > 0" label="Preview" label-size="sm" class="mb-0">
        <div class="border rounded p-2 small" style="max-height: 150px; overflow-y: auto">
          <div
            v-for="(row, idx) in previewResults"
            :key="idx"
            class="d-flex gap-2"
          >
            <span :class="{ 'text-decoration-line-through': row.changed }">{{ row.original ?? 'null' }}</span>
            <span v-if="row.changed" class="text-muted">→</span>
            <span v-if="row.changed" class="text-success fw-bold">{{ row.mapped }}</span>
          </div>
        </div>
      </BFormGroup>
    </div>

    <template #footer>
      <div class="d-flex justify-content-end gap-2 w-100">
        <BButton variant="secondary" size="sm" @click="onCancel">Cancel</BButton>
        <BButton
          variant="primary"
          size="sm"
          :disabled="!canApply"
          @click="onApply"
        >
          Apply Mapping
        </BButton>
      </div>
    </template>
  </BModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getApiUrl } from '@/utils/api'
import { useToast } from '@/composables/useToast'

interface MappingRule {
  from_value: string
  to_value: string
  is_regex: boolean
  case_sensitive: boolean
}

interface Props {
  modelValue: boolean
  column: string
  datasetId: string
  uniqueValues: string[]
  operating: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'apply': [payload: any]
}>()

const toast = useToast()

// Local state
const mappingRules = ref<MappingRule[]>([
  { from_value: '', to_value: '', is_regex: false, case_sensitive: true },
])
const missingValueAction = ref('keep')
const missingValueFill = ref('')
const defaultValue = ref('')
const regexErrors = ref<Record<number, string>>({})
const showJsonImport = ref(false)
const jsonImportText = ref('')
const sampleRows = ref<any[]>([])

const missingValueOptions = [
  { value: 'keep', text: 'Keep (nulls stay null)' },
  { value: 'fill', text: 'Fill with value' },
  { value: 'drop', text: 'Drop rows with nulls' },
  { value: 'ignore', text: 'Ignore (same as keep)' },
]

const showFillInput = computed(() => missingValueAction.value === 'fill')

const canApply = computed(() => {
  if (props.operating) return false
  if (Object.keys(regexErrors.value).length > 0) return false
  const validRules = mappingRules.value.filter(r => r.from_value.trim() !== '')
  return validRules.length > 0
})

const previewResults = computed(() => {
  return sampleRows.value.map(row => {
    const val = row[props.column]
    if (val === null || val === undefined) {
      return { original: null, mapped: null, changed: false }
    }
    const strVal = String(val)

    // Apply exact matches first
    for (const rule of mappingRules.value) {
      if (!rule.is_regex && rule.from_value && strVal === rule.from_value) {
        return { original: strVal, mapped: rule.to_value, changed: true }
      }
    }

    // Apply regex matches (first match wins)
    for (const rule of mappingRules.value) {
      if (rule.is_regex && rule.from_value) {
        try {
          const flags = rule.case_sensitive ? '' : 'i'
          const regex = new RegExp(rule.from_value, flags)
          if (regex.test(strVal)) {
            return { original: strVal, mapped: strVal.replace(regex, rule.to_value), changed: true }
          }
        } catch {
          // Invalid regex, skip
        }
      }
    }

    // Apply default value
    if (defaultValue.value && strVal !== null) {
      return { original: strVal, mapped: defaultValue.value, changed: true }
    }

    return { original: strVal, mapped: strVal, changed: false }
  })
})

function addRule() {
  mappingRules.value.push({ from_value: '', to_value: '', is_regex: false, case_sensitive: true })
}

function removeRule(index: number) {
  if (mappingRules.value.length <= 1) return
  mappingRules.value.splice(index, 1)
  // Clean up regex errors for removed index
  const newErrors: Record<number, string> = {}
  for (const [key, val] of Object.entries(regexErrors.value)) {
    const numKey = Number(key)
    if (numKey < index) {
      newErrors[numKey] = val
    } else if (numKey > index) {
      newErrors[numKey - 1] = val
    }
  }
  regexErrors.value = newErrors
}

function clearAll() {
  mappingRules.value = [{ from_value: '', to_value: '', is_regex: false, case_sensitive: true }]
  regexErrors.value = {}
}

function addFromUniqueValue(val: string) {
  // Check if already exists
  const existing = mappingRules.value.find(r => r.from_value === val)
  if (existing) return

  // Find an empty rule to fill
  const emptyRule = mappingRules.value.find(r => r.from_value.trim() === '')
  if (emptyRule) {
    emptyRule.from_value = val
  } else {
    // Add a new rule
    mappingRules.value.push({ from_value: val, to_value: '', is_regex: false, case_sensitive: true })
  }
}

function importJson(jsonStr: string) {
  try {
    const parsed = JSON.parse(jsonStr)
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    //   toast.error('Invalid JSON: expected an object like {"old": "new"}')
      console.error('Invalid JSON: expected an object like {"old": "new"}')
      return
    }
    const newRules: MappingRule[] = Object.entries(parsed).map(([from, to]) => ({
      from_value: String(from),
      to_value: String(to),
      is_regex: false,
      case_sensitive: true,
    }))
    // Replace empty rules with imported ones, keep non-empty
    const nonEmpty = mappingRules.value.filter(r => r.from_value.trim() !== '')
    mappingRules.value = [...nonEmpty, ...newRules]
    showJsonImport.value = false
    jsonImportText.value = ''
    toast.success(`Imported ${newRules.length} mapping(s)`)
  } catch {
    // toast.error('Invalid JSON format')
    console.error('Invalid JSON format')
  }
}

function validateRegex(index: number) {
  const rule = mappingRules.value[index]
  if (!rule.is_regex || !rule.from_value) {
    delete regexErrors.value[index]
    return
  }
  try {
    new RegExp(rule.from_value)
    delete regexErrors.value[index]
  } catch (e: any) {
    regexErrors.value[index] = e.message || 'Invalid regex'
  }
}

function onApply() {
  if (!canApply.value) return

  const validRules = mappingRules.value.filter(r => r.from_value.trim() !== '')
  const payload = {
    column: props.column,
    mappings: validRules.map(r => ({
      from_value: r.from_value,
      to_value: r.to_value,
      is_regex: r.is_regex,
      case_sensitive: r.case_sensitive,
    })),
    missing_value_action: missingValueAction.value,
    missing_value_fill: missingValueAction.value === 'fill' ? missingValueFill.value : null,
    default_value: defaultValue.value || null,
  }

  emit('apply', payload)
}

function onCancel() {
  emit('update:modelValue', false)
}

async function onModalOpen() {
  // Reset state
  mappingRules.value = [{ from_value: '', to_value: '', is_regex: false, case_sensitive: true }]
  missingValueAction.value = 'keep'
  missingValueFill.value = ''
  defaultValue.value = ''
  regexErrors.value = {}
  showJsonImport.value = false
  jsonImportText.value = ''

  // Fetch sample rows for preview
  try {
    const res = await fetch(
      `${getApiUrl()}/api/datasets/${props.datasetId}?limit=10`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      }
    )
    if (res.ok) {
      const data = await res.json()
      sampleRows.value = data.data || data.preview_data || []
    }
  } catch {
    // Silently fail — preview is optional
  }
}

// Validate all regex rules when they change
watch(
  () => mappingRules.value.map(r => r.is_regex ? r.from_value : ''),
  () => {
    mappingRules.value.forEach((rule, index) => {
      if (rule.is_regex && rule.from_value) {
        validateRegex(index)
      }
    })
  }
)
</script>

<style scoped>
.value-mapping-modal .cursor-pointer {
  cursor: pointer;
}
.value-mapping-modal .cursor-pointer:hover {
  opacity: 0.8;
}
</style>
