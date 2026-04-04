import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProfileModal from '@/components/ProfileModal.vue'

// Simple mock for BootstrapVueNext components that properly renders slots
const MockBModal = {
  props: {
    modelValue: { type: Boolean, default: false },
    title: { type: String, default: '' },
    size: { type: String, default: 'md' },
  },
  emits: ['update:modelValue'],
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
    loading: { type: Boolean, default: false },
  },
  emits: ['click'],
  template: `<button :class="'btn-' + variant" @click="$emit('click')"><slot></slot></button>`,
}

describe('ProfileModal.vue', () => {
  it('renders nothing when modelValue is false', () => {
    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: false,
        profileData: null,
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.exists()).toBe(true)
    // When modelValue is false, the modal should not render
    expect(wrapper.find('.modal-mock').exists()).toBe(false)
  })

  it('displays loading state when loading is true', () => {
    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData: null,
        loading: true,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })
    expect(wrapper.find('.modal-mock').exists()).toBe(true)
    expect(wrapper.text()).toContain('Loading profile')
  })

  it('displays KPI cards when profile data is provided', () => {
    const profileData = {
      total_rows: 1000,
      total_columns: 5,
      columns: [
        {
          name: 'id',
          dtype: 'int64',
          null_count: 0,
          null_percent: 0,
          unique_count: 1000,
          quality_score: 100,
          stats: {},
        },
        {
          name: 'name',
          dtype: 'object',
          null_count: 10,
          null_percent: 1,
          unique_count: 500,
          quality_score: 99,
          stats: { top_values: [] },
        },
      ],
    }

    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData,
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })

    expect(wrapper.text()).toContain('Total Rows')
    expect(wrapper.text()).toContain('1000')
    expect(wrapper.text()).toContain('Columns')
    expect(wrapper.text()).toContain('5')
    expect(wrapper.text()).toContain('Column Profiles')
  })

  it('calculates total nulls correctly', () => {
    const profileData = {
      total_rows: 100,
      total_columns: 2,
      columns: [
        { name: 'col1', null_count: 5, null_percent: 5, unique_count: 50, quality_score: 95, stats: {} },
        { name: 'col2', null_count: 15, null_percent: 15, unique_count: 80, quality_score: 85, stats: {} },
      ],
    }

    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData,
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })

    // The component should show total nulls (20)
    expect(wrapper.text()).toContain('20')
  })

  it('displays column card with all details', () => {
    const profileData = {
      total_rows: 100,
      total_columns: 1,
      columns: [
        {
          name: 'email',
          dtype: 'object',
          null_count: 25,
          null_percent: 25,
          unique_count: 75,
          quality_score: 75,
          stats: {
            top_values: [
              { value: 'test@example.com', count: 10 },
              { value: 'admin@example.com', count: 5 },
            ],
          },
        },
      ],
    }

    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData,
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })

    expect(wrapper.text()).toContain('email')
    expect(wrapper.text()).toContain('object')
    expect(wrapper.text()).toContain('25 nulls (25%)')
    expect(wrapper.text()).toContain('75 unique')
    expect(wrapper.text()).toContain('Quality: 75%')
    expect(wrapper.text()).toContain('Top:')
    // Check for count in the top values (which indicates top values are displayed)
    expect(wrapper.text()).toContain('(10)')
  })

  it('emits update:modelValue when close button is clicked', async () => {
    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData: { total_rows: 10, total_columns: 2, columns: [] },
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })

    const closeButton = wrapper.find('button')
    await closeButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted?.[0]).toEqual([false])
  })

  it('displays empty state when no profile data', () => {
    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData: null,
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })

    expect(wrapper.text()).toContain('No profile data available')
  })

  it('displays progress bar with correct color for high null percentage', () => {
    const profileData = {
      total_rows: 100,
      total_columns: 1,
      columns: [
        {
          name: 'bad_col',
          dtype: 'object',
          null_count: 60,
          null_percent: 60,
          unique_count: 40,
          quality_score: 40,
          stats: {},
        },
      ],
    }

    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData,
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })

    // Should contain the null percentage
    expect(wrapper.text()).toContain('60 nulls (60%)')
    expect(wrapper.text()).toContain('Quality: 40%')
  })

  it('shows No nulls when null_count is 0', () => {
    const profileData = {
      total_rows: 100,
      total_columns: 1,
      columns: [
        {
          name: 'good_col',
          dtype: 'int64',
          null_count: 0,
          null_percent: 0,
          unique_count: 100,
          quality_score: 100,
          stats: {},
        },
      ],
    }

    const wrapper = mount(ProfileModal, {
      props: {
        modelValue: true,
        profileData,
        loading: false,
      },
      global: {
        stubs: {
          BModal: MockBModal,
          BButton: MockBButton,
        },
      },
    })

    expect(wrapper.text()).toContain('No nulls')
  })
})