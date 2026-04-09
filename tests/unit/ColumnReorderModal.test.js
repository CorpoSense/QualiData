import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ColumnReorderModal from '@/components/ColumnReorderModal.vue'

// Simple mock for BootstrapVueNext components
const MockBModal = {
  props: {
    modelValue: { type: Boolean, default: false },
    title: { type: String, default: '' },
    size: { type: String, default: 'md' },
  },
  emits: ['update:modelValue', 'hide'],
  template: `
    <div v-if="modelValue" class="modal-mock">
      <div class="modal-title">{{ title }}</div>
      <div class="modal-body">
        <slot></slot>
      </div>
      <div class="modal-footer">
        <slot name="footer"></slot>
      </div>
    </div>
  `,
}

const MockBButton = {
  props: {
    variant: { type: String, default: 'primary' },
    size: { type: String, default: 'sm' },
    disabled: { type: Boolean, default: false },
  },
  emits: ['click'],
  template: `<button :class="'btn-' + variant" :disabled="disabled" @click="$emit('click')"><slot></slot></button>`,
}

describe('ColumnReorderModal.vue', () => {
  const mockColumns = [
    { field: 'name', label: 'Name' },
    { field: 'email', label: 'Email' },
    { field: 'age', label: 'Age' },
    { field: 'city', label: 'City' }
  ]

  it('renders modal when modelValue is true', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.find('.modal-mock').exists()).toBe(true)
  })

  it('does not render modal when modelValue is false', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: false,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.find('.modal-mock').exists()).toBe(false)
  })

  it('displays all columns in the list', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    const items = wrapper.findAll('.column-item')
    expect(items.length).toBe(4)
  })

  it('displays column labels correctly', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.text()).toContain('Name')
    expect(wrapper.text()).toContain('Email')
    expect(wrapper.text()).toContain('Age')
    expect(wrapper.text()).toContain('City')
  })

  it('has quick action buttons', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.text()).toContain('Select All')
    expect(wrapper.text()).toContain('Clear')
    expect(wrapper.text()).toContain('Move Selected Up')
    expect(wrapper.text()).toContain('Move Selected Down')
  })

  it('shows info message', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.text()).toContain('Drag and drop columns')
  })

  it('has Cancel and Apply buttons in footer', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.text()).toContain('Cancel')
    expect(wrapper.text()).toContain('Apply')
  })

  it('highlights selected columns', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: ['name', 'email']
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    // Selected items should have bg-light class (checked in component logic)
    const selectedItems = wrapper.findAll('.column-item.bg-light')
    expect(selectedItems.length).toBe(2)
  })

  it('emits cancel event when Cancel is clicked', async () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    
    const buttons = wrapper.findAllComponents(MockBButton)
    const cancelBtn = buttons.find(b => b.text().includes('Cancel'))
    await cancelBtn.trigger('click')
    
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('emits apply event with new order when Apply is clicked', async () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    
    const buttons = wrapper.findAllComponents(MockBButton)
    const applyBtn = buttons.find(b => b.text().includes('Apply') && !b.text().includes('Move'))
    await applyBtn.trigger('click')
    
    expect(wrapper.emitted('apply')).toBeTruthy()
    expect(wrapper.emitted('apply')[0][0]).toEqual(['name', 'email', 'age', 'city'])
  })

  it('emits update:modelValue when Apply is clicked', async () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    
    const buttons = wrapper.findAllComponents(MockBButton)
    const applyBtn = buttons.find(b => b.text().includes('Apply') && !b.text().includes('Move'))
    await applyBtn.trigger('click')
    
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('has up/down buttons for each column item', () => {
    const wrapper = mount(ColumnReorderModal, {
      props: {
        modelValue: true,
        columns: mockColumns,
        selectedColumns: []
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    // Each column should have up and down buttons - check in column-items
    const items = wrapper.findAll('.column-item')
    expect(items.length).toBe(4)
    // Each item has up/down buttons
    const upButtons = wrapper.findAll('.column-item .bi-arrow-up')
    const downButtons = wrapper.findAll('.column-item .bi-arrow-down')
    expect(upButtons.length).toBe(4)
    expect(downButtons.length).toBe(4)
  })
})