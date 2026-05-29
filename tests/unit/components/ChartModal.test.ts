import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock vue-chartjs - inline factory to avoid hoisting issues
vi.mock('vue-chartjs', () => ({
  Bar: { name: 'Bar', template: '<div class="mock-bar"/>' },
  Line: { name: 'Line', template: '<div class="mock-line"/>' },
  Pie: { name: 'Pie', template: '<div class="mock-pie"/>' },
  Scatter: { name: 'Scatter', template: '<div class="mock-scatter"/>' },
}))

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

// Mock bootstrap-vue-next - inline factory
vi.mock('bootstrap-vue-next', () => ({
  BButton: { name: 'BButton', template: '<button class="b-btn"><slot/></button>' },
  BBadge: { name: 'BBadge', template: '<span class="b-badge"><slot/></span>' },
  BFormGroup: { name: 'BFormGroup', template: '<div class="b-form-group"><slot/></div>' },
  BFormSelect: { name: 'BFormSelect', template: '<select class="b-form-select"><slot/></select>' },
  BFormInput: { name: 'BFormInput', template: '<input class="b-form-input"/>' },
  BFormCheckbox: { name: 'BFormCheckbox', template: '<label class="b-form-check"><slot/></label>' },
}))

import ChartModal from '@/components/ChartModal.vue'

// Mock fetch for chart-data endpoint
global.fetch = vi.fn().mockResolvedValue({
  ok: false,
  json: () => Promise.resolve({ detail: 'Not found' }),
})

describe('ChartModal', () => {
  const defaultProps = {
    modelValue: true,
    datasetId: 'test-dataset',
    datasetName: 'Test Dataset',
    columns: [
      { field: 'city', label: 'city' },
      { field: 'revenue', label: 'revenue' },
    ],
    data: [
      { city: 'NYC', revenue: 100 },
      { city: 'LA', revenue: 200 },
    ],
    selectedColumns: ['city', 'revenue'],
    profileData: {
      columns: [
        { name: 'city', dtype: 'string', unique_count: 5, null_count: 0 },
        { name: 'revenue', dtype: 'float64', unique_count: 50, null_count: 0 },
      ],
    },
    initialChartType: 'bar',
    filters: {},
  }

  it('renders when modelValue is true', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.find('.chart-modal').exists()).toBe(true)
  })

  it('does not render when modelValue is false', () => {
    const wrapper = mount(ChartModal, {
      props: { ...defaultProps, modelValue: false },
    })
    expect(wrapper.find('.chart-modal').exists()).toBe(false)
  })

  it('displays Chart Builder header', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.text()).toContain('Chart Builder')
  })

  it('displays dataset name', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.text()).toContain('Test Dataset')
  })

  it('has close button', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    const closeBtn = wrapper.find('.bi-x-lg')
    expect(closeBtn.exists()).toBe(true)
  })

  it('has Add Chart button', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.text()).toContain('Add Chart')
  })

  it('has Cancel button', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.text()).toContain('Cancel')
  })

  it('renders config panel section', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.find('.chart-config-section').exists()).toBe(true)
  })

  it('renders preview section', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.find('.chart-preview-section').exists()).toBe(true)
  })

  it('renders resize handle', () => {
    const wrapper = mount(ChartModal, {
      props: defaultProps,
    })
    expect(wrapper.find('.resize-handle').exists()).toBe(true)
  })

  // --- Wizard mode tests ---

  it('renders in wizard mode when mode="wizard"', () => {
    const wrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'wizard' },
    })
    expect(wrapper.find('.chart-modal').exists()).toBe(true)
    expect(wrapper.find('.chart-wizard').exists()).toBe(true)
  })

  it('shows step indicator in wizard mode', () => {
    const wrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'wizard' },
    })
    const stepItems = wrapper.findAll('.wizard-step-item')
    expect(stepItems).toHaveLength(5)
  })

  it('shows Back and Next buttons in wizard mode', () => {
    const wrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'wizard' },
    })
    expect(wrapper.text()).toContain('Back')
    expect(wrapper.text()).toContain('Next')
  })

  it('shows Cancel and Add Chart buttons in preset mode', () => {
    const wrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'preset' },
    })
    expect(wrapper.text()).toContain('Cancel')
    expect(wrapper.text()).toContain('Add Chart')
  })

  it('renders ChartConfigPanel in preset mode', () => {
    const wrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'preset' },
    })
    expect(wrapper.find('.chart-config-section').exists()).toBe(true)
    expect(wrapper.find('.chart-wizard').exists()).toBe(false)
  })

  it('does not render ChartWizard in preset mode', () => {
    const wrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'preset' },
    })
    expect(wrapper.find('.chart-wizard').exists()).toBe(false)
  })

  it('renders preview section in both modes', () => {
    const presetWrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'preset' },
    })
    expect(presetWrapper.find('.chart-preview-section').exists()).toBe(true)

    const wizardWrapper = mount(ChartModal, {
      props: { ...defaultProps, mode: 'wizard' },
    })
    expect(wizardWrapper.find('.chart-preview-section').exists()).toBe(true)
  })
})
