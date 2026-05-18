import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// ChartPreview uses vue-chartjs which requires a canvas.
// We'll test the wrapper logic (isEmpty computed, placeholder rendering)
// by mocking the chart components.

// Mock vue-chartjs components
vi.mock('vue-chartjs', () => ({
  Bar: { name: 'Bar', render: () => null, template: '<div class="mock-bar"/>' },
  Line: { name: 'Line', render: () => null, template: '<div class="mock-line"/>' },
  Pie: { name: 'Pie', render: () => null, template: '<div class="mock-pie"/>' },
  Scatter: { name: 'Scatter', render: () => null, template: '<div class="mock-scatter"/>' },
}))

// Mock chart.js register
vi.mock('chart.js', () => ({
  Chart: { register: () => {} },
  CategoryScale: {},
  LinearScale: {},
  BarElement: {},
  LineElement: {},
  PointElement: {},
  ArcElement: {},
  Title: {},
  Tooltip: {},
  Legend: {},
  Filler: {},
}))

import ChartPreview from './ChartPreview.vue'

describe('ChartPreview', () => {
  it('shows placeholder when no chartData', () => {
    const wrapper = mount(ChartPreview, {
      props: {
        chartType: 'bar',
        chartData: null,
        chartOptions: {},
      },
    })
    expect(wrapper.find('.chart-placeholder').exists()).toBe(true)
    expect(wrapper.text()).toContain('Select columns to preview chart')
  })

  it('shows no-data placeholder when chartData has empty datasets', () => {
    const wrapper = mount(ChartPreview, {
      props: {
        chartType: 'bar',
        chartData: { labels: [], datasets: [{ label: 'test', data: [] }] },
        chartOptions: {},
      },
    })
    expect(wrapper.find('.chart-placeholder').exists()).toBe(true)
    expect(wrapper.text()).toContain('No data to display')
  })

  it('shows no-data placeholder when all datasets have empty data', () => {
    const wrapper = mount(ChartPreview, {
      props: {
        chartType: 'bar',
        chartData: {
          labels: ['A', 'B'],
          datasets: [{ label: 'test1', data: [] }, { label: 'test2', data: [] }],
        },
        chartOptions: {},
      },
    })
    expect(wrapper.find('.chart-placeholder').exists()).toBe(true)
  })

  it('renders container with correct height', () => {
    const wrapper = mount(ChartPreview, {
      props: {
        chartType: 'bar',
        chartData: null,
        chartOptions: {},
        height: '400px',
      },
    })
    expect(wrapper.find('.chart-preview-container').attributes('style')).toContain('400px')
  })

  it('uses default height when not specified', () => {
    const wrapper = mount(ChartPreview, {
      props: {
        chartType: 'bar',
        chartData: null,
        chartOptions: {},
      },
    })
    expect(wrapper.find('.chart-preview-container').attributes('style')).toContain('100%')
  })
})
