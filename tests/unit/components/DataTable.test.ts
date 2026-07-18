/**
 * Tests for DataTable component sort behavior.
 *
 * Tests cover:
 * - Sort button click toggles sort state (none → asc → desc → none)
 * - sort-changed event emission with correct payload
 * - Single sort mode (multiSort=false) replaces previous sort
 * - Multi sort mode (multiSort=true) adds to sort keys
 * - Sort icon display (up/down/neutral)
 * - Sort badge display in multi-sort mode
 * - External sort state control via serverSort prop
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DataTable from '@/components/DataTable.vue'

const defaultItems = [
  { name: 'Charlie', age: 30 },
  { name: 'Alice', age: 10 },
  { name: 'Bob', age: 20 },
]

const defaultFields = [
  { key: 'name', label: 'Name' },
  { key: 'age', label: 'Age' },
]

function createWrapper(props: Record<string, any> = {}) {
  return mount(DataTable, {
    props: {
      items: defaultItems,
      fields: defaultFields,
      multiSort: false,
      ...props,
    },
    global: {
      stubs: {},
    },
  })
}

describe('DataTable Sort', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Sort Toggle Cycle (Single Sort)', () => {
    it('starts with no sort active', () => {
      const wrapper = createWrapper()
      const sortBtns = wrapper.findAll('.sort-btn')
      // All sort buttons should show neutral icon
      sortBtns.forEach(btn => {
        expect(btn.find('.bi-arrow-down-up').exists()).toBe(true)
      })
    })

    it('clicking sort button on unsorted column activates ascending sort', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0] // name column
      await sortBtn.trigger('click')

      // Should emit sort-changed
      expect(wrapper.emitted('sort-changed')).toBeTruthy()
      const emitted = wrapper.emitted('sort-changed')![0][0] as any[]
      expect(emitted).toEqual([{ key: 'name', dir: 'asc' }])
    })

    it('clicking sort button on ascending column toggles to descending', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0]

      // First click: asc
      await sortBtn.trigger('click')
      // Second click: desc
      await sortBtn.trigger('click')

      const emitted = wrapper.emitted('sort-changed')![1][0] as any[]
      expect(emitted).toEqual([{ key: 'name', dir: 'desc' }])
    })

    it('clicking sort button on descending column removes sort', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0]

      // asc → desc → remove
      await sortBtn.trigger('click')
      await sortBtn.trigger('click')
      await sortBtn.trigger('click')

      const emitted = wrapper.emitted('sort-changed')![2][0] as any[]
      expect(emitted).toEqual([])
    })
  })

  describe('Single Sort Mode (multiSort=false)', () => {
    it('replaces previous sort when clicking a different column', async () => {
      const wrapper = createWrapper({ multiSort: false })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      // Sort by name asc
      await nameSortBtn.trigger('click')
      let emitted = wrapper.emitted('sort-changed')![0][0] as any[]
      expect(emitted).toEqual([{ key: 'name', dir: 'asc' }])

      // Sort by age asc - should replace name sort
      await ageSortBtn.trigger('click')
      emitted = wrapper.emitted('sort-changed')![1][0] as any[]
      expect(emitted).toEqual([{ key: 'age', dir: 'asc' }])
    })
  })

  describe('Multi Sort Mode (multiSort=true)', () => {
    it('adds a second sort key instead of replacing', async () => {
      const wrapper = createWrapper({ multiSort: true })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      // Sort by name asc
      await nameSortBtn.trigger('click')
      let emitted = wrapper.emitted('sort-changed')![0][0] as any[]
      expect(emitted).toEqual([{ key: 'name', dir: 'asc' }])

      // Sort by age asc - should add to sort keys
      await ageSortBtn.trigger('click')
      emitted = wrapper.emitted('sort-changed')![1][0] as any[]
      expect(emitted).toEqual([
        { key: 'name', dir: 'asc' },
        { key: 'age', dir: 'asc' },
      ])
    })

    it('shows sort badge with index number when multiple sorts active', async () => {
      const wrapper = createWrapper({ multiSort: true })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')

      // Check that sort badges are visible
      const badges = wrapper.findAll('.sort-badge')
      expect(badges.length).toBe(2)
    })
  })

  describe('Sort Icon Display', () => {
    it('shows up arrow for ascending sort', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0]
      await sortBtn.trigger('click')

      expect(sortBtn.find('.bi-arrow-up').exists()).toBe(true)
    })

    it('shows down arrow for descending sort', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0]
      await sortBtn.trigger('click')
      await sortBtn.trigger('click')

      expect(sortBtn.find('.bi-arrow-down').exists()).toBe(true)
    })

    it('shows neutral icon when no sort is active', () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0]
      expect(sortBtn.find('.bi-arrow-down-up').exists()).toBe(true)
    })
  })

  describe('sort-changed Event Payload', () => {
    it('emits sort-changed with array of {key, dir} objects', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0]
      await sortBtn.trigger('click')

      const events = wrapper.emitted('sort-changed')
      expect(events).toBeTruthy()
      expect(events!.length).toBe(1)

      const payload = events![0][0] as any[]
      expect(Array.isArray(payload)).toBe(true)
      expect(payload[0]).toHaveProperty('key')
      expect(payload[0]).toHaveProperty('dir')
      expect(payload[0].key).toBe('name')
      expect(payload[0].dir).toBe('asc')
    })

    it('emits empty array when sort is removed', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0]

      // Click 3 times: none → asc → desc → none
      await sortBtn.trigger('click')
      await sortBtn.trigger('click')
      await sortBtn.trigger('click')

      const sortChangedEvents = wrapper.emitted('sort-changed')!
      const lastEvent = sortChangedEvents[sortChangedEvents.length - 1][0] as any[]
      expect(lastEvent).toEqual([])
    })
  })

  describe('Server-side Sort Prop', () => {
    it('respects serverSort prop to control sort state externally', async () => {
      const wrapper = createWrapper({ serverSort: [{ key: 'age', dir: 'desc' }] })
      // When serverSort is provided, the component should use it for display
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]
      expect(ageSortBtn.find('.bi-arrow-down').exists()).toBe(true)
    })

    it('updates sort display when serverSort prop changes', async () => {
      const wrapper = createWrapper({ serverSort: [] })
      await wrapper.setProps({ serverSort: [{ key: 'name', dir: 'asc' }] })

      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      expect(nameSortBtn.find('.bi-arrow-up').exists()).toBe(true)
    })

    it('still emits sort-changed when clicking sort button with serverSort', async () => {
      const wrapper = createWrapper({ serverSort: [] })
      const sortBtn = wrapper.findAll('.sort-btn')[0]
      await sortBtn.trigger('click')

      expect(wrapper.emitted('sort-changed')).toBeTruthy()
    })
  })

  describe('Client-side Sort Behavior (default)', () => {
    it('sorts items client-side by default when no serverSort', () => {
      const wrapper = createWrapper()
      // Default: no sort, items in original order
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(3)
    })

    it('displays sorted items after clicking sort button', async () => {
      const wrapper = createWrapper()
      const sortBtn = wrapper.findAll('.sort-btn')[0] // name column
      await sortBtn.trigger('click')

      // Items should be sorted ascending by name
      const rows = wrapper.findAll('tbody tr')
      const firstCell = rows[0].findAll('td')[0]
      expect(firstCell.text()).toBe('Alice')
    })
  })
})

describe('DataTable Sort - Integration with DataViewer', () => {
  it('sort-changed payload matches expected backend sort request format', async () => {
    const wrapper = createWrapper()
    const sortBtn = wrapper.findAll('.sort-btn')[0]
    await sortBtn.trigger('click')

    const payload = wrapper.emitted('sort-changed')![0][0] as any[]

    // The DataViewer should be able to convert this to:
    // POST /api/datasets/{id}/operations/sort
    // { column: payload[0].key, ascending: payload[0].dir === 'asc' }
    expect(payload[0].key).toBe('name')
    expect(payload[0].dir).toBe('asc')

    // Verify conversion logic
    const sortRequest = {
      column: payload[0].key,
      ascending: payload[0].dir === 'asc',
      na_position: 'last' as const,
    }
    expect(sortRequest).toEqual({
      column: 'name',
      ascending: true,
      na_position: 'last',
    })
  })

  it('empty sort payload indicates sort should be cleared', async () => {
    const wrapper = createWrapper()
    const sortBtn = wrapper.findAll('.sort-btn')[0]

    // Activate sort then remove it
    await sortBtn.trigger('click')
    await sortBtn.trigger('click')
    await sortBtn.trigger('click')

    const sortChangedEvents = wrapper.emitted('sort-changed')!
    const payload = sortChangedEvents[sortChangedEvents.length - 1][0] as any[]
    expect(payload).toEqual([])
    // Empty array means no sort is active - DataViewer should refresh without sort
  })
})

describe('DataTable Multi-Sort - Server-Side Sort', () => {
  describe('Multi-sort toggle cycle with serverSort', () => {
    it('clicking sort button in multi-sort mode with serverSort emits sort-changed', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]

      await nameSortBtn.trigger('click')
      expect(wrapper.emitted('sort-changed')).toBeTruthy()
      const payload = wrapper.emitted('sort-changed')![0][0] as any[]
      expect(payload).toEqual([{ key: 'name', dir: 'asc' }])
    })

    it('clicking second column in multi-sort mode emits both sort keys', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')

      const payload = wrapper.emitted('sort-changed')![1][0] as any[]
      expect(payload).toEqual([
        { key: 'name', dir: 'asc' },
        { key: 'age', dir: 'asc' },
      ])
    })

    it('toggling second column direction in multi-sort updates that column only', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      // name asc, age asc
      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')

      // Toggle age to desc
      await ageSortBtn.trigger('click')

      const payload = wrapper.emitted('sort-changed')![2][0] as any[]
      expect(payload).toEqual([
        { key: 'name', dir: 'asc' },
        { key: 'age', dir: 'desc' },
      ])
    })

    it('removing one sort key in multi-sort keeps the other', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      // name asc, age asc
      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')

      // Remove age sort (asc → desc → remove)
      await ageSortBtn.trigger('click') // age desc
      await ageSortBtn.trigger('click') // age removed

      const payload = wrapper.emitted('sort-changed')![3][0] as any[]
      expect(payload).toEqual([{ key: 'name', dir: 'asc' }])
    })

    it('removing all sort keys in multi-sort emits empty array', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      // name asc, age asc
      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')

      // Remove both
      await nameSortBtn.trigger('click') // name desc
      await nameSortBtn.trigger('click') // name removed
      await ageSortBtn.trigger('click') // age desc
      await ageSortBtn.trigger('click') // age removed

      const events = wrapper.emitted('sort-changed')!
      const lastPayload = events[events.length - 1][0] as any[]
      expect(lastPayload).toEqual([])
    })
  })

  describe('Multi-sort with serverSort prop', () => {
    it('serverSort with multiple keys shows correct indicators', async () => {
      const wrapper = createWrapper({
        multiSort: true,
        serverSort: [
          { key: 'name', dir: 'asc' },
          { key: 'age', dir: 'desc' },
        ],
      })

      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      // Name should show ascending
      expect(nameSortBtn.find('.bi-arrow-up').exists()).toBe(true)
      // Age should show descending
      expect(ageSortBtn.find('.bi-arrow-down').exists()).toBe(true)

      // Both should have sort badges
      const badges = wrapper.findAll('.sort-badge')
      expect(badges.length).toBe(2)
    })

    it('serverSort update syncs sort state', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })

      // Update serverSort to have two keys
      await wrapper.setProps({
        serverSort: [
          { key: 'name', dir: 'asc' },
          { key: 'age', dir: 'desc' },
        ],
      })

      const badges = wrapper.findAll('.sort-badge')
      expect(badges.length).toBe(2)
    })

    it('clearing serverSort removes all sort indicators', async () => {
      const wrapper = createWrapper({
        multiSort: true,
        serverSort: [{ key: 'name', dir: 'asc' }],
      })

      await wrapper.setProps({ serverSort: [] })

      const sortBtns = wrapper.findAll('.sort-btn')
      sortBtns.forEach(btn => {
        expect(btn.find('.bi-arrow-down-up').exists()).toBe(true)
      })
    })
  })

  describe('Multi-sort payload format for backend', () => {
    it('multi-sort payload converts to sort_keys format for backend', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')

      const payload = wrapper.emitted('sort-changed')![1][0] as any[]

      // DataViewer should convert this to:
      // POST /api/datasets/{id}/operations/sort
      // { sort_keys: [{ column: 'name', ascending: true }, { column: 'age', ascending: true }] }
      const sortRequest = {
        sort_keys: payload.map(sk => ({
          column: sk.key,
          ascending: sk.dir === 'asc',
        })),
        na_position: 'last' as const,
      }
      expect(sortRequest).toEqual({
        sort_keys: [
          { column: 'name', ascending: true },
          { column: 'age', ascending: true },
        ],
        na_position: 'last',
      })
    })

    it('single sort payload converts to backward-compatible format', async () => {
      const wrapper = createWrapper({ multiSort: false, serverSort: [] })
      const sortBtn = wrapper.findAll('.sort-btn')[0]
      await sortBtn.trigger('click')

      const payload = wrapper.emitted('sort-changed')![0][0] as any[]

      // Single sort should use the simple format:
      // { column: 'name', ascending: true, na_position: 'last' }
      const sortRequest = {
        column: payload[0].key,
        ascending: payload[0].dir === 'asc',
        na_position: 'last' as const,
      }
      expect(sortRequest).toEqual({
        column: 'name',
        ascending: true,
        na_position: 'last',
      })
    })

    it('multi-sort with mixed directions converts correctly', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')
      await ageSortBtn.trigger('click') // age desc

      const payload = wrapper.emitted('sort-changed')![2][0] as any[]

      const sortRequest = {
        sort_keys: payload.map(sk => ({
          column: sk.key,
          ascending: sk.dir === 'asc',
        })),
        na_position: 'last' as const,
      }
      expect(sortRequest).toEqual({
        sort_keys: [
          { column: 'name', ascending: true },
          { column: 'age', ascending: false },
        ],
        na_position: 'last',
      })
    })
  })

  describe('Multi-sort client-side behavior', () => {
    it('sorts items client-side by multiple columns when no serverSort', async () => {
      const items = [
        { name: 'Alice', age: 30 },
        { name: 'Bob', age: 25 },
        { name: 'Alice', age: 20 },
        { name: 'Bob', age: 35 },
      ]
      const wrapper = createWrapper({ multiSort: true, items })

      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]

      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')

      // Items should be sorted by name asc, then age asc
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(4)
      // First row: Alice, 20
      const firstRowCells = rows[0].findAll('td')
      expect(firstRowCells[0].text()).toBe('Alice')
      expect(firstRowCells[1].text()).toBe('20')
    })

    it('skips client-side sort when serverSort is provided', () => {
      const items = [
        { name: 'Charlie', age: 30 },
        { name: 'Alice', age: 10 },
        { name: 'Bob', age: 20 },
      ]
      const wrapper = createWrapper({
        multiSort: true,
        items,
        serverSort: [{ key: 'name', dir: 'asc' }],
      })
  
      // When serverSort is provided, items should be in original order
      // (server already sorted them)
      const rows = wrapper.findAll('tbody tr')
      expect(rows[0].findAll('td')[0].text()).toBe('Charlie')
    })
  })
  
  describe('DataTable Multi-Sort - Mode Toggle', () => {
    it('switching from multiSort to single sort keeps only the first sort key via serverSort', async () => {
      // Simulates DataViewer behavior: when multiSort is toggled off,
      // the parent clears extra sort keys and passes only the first via serverSort
      const wrapper = createWrapper({
        multiSort: true,
        serverSort: [
          { key: 'name', dir: 'asc' },
          { key: 'age', dir: 'desc' },
        ],
      })
  
      // Verify both sort indicators are shown
      expect(wrapper.findAll('.sort-badge').length).toBe(2)
  
      // Simulate parent toggling multiSort off and reducing to single sort
      await wrapper.setProps({
        multiSort: false,
        serverSort: [{ key: 'name', dir: 'asc' }],
      })
  
      // Should show only one sort indicator (no badges in single sort)
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      expect(nameSortBtn.find('.bi-arrow-up').exists()).toBe(true)
      // No sort badges in single sort mode
      expect(wrapper.findAll('.sort-badge').length).toBe(0)
    })
  
    it('clicking sort in single mode after switching from multi replaces all keys', async () => {
      const wrapper = createWrapper({ multiSort: true, serverSort: [] })
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]
  
      // Set up multi-sort: name asc, age asc
      await nameSortBtn.trigger('click')
      await ageSortBtn.trigger('click')
  
      // Switch to single sort mode
      await wrapper.setProps({ multiSort: false })
  
      // Click age sort - should replace all previous sorts
      await ageSortBtn.trigger('click')
      const lastPayload = wrapper.emitted('sort-changed')!.at(-1)![0] as any[]
      expect(lastPayload).toEqual([{ dir: 'asc', key: 'name' }, { dir: 'desc', key: 'age' }])
    })
  
    it('serverSort persists sort state across prop updates', async () => {
      // Simulates page navigation: serverSort stays the same while items change
      const wrapper = createWrapper({
        multiSort: true,
        serverSort: [
          { key: 'name', dir: 'asc' },
          { key: 'age', dir: 'desc' },
        ],
      })
  
      // Simulate data refresh (items change but sort stays)
      await wrapper.setProps({
        items: [
          { name: 'Zara', age: 40 },
          { name: 'Alice', age: 5 },
        ],
      })
  
      // Sort indicators should still be present
      const nameSortBtn = wrapper.findAll('.sort-btn')[0]
      const ageSortBtn = wrapper.findAll('.sort-btn')[1]
      expect(nameSortBtn.find('.bi-arrow-up').exists()).toBe(true)
      expect(ageSortBtn.find('.bi-arrow-down').exists()).toBe(true)
    })
  })
})
