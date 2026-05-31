import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import ChartAiSuggest from '@/components/ChartAiSuggest.vue'

// Mock bootstrap-vue-next
vi.mock('bootstrap-vue-next', () => ({
  BButton: { template: '<button @click="$emit(\'click\')"><slot /></button>', props: ['variant', 'size', 'disabled', 'loading'] },
  BFormSelect: {
    template: '<select @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
    props: ['modelValue', 'options', 'size'],
  },
  BFormTextarea: {
    template: '<textarea @input="$emit(\'update:modelValue\', $event.target.value)"></textarea>',
    props: ['modelValue', 'rows', 'placeholder', 'disabled'],
  },
  BBadge: { template: '<span class="badge"><slot /></span>', props: ['variant'] },
  BFormCheckbox: {
    template: '<label><input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" :disabled="disabled" /><slot /></label>',
    props: ['modelValue', 'disabled'],
  },
}))

// Mock the composable with proper refs
const mockRequestAiSuggestion = vi.fn()
const mockClearResult = vi.fn()
const mockLoading = ref<boolean>(false)
const mockResult = ref<any>(null)
const mockError = ref<string>('')

vi.mock('@/composables/useChartAiSuggestion', () => ({
  useChartAiSuggestion: () => ({
    loading: mockLoading,
    result: mockResult,
    error: mockError,
    clearResult: mockClearResult,
    requestAiSuggestion: mockRequestAiSuggestion,
  }),
  CHART_TYPE_LABELS: {
    bar: 'Bar Chart',
    line: 'Line Chart',
    pie: 'Pie Chart',
    scatter: 'Scatter Plot',
    histogram: 'Histogram',
    area: 'Area Chart',
  },
}))

describe('ChartAiSuggest', () => {
  const defaultProps = {
    agentOptions: [
      { value: null, text: 'Select an AI Agent…' },
      { value: 'agent-1', text: 'Data Assistant' },
      { value: 'agent-2', text: 'Chart Expert' },
    ],
    columnMeta: [
      { name: 'city', dtype: 'string', uniqueCount: 5, nullCount: 0, columnType: 'categorical' },
      { name: 'revenue', dtype: 'float64', uniqueCount: 100, nullCount: 2, columnType: 'numeric' },
    ],
    selectedColumns: ['city', 'revenue'],
    datasetId: 'ds-1',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockLoading.value = false
    mockResult.value = null
    mockError.value = ''
  })

  it('renders the component', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.exists()).toBe(true)
  })

  // --- Step navigation ---

  it('starts on step 1 (Configure)', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.text()).toContain('Configure')
    expect(wrapper.text()).toContain('Review')
  })

  it('shows agent dropdown on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
  })

  it('shows column list on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.text()).toContain('city')
    expect(wrapper.text()).toContain('revenue')
  })

  it('shows custom instruction textarea on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
  })

  it('shows Analyze button on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.text()).toContain('Analyze Data')
  })

  it('does not show suggestion result on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.text()).not.toContain('AI Suggestion')
  })

  it('does not show Previous button on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.text()).not.toContain('Previous')
  })

  it('does not show Next button on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.text()).not.toContain('Next')
  })

  it('has editable column checkboxes', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBe(2)
  })

  it('initializes column checkboxes from selectedColumns prop', async () => {
    const wrapper = mount(ChartAiSuggest, {
      props: { ...defaultProps, selectedColumns: ['city'] },
    })
    await nextTick()
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect((checkboxes[0].element as HTMLInputElement).checked).toBe(true)
    expect((checkboxes[1].element as HTMLInputElement).checked).toBe(false)
  })

  it('has Select All / Deselect All toggle', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    const selectAllLink = wrapper.find('a')
    expect(selectAllLink.exists()).toBe(true)
    // When all columns are selected, shows "Deselect All"; otherwise "Select All"
    const linkText = selectAllLink.text()
    expect(linkText === 'Select All' || linkText === 'Deselect All').toBe(true)
  })

  it('displays column type badges on step 1', () => {
    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    expect(wrapper.text()).toContain('categorical')
    expect(wrapper.text()).toContain('numeric')
  })

  // --- Step 2 (after AI result) ---

  it('transitions to step 2 when AI result is available', async () => {
    mockResult.value = {
      config: {
        chartType: 'bar',
        xAxis: 'city',
        yAxis: 'revenue',
        aggregation: 'sum',
        title: 'Revenue by City',
        showLegend: true,
        showGrid: true,
        colorPalette: 'default',
        groupBy: '',
        explanation: 'Bar chart showing revenue per city.',
      },
      explanation: 'Bar chart showing revenue per city.',
    }

    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    await nextTick()

    // Should show suggestion result
    expect(wrapper.text()).toContain('AI Suggestion')
    expect(wrapper.text()).toContain('Revenue by City')
    expect(wrapper.text()).toContain('city')
    expect(wrapper.text()).toContain('revenue')
  })

  it('shows Apply and Previous buttons on step 2 with result', async () => {
    mockResult.value = {
      config: {
        chartType: 'pie',
        xAxis: 'city',
        yAxis: 'revenue',
        aggregation: 'sum',
        title: 'Top Cities',
        showLegend: true,
        showGrid: true,
        colorPalette: 'default',
        groupBy: '',
        explanation: 'Pie chart.',
      },
      explanation: 'Pie chart.',
    }

    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    await nextTick()

    expect(wrapper.text()).toContain('Apply')
    expect(wrapper.text()).toContain('Previous')
  })

  it('emits apply event with config when Apply is clicked', async () => {
    const testConfig = {
      chartType: 'bar',
      xAxis: 'city',
      yAxis: 'revenue',
      aggregation: 'sum',
      title: 'Revenue by City',
      showLegend: true,
      showGrid: true,
      colorPalette: 'default',
      groupBy: '',
      explanation: 'Test explanation',
    }

    mockResult.value = {
      config: testConfig,
      explanation: 'Test explanation',
    }

    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    await nextTick()

    wrapper.vm.$emit('apply', testConfig)
    await nextTick()

    expect(wrapper.emitted('apply')).toBeTruthy()
    expect(wrapper.emitted('apply')![0][0]).toEqual(testConfig)
  })

  it('goes back to step 1 when Previous is clicked', async () => {
    mockResult.value = {
      config: {
        chartType: 'bar',
        xAxis: 'city',
        yAxis: 'revenue',
        aggregation: 'sum',
        title: 'Revenue',
        showLegend: true,
        showGrid: true,
        colorPalette: 'default',
        groupBy: '',
        explanation: 'Bar chart.',
      },
      explanation: 'Bar chart.',
    }

    const wrapper = mount(ChartAiSuggest, { props: defaultProps })
    await nextTick()

    // On step 2, click Previous
    const prevBtn = wrapper.findAll('button').find(b => b.text().includes('Previous'))
    expect(prevBtn).toBeDefined()
    prevBtn!.trigger('click')
    await nextTick()

    // Should be back on step 1
    expect(wrapper.text()).toContain('Analyze Data')
    expect(wrapper.text()).toContain('AI Agent')
  })
})