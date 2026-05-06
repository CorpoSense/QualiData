/**
 * Tests for ValueMappingModal component
 * Tests rendering, mapping rule management, regex toggle, JSON import,
 * validation, apply/cancel, and missing value handling
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import ValueMappingModal from './ValueMappingModal.vue'

// Mock getApiUrl
vi.mock('@/utils/api', () => ({
  getApiUrl: () => 'http://localhost:8000',
}))

// Mock useToast
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  }),
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'test-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

// Mock fetch
const mockFetch = vi.fn()
globalThis.fetch = mockFetch

function createWrapper(props: Record<string, any> = {}) {
  return mount(ValueMappingModal, {
    props: {
      modelValue: true,
      column: 'country',
      datasetId: 'ds-123',
      uniqueValues: ['USA', 'UK', 'France', 'Netherlands'],
      operating: false,
      ...props,
    },
    global: {
      stubs: {
        BModal: {
          template: '<div class="b-modal" v-if="modelValue"><slot /><slot name="footer" /></div>',
          props: ['modelValue', 'title', 'size'],
          emits: ['update:modelValue', 'show', 'hide'],
        },
        BButton: {
          template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /></button>',
          props: ['variant', 'loading', 'disabled', 'size'],
          emits: ['click'],
        },
        BFormGroup: {
          template: '<div><slot /></div>',
          props: ['label', 'labelSize'],
        },
        BFormSelect: {
          template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
          props: ['modelValue', 'options', 'size'],
          emits: ['update:modelValue'],
        },
        BFormInput: {
          template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
          props: ['modelValue', 'placeholder', 'size', 'type'],
          emits: ['update:modelValue'],
        },
        BFormCheckbox: {
          template: '<input type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" />',
          props: ['modelValue', 'checked'],
          emits: ['update:modelValue'],
        },
        BBadge: {
          template: '<span @click="$emit(\'click\')"><slot /></span>',
          props: ['variant', 'pill'],
          emits: ['click'],
        },
      },
    },
  })
}

describe('ValueMappingModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockReset()
  })

  describe('Rendering', () => {
    it('renders the modal container when modelValue is true', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.b-modal').exists()).toBe(true)
    })

    it('does not render when modelValue is false', () => {
      const wrapper = createWrapper({ modelValue: false })
      expect(wrapper.find('.b-modal').exists()).toBe(false)
    })

    it('shows column name in the component', () => {
      const wrapper = createWrapper({ column: 'country' })
      expect(wrapper.text()).toContain('country')
    })

    it('renders unique value chips', () => {
      const wrapper = createWrapper({ uniqueValues: ['USA', 'UK', 'France'] })
      expect(wrapper.text()).toContain('USA')
      expect(wrapper.text()).toContain('UK')
      expect(wrapper.text()).toContain('France')
    })

    it('renders missing value action dropdown', () => {
      const wrapper = createWrapper()
      const selects = wrapper.findAll('select')
      expect(selects.length).toBeGreaterThanOrEqual(1)
    })

    it('renders default value input', () => {
      const wrapper = createWrapper()
      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Mapping Rule Management', () => {
    it('starts with one empty mapping rule', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      expect(vm.mappingRules.length).toBe(1)
      expect(vm.mappingRules[0].from_value).toBe('')
      expect(vm.mappingRules[0].to_value).toBe('')
      expect(vm.mappingRules[0].is_regex).toBe(false)
    })

    it('adds a new mapping rule', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      await vm.addRule()
      await nextTick()
      expect(vm.mappingRules.length).toBe(2)
    })

    it('removes a mapping rule', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      // Add two rules
      await vm.addRule()
      await nextTick()
      expect(vm.mappingRules.length).toBe(2)
      // Remove the first rule
      await vm.removeRule(0)
      await nextTick()
      expect(vm.mappingRules.length).toBe(1)
    })

    it('does not remove the last mapping rule', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      expect(vm.mappingRules.length).toBe(1)
      await vm.removeRule(0)
      await nextTick()
      expect(vm.mappingRules.length).toBe(1)
    })

    it('clears all mapping rules and adds one empty rule', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [
        { from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true },
        { from_value: 'UK', to_value: 'United Kingdom', is_regex: false, case_sensitive: true },
      ]
      await nextTick()
      await vm.clearAll()
      await nextTick()
      expect(vm.mappingRules.length).toBe(1)
      expect(vm.mappingRules[0].from_value).toBe('')
    })
  })

  describe('Regex Toggle', () => {
    it('toggles is_regex on a mapping rule', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      expect(vm.mappingRules[0].is_regex).toBe(false)
      vm.mappingRules[0].is_regex = true
      await nextTick()
      expect(vm.mappingRules[0].is_regex).toBe(true)
    })

    it('shows case_sensitive option when is_regex is true', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules[0].is_regex = true
      await nextTick()
      // The case_sensitive checkbox should be relevant when is_regex is true
      expect(vm.mappingRules[0].case_sensitive).toBe(true)
    })
  })

  describe('Unique Value Click', () => {
    it('adds a mapping rule when clicking a unique value chip', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      await vm.addFromUniqueValue('USA')
      await nextTick()
      // Should find the empty rule and fill it, or add a new one
      const filledRule = vm.mappingRules.find((r: any) => r.from_value === 'USA')
      expect(filledRule).toBeTruthy()
      expect(filledRule.to_value).toBe('')
    })

    it('does not add duplicate from_value from unique values', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [{ from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true }]
      await nextTick()
      await vm.addFromUniqueValue('USA')
      await nextTick()
      // Should not add a duplicate
      const usaRules = vm.mappingRules.filter((r: any) => r.from_value === 'USA')
      expect(usaRules.length).toBe(1)
    })
  })

  describe('JSON Import', () => {
    it('imports JSON mapping into rules', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      const jsonStr = '{"USA": "US", "UK": "United Kingdom"}'
      await vm.importJson(jsonStr)
      await nextTick()
      expect(vm.mappingRules.length).toBe(2)
      const fromValues = vm.mappingRules.map((r: any) => r.from_value)
      expect(fromValues).toContain('USA')
      expect(fromValues).toContain('UK')
      const usaRule = vm.mappingRules.find((r: any) => r.from_value === 'USA')
      expect(usaRule.to_value).toBe('US')
    })

    it('handles invalid JSON gracefully', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      const originalLength = vm.mappingRules.length
      await vm.importJson('not valid json')
      await nextTick()
      // Should not change rules on invalid JSON
      expect(vm.mappingRules.length).toBe(originalLength)
    })
  })

  describe('Validation', () => {
    it('detects invalid regex pattern', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [{ from_value: '[invalid', to_value: 'X', is_regex: true, case_sensitive: true }]
      await nextTick()
      await vm.validateRegex(0)
      await nextTick()
      expect(vm.regexErrors[0]).toBeTruthy()
    })

    it('clears regex error when pattern is valid', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.regexErrors = { 0: 'Invalid regex' }
      vm.mappingRules = [{ from_value: '^valid.*$', to_value: 'X', is_regex: true, case_sensitive: true }]
      await nextTick()
      await vm.validateRegex(0)
      await nextTick()
      expect(vm.regexErrors[0]).toBeFalsy()
    })

    it('canApply is false when there are regex errors', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.regexErrors = { 0: 'Invalid regex' }
      expect(vm.canApply).toBe(false)
    })

    it('canApply is false when all from_values are empty', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [{ from_value: '', to_value: '', is_regex: false, case_sensitive: true }]
      expect(vm.canApply).toBe(false)
    })

    it('canApply is true when at least one valid rule exists', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [{ from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true }]
      vm.regexErrors = {}
      expect(vm.canApply).toBe(true)
    })

    it('canApply is false when operating is true', () => {
      const wrapper = createWrapper({ operating: true })
      const vm = wrapper.vm as any
      vm.mappingRules = [{ from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true }]
      vm.regexErrors = {}
      expect(vm.canApply).toBe(false)
    })
  })

  describe('Apply and Cancel', () => {
    it('emits apply with correct payload', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [
        { from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true },
        { from_value: '^Neth.*$', to_value: 'NL', is_regex: true, case_sensitive: true },
      ]
      vm.missingValueAction = 'fill'
      vm.missingValueFill = 'Unknown'
      vm.defaultValue = 'Other'
      vm.regexErrors = {}
      await nextTick()

      await vm.onApply()

      expect(wrapper.emitted('apply')).toBeTruthy()
      const payload = wrapper.emitted('apply')![0][0] as any
      expect(payload.column).toBe('country')
      expect(payload.mappings.length).toBe(2)
      expect(payload.mappings[0].from_value).toBe('USA')
      expect(payload.mappings[0].to_value).toBe('US')
      expect(payload.mappings[0].is_regex).toBe(false)
      expect(payload.mappings[1].from_value).toBe('^Neth.*$')
      expect(payload.mappings[1].is_regex).toBe(true)
      expect(payload.missing_value_action).toBe('fill')
      expect(payload.missing_value_fill).toBe('Unknown')
      expect(payload.default_value).toBe('Other')
    })

    it('emits update:modelValue with false on cancel', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      await vm.onCancel()
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')![0][0]).toBe(false)
    })

    it('does not apply when canApply is false', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [{ from_value: '', to_value: '', is_regex: false, case_sensitive: true }]
      await vm.onApply()
      expect(wrapper.emitted('apply')).toBeFalsy()
    })

    it('filters out empty rules in apply payload', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [
        { from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true },
        { from_value: '', to_value: '', is_regex: false, case_sensitive: true },
      ]
      vm.regexErrors = {}
      await nextTick()

      await vm.onApply()

      const payload = wrapper.emitted('apply')![0][0] as any
      expect(payload.mappings.length).toBe(1)
      expect(payload.mappings[0].from_value).toBe('USA')
    })
  })

  describe('Missing Value Action', () => {
    it('updates missing value action', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.missingValueAction = 'drop'
      await nextTick()
      expect(vm.missingValueAction).toBe('drop')
    })

    it('shows fill input when action is fill', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.missingValueAction = 'fill'
      await nextTick()
      expect(vm.showFillInput).toBe(true)
    })

    it('hides fill input when action is keep', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.missingValueAction = 'keep'
      await nextTick()
      expect(vm.showFillInput).toBe(false)
    })
  })

  describe('Preview', () => {
    it('computes preview from mapping rules', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [
        { from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true },
      ]
      vm.sampleRows = [
        { country: 'USA' },
        { country: 'France' },
        { country: null },
      ]
      await nextTick()
      const preview = vm.previewResults
      expect(preview.length).toBe(3)
      const usaPreview = preview.find((p: any) => p.original === 'USA')
      expect(usaPreview.mapped).toBe('US')
      const francePreview = preview.find((p: any) => p.original === 'France')
      expect(francePreview.mapped).toBe('France') // Unchanged
    })

    it('applies regex in preview', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [
        { from_value: '^Neth.*$', to_value: 'NL', is_regex: true, case_sensitive: true },
      ]
      vm.sampleRows = [
        { country: 'Netherlands' },
        { country: 'France' },
      ]
      await nextTick()
      const preview = vm.previewResults
      const nethPreview = preview.find((p: any) => p.original === 'Netherlands')
      expect(nethPreview.mapped).toBe('NL')
    })

    it('applies default value in preview for unmatched', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [
        { from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true },
      ]
      vm.defaultValue = 'Other'
      vm.sampleRows = [
        { country: 'USA' },
        { country: 'France' },
      ]
      await nextTick()
      const preview = vm.previewResults
      const francePreview = preview.find((p: any) => p.original === 'France')
      expect(francePreview.mapped).toBe('Other')
    })
  })

  describe('Edge Cases', () => {
    it('handles empty unique values', () => {
      const wrapper = createWrapper({ uniqueValues: [] })
      expect(wrapper.find('.b-modal').exists()).toBe(true)
    })

    it('handles empty column name', () => {
      const wrapper = createWrapper({ column: '' })
      expect(wrapper.find('.b-modal').exists()).toBe(true)
    })

    it('resets state on modal open', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.mappingRules = [
        { from_value: 'USA', to_value: 'US', is_regex: false, case_sensitive: true },
      ]
      vm.defaultValue = 'Other'
      await vm.onModalOpen()
      await nextTick()
      expect(vm.mappingRules.length).toBe(1)
      expect(vm.mappingRules[0].from_value).toBe('')
      expect(vm.defaultValue).toBe('')
    })
  })
})
