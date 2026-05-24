<template>
  <div
    v-if="modelValue"
    class="chart-modal"
    :style="modalStyle"
    @mousedown="bringToFront"
  >
    <!-- Header (Drag Handle) -->
    <div class="chart-modal-header" @mousedown="startDrag">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-bar-chart-line"></i>
        <h6 class="mb-0">Chart Builder</h6>
        <span v-if="datasetName" class="text-muted small">— {{ datasetName }}</span>
      </div>
      <div class="d-flex gap-1">
        <BButton
          size="sm"
          variant="link"
          class="p-0"
          @click="togglePin"
          :title="isPinned ? 'Unpin' : 'Pin on top'"
        >
          <i :class="isPinned ? 'bi bi-pin-fill text-primary' : 'bi bi-pin'"></i>
        </BButton>
        <BButton
          size="sm"
          variant="link"
          class="p-0"
          @click="toggleMinimize"
          :title="isMinimized ? 'Maximize' : 'Minimize'"
        >
          <i :class="isMinimized ? 'bi bi-arrows-angle-expand' : 'bi bi-arrows-angle-contract'"></i>
        </BButton>
        <BButton
          size="sm"
          variant="link"
          class="p-0"
          @click="closeModal"
          title="Close"
        >
          <i class="bi bi-x-lg"></i>
        </BButton>
      </div>
    </div>

    <!-- Content -->
    <div v-show="!isMinimized" class="chart-modal-content">
      <div class="chart-modal-body">
        <!-- Left: Config Panel -->
        <div class="chart-config-section">
          <ChartConfigPanel
            :config="chartConfig.config.value"
            :column-meta="columnMeta"
            :warning="suggestionWarning"
          />
        </div>

        <!-- Right: Live Preview -->
        <div class="chart-preview-section">
          <div v-if="chartLoading" class="chart-loading-overlay">
            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            <span class="ms-2 small text-muted">Loading chart data...</span>
          </div>
          <div v-if="chartWarning" class="chart-warning-banner">
            <i class="bi bi-exclamation-triangle me-1"></i>{{ chartWarning }}
          </div>
          <div v-if="chartError" class="chart-error-banner">
            <i class="bi bi-x-circle me-1"></i>{{ chartError }}
            <small class="d-block text-muted">Using preview data as fallback</small>
          </div>
          <ChartPreview
            :chart-type="chartConfig.config.value.chartType"
            :chart-data="chartData"
            :chart-options="chartOptions"
            height="100%"
          />
        </div>
      </div>

      <!-- Footer -->
      <div class="chart-modal-footer">
        <BButton size="sm" variant="outline-secondary" @click="closeModal">Cancel</BButton>
        <BButton size="sm" variant="primary" :disabled="!canApply" @click="applyChart">
          <i class="bi bi-check-lg me-1"></i>Add Chart
        </BButton>
      </div>
    </div>

    <!-- Resize Handle -->
    <div
      v-if="!isMinimized"
      class="resize-handle"
      @mousedown="startResize"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { BButton } from 'bootstrap-vue-next'
import ChartConfigPanel from './ChartConfigPanel.vue'
import ChartPreview from './ChartPreview.vue'
import { useColumnTypes } from '@/composables/useColumnTypes'
import { useChartConfig, fetchChartData } from '@/composables/useChartConfig'
import { useChartHeuristic } from '@/composables/useChartHeuristic'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  datasetId: { type: String, required: true },
  datasetName: { type: String, default: '' },
  columns: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] },
  profileData: { type: Object, default: null },
  initialChartType: { type: String, default: '' },
  filters: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'apply', 'close'])

// Composables
const { classifyColumns } = useColumnTypes()
const chartConfig = useChartConfig()
const { suggestChart } = useChartHeuristic()

// Modal state (same pattern as PivotModal)
const isMinimized = ref(false)
const isPinned = ref(false)
const isDragging = ref(false)
const isResizing = ref(false)
const position = ref({ x: 80, y: 80 })
const size = ref({ width: 850, height: 550 })
const zIndex = ref(10000)
const dragOffset = ref({ x: 0, y: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0 })
const suggestionWarning = ref('')

// Server-side chart data state
const serverChartData = ref(null)
const chartLoading = ref(false)
const chartError = ref('')
const chartWarning = ref('')
const chartRowCount = ref(0)
const chartFilteredCount = ref(0)
let fetchDebounceTimer = null

// Column metadata from profiling data
const columnMeta = computed(() => {
  if (!props.profileData?.columns) return []
  return classifyColumns(props.profileData.columns)
})

// Computed chart data: prefer server data, fallback to client-side
const chartData = computed(() => {
  if (serverChartData.value) return serverChartData.value
  // Fallback: client-side computation from preview data
  if (!props.data?.length || !chartConfig.config.value.xAxis) return null
  return chartConfig.computeChartData(props.data, columnMeta.value)
})

const chartOptions = computed(() => chartConfig.computeChartOptions())

// Can apply chart
const canApply = computed(() => {
  const cfg = chartConfig.config.value
  if (!cfg.xAxis) return false
  if (cfg.chartType !== 'histogram' && !cfg.yAxis && cfg.aggregation !== 'count') return false
  return true
})

// Modal style
const modalStyle = computed(() => ({
  left: `${position.value.x}px`,
  top: `${position.value.y}px`,
  width: isMinimized.value ? 'auto' : `${size.value.width}px`,
  height: isMinimized.value ? 'auto' : `${size.value.height}px`,
  zIndex: zIndex.value,
}))

// Drag methods (same as PivotModal)
function startDrag(event) {
  if (event.target.closest && event.target.closest('button')) return
  isDragging.value = true
  dragOffset.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y,
  }
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event) {
  if (!isDragging.value) return
  position.value = {
    x: event.clientX - dragOffset.value.x,
    y: event.clientY - dragOffset.value.y,
  }
}

function stopDrag() {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  savePosition()
}

function startResize(event) {
  isResizing.value = true
  resizeStart.value = {
    x: event.clientX,
    y: event.clientY,
    width: size.value.width,
    height: size.value.height,
  }
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  event.preventDefault()
}

function onResize(event) {
  if (!isResizing.value) return
  const deltaX = event.clientX - resizeStart.value.x
  const deltaY = event.clientY - resizeStart.value.y
  size.value = {
    width: Math.max(500, resizeStart.value.width + deltaX),
    height: Math.max(350, resizeStart.value.height + deltaY),
  }
}

function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  saveSize()
}

function toggleMinimize() {
  isMinimized.value = !isMinimized.value
}

function togglePin() {
  isPinned.value = !isPinned.value
}

function bringToFront() {
  if (!isPinned.value) {
    zIndex.value = Math.max(zIndex.value, 10000) + 1
  }
}

function closeModal() {
  emit('update:modelValue', false)
  emit('close')
}

function applyChart() {
  if (!canApply.value) return
  emit('apply', chartConfig.config.value, chartData.value, chartOptions.value, {
    rowCount: chartRowCount.value,
    filteredCount: chartFilteredCount.value,
    warning: chartWarning.value,
  })
  emit('update:modelValue', false)
}

// Server-side chart data fetching
async function loadChartDataFromServer() {
  const cfg = chartConfig.config.value
  if (!cfg.xAxis) {
    serverChartData.value = null
    return
  }

  chartLoading.value = true
  chartError.value = ''
  chartWarning.value = ''

  try {
    const result = await fetchChartData(props.datasetId, cfg, props.filters)
    serverChartData.value = result.chartData
    chartWarning.value = result.warning || ''
    chartRowCount.value = result.rowCount
    chartFilteredCount.value = result.filteredCount
  } catch (e) {
    chartError.value = e.message || 'Failed to load chart data'
    // Fallback to client-side computation
    serverChartData.value = null
  } finally {
    chartLoading.value = false
  }
}

function debouncedLoadChartData() {
  if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
  fetchDebounceTimer = setTimeout(() => {
    loadChartDataFromServer()
  }, 300)
}

// Persistence
function savePosition() {
  try { localStorage.setItem('chart-modal-position', JSON.stringify(position.value)) } catch { /* ignore */ }
}

function saveSize() {
  try { localStorage.setItem('chart-modal-size', JSON.stringify(size.value)) } catch { /* ignore */ }
}

function loadPosition() {
  try {
    const saved = localStorage.getItem('chart-modal-position')
    if (saved) position.value = JSON.parse(saved)
  } catch { /* ignore */ }
}

function loadSize() {
  try {
    const saved = localStorage.getItem('chart-modal-size')
    if (saved) size.value = JSON.parse(saved)
  } catch { /* ignore */ }
}

// Keyboard shortcut
function handleKeydown(event) {
  if (event.key === 'Escape' && props.modelValue) closeModal()
}

// Watch for modal open — apply heuristic suggestion and fetch data
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    isMinimized.value = false
    bringToFront()

    // Apply initial chart type if provided
    if (props.initialChartType) {
      const suggestion = suggestChart(columnMeta.value, props.selectedColumns)
      chartConfig.setPreset(props.initialChartType, suggestion.xAxis, suggestion.yAxis)
      if (suggestion.aggregation) {
        chartConfig.config.value.aggregation = suggestion.aggregation
      }
      if (suggestion.groupBy) {
        chartConfig.config.value.groupBy = suggestion.groupBy
      }
      suggestionWarning.value = suggestion.warning || ''
    } else {
      // Auto-suggest
      const suggestion = suggestChart(columnMeta.value, props.selectedColumns)
      chartConfig.config.value.chartType = suggestion.chartType
      chartConfig.config.value.xAxis = suggestion.xAxis
      chartConfig.config.value.yAxis = suggestion.yAxis
      chartConfig.config.value.groupBy = suggestion.groupBy
      chartConfig.config.value.aggregation = suggestion.aggregation
      suggestionWarning.value = suggestion.warning || ''
    }

    // Fetch chart data from server
    loadChartDataFromServer()
  } else {
    // Reset server data when modal closes
    serverChartData.value = null
    chartError.value = ''
    chartWarning.value = ''
  }
})

// Watch config changes — debounced re-fetch from server
watch(
  () => [
    chartConfig.config.value.chartType,
    chartConfig.config.value.xAxis,
    chartConfig.config.value.yAxis,
    chartConfig.config.value.aggregation,
    chartConfig.config.value.groupBy,
    chartConfig.config.value.nullHandling,
  ],
  () => {
    if (props.modelValue) {
      debouncedLoadChartData()
    }
  },
)

// Watch filters changes — re-fetch
watch(() => props.filters, () => {
  if (props.modelValue) {
    debouncedLoadChartData()
  }
}, { deep: true })

onMounted(() => {
  loadPosition()
  loadSize()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
})
</script>

<style scoped>
.chart-modal {
  position: fixed;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chart-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  cursor: move;
  user-select: none;
}

.chart-modal-header h6 {
  font-weight: 600;
  color: #334155;
}

.chart-modal-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chart-modal-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chart-config-section {
  width: 280px;
  min-width: 250px;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
}

.chart-preview-section {
  flex: 1;
  padding: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 14px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.chart-loading-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
  display: flex;
  align-items: center;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  font-size: 0.8rem;
}

.chart-warning-banner {
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  z-index: 10;
  padding: 4px 10px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #856404;
}

.chart-error-banner {
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  z-index: 10;
  padding: 4px 10px;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #721c24;
}

.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  background: linear-gradient(
    135deg,
    transparent 50%,
    #cbd5e1 50%,
    #cbd5e1 60%,
    transparent 60%,
    transparent 70%,
    #cbd5e1 70%,
    #cbd5e1 80%,
    transparent 80%
  );
}

.resize-handle:hover {
  background: linear-gradient(
    135deg,
    transparent 50%,
    #3b82f6 50%,
    #3b82f6 60%,
    transparent 60%,
    transparent 70%,
    #3b82f6 70%,
    #3b82f6 80%,
    transparent 80%
  );
}
</style>
