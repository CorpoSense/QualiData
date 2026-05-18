<template>
  <div class="chart-config-panel">
    <!-- Chart Type Selector -->
    <BFormGroup label="Chart Type" label-size="sm" class="mb-2">
      <BFormSelect v-model="config.chartType" size="sm" :options="chartTypeOptions"></BFormSelect>
    </BFormGroup>

    <!-- X-Axis -->
    <BFormGroup v-if="showXAxis" label="X-Axis" label-size="sm" class="mb-2">
      <BFormSelect v-model="config.xAxis" size="sm" :options="xAxisOptions"></BFormSelect>
    </BFormGroup>

    <!-- Y-Axis -->
    <BFormGroup v-if="showYAxis" label="Y-Axis" label-size="sm" class="mb-2">
      <BFormSelect v-model="config.yAxis" size="sm" :options="yAxisOptions">
        <template #first>
          <option value="">— None (count) —</option>
        </template>
      </BFormSelect>
    </BFormGroup>

    <!-- Group By -->
    <BFormGroup v-if="showGroupBy" label="Group By" label-size="sm" class="mb-2">
      <BFormSelect v-model="config.groupBy" size="sm" :options="groupByOptions">
        <template #first>
          <option value="">— None —</option>
        </template>
      </BFormSelect>
    </BFormGroup>

    <!-- Aggregation -->
    <BFormGroup v-if="showAggregation" label="Aggregation" label-size="sm" class="mb-2">
      <BFormSelect v-model="config.aggregation" size="sm" :options="aggregationOptions"></BFormSelect>
    </BFormGroup>

    <hr class="my-2" />

    <!-- Options -->
    <div class="form-check form-switch mb-1">
      <input class="form-check-input" type="checkbox" v-model="config.showLegend" id="chart-legend">
      <label class="form-check-label small" for="chart-legend">Show legend</label>
    </div>
    <div class="form-check form-switch mb-1">
      <input class="form-check-input" type="checkbox" v-model="config.showGrid" id="chart-grid">
      <label class="form-check-label small" for="chart-grid">Show grid</label>
    </div>

    <!-- Color Palette -->
    <BFormGroup label="Color Palette" label-size="sm" class="mt-2 mb-2">
      <BFormSelect v-model="config.colorPalette" size="sm" :options="paletteOptions"></BFormSelect>
    </BFormGroup>

    <!-- Title -->
    <BFormGroup label="Chart Title" label-size="sm" class="mb-2">
      <BFormInput v-model="config.title" size="sm" placeholder="Optional chart title"></BFormInput>
    </BFormGroup>

    <!-- Null Handling -->
    <BFormGroup label="Null Values" label-size="sm" class="mb-2">
      <BFormSelect v-model="config.nullHandling" size="sm" :options="nullHandlingOptions"></BFormSelect>
    </BFormGroup>

    <!-- Warning -->
    <div v-if="warning" class="alert alert-warning py-1 px-2 small mt-2">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ warning }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { BFormGroup, BFormSelect, BFormInput } from 'bootstrap-vue-next'
import { CHART_TYPE_OPTIONS, AGGREGATION_OPTIONS, COLOR_PALETTES } from '@/composables/useChartConfig'

const props = defineProps({
  config: { type: Object, required: true },
  columnMeta: { type: Array, default: () => [] },
  warning: { type: String, default: '' },
})

const emit = defineEmits(['update:config'])

// Chart type options
const chartTypeOptions = computed(() =>
  CHART_TYPE_OPTIONS.map(o => ({ value: o.value, text: o.label }))
)

// Aggregation options
const aggregationOptions = computed(() =>
  AGGREGATION_OPTIONS.map(o => ({ value: o.value, text: o.label }))
)

// Palette options
const paletteOptions = computed(() =>
  Object.keys(COLOR_PALETTES).map(k => ({ value: k, text: k.charAt(0).toUpperCase() + k.slice(1) }))
)

// Null handling options
const nullHandlingOptions = [
  { value: 'exclude', text: 'Exclude nulls' },
  { value: 'category', text: 'Treat as category' },
  { value: 'zero', text: 'Fill with 0' },
]

// Column options by type
const numericColumns = computed(() =>
  props.columnMeta.filter(c => c.columnType === 'numeric').map(c => ({ value: c.name, text: c.name }))
)

const categoricalColumns = computed(() =>
  props.columnMeta.filter(c => ['categorical', 'datetime', 'boolean'].includes(c.columnType)).map(c => ({
    value: c.name,
    text: `${c.name} (${c.columnType})`,
  }))
)

const allColumns = computed(() =>
  props.columnMeta.map(c => ({ value: c.name, text: `${c.name} (${c.columnType})` }))
)

const groupableColumns = computed(() =>
  props.columnMeta.filter(c => ['categorical', 'boolean'].includes(c.columnType)).map(c => ({
    value: c.name,
    text: c.name,
  }))
)

// Axis options based on chart type
const xAxisOptions = computed(() => {
  if (props.config.chartType === 'scatter' || props.config.chartType === 'histogram') {
    return numericColumns.value
  }
  return categoricalColumns.value.length > 0 ? categoricalColumns.value : allColumns.value
})

const yAxisOptions = computed(() => numericColumns.value)

const groupByOptions = computed(() => groupableColumns.value)

// Visibility of config sections
const showXAxis = computed(() => true)
const showYAxis = computed(() => props.config.chartType !== 'histogram')
const showGroupBy = computed(() => !['pie', 'scatter', 'histogram'].includes(props.config.chartType))
const showAggregation = computed(() => !['scatter'].includes(props.config.chartType))
</script>

<style scoped>
.chart-config-panel {
  padding: 8px;
  overflow-y: auto;
  max-height: 100%;
}
</style>
