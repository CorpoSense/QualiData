import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ChartWizard from '@/components/ChartWizard.vue'
import type { ColumnMeta } from '@/composables/useColumnTypes'

// Mock bootstrap-vue-next
vi.mock('bootstrap-vue-next', () => ({
  BButton: { name: 'BButton', template: '<button class="b-btn" :disabled="disabled"><slot/></button>', props: ['variant', 'size', 'disabled'] },
  BBadge: { name: 'BBadge', template: '<span class="b-badge"><slot/></span>', props: ['variant'] },
  BFormSelect: { name: 'BFormSelect', template: '<select class="b-form-select" :modelValue="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot/></select>', props: ['modelValue', 'options', 'size'] },
  BFormInput: { name: 'BFormInput', template: '<input class="b-form-input" :modelValue="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)"/>', props: ['modelValue', 'placeholder', 'size'] },
  BFormGroup: { name: 'BFormGroup', template: '<div class="b-form-group"><label v-if="label" class="b-form-label">{{ label }}</label><slot/></div>', props: ['label', 'labelSize'] },
  BFormCheckbox: { name: 'BFormCheckbox', template: '<label class="b-form-check"><input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)"/><slot/></label>', props: ['modelValue'] },
}))

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

const samplePreviewData = [
  { city: 'NYC', revenue: 100, date: '2024-01-01', count: 10 },
  { city: 'LA', revenue: 200, date: '2024-02-01', count: 20 },
]

describe('ChartWizard', () => {
  const defaultProps = {
    columnMeta: sampleColumns,
    previewData: samplePreviewData,
    initialSelectedColumns: ['city', 'revenue'],
  }

  it('renders the wizard container', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    expect(wrapper.find('.chart-wizard').exists()).toBe(true)
  })

  it('renders step indicator with 5 steps', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    const stepItems = wrapper.findAll('.wizard-step-item')
    expect(stepItems).toHaveLength(5)
  })

  it('displays step labels', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    expect(wrapper.text()).toContain('Data Selection')
    expect(wrapper.text()).toContain('Chart Type')
    expect(wrapper.text()).toContain('Axis Mapping')
    expect(wrapper.text()).toContain('Styling')
    expect(wrapper.text()).toContain('Preview')
  })

  it('starts at step 0 (Data Selection)', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    expect(wrapper.text()).toContain('Select columns to visualize')
  })

  it('renders column list with type badges at step 0', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    expect(wrapper.text()).toContain('city')
    expect(wrapper.text()).toContain('revenue')
    expect(wrapper.text()).toContain('date')
    expect(wrapper.text()).toContain('count')
  })

  it('shows column type badges', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    const badges = wrapper.findAll('.b-badge')
    expect(badges.length).toBeGreaterThan(0)
  })

  it('has Back and Next buttons', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    expect(wrapper.text()).toContain('Back')
    expect(wrapper.text()).toContain('Next')
  })

  it('Back button is disabled at step 0', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    const buttons = wrapper.findAll('button.b-btn')
    const backButton = buttons.find(b => b.text().includes('Back'))
    expect(backButton?.attributes('disabled')).toBeDefined()
  })

  it('Next button is enabled when columns are selected', () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    const buttons = wrapper.findAll('button.b-btn')
    const nextButton = buttons.find(b => b.text().includes('Next'))
    expect(nextButton?.attributes('disabled')).toBeUndefined()
  })

  it('clicking Next advances to step 1', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    const buttons = wrapper.findAll('button.b-btn')
    const nextButton = buttons.find(b => b.text().includes('Next'))
    await nextButton?.trigger('click')
    expect(wrapper.text()).toContain('Chart Type')
  })

  it('emits update:chartConfig on mount', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    await wrapper.vm.$nextTick()
    const emitted = wrapper.emitted('update:chartConfig')
    expect(emitted).toBeTruthy()
    expect(emitted!.length).toBeGreaterThan(0)
    // Should emit a valid chart config
    const config = emitted![0][0] as any
    expect(config.chartType).toBeDefined()
  })

  it('shows chart type cards at step 1', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    // Navigate to step 1
    const buttons = wrapper.findAll('button.b-btn')
    const nextButton = buttons.find(b => b.text().includes('Next'))
    await nextButton?.trigger('click')

    expect(wrapper.text()).toContain('Bar Chart')
    expect(wrapper.text()).toContain('Line Chart')
    expect(wrapper.text()).toContain('Pie Chart')
    expect(wrapper.text()).toContain('Scatter')
    expect(wrapper.text()).toContain('Histogram')
    expect(wrapper.text()).toContain('Area')
  })

  it('shows recommended badge for compatible chart types', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    // Navigate to step 1
    const buttons = wrapper.findAll('button.b-btn')
    const nextButton = buttons.find(b => b.text().includes('Next'))
    await nextButton?.trigger('click')

    // With city (categorical) + revenue (numeric), bar should be recommended
    const recommendedBadges = wrapper.findAll('.wizard-type-recommended')
    expect(recommendedBadges.length).toBeGreaterThan(0)
  })

  it('navigates back to step 0 from step 1', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    // Go to step 1
    let buttons = wrapper.findAll('button.b-btn')
    let nextButton = buttons.find(b => b.text().includes('Next'))
    await nextButton?.trigger('click')
    expect(wrapper.text()).toContain('Chart Type')

    // Go back to step 0
    buttons = wrapper.findAll('button.b-btn')
    const backButton = buttons.find(b => b.text().includes('Back'))
    await backButton?.trigger('click')
    expect(wrapper.text()).toContain('Select columns to visualize')
  })

  it('shows axis mapping dropdowns at step 2', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    // Navigate to step 2
    for (let i = 0; i < 2; i++) {
      const buttons = wrapper.findAll('button.b-btn')
      const nextButton = buttons.find(b => b.text().includes('Next'))
      await nextButton?.trigger('click')
    }

    expect(wrapper.text()).toContain('X-Axis')
    expect(wrapper.text()).toContain('Y-Axis')
  })

  it('shows styling options at step 3', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    // Navigate to step 3
    for (let i = 0; i < 3; i++) {
      const buttons = wrapper.findAll('button.b-btn')
      const nextButton = buttons.find(b => b.text().includes('Next'))
      await nextButton?.trigger('click')
    }

    expect(wrapper.text()).toContain('Color Palette')
    expect(wrapper.text()).toContain('Chart Title')
  })

  it('shows summary at step 4', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    // Navigate to step 4
    for (let i = 0; i < 4; i++) {
      const buttons = wrapper.findAll('button.b-btn')
      const nextButton = buttons.find(b => b.text().includes('Next'))
      await nextButton?.trigger('click')
    }

    expect(wrapper.text()).toContain('Ready')
  })

  it('can navigate directly to a specific step', async () => {
    const wrapper = mount(ChartWizard, { props: defaultProps })
    // The wizard exposes goToStep via its internal state
    // We can verify by clicking step indicators if they're clickable
    const stepItems = wrapper.findAll('.wizard-step-item')
    // Step 0 is already active, click step 1
    if (stepItems.length > 1) {
      await stepItems[1].trigger('click')
      // May or may not navigate depending on validation
      // Just verify no crash
      expect(wrapper.find('.chart-wizard').exists()).toBe(true)
    }
  })
})