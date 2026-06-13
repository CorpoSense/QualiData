import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.mock('@/components/ChartPreview.vue', () => ({
  default: {
    name: 'ChartPreview',
    template: '<div class="mock-chart-preview"/>',
    props: ['chartType', 'chartData', 'chartOptions', 'height'],
  },
}))

import ChartPanel from '@/components/ChartPanel.vue'

function makeChart(id = 'chart-1', overrides = {}) {
  return {
    id,
    config: {
      chartType: 'bar',
      xAxis: 'col_a',
      yAxis: 'col_b',
      aggregation: 'sum',
      colorPalette: 'default',
      title: 'My Chart',
      showLegend: true,
      showGrid: true,
    },
    chartData: { labels: ['A'], datasets: [{ label: 'test', data: [1] }] },
    chartOptions: {},
    isFullscreen: false,
    meta: { rowCount: 100 },
    warning: '',
    ...overrides,
  }
}

describe('ChartPanel', () => {
  it('renders nothing when no charts', () => {
    const wrapper = mount(ChartPanel, { props: { charts: [] } })
    expect(wrapper.find('.chart-panel').exists()).toBe(false)
  })

  it('renders charts when provided', () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart(), makeChart('chart-2')] },
    })
    expect(wrapper.find('.chart-panel').exists()).toBe(true)
    expect(wrapper.findAll('.chart-panel-item')).toHaveLength(2)
  })

  it('displays chart count in header', () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart(), makeChart('c2'), makeChart('c3')] },
    })
    expect(wrapper.text()).toContain('Charts (3)')
  })

  it('shows chart title from config', () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart()] },
    })
    expect(wrapper.text()).toContain('My Chart')
  })

  it('shows row count badge from meta', () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart()] },
    })
    expect(wrapper.text()).toContain('100 rows')
  })

  it('emits remove with index', async () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart(), makeChart('c2')] },
    })
    const removeBtn = wrapper.find('button[title="Close chart"]')
    expect(removeBtn).toBeTruthy()
    await removeBtn.trigger('click')
    expect(wrapper.emitted('remove')).toBeTruthy()
    expect(wrapper.emitted('remove')![0]).toEqual([0])
  })

  it('emits clear when Clear All clicked', async () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart()] },
    })
    const clearButton = wrapper.findAll('button').find(b => b.text().includes('Clear All'))
    expect(clearButton).toBeTruthy()
    await clearButton!.trigger('click')
    expect(wrapper.emitted('clear')).toBeTruthy()
  })

  it('emits refresh with index when refresh button clicked', async () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart(), makeChart('c2')] },
    })
    const refreshBtn = wrapper.find('button[title="Refresh chart data"]')
    expect(refreshBtn).toBeTruthy()
    await refreshBtn.trigger('click')
    expect(wrapper.emitted('refresh')).toBeTruthy()
    expect(wrapper.emitted('refresh')![0]).toEqual([0])
  })

  it('does not show refresh button when no charts', () => {
    const wrapper = mount(ChartPanel, { props: { charts: [] } })
    expect(wrapper.find('button[title="Refresh chart data"]').exists()).toBe(false)
  })

  it('emits update:charts on fullscreen toggle', async () => {
    const wrapper = mount(ChartPanel, {
      props: { charts: [makeChart()] },
    })
    const fullscreenBtn = wrapper.find('button[title="Fullscreen"]')
    expect(fullscreenBtn).toBeTruthy()
    await fullscreenBtn.trigger('click')
    expect(wrapper.emitted('update:charts')).toBeTruthy()
  })
})