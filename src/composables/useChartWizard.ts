/**
 * Chart Wizard composable — manages step-by-step wizard state
 * for the Custom Chart Builder wizard (Mode B).
 *
 * Steps:
 * 0. Data Selection  — pick columns
 * 1. Chart Type      — choose chart type with recommendations
 * 2. Axis Mapping    — assign X/Y/Group
 * 3. Styling         — palette, legend, grid, title, aggregation
 * 4. Preview         — final review
 */

import { ref, computed, watch } from 'vue'
import type { ColumnMeta } from './useColumnTypes'
import type { ChartConfig, ChartType, AggregationMethod } from './useChartConfig'
import { suggestChart, getRecommendedChartTypes } from './useChartHeuristic'

export interface WizardStep {
  label: string
  icon: string
  description: string
}

export interface WizardAxisConfig {
  xAxis: string
  yAxis: string
  groupBy: string
  aggregation: AggregationMethod
}

export interface WizardStyleConfig {
  showLegend: boolean
  showGrid: boolean
  colorPalette: string
  title: string
  nullHandling: 'exclude' | 'category' | 'zero'
}

const WIZARD_STEPS: WizardStep[] = [
  { label: 'Data Selection', icon: 'bi-list-check', description: 'Select columns to visualize' },
  { label: 'Chart Type', icon: 'bi-bar-chart', description: 'Choose chart type' },
  { label: 'Axis Mapping', icon: 'bi-arrow-left-right', description: 'Assign axes' },
  { label: 'Styling', icon: 'bi-palette', description: 'Customize appearance' },
  { label: 'Preview', icon: 'bi-eye', description: 'Review & apply' },
]

const MAX_STEPS = 5

/**
 * Composable for the Custom Chart Wizard.
 * Manages wizard state, navigation, validation, and config building.
 */
export function useChartWizard(
  columns: ColumnMeta[],
  initialSelectedColumns: string[] = [],
) {
  const currentStep = ref(0)
  const selectedColumns = ref<string[]>([...initialSelectedColumns])
  const chartType = ref<ChartType>('bar')
  const axisConfig = ref<WizardAxisConfig>({
    xAxis: '',
    yAxis: '',
    groupBy: '',
    aggregation: 'sum',
  })
  const styleConfig = ref<WizardStyleConfig>({
    showLegend: true,
    showGrid: true,
    colorPalette: 'default',
    title: '',
    nullHandling: 'exclude',
  })

  const steps = computed(() => WIZARD_STEPS)

  // --- Derived state ---

  const selectedColumnMeta = computed(() =>
    columns.filter(c => selectedColumns.value.includes(c.name)),
  )

  const recommendedTypes = computed(() =>
    getRecommendedChartTypes(columns, selectedColumns.value),
  )

  // --- Validation ---

  const canGoNext = computed(() => {
    switch (currentStep.value) {
      case 0: // Data Selection — at least 1 column
        return selectedColumns.value.length > 0
      case 1: // Chart Type — must be chosen
        return !!chartType.value
      case 2: // Axis Mapping — xAxis required
        if (chartType.value === 'histogram') return !!axisConfig.value.xAxis
        return !!axisConfig.value.xAxis && !!axisConfig.value.yAxis
      case 3: // Styling — always valid
        return true
      case 4: // Preview — always valid
        return true
      default:
        return false
    }
  })

  const canGoPrev = computed(() => currentStep.value > 0)

  // --- Navigation ---

  function goToStep(step: number) {
    if (step >= 0 && step < MAX_STEPS) {
      currentStep.value = step
    }
  }

  function nextStep() {
    if (canGoNext.value && currentStep.value < MAX_STEPS - 1) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 0) {
      currentStep.value--
    }
  }

  // --- Auto-fill axes when chart type changes ---

  let isAutoFilling = false

  function autoFillAxes() {
    if (isAutoFilling) return
    isAutoFilling = true
    try {
      const suggestion = suggestChart(selectedColumnMeta.value.length > 0 ? selectedColumnMeta.value : columns, selectedColumns.value)
      // Only set axes if they're empty or if the chart type changed
      axisConfig.value.xAxis = suggestion.xAxis
      axisConfig.value.yAxis = suggestion.yAxis
      axisConfig.value.groupBy = suggestion.groupBy
      axisConfig.value.aggregation = suggestion.aggregation
    } finally {
      isAutoFilling = false
    }
  }

  watch(chartType, () => {
    autoFillAxes()
  })

  // Auto-fill when selected columns change (only at step 0-1)
  watch(selectedColumns, () => {
    if (currentStep.value <= 1) {
      autoFillAxes()
    }
  }, { deep: true })

  // --- Auto-fill on initialization ---
  autoFillAxes()

  // --- Build final ChartConfig ---

  function buildChartConfig(): ChartConfig {
    return {
      chartType: chartType.value,
      xAxis: axisConfig.value.xAxis,
      yAxis: axisConfig.value.yAxis,
      sizeColumn: '',
      groupBy: axisConfig.value.groupBy,
      aggregation: axisConfig.value.aggregation,
      showLegend: styleConfig.value.showLegend,
      showGrid: styleConfig.value.showGrid,
      colorPalette: styleConfig.value.colorPalette,
      title: styleConfig.value.title,
      nullHandling: styleConfig.value.nullHandling,
    }
  }

  return {
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
    nextStep,
    prevStep,
    buildChartConfig,
  }
}