<template>
  <div class="boxplot-chart-container" :style="{ height: height }">
    <div v-if="isEmpty" class="chart-placeholder">
      <i class="bi bi-box-seam fs-1 text-muted"></i>
      <p class="text-muted mt-2">No data to display</p>
    </div>
    <canvas v-else ref="canvasRef"></canvas>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, shallowRef } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js'
import {
  BoxPlotController,
  ViolinController,
  BoxAndWiskers,
  Violin,
} from '@sgratzl/chartjs-chart-boxplot'

// Register Chart.js components and boxplot/violin extensions
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  BoxPlotController,
  ViolinController,
  BoxAndWiskers,
  Violin,
)

const props = defineProps({
  chartType: { type: String, default: 'boxplot', validator: (v) => ['boxplot', 'violin'].includes(v) },
  chartData: { type: Object, default: null },
  chartOptions: { type: Object, default: () => ({}) },
  height: { type: String, default: '100%' },
})

const canvasRef = ref(null)
const chartInstance = shallowRef(null)

const isEmpty = computed(() => {
  if (!props.chartData) return true
  if (props.chartData.datasets) {
    return props.chartData.datasets.every(ds => !ds.data || ds.data.length === 0)
  }
  return true
})

function createChart() {
  if (!canvasRef.value || isEmpty.value) return
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }

  const ctx = canvasRef.value.getContext('2d')
  chartInstance.value = new ChartJS(ctx, {
    type: props.chartType,
    data: props.chartData,
    options: props.chartOptions,
  })
}

function updateChart() {
  if (!chartInstance.value || !props.chartData) return
  chartInstance.value.data = props.chartData
  chartInstance.value.options = props.chartOptions
  chartInstance.value.update()
}

watch(() => props.chartData, () => {
  if (chartInstance.value) {
    updateChart()
  } else {
    createChart()
  }
}, { deep: true })

watch(() => props.chartOptions, () => {
  if (chartInstance.value) {
    updateChart()
  }
}, { deep: true })

watch(() => props.chartType, () => {
  // Chart type change requires full re-creation
  createChart()
})

onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
})
</script>

<style scoped>
.boxplot-chart-container {
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