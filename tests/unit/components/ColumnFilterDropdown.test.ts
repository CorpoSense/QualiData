/**
 * Tests for ColumnFilterDropdown component
 * Tests rendering, search filtering, selection, apply/clear, null handling, and truncation warning
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ColumnFilterDropdown from '@/components/ColumnFilterDropdown.vue'

const defaultValues = [
  { value: 'Paris', count: 15 },
  { value: 'London', count: 10 },
  { value: 'Berlin', count: 8 },
  { value: null, count: 3 },
]

const defaultField = { key: 'city', label: 'City' }

function createWrapper(props: Record<string, any> = {}) {
  return mount(ColumnFilterDropdown, {
    props: {
      field: defaultField,
      values: defaultValues,
      selectedValues: [],
      loading: false,
      totalUnique: 4,
      ...props,
    },
    global: {
      stubs: {},
    },
  })
}

function getChecked(wrapper: any, index: number): boolean {
  const checkboxes = wrapper.findAll('.filter-item .form-check-input')
  return (checkboxes[index].element as HTMLInputElement).checked
}

describe('ColumnFilterDropdown', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders the column label in the header', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.filter-header .fw-bold').text()).toBe('City')
    })

    it('renders the column key when label is not provided', () => {
      const wrapper = createWrapper({ field: { key: 'city', label: '' } })
      expect(wrapper.find('.filter-header .fw-bold').text()).toBe('city')
    })

    it('renders all values as filter items', () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')
      expect(items.length).toBe(4) // Paris, London, Berlin, null
    })

    it('displays value counts as badges', () => {
      const wrapper = createWrapper()
      const counts = wrapper.findAll('.filter-count')
      expect(counts[0].text()).toBe('15')
      expect(counts[1].text()).toBe('10')
      expect(counts[2].text()).toBe('8')
      expect(counts[3].text()).toBe('3')
    })

    it('displays null values as (null)', () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')
      const nullItem = items[3]
      expect(nullItem.find('.filter-value').text()).toBe('(null)')
    })

    it('renders search input', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.filter-search input').exists()).toBe(true)
    })

    it('renders Select All and Unselect All buttons', () => {
      const wrapper = createWrapper()
      const buttons = wrapper.findAll('.filter-actions .btn-link')
      expect(buttons.length).toBe(2)
      expect(buttons[0].text()).toBe('Select All')
      expect(buttons[1].text()).toBe('Unselect All')
    })

    it('renders Clear and Apply buttons in footer', () => {
      const wrapper = createWrapper()
      const footer = wrapper.find('.filter-footer')
      expect(footer.findAll('button').length).toBe(2)
      expect(footer.findAll('button')[0].text()).toBe('Clear')
      expect(footer.findAll('button')[1].text()).toBe('Apply')
    })

    it('shows selected count in actions bar', () => {
      const wrapper = createWrapper({ selectedValues: ['Paris', 'London'] })
      expect(wrapper.find('.filter-actions .text-muted').text()).toBe('2/4')
    })
  })

  describe('Loading State', () => {
    it('shows loading spinner when loading is true', () => {
      const wrapper = createWrapper({ loading: true })
      expect(wrapper.find('.filter-loading').exists()).toBe(true)
      expect(wrapper.find('.spinner-border').exists()).toBe(true)
    })

    it('hides value list when loading', () => {
      const wrapper = createWrapper({ loading: true })
      expect(wrapper.find('.filter-list').exists()).toBe(false)
    })

    it('shows value list when not loading', () => {
      const wrapper = createWrapper({ loading: false })
      expect(wrapper.find('.filter-list').exists()).toBe(true)
      expect(wrapper.find('.filter-loading').exists()).toBe(false)
    })
  })

  describe('Search Filtering', () => {
    it('filters values by search query (case-insensitive)', async () => {
      const wrapper = createWrapper()
      const searchInput = wrapper.find('.filter-search input')
      await searchInput.setValue('par')

      const items = wrapper.findAll('.filter-item')
      expect(items.length).toBe(1)
      expect(items[0].find('.filter-value').text()).toBe('Paris')
    })

    it('shows null values when search query contains "null"', async () => {
      const wrapper = createWrapper()
      const searchInput = wrapper.find('.filter-search input')
      await searchInput.setValue('null')

      const items = wrapper.findAll('.filter-item')
      expect(items.length).toBe(1)
      expect(items[0].find('.filter-value').text()).toBe('(null)')
    })

    it('shows "No values found" when search has no matches', async () => {
      const wrapper = createWrapper()
      const searchInput = wrapper.find('.filter-search input')
      await searchInput.setValue('xyz')

      expect(wrapper.find('.filter-list .text-center.text-muted').text()).toBe('No values found')
    })

    it('shows all values when search is cleared', async () => {
      const wrapper = createWrapper()
      const searchInput = wrapper.find('.filter-search input')
      await searchInput.setValue('par')
      expect(wrapper.findAll('.filter-item').length).toBe(1)

      await searchInput.setValue('')
      expect(wrapper.findAll('.filter-item').length).toBe(4)
    })
  })

  describe('Selection', () => {
    it('initializes with pre-selected values checked', () => {
      const wrapper = createWrapper({ selectedValues: ['Paris'] })
      expect(getChecked(wrapper, 0)).toBe(true)
      expect(getChecked(wrapper, 1)).toBe(false)
    })

    it('toggles a value when clicking a filter item', async () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')

      await items[0].trigger('click')
      expect(getChecked(wrapper, 0)).toBe(true)
    })

    it('deselects a value when clicking an already selected item', async () => {
      const wrapper = createWrapper({ selectedValues: ['Paris'] })
      const items = wrapper.findAll('.filter-item')

      await items[0].trigger('click')
      expect(getChecked(wrapper, 0)).toBe(false)
    })

    it('selects all values when clicking Select All', async () => {
      const wrapper = createWrapper()
      const selectAllBtn = wrapper.findAll('.filter-actions .btn-link')[0]
      await selectAllBtn.trigger('click')

      const checkboxes = wrapper.findAll('.filter-item .form-check-input')
      checkboxes.forEach(cb => {
        expect((cb.element as HTMLInputElement).checked).toBe(true)
      })
    })

    it('deselects all values when clicking Unselect All', async () => {
      const wrapper = createWrapper({ selectedValues: ['Paris', 'London'] })
      const unselectAllBtn = wrapper.findAll('.filter-actions .btn-link')[1]
      await unselectAllBtn.trigger('click')

      const checkboxes = wrapper.findAll('.filter-item .form-check-input')
      checkboxes.forEach(cb => {
        expect((cb.element as HTMLInputElement).checked).toBe(false)
      })
    })

    it('disables Select All button when all are already selected', async () => {
      const wrapper = createWrapper({ selectedValues: ['Paris', 'London', 'Berlin', null] })
      const selectAllBtn = wrapper.findAll('.filter-actions .btn-link')[0]
      expect(selectAllBtn.attributes('disabled')).toBeDefined()
    })

    it('disables Unselect All button when none are selected', () => {
      const wrapper = createWrapper({ selectedValues: [] })
      const unselectAllBtn = wrapper.findAll('.filter-actions .btn-link')[1]
      expect(unselectAllBtn.attributes('disabled')).toBeDefined()
    })

    it('updates selected count display when toggling values', async () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')

      expect(wrapper.find('.filter-actions .text-muted').text()).toBe('0/4')

      await items[0].trigger('click')
      expect(wrapper.find('.filter-actions .text-muted').text()).toBe('1/4')

      await items[1].trigger('click')
      expect(wrapper.find('.filter-actions .text-muted').text()).toBe('2/4')
    })
  })

  describe('Apply and Clear', () => {
    it('emits "apply" with selected values array when Apply is clicked', async () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')

      await items[0].trigger('click')
      await items[1].trigger('click')

      await wrapper.find('.filter-footer .btn-primary').trigger('click')

      expect(wrapper.emitted('apply')).toBeTruthy()
      const emittedValues = wrapper.emitted('apply')![0][0] as any[]
      expect(emittedValues).toContain('Paris')
      expect(emittedValues).toContain('London')
      expect(emittedValues.length).toBe(2)
    })

    it('emits "apply" with empty array when Clear is clicked', async () => {
      const wrapper = createWrapper({ selectedValues: ['Paris'] })

      await wrapper.find('.filter-footer .btn-outline-secondary').trigger('click')

      expect(wrapper.emitted('apply')).toBeTruthy()
      expect(wrapper.emitted('apply')![0][0]).toEqual([])
    })

    it('emits "close" when close button is clicked', async () => {
      const wrapper = createWrapper()
      await wrapper.find('.filter-header .btn-close').trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('includes null in apply payload when null is selected', async () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')

      await items[3].trigger('click')

      await wrapper.find('.filter-footer .btn-primary').trigger('click')

      const emittedValues = wrapper.emitted('apply')![0][0] as any[]
      expect(emittedValues).toContain(null)
    })
  })

  describe('Truncation Warning', () => {
    it('shows warning when totalUnique > values.length', () => {
      const wrapper = createWrapper({ totalUnique: 100, values: defaultValues })
      expect(wrapper.find('.filter-warning').exists()).toBe(true)
      expect(wrapper.find('.filter-warning').text()).toContain('Showing top 4 of 100')
    })

    it('does not show warning when totalUnique equals values.length', () => {
      const wrapper = createWrapper({ totalUnique: 4, values: defaultValues })
      expect(wrapper.find('.filter-warning').exists()).toBe(false)
    })

    it('does not show warning when loading', () => {
      const wrapper = createWrapper({ totalUnique: 100, values: defaultValues, loading: true })
      expect(wrapper.find('.filter-warning').exists()).toBe(false)
    })
  })

  describe('Null Value Handling', () => {
    it('displays null as (null) in the value list', () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')
      const nullItem = items.find(item => item.find('.filter-value').text() === '(null)')
      expect(nullItem).toBeTruthy()
    })

    it('can select and apply null value', async () => {
      const wrapper = createWrapper()
      const items = wrapper.findAll('.filter-item')

      await items[3].trigger('click')
      await wrapper.find('.filter-footer .btn-primary').trigger('click')

      const emittedValues = wrapper.emitted('apply')![0][0] as any[]
      expect(emittedValues).toContain(null)
      expect(emittedValues.length).toBe(1)
    })
  })

  describe('Edge Cases', () => {
    it('handles empty values array', () => {
      const wrapper = createWrapper({ values: [] as any[], totalUnique: 0 })
      expect(wrapper.findAll('.filter-item').length).toBe(0)
      expect(wrapper.find('.filter-list .text-center.text-muted').text()).toBe('No values found')
    })

    it('handles values with only a single entry', () => {
      const wrapper = createWrapper({
        values: [{ value: 'OnlyValue', count: 50 }],
        totalUnique: 1,
      })
      expect(wrapper.findAll('.filter-item').length).toBe(1)
      expect(wrapper.findAll('.filter-item')[0].find('.filter-value').text()).toBe('OnlyValue')
    })

    it('handles numeric values converted to strings', () => {
      const wrapper = createWrapper({
        values: [
          { value: '85.0', count: 10 },
          { value: '90.0', count: 5 },
        ],
        totalUnique: 2,
      })
      const items = wrapper.findAll('.filter-item')
      expect(items[0].find('.filter-value').text()).toBe('85.0')
      expect(items[1].find('.filter-value').text()).toBe('90.0')
    })

    it('Select All is disabled when values array is empty', () => {
      const wrapper = createWrapper({ values: [] as any[], totalUnique: 0 })
      const selectAllBtn = wrapper.findAll('.filter-actions .btn-link')[0]
      expect(selectAllBtn.attributes('disabled')).toBeDefined()
    })
  })
})

describe('ColumnFilterDropdown - Filter State Logic', () => {
  it('correctly identifies hasColumnFilter when filter state has values', () => {
    const columnFilterState: Record<string, any[]> = { city: ['Paris', 'London'] }
    const hasFilter = !!(columnFilterState['city'] && columnFilterState['city'].length > 0)
    expect(hasFilter).toBe(true)
  })

  it('correctly identifies no filter when filter state is empty', () => {
    const columnFilterState: Record<string, any[]> = {}
    const hasFilter = !!(columnFilterState['city'] && columnFilterState['city'].length > 0)
    expect(hasFilter).toBe(false)
  })

  it('correctly identifies no filter when filter state array is empty', () => {
    const columnFilterState: Record<string, any[]> = { city: [] }
    const hasFilter = !!(columnFilterState['city'] && columnFilterState['city'].length > 0)
    expect(hasFilter).toBe(false)
  })

  it('counts active column filters correctly', () => {
    const columnFilterState: Record<string, any[]> = {
      city: ['Paris'],
      country: ['US', 'UK'],
      name: [],
    }
    const activeCount = Object.keys(columnFilterState).filter(
      k => columnFilterState[k] && columnFilterState[k].length > 0
    ).length
    expect(activeCount).toBe(2)
  })

  it('builds selected_values filter format correctly', () => {
    const columnFilterState: Record<string, any[]> = {
      city: ['Paris', 'London', null],
    }
    const filterBody: Record<string, any> = {}
    for (const [col, vals] of Object.entries(columnFilterState)) {
      if (vals && vals.length > 0) {
        filterBody[col] = { selected_values: vals }
      }
    }
    expect(filterBody).toEqual({
      city: { selected_values: ['Paris', 'London', null] },
    })
  })

  it('combines substring and selected_values filters', () => {
    const rowFilters: Record<string, string> = { name: 'John' }
    const columnFilterState: Record<string, any[]> = { city: ['Paris'] }

    const filterBody: Record<string, any> = {}
    for (const [k, v] of Object.entries(rowFilters)) {
      if (v && String(v).trim()) filterBody[k] = v
    }
    for (const [col, vals] of Object.entries(columnFilterState)) {
      if (vals && vals.length > 0) {
        filterBody[col] = { selected_values: vals }
      }
    }

    expect(filterBody).toEqual({
      name: 'John',
      city: { selected_values: ['Paris'] },
    })
  })

  it('clears column filter state correctly', () => {
    let columnFilterState: Record<string, any[]> = { city: ['Paris'], country: ['US'] }
    columnFilterState = {}
    expect(Object.keys(columnFilterState).length).toBe(0)
  })

  it('removes individual column filter when selectedValues is empty', () => {
    const columnFilterState: Record<string, any[]> = { city: ['Paris'], country: ['US'] }
    const column = 'city'
    const selectedValues: any[] = []

    if (selectedValues.length === 0) {
      delete columnFilterState[column]
    } else {
      columnFilterState[column] = selectedValues
    }

    expect(columnFilterState).toEqual({ country: ['US'] })
  })
})
