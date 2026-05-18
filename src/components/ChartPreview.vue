<template>
  <div class="chart-preview-container" :style="{ height: height }">
    <div v-if="!chartData" class="chart-placeholder">
      <i class="bi bi-bar-chart-line fs-1 text-muted"></i>
      <p class="text-muted mt-2">Select columns to preview chart</p>
    </div>
    <div v-else-if="isEmpty" class="chart-placeholder">
      <i class="bi bi-exclamation-circle fs-1 text-warning"></i>
      <p class="text-muted mt-2">No data to display</p>
    </div>
    <Bar v-if="chartType === 'bar' && !isEmpty" :data="chartData" :options="chartOptions" />
    <Line v-if="(chartType === 'line' || chartType === 'area') && !isEmpty" :data="chartData" :options="chartOptions" />
    <Pie v-if="chartType === 'pie' && !isEmpty" :data="chartData" :options="chartOptions" />
    <Scatter v-if="chartType === 'scatter' && !isEmpty" :data="chartData" :options="chartOptions" />
    <Bar v-if="chartType === 'histogram' && !isEmpty" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar, Line, Pie, Scatter } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

const props = defineProps({
  chartType: { type: String, default: 'bar' },
  chartData: { type: Object, default: null },
  chartOptions: { type: Object, default: () => ({}) },
  height: { type: String, default: '100%' },
})

const isEmpty = computed(() => {
  if (!props.chartData) return true
  if (props.chartData.datasets) {
    return props.chartData.datasets.every(ds => !ds.data || ds.data.length === 0)
  }
  return true
})
</script>

<style scoped>
.chart-preview-container {
  position: relative;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
}
</style>
