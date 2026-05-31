<template>
  <div class="chart-ai-suggest">
    <!-- Step Indicator -->
    <div class="step-indicator mb-3">
      <div class="d-flex align-items-center justify-content-center gap-2">
        <div class="step-dot" :class="{ active: currentStep === 1, completed: currentStep === 2 }">
          <i v-if="currentStep === 2" class="bi bi-check-lg" style="font-size: 0.6rem;"></i>
          <span v-else>1</span>
        </div>
        <div class="step-line" :class="{ active: currentStep === 2 }"></div>
        <div class="step-dot" :class="{ active: currentStep === 2 }">2</div>
      </div>
      <div class="d-flex justify-content-between px-1 mt-1">
        <small class="text-muted" :class="{ 'fw-bold text-primary': currentStep === 1 }">Configure</small>
        <small class="text-muted" :class="{ 'fw-bold text-primary': currentStep === 2 }">Review</small>
      </div>
    </div>

    <!-- Step 1: Configure -->
    <div v-if="currentStep === 1">
      <!-- Agent Selection -->
      <div class="mb-3">
        <label class="form-label small fw-bold">AI Agent</label>
        <BFormSelect
          v-model="selectedAgentId"
          :options="agentOptions"
          size="sm"
        />
      </div>

      <!-- Column Selection -->
      <div v-if="columnMeta.length > 0" class="mb-3">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <label class="form-label small fw-bold mb-0">Dataset Columns</label>
          <a href="#" class="small text-decoration-none" @click.prevent="toggleAllColumns">
            {{ allColumnsSelected ? 'Deselect All' : 'Select All' }}
          </a>
        </div>
        <div class="column-info-list">
          <div
            v-for="col in columnMeta"
            :key="col.name"
            class="column-info-item d-flex align-items-center gap-2 py-1"
            :class="{ 'selected': activeSelectedColumns.includes(col.name) }"
          >
            <BFormCheckbox
              :model-value="activeSelectedColumns.includes(col.name)"
              @update:model-value="(val) => {
                if (val) {
                  activeSelectedColumns.push(col.name)
                } else {
                  activeSelectedColumns = activeSelectedColumns.filter(c => c !== col.name)
                }
              }"
              class="mb-0"
            />
            <span class="small text-truncate flex-grow-1">{{ col.name }}</span>
            <BBadge :variant="badgeVariant(col.columnType)" style="font-size: 0.55rem;">
              {{ col.columnType }}
            </BBadge>
          </div>
        </div>
      </div>

      <!-- Custom Instruction -->
      <div class="mb-3">
        <label class="form-label small fw-bold">
          Custom Instruction
          <span class="text-muted fw-normal">(optional)</span>
        </label>
        <BFormTextarea
          v-model="customInstruction"
          :rows="2"
          placeholder="e.g. Show top 5 cities by revenue, or compare trends over time..."
          :disabled="loading"
        />
      </div>

      <!-- Analyze Button -->
      <BButton
        variant="primary"
        size="sm"
        class="w-100 mb-2"
        :disabled="!selectedAgentId || loading"
        @click="analyze"
      >
        <template v-if="loading">
          <span class="spinner-border spinner-border-sm me-1" role="status"></span>
          Analyzing...
        </template>
        <template v-else>
          <i class="bi bi-search me-1"></i>Analyze Data
        </template>
      </BButton>

      <!-- Error -->
      <div v-if="error" class="alert alert-danger py-2 mb-2 small">
        <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      </div>
    </div>

    <!-- Step 2: Review -->
    <div v-if="currentStep === 2 && result && result.config">
      <!-- Suggestion Result -->
      <div class="suggestion-card p-3 bg-light rounded mb-3">
        <div class="d-flex align-items-center gap-2 mb-2">
          <i class="bi bi-check-circle-fill text-success"></i>
          <span class="fw-bold small">AI Suggestion</span>
        </div>

        <div class="suggestion-details">
          <div class="d-flex align-items-center gap-2 mb-1">
            <span class="badge bg-primary">{{ chartTypeLabel }}</span>
            <span class="small fw-bold">{{ result.config.title || 'Untitled Chart' }}</span>
          </div>

          <table class="table table-sm table-borderless mb-1" style="font-size: 0.75rem;">
            <tbody>
              <tr>
                <td class="text-muted" style="width: 80px;">X-Axis</td>
                <td class="fw-medium">{{ result.config.xAxis }}</td>
              </tr>
              <tr v-if="result.config.chartType !== 'histogram'">
                <td class="text-muted">Y-Axis</td>
                <td class="fw-medium">{{ result.config.yAxis || '—' }}</td>
              </tr>
              <tr v-if="result.config.groupBy">
                <td class="text-muted">Group</td>
                <td class="fw-medium">{{ result.config.groupBy }}</td>
              </tr>
              <tr v-if="result.config.chartType !== 'scatter' && result.config.chartType !== 'histogram'">
                <td class="text-muted">Agg.</td>
                <td class="fw-medium">{{ result.config.aggregation }}</td>
              </tr>
              <tr>
                <td class="text-muted">Palette</td>
                <td class="fw-medium">{{ result.config.colorPalette }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Explanation -->
        <div v-if="result.explanation" class="explanation-text mt-2 p-2 bg-white rounded border small text-muted">
          <i class="bi bi-lightbulb me-1 text-warning"></i>{{ result.explanation }}
        </div>
      </div>

      <!-- Navigation -->
      <div class="d-flex gap-2">
        <BButton variant="outline-secondary" size="sm" @click="goBack">
          <i class="bi bi-arrow-left me-1"></i>Previous
        </BButton>
        <BButton variant="success" size="sm" class="flex-grow-1" @click="applySuggestion">
          <i class="bi bi-check-lg me-1"></i>Apply
        </BButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { BButton, BFormSelect, BFormTextarea, BBadge, BFormCheckbox } from 'bootstrap-vue-next'
import { useChartAiSuggestion, CHART_TYPE_LABELS } from '@/composables/useChartAiSuggestion'

const props = defineProps({
  agentOptions: { type: Array, default: () => [] },
  columnMeta: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] },
  datasetId: { type: String, default: '' },
})

const emit = defineEmits(['apply'])

// AI suggestion composable
const { loading, result, error, clearResult, requestAiSuggestion } = useChartAiSuggestion()

// Local state
const selectedAgentId = ref(null)
const customInstruction = ref('')
const currentStep = ref(1)
const activeSelectedColumns = ref([...props.selectedColumns])

// Auto-advance to step 2 when result becomes available
watch(result, (val) => {
  if (val?.config && currentStep.value === 1) {
    currentStep.value = 2
  }
}, { immediate: true })

// Select All / Deselect All toggle
const allColumnsSelected = computed(() =>
  props.columnMeta.length > 0 && activeSelectedColumns.value.length === props.columnMeta.length
)

function toggleAllColumns() {
  if (allColumnsSelected.value) {
    activeSelectedColumns.value = []
  } else {
    activeSelectedColumns.value = props.columnMeta.map(c => c.name)
  }
}

// Chart type display label
const chartTypeLabel = computed(() => {
  if (!result.value?.config?.chartType) return ''
  return CHART_TYPE_LABELS[result.value.config.chartType] || result.value.config.chartType
})

// Badge variant based on column type
function badgeVariant(columnType) {
  const map = {
    numeric: 'primary',
    categorical: 'success',
    datetime: 'info',
    boolean: 'warning',
    text: 'secondary',
  }
  return map[columnType] || 'secondary'
}

// Analyze data with AI
async function analyze() {
  await requestAiSuggestion({
    agentId: selectedAgentId.value,
    datasetId: props.datasetId,
    columnMeta: props.columnMeta,
    selectedColumns: activeSelectedColumns.value,
    customInstruction: customInstruction.value || undefined,
  })
  // Auto-advance to step 2 if result was received
  if (result.value?.config) {
    currentStep.value = 2
  }
}

// Go back to step 1
function goBack() {
  currentStep.value = 1
}

// Apply the AI suggestion
function applySuggestion() {
  if (result.value?.config) {
    emit('apply', { ...result.value.config })
  }
}
</script>

<style scoped>
.chart-ai-suggest {
  padding: 4px;
}

/* Step indicator */
.step-indicator {
  padding: 4px 8px;
}

.step-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 600;
  background: #e2e8f0;
  color: #94a3b8;
  transition: all 0.2s;
}

.step-dot.active {
  background: #3b82f6;
  color: white;
}

.step-dot.completed {
  background: #22c55e;
  color: white;
}

.step-line {
  flex: 1;
  height: 2px;
  background: #e2e8f0;
  transition: background 0.2s;
}

.step-line.active {
  background: #22c55e;
}

/* Column info list */
.column-info-list {
  max-height: 120px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
}

.column-info-item {
  padding: 2px 8px;
  border-bottom: 1px solid #f1f5f9;
}

.column-info-item:last-child {
  border-bottom: none;
}

.column-info-item.selected {
  background: #eff6ff;
}

/* Suggestion card */
.suggestion-card {
  border: 1px solid #e2e8f0;
}

.suggestion-details .table td {
  padding: 1px 4px;
}

.explanation-text {
  line-height: 1.4;
}
</style>