<template>
  <div class="chart-wizard">
    <!-- Step Indicator -->
    <div class="wizard-steps-indicator">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="wizard-step-item"
        :class="{
          active: index === currentStep,
          completed: index < currentStep,
          clickable: index <= highestReachedStep,
        }"
        @click="goToStepIfAllowed(index)"
      >
        <div class="step-dot">
          <i v-if="index < currentStep" class="bi bi-check-lg"></i>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <span class="step-label">{{ step.label }}</span>
      </div>
    </div>

    <!-- Step Content -->
    <div class="wizard-step-content">
      <!-- Step 0: Data Selection -->
      <div v-if="currentStep === 0" class="wizard-step-panel">
        <p class="step-description text-muted small mb-2">Select columns to visualize</p>
        <div class="column-list">
          <label
            v-for="col in columnMeta"
            :key="col.name"
            class="column-item"
            :class="{ selected: selectedColumns.includes(col.name) }"
          >
            <input
              type="checkbox"
              :checked="selectedColumns.includes(col.name)"
              @change="toggleColumn(col.name)"
            />
            <span class="column-name">{{ col.name }}</span>
            <BBadge :variant="badgeVariant(col.columnType)" class="ms-auto" style="font-size: 0.6rem;">
              {{ col.columnType }}
            </BBadge>
          </label>
        </div>

        <!-- Mini preview -->
        <div v-if="selectedColumns.length > 0 && previewData.length > 0" class="mini-preview mt-2">
          <small class="text-muted d-block mb-1">Preview (first {{ Math.min(previewData.length, 5) }} rows):</small>
          <div class="table-responsive">
            <table class="table table-sm table-bordered mb-0" style="font-size: 0.7rem;">
              <thead>
                <tr>
                  <th v-for="col in selectedColumns" :key="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in previewData.slice(0, 5)" :key="i">
                  <td v-for="col in selectedColumns" :key="col">{{ row[col] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Step 1: Chart Type -->
      <div v-if="currentStep === 1" class="wizard-step-panel">
        <p class="step-description text-muted small mb-2">Choose a chart type</p>
        <div class="chart-type-grid">
          <div
            v-for="rec in recommendedTypes"
            :key="rec.type"
            class="chart-type-card"
            :class="{ selected: chartType === rec.type, recommended: rec.recommended }"
            @click="selectChartType(rec.type)"
          >
            <i :class="chartTypeIcon(rec.type)" class="chart-type-icon"></i>
            <span class="chart-type-name">{{ chartTypeName(rec.type) }}</span>
            <BBadge
              v-if="rec.recommended"
              variant="success"
              class="wizard-type-recommended"
              style="font-size: 0.55rem;"
            >
              Recommended
            </BBadge>
            <small v-else class="text-muted" style="font-size: 0.6rem;">{{ rec.reason }}</small>
          </div>
        </div>
      </div>

      <!-- Step 2: Axis Mapping -->
      <div v-if="currentStep === 2" class="wizard-step-panel">
        <p class="step-description text-muted small mb-2">Assign axes</p>
        <BFormGroup label="X-Axis" label-size="sm" class="mb-2">
          <BFormSelect
            :modelValue="axisConfig.xAxis"
            @update:modelValue="axisConfig.xAxis = $event"
            size="sm"
            :options="xAxisOptions"
          />
        </BFormGroup>
        <BFormGroup v-if="chartType !== 'histogram'" label="Y-Axis" label-size="sm" class="mb-2">
          <BFormSelect
            :modelValue="axisConfig.yAxis"
            @update:modelValue="axisConfig.yAxis = $event"
            size="sm"
            :options="yAxisOptions"
          >
            <option value="">— None (count) —</option>
          </BFormSelect>
        </BFormGroup>
        <BFormGroup v-if="showGroupBy" label="Group By" label-size="sm" class="mb-2">
          <BFormSelect
            :modelValue="axisConfig.groupBy"
            @update:modelValue="axisConfig.groupBy = $event"
            size="sm"
            :options="groupByOptions"
          >
            <option value="">— None —</option>
          </BFormSelect>
        </BFormGroup>
        <BFormGroup v-if="chartType !== 'scatter'" label="Aggregation" label-size="sm" class="mb-2">
          <BFormSelect
            :modelValue="axisConfig.aggregation"
            @update:modelValue="axisConfig.aggregation = $event"
            size="sm"
            :options="aggregationOptions"
          />
        </BFormGroup>
      </div>

      <!-- Step 3: Styling -->
      <div v-if="currentStep === 3" class="wizard-step-panel">
        <p class="step-description text-muted small mb-2">Customize appearance</p>
        <BFormGroup label="Color Palette" label-size="sm" class="mb-2">
          <BFormSelect
            :modelValue="styleConfig.colorPalette"
            @update:modelValue="styleConfig.colorPalette = $event"
            size="sm"
            :options="paletteOptions"
          />
        </BFormGroup>
        <BFormGroup label="Chart Title" label-size="sm" class="mb-2">
          <BFormInput
            :modelValue="styleConfig.title"
            @update:modelValue="styleConfig.title = $event"
            size="sm"
            placeholder="Optional chart title"
          />
        </BFormGroup>
        <div class="form-check form-switch mb-1">
          <input
            class="form-check-input"
            type="checkbox"
            :checked="styleConfig.showLegend"
            @change="styleConfig.showLegend = $event.target.checked"
            id="wizard-legend"
          />
          <label class="form-check-label small" for="wizard-legend">Show legend</label>
        </div>
        <div class="form-check form-switch mb-1">
          <input
            class="form-check-input"
            type="checkbox"
            :checked="styleConfig.showGrid"
            @change="styleConfig.showGrid = $event.target.checked"
            id="wizard-grid"
          />
          <label class="form-check-label small" for="wizard-grid">Show grid</label>
        </div>
      </div>

      <!-- Step 4: Preview -->
      <div v-if="currentStep === 4" class="wizard-step-panel">
        <p class="step-description text-muted small mb-2">Review your chart configuration</p>
        <div class="config-summary">
          <div class="summary-row">
            <strong>Chart Type:</strong>
            <span>{{ chartTypeName(chartType) }}</span>
          </div>
          <div class="summary-row">
            <strong>X-Axis:</strong>
            <span>{{ axisConfig.xAxis || '—' }}</span>
          </div>
          <div v-if="chartType !== 'histogram'" class="summary-row">
            <strong>Y-Axis:</strong>
            <span>{{ axisConfig.yAxis || '— (count)' }}</span>
          </div>
          <div v-if="axisConfig.groupBy" class="summary-row">
            <strong>Group By:</strong>
            <span>{{ axisConfig.groupBy }}</span>
          </div>
          <div v-if="chartType !== 'scatter'" class="summary-row">
            <strong>Aggregation:</strong>
            <span>{{ axisConfig.aggregation }}</span>
          </div>
          <div class="summary-row">
            <strong>Color Palette:</strong>
            <span>{{ styleConfig.colorPalette }}</span>
          </div>
          <div v-if="styleConfig.title" class="summary-row">
            <strong>Title:</strong>
            <span>{{ styleConfig.title }}</span>
          </div>
          <div class="summary-row">
            <strong>Legend:</strong>
            <span>{{ styleConfig.showLegend ? 'Visible' : 'Hidden' }}</span>
          </div>
          <div class="summary-row">
            <strong>Grid:</strong>
            <span>{{ styleConfig.showGrid ? 'Visible' : 'Hidden' }}</span>
          </div>
        </div>
        <div class="alert alert-success py-2 px-3 mt-2 mb-0 small">
          <i class="bi bi-check-circle me-1"></i>
          Ready to apply! Click <strong>Add Chart</strong> in the modal footer.
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="wizard-nav">
      <BButton size="sm" variant="outline-secondary" :disabled="!canGoPrev" @click="prevStep">
        <i class="bi bi-arrow-left me-1"></i>Back
      </BButton>
      <BButton size="sm" variant="primary" :disabled="!canGoNext || currentStep == 4" @click="nextStep">
        Next<i class="bi bi-arrow-right ms-1"></i>
      </BButton>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { BButton, BBadge, BFormGroup, BFormSelect, BFormInput } from 'bootstrap-vue-next'
import { useChartWizard } from '@/composables/useChartWizard'
import { CHART_TYPE_OPTIONS, AGGREGATION_OPTIONS, COLOR_PALETTES } from '@/composables/useChartConfig'

const props = defineProps({
  columnMeta: { type: Array, default: () => [] },
  previewData: { type: Array, default: () => [] },
  initialSelectedColumns: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:chartConfig'])

// Wizard composable
const wizard = useChartWizard(props.columnMeta, props.initialSelectedColumns)

const {
  currentStep,
  steps,
  selectedColumns,
  chartType,
  axisConfig,
  styleConfig,
  canGoNext,
  canGoPrev,
  recommendedTypes,
  goToStep,
  nextStep: wizardNext,
  prevStep: wizardPrev,
  buildChartConfig,
} = wizard

const highestReachedStep = computed(() => currentStep.value)

function nextStep() {
  wizardNext()
}

function prevStep() {
  wizardPrev()
}

function goToStepIfAllowed(index) {
  if (index <= highestReachedStep.value) {
    goToStep(index)
  }
}

// Column selection
function toggleColumn(name) {
  const idx = selectedColumns.value.indexOf(name)
  if (idx >= 0) {
    selectedColumns.value.splice(idx, 1)
  } else {
    selectedColumns.value.push(name)
  }
}

// Chart type selection
function selectChartType(type) {
  chartType.value = type
}

// Helpers
function badgeVariant(columnType) {
  const map = { numeric: 'primary', categorical: 'info', datetime: 'warning', boolean: 'secondary', text: 'light' }
  return map[columnType] || 'light'
}

function chartTypeIcon(type) {
  const opt = CHART_TYPE_OPTIONS.find(o => o.value === type)
  return `bi ${opt?.icon || 'bi-bar-chart'}`
}

function chartTypeName(type) {
  const opt = CHART_TYPE_OPTIONS.find(o => o.value === type)
  return opt?.label || type
}

// Column options for axis dropdowns
const numericColumns = computed(() =>
  props.columnMeta.filter(c => c.columnType === 'numeric').map(c => ({ value: c.name, text: c.name })),
)

const categoricalColumns = computed(() =>
  props.columnMeta.filter(c => ['categorical', 'datetime', 'boolean'].includes(c.columnType)).map(c => ({
    value: c.name,
    text: `${c.name} (${c.columnType})`,
  })),
)

const allColumns = computed(() =>
  props.columnMeta.map(c => ({ value: c.name, text: `${c.name} (${c.columnType})` })),
)

const groupableColumns = computed(() =>
  props.columnMeta.filter(c => ['categorical', 'boolean'].includes(c.columnType)).map(c => ({
    value: c.name,
    text: c.name,
  })),
)

const xAxisOptions = computed(() => {
  if (chartType.value === 'scatter' || chartType.value === 'histogram') return numericColumns.value
  return categoricalColumns.value.length > 0 ? categoricalColumns.value : allColumns.value
})

const yAxisOptions = computed(() => numericColumns.value)

const groupByOptions = computed(() => groupableColumns.value)

const showGroupBy = computed(() => !['pie', 'scatter', 'histogram'].includes(chartType.value))

const aggregationOptions = AGGREGATION_OPTIONS.map(o => ({ value: o.value, text: o.label }))

const paletteOptions = Object.keys(COLOR_PALETTES).map(k => ({
  value: k,
  text: k.charAt(0).toUpperCase() + k.slice(1),
}))

// Emit config changes for live preview
function emitConfig() {
  emit('update:chartConfig', buildChartConfig())
}

// Watch all wizard state and emit on any change
watch([chartType, axisConfig, styleConfig, selectedColumns], emitConfig, { deep: true, immediate: true })
</script>

<style scoped>
.chart-wizard {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* Step indicator */
.wizard-steps-indicator {
  display: flex;
  gap: 2px;
  padding: 8px 10px;
  border-bottom: 1px solid #e2e8f0;
  background: #f1f5f9;
}

.wizard-step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  cursor: default;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.wizard-step-item.active,
.wizard-step-item.completed {
  opacity: 1;
}

.wizard-step-item.clickable {
  cursor: pointer;
}

.step-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 600;
  color: #64748b;
  transition: background 0.2s, color 0.2s;
}

.wizard-step-item.active .step-dot {
  background: #3b82f6;
  color: white;
}

.wizard-step-item.completed .step-dot {
  background: #22c55e;
  color: white;
}

.step-label {
  font-size: 0.55rem;
  margin-top: 2px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  color: #64748b;
}

.wizard-step-item.active .step-label {
  color: #1e40af;
  font-weight: 600;
}

/* Step content */
.wizard-step-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 10px;
}

.wizard-step-panel {
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.step-description {
  margin-bottom: 8px;
}

/* Column list */
.column-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.column-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 0.8rem;
}

.column-item:hover {
  background: #e2e8f0;
}

.column-item.selected {
  background: #dbeafe;
}

.column-item input[type="checkbox"] {
  margin: 0;
}

.column-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Mini preview */
.mini-preview {
  overflow-x: auto;
}

/* Chart type grid */
.chart-type-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
}

.chart-type-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 6px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: center;
}

.chart-type-card:hover {
  border-color: #93c5fd;
  background: #f0f9ff;
}

.chart-type-card.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.chart-type-card.recommended {
  border-color: #86efac;
}

.chart-type-card.recommended.selected {
  border-color: #22c55e;
  background: #f0fdf4;
}

.chart-type-icon {
  font-size: 1.2rem;
  color: #475569;
}

.chart-type-card.selected .chart-type-icon {
  color: #2563eb;
}

.chart-type-name {
  font-size: 0.7rem;
  font-weight: 500;
}

/* Config summary */
.config-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 3px 0;
  font-size: 0.8rem;
  border-bottom: 1px solid #f1f5f9;
}

.summary-row strong {
  color: #475569;
}

/* Navigation */
.wizard-nav {
  display: flex;
  justify-content: space-between;
  padding: 8px 10px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  flex-shrink: 0;
}
</style>