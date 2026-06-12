<template>
  <div v-if="charts.length > 0" class="chart-panel">
    <div class="chart-panel-header">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-bar-chart-line"></i>
        <h6 class="mb-0">Charts ({{ charts.length }})</h6>
      </div>
      <div class="d-flex gap-1">
        <BButton size="sm" variant="outline-secondary" @click="clearAll" title="Close all charts">
          <i class="bi bi-x-lg"></i> Clear All
        </BButton>
      </div>
    </div>
    <div class="chart-panel-body">
      <div v-for="(chart, index) in charts" :key="index" class="chart-panel-item">
        <div class="chart-panel-item-header">
          <div>
            <span class="small fw-bold">{{ chart.config.title || chartLabel(chart.config) }}</span>
            <span v-if="chart.meta?.rowCount" class="badge bg-light text-dark ms-2" style="font-size: 0.65rem;">{{ chart.meta.rowCount }} rows</span>
            <span v-if="chart.meta?.filteredCount && chart.meta.filteredCount !== chart.meta.rowCount" class="badge bg-info ms-2" style="font-size: 0.65rem;">{{ chart.meta.filteredCount }} filtered</span>
          </div>
          <div class="d-flex gap-1">
            <BButton size="sm" variant="link" class="p-0" @click="toggleFullscreen(index)" :title="chart.isFullscreen ? 'Exit fullscreen' : 'Fullscreen'">
              <i :class="chart.isFullscreen ? 'bi bi-fullscreen-exit' : 'bi bi-fullscreen'"></i>
            </BButton>
            <BButton size="sm" variant="link" class="p-0" @click="exportPng(index)" title="Download as PNG">
              <i class="bi bi-download"></i>
            </BButton>
            <BButton size="sm" variant="link" class="p-0 text-danger" @click="removeChart(index)" title="Close chart">
              <i class="bi bi-x-lg"></i>
            </BButton>
          </div>
        </div>
        <div v-if="chart.meta?.warning" class="chart-panel-warning">
          <i class="bi bi-exclamation-triangle me-1"></i>{{ chart.meta.warning }}
        </div>
        <div class="chart-panel-item-canvas" :class="{ 'chart-fullscreen': chart.isFullscreen }" :ref="el => setChartRef(el, index)">
          <BButton
            v-if="chart.isFullscreen"
            size="sm"
            variant="light"
            class="chart-fullscreen-exit-btn"
            @click="toggleFullscreen(index)"
            title="Exit fullscreen"
          >
            <i class="bi bi-fullscreen-exit"></i>
          </BButton>
          <ChartPreview
            :chart-type="chart.config.chartType"
            :chart-data="chart.chartData"
            :chart-options="chart.chartOptions"
            :height="chart.isFullscreen ? '100vh' : '300px'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BButton } from 'bootstrap-vue-next'
import ChartPreview from './ChartPreview.vue'

const props = defineProps({
  charts: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:charts', 'remove', 'clear'])

const chartRefs = ref({})

function setChartRef(el, index) {
  if (el) chartRefs.value[index] = el
}

function chartLabel(config) {
  const typeLabel = config.chartType.charAt(0).toUpperCase() + config.chartType.slice(1)
  if (config.chartType === 'histogram') return `${typeLabel}: ${config.xAxis}`
  return `${typeLabel}: ${config.xAxis} → ${config.yAxis || 'count'}`
}

function removeChart(index) {
  emit('remove', index)
}

function clearAll() {
  emit('clear')
}

function toggleFullscreen(index) {
  const updated = [...props.charts]
  updated[index] = { ...updated[index], isFullscreen: !updated[index].isFullscreen }
  emit('update:charts', updated)
}

function exportPng(index) {
  const container = chartRefs.value[index]
  if (!container) return

  const canvas = container.querySelector('canvas')
  if (!canvas) return

  const link = document.createElement('a')
  link.download = `chart-${props.charts[index].config.chartType}-${Date.now()}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}
</script>

<style scoped>
.chart-panel {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.chart-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
}

.chart-panel-header h6 {
  font-weight: 600;
  color: #334155;
  font-size: 0.85rem;
}

.chart-panel-body {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-panel-item {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.chart-panel-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.chart-panel-item-canvas {
  padding: 8px;
  min-height: 300px;
}

.chart-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 99999;
  background: white;
  padding: 20px;
  min-height: unset;
  display: flex;
  flex-direction: column;
}

.chart-fullscreen-exit-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border-radius: 6px;
}

.chart-panel-warning {
  padding: 4px 10px;
  background: #fff3cd;
  border-bottom: 1px solid #ffc107;
  font-size: 0.7rem;
  color: #856404;
}
</style>
