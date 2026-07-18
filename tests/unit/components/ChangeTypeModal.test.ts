/**
 * Tests for ChangeTypeModal component
 * Tests rendering, type selection, error handling, preview, suggestions, and apply/cancel
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import ChangeTypeModal from '@/components/ChangeTypeModal.vue'

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
  return mount(ChangeTypeModal, {
    props: {
      modelValue: true,
      selectedColumns: ['age', 'score'],
      datasetId: 'ds-123',
      operating: false,
      ...props,
    },
    global: {
      stubs: {
        BModal: {
          template: '<div class="b-modal"><slot /><slot name="footer" /></div>',
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
          props: ['modelValue', 'placeholder', 'size'],
          emits: ['update:modelValue'],
        },
        BBadge: {
          template: '<span><slot /></span>',
          props: ['variant', 'pill'],
        },
      },
    },
  })
}

describe('ChangeTypeModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockReset()
  })

  describe('Rendering', () => {
    it('renders the modal container', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.b-modal').exists()).toBe(true)
    })

    it('shows selected columns as badges', () => {
      const wrapper = createWrapper({ selectedColumns: ['age', 'score'] })
      const badges = wrapper.findAll('span')
      const badgeTexts = badges.map(b => b.text())
      expect(badgeTexts).toContain('age')
      expect(badgeTexts).toContain('score')
    })

    it('renders type selector dropdown', () => {
      const wrapper = createWrapper()
      const selects = wrapper.findAll('select')
      expect(selects.length).toBeGreaterThanOrEqual(1)
    })

    it('renders error handling dropdown', () => {
      const wrapper = createWrapper()
      const selects = wrapper.findAll('select')
      expect(selects.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Computed Properties', () => {
    it('canApply is false when no type is selected', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = ''
      expect(vm.canApply).toBe(false)
    })

    it('canApply is true when type is selected and not operating', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.previewData = []
      expect(vm.canApply).toBe(true)
    })

    it('canApply is false when operating is true', () => {
      const wrapper = createWrapper({ operating: true })
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      expect(vm.canApply).toBe(false)
    })

    it('canApply is false when error_handling is raise and there are errors', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.errorHandling = 'raise'
      vm.previewData = [{ column: 'age', total_errors: 5, total_rows: 10 }]
      expect(vm.canApply).toBe(false)
    })

    it('canApply is false when error_handling is fallback with no value and errors exist', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.errorHandling = 'fallback'
      vm.fallbackValue = ''
      vm.previewData = [{ column: 'age', total_errors: 5, total_rows: 10 }]
      expect(vm.canApply).toBe(false)
    })

    it('canApply is true when error_handling is fallback with value and errors exist', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.errorHandling = 'fallback'
      vm.fallbackValue = '0'
      vm.previewData = [{ column: 'age', total_errors: 5, total_rows: 10 }]
      expect(vm.canApply).toBe(true)
    })

    it('totalErrorCount sums errors across columns', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.previewData = [
        { column: 'age', total_errors: 3, total_rows: 10 },
        { column: 'score', total_errors: 2, total_rows: 10 },
      ]
      expect(vm.totalErrorCount).toBe(5)
    })

    it('totalErrorCount is 0 when no preview data', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.previewData = []
      expect(vm.totalErrorCount).toBe(0)
    })

    it('fallbackPlaceholder changes based on target type', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any

      vm.targetType = 'integer'
      expect(vm.fallbackPlaceholder).toContain('0')

      vm.targetType = 'float'
      expect(vm.fallbackPlaceholder).toContain('0.0')

      vm.targetType = 'boolean'
      expect(vm.fallbackPlaceholder).toContain('false')

      vm.targetType = 'datetime'
      expect(vm.fallbackPlaceholder).toContain('1970')

      vm.targetType = 'string'
      expect(vm.fallbackPlaceholder).toContain('N/A')
    })
  })

  describe('Type Mismatch Feedback', () => {
    it('shows mismatch when selected type has low score', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.detectionResults = [{
        column: 'name',
        suggested_type: 'string',
        type_scores: { string: 1.0, integer: 0.1, float: 0.1, boolean: 0.0, datetime: 0.0, category: 0.5 },
      }]
      expect(vm.typeMismatchFeedback).toContain('mismatch')
      expect(vm.typeMismatchFeedback).toContain('name')
    })

    it('returns empty string when no type is selected', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = ''
      vm.detectionResults = [{ column: 'name', suggested_type: 'string', type_scores: {} }]
      expect(vm.typeMismatchFeedback).toBe('')
    })

    it('returns empty string when no detection results', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.detectionResults = []
      expect(vm.typeMismatchFeedback).toBe('')
    })

    it('returns empty string when selected type matches suggestion', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.detectionResults = [{
        column: 'age',
        suggested_type: 'integer',
        type_scores: { integer: 0.95 },
      }]
      expect(vm.typeMismatchFeedback).toBe('')
    })

    it('returns empty string when target score is above 0.5', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'float'
      vm.detectionResults = [{
        column: 'age',
        suggested_type: 'integer',
        type_scores: { integer: 0.95, float: 0.8 },
      }]
      expect(vm.typeMismatchFeedback).toBe('')
    })
  })

  describe('Apply and Cancel', () => {
    it('emits apply with correct payload for coerce mode', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.errorHandling = 'coerce'
      vm.previewData = []
      await nextTick()

      await vm.onApply()

      expect(wrapper.emitted('apply')).toBeTruthy()
      const payload = wrapper.emitted('apply')![0][0] as any
      expect(payload.targetType).toBe('integer')
      expect(payload.errorHandling).toBe('coerce')
      expect(payload.fallbackValue).toBeNull()
    })

    it('emits apply with fallback value when error_handling is fallback', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'float'
      vm.errorHandling = 'fallback'
      vm.fallbackValue = '0.0'
      vm.previewData = []
      await nextTick()

      await vm.onApply()

      const payload = wrapper.emitted('apply')![0][0] as any
      expect(payload.errorHandling).toBe('fallback')
      expect(payload.fallbackValue).toBe('0.0')
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
      vm.targetType = '' // No type selected
      await vm.onApply()
      expect(wrapper.emitted('apply')).toBeFalsy()
    })

    it('uses first selected column in apply payload', async () => {
      const wrapper = createWrapper({ selectedColumns: ['age', 'score'] })
      const vm = wrapper.vm as any
      vm.targetType = 'string'
      vm.errorHandling = 'coerce'
      vm.previewData = []
      await nextTick()

      await vm.onApply()

      const payload = wrapper.emitted('apply')![0][0] as any
      expect(payload.column).toBe('age')
    })
  })

  describe('Auto-Detection', () => {
    it('calls detect-type API on modal open', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          status: 'success',
          columns: [{
            column: 'age',
            current_type: 'object',
            suggested_type: 'integer',
            confidence: 0.95,
            reason: '95% of non-null values are valid integers',
            type_scores: { string: 1.0, integer: 0.95 },
            sample_values: ['30'],
            null_count: 0,
            total_rows: 100,
          }],
        }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      await vm.onModalOpen()
      await nextTick()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/datasets/ds-123/operations/detect-type',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ columns: ['age', 'score'] }),
        }),
      )
    })

    it('sets suggested type from detection results', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          status: 'success',
          columns: [{
            column: 'age',
            current_type: 'object',
            suggested_type: 'integer',
            confidence: 0.95,
            reason: '95% match',
            type_scores: { string: 1.0, integer: 0.95 },
            sample_values: ['30'],
            null_count: 0,
            total_rows: 100,
          }, {
            column: 'score',
            current_type: 'object',
            suggested_type: 'integer',
            confidence: 0.9,
            reason: '90% match',
            type_scores: { string: 1.0, integer: 0.9 },
            sample_values: ['85'],
            null_count: 0,
            total_rows: 100,
          }],
        }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      // Call fetchDetection directly (onModalOpen resets state first)
      await vm.fetchDetection()
      await nextTick()

      // Both columns agree on integer, so targetType should be auto-set
      expect(vm.suggestedType).toBe('integer')
      expect(vm.suggestedConfidence).toBe(95)
      expect(vm.targetType).toBe('integer')
    })

    it('does not auto-set type when columns disagree', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          status: 'success',
          columns: [{
            column: 'age',
            current_type: 'object',
            suggested_type: 'integer',
            confidence: 0.95,
            reason: '95% match',
            type_scores: { string: 1.0, integer: 0.95 },
            sample_values: ['30'],
            null_count: 0,
            total_rows: 100,
          }, {
            column: 'name',
            current_type: 'object',
            suggested_type: 'string',
            confidence: 1.0,
            reason: 'Default string type',
            type_scores: { string: 1.0, integer: 0.1 },
            sample_values: ['Alice'],
            null_count: 0,
            total_rows: 100,
          }],
        }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      await vm.fetchDetection()
      await nextTick()

      // Columns disagree, so targetType should remain empty
      expect(vm.suggestedType).toBe('integer')
      expect(vm.targetType).toBe('')
    })

    it('handles detect-type API failure gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Dataset not found' }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      await vm.onModalOpen()
      await nextTick()

      expect(vm.detectionResults).toEqual([])
      expect(vm.suggestedType).toBe('')
    })
  })

  describe('Preview Fetching', () => {
    it('calls change-type-preview when target type is set', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          status: 'success',
          columns: [{
            column: 'age',
            current_type: 'object',
            target_type: 'integer',
            preview: [
              { before: '30', after: '30', changed: true, error: false, error_reason: null },
            ],
            warnings: [],
            data_loss_warnings: [],
            total_errors: 0,
            total_rows: 10,
          }],
        }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.errorHandling = 'coerce'
      await vm.fetchPreview()
      await nextTick()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/datasets/ds-123/operations/change-type-preview',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('integer'),
        }),
      )
      expect(vm.previewData.length).toBe(1)
      expect(vm.previewData[0].column).toBe('age')
    })

    it('sets previewError on API failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Invalid target type' }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'invalid'
      await vm.fetchPreview()
      await nextTick()

      expect(vm.previewError).toBeTruthy()
      expect(vm.previewData).toEqual([])
    })

    it('clears preview data when target type is empty', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = ''
      await vm.fetchPreview()

      expect(vm.previewData).toEqual([])
      expect(vm.dataLossWarnings).toEqual([])
      expect(vm.previewError).toBe('')
    })

    it('aggregates data loss warnings from all columns', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          status: 'success',
          columns: [{
            column: 'age',
            current_type: 'float64',
            target_type: 'integer',
            preview: [],
            warnings: [],
            data_loss_warnings: ['Precision loss: 5 value(s) have non-zero fractional parts'],
            total_errors: 0,
            total_rows: 10,
          }, {
            column: 'score',
            current_type: 'float64',
            target_type: 'integer',
            preview: [],
            warnings: [],
            data_loss_warnings: ['Precision loss: 3 value(s) have non-zero fractional parts'],
            total_errors: 0,
            total_rows: 10,
          }],
        }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      await vm.fetchPreview()
      await nextTick()

      // Should deduplicate warnings (both have same text pattern but different counts)
      expect(vm.dataLossWarnings.length).toBeGreaterThanOrEqual(1)
    })

    it('includes fallback_value in preview request when error_handling is fallback', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          status: 'success',
          columns: [],
        }),
      })

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      vm.errorHandling = 'fallback'
      vm.fallbackValue = '0'
      await vm.fetchPreview()
      await nextTick()

      const callBody = JSON.parse(mockFetch.mock.calls[0][1].body)
      expect(callBody.fallback_value).toBe('0')
    })
  })

  describe('Modal Reset', () => {
    it('resets all state on modal open', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any

      // Set some state
      vm.targetType = 'integer'
      vm.errorHandling = 'fallback'
      vm.fallbackValue = '0'
      vm.previewData = [{ column: 'age', total_errors: 5 }]
      vm.previewError = 'some error'

      // Mock the detect-type call for onModalOpen
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'success', columns: [] }),
      })

      await vm.onModalOpen()
      await nextTick()

      expect(vm.targetType).toBe('')
      expect(vm.errorHandling).toBe('coerce')
      expect(vm.fallbackValue).toBe('')
      expect(vm.previewData).toEqual([])
      expect(vm.previewError).toBe('')
      expect(vm.dataLossWarnings).toEqual([])
    })
  })

  describe('Edge Cases', () => {
    it('handles empty selected columns', () => {
      const wrapper = createWrapper({ selectedColumns: [] })
      // Should still render without errors
      expect(wrapper.find('.b-modal').exists()).toBe(true)
    })

    it('handles network error during fetch', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.targetType = 'integer'
      await vm.fetchPreview()
      await nextTick()

      expect(vm.previewError).toBe('Network error')
      expect(vm.previewData).toEqual([])
    })

    it('handles null preview data gracefully', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as any
      vm.previewData = [{ column: 'age', total_errors: 0 }]
      expect(vm.totalErrorCount).toBe(0)
    })
  })
})
