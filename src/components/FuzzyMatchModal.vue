<template>
  <BModal
    v-model="isOpen"
    title="Fuzzy Match"
    size="lg"
    no-close-on-backdrop
    @hide="onClose"
  >
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
      <div class="alert alert-secondary mb-3">
        <i class="bi bi-info-circle me-1"></i>
        <strong>Quick fuzzy matching:</strong> Find and merge similar values with one click.
      </div>

      <!-- Selected Column Display -->
      <div class="alert alert-info mb-3" v-if="simpleColumn">
        <i class="bi bi-check-circle me-1"></i>
        Column: <strong>{{ simpleColumn }}</strong>
      </div>
      <div class="alert alert-warning mb-3" v-else>
        <i class="bi bi-exclamation-circle me-1"></i>
        Please select a column from the table header first.
      </div>

      <!-- Algorithm -->
      <BFormGroup label="Algorithm" label-for="simple-algorithm" class="mt-2">
      <BFormSelect
      id="simple-algorithm"
      v-model="simpleMatchingType"
      :options="algorithmOptions"
      ></BFormSelect>
      </BFormGroup>
      
      <!-- Algorithm Info Panel (Simple) -->
      <Transition name="algo-fade" mode="out-in">
      <div :key="simpleMatchingType" class="algo-info-card" :class="`border-${simpleAlgorithmInfo.color}`">
        <div class="algo-info-header">
          <span class="algo-info-icon" :class="`text-${simpleAlgorithmInfo.color}`">
            <i :class="`bi ${simpleAlgorithmInfo.icon}`"></i>
          </span>
          <strong :class="`text-${simpleAlgorithmInfo.color}`">{{ simpleAlgorithmInfo.title }}</strong>
        </div>
        <p class="algo-info-desc">{{ simpleAlgorithmInfo.description }}</p>
        <div class="algo-info-best">
          <i class="bi bi-bullseye me-1"></i>
          <strong>Best for:</strong> {{ simpleAlgorithmInfo.bestFor }}
        </div>
        <div class="algo-info-examples">
          <div class="algo-example-row">
            <code>{{ simpleAlgorithmInfo.example.input }}</code>
            <span class="algo-example-badge bg-success-subtle text-success">{{ simpleAlgorithmInfo.example.result }}</span>
          </div>
          <div class="algo-example-row">
            <code>{{ simpleAlgorithmInfo.example.input2 }}</code>
            <span class="algo-example-badge bg-success-subtle text-success">{{ simpleAlgorithmInfo.example.result2 }}</span>
          </div>
        </div>
      </div>
      </Transition>
      
      <!-- Mode -->
      <BFormGroup label="Action" label-for="simple-mode" class="mt-2">
        <BFormSelect
          id="simple-mode"
          v-model="simpleMode"
          :options="modeOptions"
        ></BFormSelect>
      </BFormGroup>

      <!-- Threshold -->
      <BFormGroup label="Threshold" label-for="simple-threshold" class="mt-2">
        <BFormInput
          id="simple-threshold"
          v-model.number="simpleThreshold"
          type="number"
          min="0"
          max="1"
          step="0.05"
        ></BFormInput>
        <small class="text-muted">Higher = more strict matching (0.8 = 80% similarity)</small>
      </BFormGroup>

      <!-- Error message -->
      <div v-if="error" class="alert alert-danger mt-3 mb-0 py-2 small">
        <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      </div>

      <!-- Apply -->
      <div class="mt-3">
        <button
          class="btn btn-primary"
          :disabled="!simpleColumn || applying"
          @click="applySimpleFuzzy"
        >
          <span v-if="applying">
            <span class="spinner-border spinner-border-sm me-1"></span> Applying...
          </span>
          <span v-else>
            <i class="bi bi-check me-1"></i> Apply
          </span>
        </button>
      </div>
    </div>

    <!-- Advanced Tab -->
    <div v-if="activeTab === 'advanced'">
      <!-- Step Indicator -->
      <div class="mb-3">
        <div class="d-flex justify-content-between">
          <div
            v-for="step in steps"
            :key="step.num"
            class="text-center"
            :class="{ 'text-primary': currentStep >= step.num, 'text-muted': currentStep < step.num }"
          >
            <div
              class="rounded-circle d-inline-flex align-items-center justify-content-center"
              :class="currentStep >= step.num ? 'bg-primary text-white' : 'bg-light'"
              style="width: 32px; height: 32px;"
            >
              {{ step.num }}
            </div>
            <div class="small">{{ step.label }}</div>
          </div>
        </div>
      </div>

      <!-- Step 1: Select Column -->
      <div v-if="currentStep === 1">
        <div class="alert alert-info mb-3">
          <i class="bi bi-info-circle me-1"></i>
          Column: <strong>{{ advColumn }}</strong>
        </div>

        <div class="mt-3">
          <button
            class="btn btn-primary"
            :disabled="!advColumn"
            @click="loadUniqueValues"
          >
            <i class="bi bi-search me-1"></i> View Unique Values
          </button>
        </div>

        <div v-if="loading" class="mt-3 text-center">
          <div class="spinner-border spinner-border-sm"></div>
          <span class="ms-2">Loading...</span>
        </div>

        <div v-if="uniqueValues.length && !loading" class="mt-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <strong>Unique Values ({{ uniqueValues.length }}{{ hasMore ? '+' : '' }})</strong>
            <div class="d-flex gap-2">
              <BFormSelect
                v-model="previewLimit"
                :options="limitOptions"
                size="sm"
                style="width: 120px;"
                @change="loadUniqueValues"
              ></BFormSelect>
              <button
                class="btn btn-sm"
                :class="sortAsc ? 'btn-primary' : 'btn-outline-secondary'"
                @click="sortAsc = !sortAsc; sortValues()"
              >
                <i :class="sortAsc ? 'bi-arrow-up' : 'bi-arrow-down'"></i>
              </button>
            </div>
          </div>

          <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
            <table class="table table-sm table-striped">
              <thead>
                <tr>
                  <th>Value</th>
                  <th>Frequency</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="uv in uniqueValues" :key="uv.value">
                  <td>{{ uv.value }}</td>
                  <td>{{ uv.frequency }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Step 2: Choose Algorithm -->
      <div v-if="currentStep === 2">
        <div class="alert alert-info">
          <i class="bi bi-info-circle me-1"></i>
          Choose an algorithm to find similar values.
        </div>

        <BFormGroup label="Algorithm *" label-for="adv-algorithm">
        <BFormSelect
        id="adv-algorithm"
        v-model="advMatchingType"
        :options="algorithmOptions"
        ></BFormSelect>
        </BFormGroup>
        
        <!-- Algorithm Info Panel (Advanced) -->
        <Transition name="algo-fade" mode="out-in">
        <div :key="advMatchingType" class="algo-info-card" :class="`border-${advAlgorithmInfo.color}`">
          <div class="algo-info-header">
            <span class="algo-info-icon" :class="`text-${advAlgorithmInfo.color}`">
              <i :class="`bi ${advAlgorithmInfo.icon}`"></i>
            </span>
            <strong :class="`text-${advAlgorithmInfo.color}`">{{ advAlgorithmInfo.title }}</strong>
          </div>
          <p class="algo-info-desc">{{ advAlgorithmInfo.description }}</p>
          <div class="algo-info-best">
            <i class="bi bi-bullseye me-1"></i>
            <strong>Best for:</strong> {{ advAlgorithmInfo.bestFor }}
          </div>
          <div class="algo-info-examples">
            <div class="algo-example-row">
              <code>{{ advAlgorithmInfo.example.input }}</code>
              <span class="algo-example-badge bg-success-subtle text-success">{{ advAlgorithmInfo.example.result }}</span>
            </div>
            <div class="algo-example-row">
              <code>{{ advAlgorithmInfo.example.input2 }}</code>
              <span class="algo-example-badge bg-success-subtle text-success">{{ advAlgorithmInfo.example.result2 }}</span>
            </div>
          </div>
        </div>
        </Transition>
        
        <BFormGroup label="Threshold" label-for="adv-threshold" class="mt-2">
          <BFormInput
            id="adv-threshold"
            v-model.number="advThreshold"
            type="number"
            min="0"
            max="1"
            step="0.05"
          ></BFormInput>
          <small class="text-muted">Higher = stricter matching (0.8 = 80% similarity needed)</small>
        </BFormGroup>

        <div class="mt-3">
          <button
            class="btn btn-primary"
            @click="previewTransformation"
          >
            <i class="bi bi-play me-1"></i> Preview
          </button>
        </div>

        <div v-if="previewLoading" class="mt-3 text-center">
          <div class="spinner-border spinner-border-sm"></div>
          <span class="ms-2">Generating preview...</span>
        </div>

        <div v-if="clusters.length && !previewLoading" class="mt-3">
          <strong>Found {{ clusters.length }} cluster(s)</strong>
          <div class="mt-2">
            <div
              v-for="(cluster, idx) in clusters"
              :key="idx"
              class="card mb-2"
            >
              <div class="card-body">
                <strong>Group {{ idx + 1 }} ({{ cluster.values.length }} values)</strong>
                <div class="mt-1">
                  <span
                    v-for="val in cluster.values"
                    :key="val"
                    class="badge bg-secondary me-1"
                  >
                    {{ val }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Select Values to Keep / Skip -->
      <div v-if="currentStep === 3">
        <div class="alert alert-info">
          <i class="bi bi-info-circle me-1"></i>
          For each group, choose which value to keep or skip values that should remain distinct.
        </div>

        <div v-if="clusterGroups.length">
          <div
            v-for="(group, idx) in clusterGroups"
            :key="idx"
            class="card mb-3"
          >
            <div class="card-header">
              <strong>Group {{ idx + 1 }}</strong>
            </div>
            <div class="card-body">
              <div
                v-for="item in group.values"
                :key="item.value"
                class="d-flex align-items-center mb-2"
              >
                <input
                  :id="`skip-${idx}-${item.value}`"
                  v-model="item.skipped"
                  type="checkbox"
                  class="form-check-input me-2"
                >
                <label :for="`skip-${idx}-${item.value}`" class="form-check-label me-auto small text-muted">
                  Skip (keep as-is)
                </label>
                <input
                  :id="`keep-${idx}-${item.value}`"
                  v-model="group.selected"
                  type="radio"
                  :value="item.value"
                  :name="`group-${idx}`"
                  class="form-check-input me-2"
                  :disabled="item.skipped"
                >
                <label :for="`keep-${idx}-${item.value}`" class="form-check-label">
                  {{ item.value }} ({{ item.frequency }} occurrences)
                </label>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="alert alert-warning">
          No clusters found. Try lowering the threshold.
        </div>

        <div class="mt-3 d-flex gap-2">
          <button
            class="btn btn-outline-primary"
            @click="aiHelp"
          >
            <i class="bi bi-robot me-1"></i> AI Help
          </button>
          <button
            class="btn btn-primary"
            :disabled="!canProceed"
            @click="currentStep = 4"
          >
            Next <i class="bi bi-arrow-right ms-1"></i>
          </button>
        </div>
      </div>

      <!-- Step 4: Review & Apply -->
      <div v-if="currentStep === 4">
        <div class="alert alert-success">
          <i class="bi bi-check-circle me-1"></i>
          Ready to apply the operation.
        </div>

        <div class="card">
          <div class="card-header">Summary</div>
          <div class="card-body">
            <p><strong>Column:</strong> {{ advColumn }}</p>
            <p><strong>Algorithm:</strong> {{ advMatchingType }}</p>
            <p><strong>Threshold:</strong> {{ advThreshold }}</p>
            <p><strong>Changes:</strong> {{ totalChanges }} values to merge</p>
          </div>
        </div>

        <div class="mt-3">
          <button
            class="btn btn-primary"
            :disabled="applying"
            @click="applyOperation"
          >
            <span v-if="applying">
              <span class="spinner-border spinner-border-sm me-1"></span> Applying...
            </span>
            <span v-else>
              <i class="bi bi-check me-1"></i> Apply
            </span>
          </button>
        </div>
      </div>

      <!-- Navigation Buttons -->
      <div v-if="currentStep < 4" class="mt-3 d-flex gap-2">
        <button
          v-if="currentStep > 1"
          class="btn btn-outline-secondary"
          @click="currentStep--"
        >
          <i class="bi bi-arrow-left me-1"></i> Back
        </button>
        <button
          v-if="currentStep < 3"
          class="btn btn-primary"
          :disabled="!canProceed"
          @click="currentStep++"
        >
          Next <i class="bi bi-arrow-right ms-1"></i>
        </button>
      </div>
    </div>

    <template #footer>
      <BButton variant="outline-secondary" @click="onClose">Cancel</BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { BModal, BFormGroup, BFormSelect, BFormInput, BButton } from 'bootstrap-vue-next'
import { getApiUrl } from '@/utils/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  columns: { type: Array, default: () => [] },
  datasetId: { type: String, default: '' },
  agentOptions: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'apply', 'applySimple', 'aiHelp'])

// State
const activeTab = ref('simple')
const currentStep = ref(1)
const loading = ref(false)
const previewLoading = ref(false)
const applying = ref(false)
const error = ref('')

// Simple mode state
const simpleColumn = ref('')
const simpleMatchingType = ref('standard')
const simpleMode = ref('merge_first')
const simpleThreshold = ref(0.8)

// Advanced mode state
const advColumn = ref('')
const advMatchingType = ref('standard')
const advThreshold = ref(0.8)
const previewLimit = ref(50)
const sortAsc = ref(false)
const uniqueValues = ref([])
const hasMore = ref(false)
const clusters = ref([])
const clusterGroups = ref([])

// Steps
const steps = [
  { num: 1, label: 'Column' },
  { num: 2, label: 'Algorithm' },
  { num: 3, label: 'Select' },
  { num: 4, label: 'Apply' }
]

// Computed
const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const columnOptions = computed(() => {
  return props.columns.map(c => ({ value: c.field || c.name, text: c.label || c.field || c.name }))
})

const algorithmOptions = [
  { value: 'standard', text: 'Standard (SequenceMatcher)' },
  { value: 'permutation', text: 'Permutation (word order insensitive)' },
  { value: 'levenshtein', text: 'Levenshtein (edit distance)' }
]

const algorithmDescriptions = {
  standard: {
    title: 'Standard — SequenceMatcher',
    icon: 'bi-barcode',
    color: 'primary',
    description: 'Compares the longest matching subsequences between two strings. It finds common character sequences regardless of position, making it great for catching typos and slight misspellings.',
    bestFor: 'Typos, misspellings, and slight variations in text',
    example: {
      input: '"New York" vs "New Yrk"',
      result: '92% match ✓',
      input2: '"California" vs "Calfornia"',
      result2: '86% match ✓'
    }
  },
  permutation: {
    title: 'Permutation — Word Order Insensitive',
    icon: 'bi-shuffle',
    color: 'success',
    description: 'Splits text into words and compares all possible word orderings. The match score is the best score across any word permutation, so reordering words has no effect on similarity.',
    bestFor: 'Values where word order varies but words are the same',
    example: {
      input: '"John Smith" vs "Smith John"',
      result: '100% match ✓',
      input2: '"New York City" vs "City New York"',
      result2: '100% match ✓'
    }
  },
  levenshtein: {
    title: 'Levenshtein — Edit Distance',
    icon: 'bi-pencil-square',
    color: 'warning',
    description: 'Counts the minimum number of single-character edits (insertions, deletions, substitutions) needed to transform one string into another. Fewer edits = higher similarity.',
    bestFor: 'Short strings, codes, and exact character-level differences',
    example: {
      input: '"Kitten" → "Sitten" (1 substitution)',
      result: '83% match ✓',
      input2: '"ABC123" vs "ABC124"',
      result2: '83% match ✓'
    }
  }
}

const simpleAlgorithmInfo = computed(() => algorithmDescriptions[simpleMatchingType.value])
const advAlgorithmInfo = computed(() => algorithmDescriptions[advMatchingType.value])

const modeOptions = [
  { value: 'delete', text: 'Remove duplicates' },
  { value: 'merge_first', text: 'Merge to first occurrence' },
  { value: 'merge_most_frequent', text: 'Merge to most frequent' }
]

const limitOptions = [
  { value: 25, text: '25 values' },
  { value: 50, text: '50 values' },
  { value: 100, text: '100 values' },
  { value: 200, text: '200 values' }
]

const canProceed = computed(() => {
  if (currentStep.value === 1) return !!advColumn.value
  if (currentStep.value === 2) return true // Can always preview
  if (currentStep.value === 3) return clusterGroups.value.length > 0 || clusters.value.length === 0
  return false
})

const totalChanges = computed(() => {
  let count = 0
  for (const group of clusterGroups.value) {
    const nonSkipped = group.values.filter(v => !v.skipped)
    if (nonSkipped.length > 1) {
      count += nonSkipped.length - 1
    }
  }
  return count
})

// Methods
async function loadUniqueValues() {
  if (!advColumn.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const apiUrl = getApiUrl()
    const params = new URLSearchParams({
      column: advColumn.value,
      limit: String(previewLimit.value),
      threshold: String(advThreshold.value),
      matching_type: advMatchingType.value
    })
    const res = await fetch(
      `${apiUrl}/api/datasets/${props.datasetId}/operations/fuzzy-preview?${params}`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      }
    )
    
    if (res.ok) {
      const data = await res.json()
      uniqueValues.value = data.unique_values || []
      hasMore.value = data.has_more || false
      clusters.value = data.clusters || []
      
      // Build cluster groups for selection
      clusterGroups.value = clusters.value.map((cluster, idx) => ({
        values: cluster.values.map(v => ({ value: v, frequency: uniqueValues.value.find(uv => uv.value === v)?.frequency || 0, skipped: false })),
        selected: cluster.values[0]
      }))
    } else {
      const err = await res.json().catch(() => ({}))
      error.value = err.detail || 'Failed to load unique values'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function sortValues() {
  uniqueValues.value.sort((a, b) => {
    return sortAsc.value ? a.frequency - b.frequency : b.frequency - a.frequency
  })
}

async function previewTransformation() {
  if (!advColumn.value) return
  previewLoading.value = true
  error.value = ''

  try {
    const apiUrl = getApiUrl()
    const params = new URLSearchParams({
      column: advColumn.value,
      limit: String(previewLimit.value),
      threshold: String(advThreshold.value),
      matching_type: advMatchingType.value
    })
    const res = await fetch(
      `${apiUrl}/api/datasets/${props.datasetId}/operations/fuzzy-preview?${params}`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    if (res.ok) {
      const data = await res.json()
      uniqueValues.value = data.unique_values || []
      hasMore.value = data.has_more || false
      clusters.value = data.clusters || []

      // Build cluster groups for selection with skipped flag
      clusterGroups.value = clusters.value.map((cluster) => ({
        values: cluster.values.map(v => ({ value: v, frequency: uniqueValues.value.find(uv => uv.value === v)?.frequency || 0, skipped: false })),
        selected: cluster.values[0]
      }))
      currentStep.value = 3
    } else {
      const err = await res.json().catch(() => ({}))
      error.value = err.detail || 'Failed to generate preview'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    previewLoading.value = false
  }
}

function aiHelp() {
  // Emit event to open AI modal with fuzzy matching context
  emit('aiHelp', {
    column: advColumn.value,
    uniqueValues: uniqueValues.value,
    clusters: clusters.value,
    mode: 'fuzzy-match'
  })
}

async function applySimpleFuzzy() {
  if (!simpleColumn.value) {
    error.value = 'Please select a column from the table header first.'
    return
  }

  applying.value = true
  error.value = ''

  try {
    const apiUrl = getApiUrl()
    const res = await fetch(
      `${apiUrl}/api/datasets/${props.datasetId}/operations/fuzzy-dedupe`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          column: simpleColumn.value,
          threshold: simpleThreshold.value,
          matching_type: simpleMatchingType.value,
          mode: simpleMode.value
        })
      }
    )

    if (res.ok) {
      const data = await res.json()
      emit('applySimple', {
        status: 'success',
        data,
        column: simpleColumn.value,
        matching_type: simpleMatchingType.value,
        threshold: simpleThreshold.value,
        mode: simpleMode.value
      })
      onClose()
    } else {
      const err = await res.json().catch(() => ({}))
      error.value = err.detail || 'Operation failed'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    applying.value = false
  }
}

async function applyOperation() {
  // Build mapping from cluster groups, respecting skipped values
  const mapping = {}
  
  for (const group of clusterGroups.value) {
    const selectedValue = group.selected
    for (const item of group.values) {
      // Skip values marked as "keep as-is" and the selected value itself
      if (!item.skipped && item.value !== selectedValue) {
        mapping[item.value] = selectedValue
      }
    }
  }
  
  applying.value = true
  
  try {
    const apiUrl = getApiUrl()
    const res = await fetch(
      `${apiUrl}/api/datasets/${props.datasetId}/operations/fuzzy-advanced`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          column: advColumn.value,
          mapping: mapping,
          matching_type: advMatchingType.value,
          threshold: advThreshold.value
        })
      }
    )
    
    if (res.ok) {
      const data = await res.json()
      emit('apply', { status: 'success', data })
      onClose()
    } else {
      const err = await res.json().catch(() => ({}))
      error.value = err.detail || 'Operation failed'
    }
  } catch (e) {
    error.value = e.message
  } finally {
    applying.value = false
  }
}

function onClose() {
  emit('update:modelValue', false)
  resetState()
}

function resetState() {
  currentStep.value = 1
  uniqueValues.value = []
  clusters.value = []
  clusterGroups.value = []
  error.value = ''
}

// Watch for modal open
watch(() => props.modelValue, (val) => {
  if (val) {
    activeTab.value = 'simple'
    currentStep.value = 1
    // Auto-select from selected columns
    if (props.selectedColumns && props.selectedColumns.length > 0) {
      const col = props.selectedColumns[0]
      simpleColumn.value = col
      advColumn.value = col
    } else {
      simpleColumn.value = ''
      advColumn.value = ''
    }
  }
})

// Apply simple operation
watch(simpleColumn, (val) => {
  if (activeTab.value === 'simple' && val) {
    advColumn.value = val
  }
})
</script>

<style scoped>
.algo-info-card {
  margin-top: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: 0.5rem;
  border-left: 4px solid;
  background: var(--bs-gray-100);
  transition: all 0.2s ease;
}

.algo-info-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.algo-info-icon {
  font-size: 1.15rem;
  line-height: 1;
}

.algo-info-desc {
  font-size: 0.82rem;
  margin-bottom: 0.45rem;
  color: var(--bs-secondary-color);
  line-height: 1.45;
}

.algo-info-best {
  font-size: 0.78rem;
  margin-bottom: 0.55rem;
  color: var(--bs-secondary-color);
}

.algo-info-examples {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.algo-example-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.78rem;
}

.algo-example-row code {
  background: var(--bs-gray-200);
  padding: 0.15rem 0.45rem;
  border-radius: 0.25rem;
  font-size: 0.78rem;
  white-space: nowrap;
}

.algo-example-badge {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 1rem;
  font-weight: 600;
  white-space: nowrap;
}

/* Transition for switching algorithms */
.algo-fade-enter-active,
.algo-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.algo-fade-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}

.algo-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>