import { describe, it, expect } from 'vitest'
import { useChartWizard } from '@/composables/useChartWizard'
import type { ColumnMeta } from '@/composables/useColumnTypes'

function makeCol(name: string, columnType: string, uniqueCount = 10, nullCount = 0): ColumnMeta {
  return {
    name,
    dtype: columnType === 'numeric' ? 'float64' : columnType === 'datetime' ? 'datetime' : columnType === 'boolean' ? 'bool' : 'string',
    uniqueCount,
    nullCount,
    columnType: columnType as any,
  }
}

const sampleColumns: ColumnMeta[] = [
  makeCol('city', 'categorical', 5),
  makeCol('revenue', 'numeric', 50),
  makeCol('date', 'datetime', 100),
  makeCol('count', 'numeric', 30),
]

describe('useChartWizard', () => {
  describe('initial state', () => {
    it('starts at step 0', () => {
      const { currentStep } = useChartWizard(sampleColumns, [])
      expect(currentStep.value).toBe(0)
    })

    it('has 5 steps', () => {
      const { steps } = useChartWizard(sampleColumns, [])
      expect(steps.value).toHaveLength(5)
    })

    it('step labels are correct', () => {
      const { steps } = useChartWizard(sampleColumns, [])
      expect(steps.value[0].label).toBe('Data Selection')
      expect(steps.value[1].label).toBe('Chart Type')
      expect(steps.value[2].label).toBe('Axis Mapping')
      expect(steps.value[3].label).toBe('Styling')
      expect(steps.value[4].label).toBe('Preview')
    })

    it('initializes with provided selectedColumns', () => {
      const { selectedColumns } = useChartWizard(sampleColumns, ['city', 'revenue'])
      expect(selectedColumns.value).toEqual(['city', 'revenue'])
    })

    it('initializes with empty selectedColumns when none provided', () => {
      const { selectedColumns } = useChartWizard(sampleColumns, [])
      expect(selectedColumns.value).toEqual([])
    })

    it('has canGoNext false at step 0 with no columns selected', () => {
      const { canGoNext } = useChartWizard(sampleColumns, [])
      expect(canGoNext.value).toBe(false)
    })

    it('has canGoPrev false at step 0', () => {
      const { canGoPrev } = useChartWizard(sampleColumns, ['city'])
      expect(canGoPrev.value).toBe(false)
    })
  })

  describe('step navigation', () => {
    it('nextStep advances to next step', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep()
      expect(wizard.currentStep.value).toBe(1)
    })

    it('prevStep goes back one step', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep() // step 1
      wizard.nextStep() // step 2
      wizard.prevStep() // step 1
      expect(wizard.currentStep.value).toBe(1)
    })

    it('goToStep navigates to specific step', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.goToStep(3)
      expect(wizard.currentStep.value).toBe(3)
    })

    it('cannot go below step 0', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.prevStep()
      expect(wizard.currentStep.value).toBe(0)
    })

    it('cannot go past step 4', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      for (let i = 0; i < 10; i++) wizard.nextStep()
      expect(wizard.currentStep.value).toBe(4)
    })
  })

  describe('step validation', () => {
    it('canGoNext is true at step 0 when columns are selected', () => {
      const { canGoNext } = useChartWizard(sampleColumns, ['city', 'revenue'])
      expect(canGoNext.value).toBe(true)
    })

    it('canGoNext is false at step 1 when no chart type is selected', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep() // step 1
      wizard.chartType.value = '' as any
      expect(wizard.canGoNext.value).toBe(false)
    })

    it('canGoNext is true at step 1 when chart type is selected', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep() // step 1
      wizard.chartType.value = 'bar'
      expect(wizard.canGoNext.value).toBe(true)
    })

    it('canGoNext is false at step 2 when xAxis is empty (non-histogram)', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep() // step 1
      wizard.chartType.value = 'bar'
      wizard.nextStep() // step 2
      wizard.axisConfig.value.xAxis = ''
      expect(wizard.canGoNext.value).toBe(false)
    })

    it('canGoNext is true at step 2 when xAxis is set', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep() // step 1
      wizard.chartType.value = 'bar'
      wizard.nextStep() // step 2
      wizard.axisConfig.value.xAxis = 'city'
      wizard.axisConfig.value.yAxis = 'revenue'
      expect(wizard.canGoNext.value).toBe(true)
    })

    it('canGoNext is true at step 2 for histogram with only xAxis', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep() // step 1
      wizard.chartType.value = 'histogram'
      wizard.nextStep() // step 2
      wizard.axisConfig.value.xAxis = 'revenue'
      expect(wizard.canGoNext.value).toBe(true)
    })

    it('canGoNext is always true at steps 3 and 4', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.goToStep(3)
      expect(wizard.canGoNext.value).toBe(true)
      wizard.goToStep(4)
      expect(wizard.canGoNext.value).toBe(true)
    })
  })

  describe('recommendedTypes', () => {
    it('returns 12 chart type recommendations', () => {
      const { recommendedTypes } = useChartWizard(sampleColumns, ['city', 'revenue'])
      expect(recommendedTypes.value).toHaveLength(12)
    })

    it('recommends bar for categorical + numeric selection', () => {
      const { recommendedTypes } = useChartWizard(sampleColumns, ['city', 'revenue'])
      const bar = recommendedTypes.value.find(r => r.type === 'bar')
      expect(bar?.recommended).toBe(true)
    })

    it('recommends line for datetime + numeric selection', () => {
      const { recommendedTypes } = useChartWizard(sampleColumns, ['date', 'revenue'])
      const line = recommendedTypes.value.find(r => r.type === 'line')
      expect(line?.recommended).toBe(true)
    })

    it('recommends scatter for two numeric columns', () => {
      const { recommendedTypes } = useChartWizard(sampleColumns, ['revenue', 'count'])
      const scatter = recommendedTypes.value.find(r => r.type === 'scatter')
      expect(scatter?.recommended).toBe(true)
    })
  })

  describe('chartType change auto-fills axes', () => {
    it('sets axes when switching to bar with categorical+numeric selected', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep()
      wizard.chartType.value = 'bar'
      // Should auto-fill from heuristic
      expect(wizard.axisConfig.value.xAxis).toBe('city')
      expect(wizard.axisConfig.value.yAxis).toBe('revenue')
    })

    it('sets xAxis only for histogram', () => {
      const wizard = useChartWizard(sampleColumns, ['revenue'])
      wizard.nextStep()
      wizard.chartType.value = 'histogram'
      expect(wizard.axisConfig.value.xAxis).toBe('revenue')
      expect(wizard.axisConfig.value.yAxis).toBe('')
    })
  })

  describe('buildChartConfig', () => {
    it('returns valid ChartConfig from wizard state', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.nextStep()
      wizard.chartType.value = 'bar'
      wizard.axisConfig.value.xAxis = 'city'
      wizard.axisConfig.value.yAxis = 'revenue'
      wizard.axisConfig.value.aggregation = 'sum'

      const config = wizard.buildChartConfig()
      expect(config.chartType).toBe('bar')
      expect(config.xAxis).toBe('city')
      expect(config.yAxis).toBe('revenue')
      expect(config.aggregation).toBe('sum')
      expect(config.showLegend).toBe(true)
      expect(typeof config.colorPalette).toBe('string')
    })

    it('includes style config in built chart', () => {
      const wizard = useChartWizard(sampleColumns, ['city', 'revenue'])
      wizard.styleConfig.value.showLegend = false
      wizard.styleConfig.value.showGrid = false
      wizard.styleConfig.value.title = 'My Chart'
      wizard.styleConfig.value.colorPalette = 'vivid'

      const config = wizard.buildChartConfig()
      expect(config.showLegend).toBe(false)
      expect(config.showGrid).toBe(false)
      expect(config.title).toBe('My Chart')
      expect(config.colorPalette).toBe('vivid')
    })
  })

  describe('composable return value', () => {
    it('exposes all expected properties and methods', () => {
      const wizard = useChartWizard(sampleColumns, [])
      expect(typeof wizard.currentStep.value).toBe('number')
      expect(Array.isArray(wizard.steps.value)).toBe(true)
      expect(Array.isArray(wizard.selectedColumns.value)).toBe(true)
      expect(typeof wizard.chartType.value).toBe('string')
      expect(typeof wizard.axisConfig.value).toBe('object')
      expect(typeof wizard.styleConfig.value).toBe('object')
      expect(typeof wizard.canGoNext.value).toBe('boolean')
      expect(typeof wizard.canGoPrev.value).toBe('boolean')
      expect(typeof wizard.goToStep).toBe('function')
      expect(typeof wizard.nextStep).toBe('function')
      expect(typeof wizard.prevStep).toBe('function')
      expect(typeof wizard.buildChartConfig).toBe('function')
      expect(Array.isArray(wizard.recommendedTypes.value)).toBe(true)
    })
  })
})