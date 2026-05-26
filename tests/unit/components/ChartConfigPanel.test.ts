import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock bootstrap-vue-next - use inline factory to avoid hoisting issues
vi.mock('bootstrap-vue-next', () => ({
  BFormGroup: { name: 'BFormGroup', template: '<div class="b-form-group"><slot/></div>' },
  BFormSelect: { name: 'BFormSelect', template: '<select class="b-form-select"><slot/></select>' },
  BFormInput: { name: 'BFormInput', template: '<input class="b-form-input"/>' },
}))

import ChartConfigPanel from '@/components/ChartConfigPanel.vue'

describe('ChartConfigPanel', () => {
  const defaultConfig = {
    chartType: 'bar',
    xAxis: 'city',
    yAxis: 'salary',
    groupBy: '',
    aggregation: 'sum',
    showLegend: true,
    showGrid: true,
    colorPalette: 'default',
    title: '',
    nullHandling: 'exclude',
  }

  const sampleColumnMeta = [
    { name: 'age', dtype: 'int64', uniqueCount: 30, nullCount: 0, columnType: 'numeric' },
    { name: 'salary', dtype: 'float64', uniqueCount: 50, nullCount: 2, columnType: 'numeric' },
    { name: 'city', dtype: 'string', uniqueCount: 5, nullCount: 0, columnType: 'categorical' },
    { name: 'date', dtype: 'datetime64[ns]', uniqueCount: 100, nullCount: 0, columnType: 'datetime' },
  ]

  it('renders chart config panel', () => {
    const wrapper = mount(ChartConfigPanel, {
      props: {
        config: defaultConfig,
        columnMeta: sampleColumnMeta,
      },
    })
    expect(wrapper.find('.chart-config-panel').exists()).toBe(true)
  })

  it('renders warning when provided', () => {
    const wrapper = mount(ChartConfigPanel, {
      props: {
        config: defaultConfig,
        columnMeta: sampleColumnMeta,
        warning: 'Test warning message',
      },
    })
    expect(wrapper.text()).toContain('Test warning message')
  })

  it('does not render warning when not provided', () => {
    const wrapper = mount(ChartConfigPanel, {
      props: {
        config: defaultConfig,
        columnMeta: sampleColumnMeta,
      },
    })
    expect(wrapper.find('.alert-warning').exists()).toBe(false)
  })

  it('renders legend toggle', () => {
    const wrapper = mount(ChartConfigPanel, {
      props: {
        config: defaultConfig,
        columnMeta: sampleColumnMeta,
      },
    })
    expect(wrapper.find('#chart-legend').exists()).toBe(true)
  })

  it('renders grid toggle', () => {
    const wrapper = mount(ChartConfigPanel, {
      props: {
        config: defaultConfig,
        columnMeta: sampleColumnMeta,
      },
    })
    expect(wrapper.find('#chart-grid').exists()).toBe(true)
  })

  it('renders null handling selector', () => {
    const wrapper = mount(ChartConfigPanel, {
      props: {
        config: defaultConfig,
        columnMeta: sampleColumnMeta,
      },
    })
    const selects = wrapper.findAll('select')
    expect(selects.length).toBeGreaterThanOrEqual(1)
  })
})
