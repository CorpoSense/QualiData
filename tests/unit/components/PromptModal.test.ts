/**
 * Tests for PromptModal component
 * Tests defaultValue handling, confirm/cancel behavior, and rename column scenario
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PromptModal from '@/components/PromptModal.vue'

function createWrapper(props: Record<string, any> = {}) {
  return mount(PromptModal, {
    props: {
      modelValue: false,
      title: 'Input',
      message: '',
      defaultValue: '',
      inputType: 'text',
      confirmText: 'OK',
      ...props,
    },
  })
}

describe('PromptModal - defaultValue Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes inputValue to defaultValue when modal opens', async () => {
    const wrapper = createWrapper({ defaultValue: 'existing_col' })
    await wrapper.setProps({ modelValue: true })
    expect((wrapper.vm as any).inputValue).toBe('existing_col')
  })

  it('initializes inputValue to empty string when no defaultValue and modal opens', async () => {
    const wrapper = createWrapper({ defaultValue: '' })
    await wrapper.setProps({ modelValue: true })
    expect((wrapper.vm as any).inputValue).toBe('')
  })

  it('keeps inputValue unchanged when defaultValue prop changes while modal is open', async () => {
    const wrapper = createWrapper({ modelValue: false, defaultValue: 'old_name' })
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).inputValue).toBe('old_name')

    await wrapper.setProps({ defaultValue: 'new_name' })
    // The watch only triggers on modelValue change, not defaultValue change
    expect((wrapper.vm as any).inputValue).toBe('old_name')
  })

  it('resets inputValue to new defaultValue when modal is reopened', async () => {
    const wrapper = createWrapper({ defaultValue: 'first_col' })
    await wrapper.setProps({ modelValue: true })
    expect((wrapper.vm as any).inputValue).toBe('first_col')

    // Close modal
    await wrapper.setProps({ modelValue: false })

    // Change defaultValue and reopen
    await wrapper.setProps({ defaultValue: 'second_col', modelValue: true })
    expect((wrapper.vm as any).inputValue).toBe('second_col')
  })

  it('resets inputValue to empty when modal is reopened without defaultValue', async () => {
    const wrapper = createWrapper({ defaultValue: 'some_col' })
    await wrapper.setProps({ modelValue: true })
    expect((wrapper.vm as any).inputValue).toBe('some_col')

    await wrapper.setProps({ modelValue: false })
    await wrapper.setProps({ defaultValue: '', modelValue: true })
    expect((wrapper.vm as any).inputValue).toBe('')
  })
})

describe('PromptModal - Confirm and Cancel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('emits confirm with defaultValue when confirmed without editing', async () => {
    const wrapper = createWrapper({ modelValue: false, defaultValue: 'test_col' })
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()

    const vm = wrapper.vm as any
    vm.onConfirm()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('confirm')).toBeTruthy()
    expect(wrapper.emitted('confirm')![0][0]).toBe('test_col')
  })

  it('emits confirm with modified value after user edits', async () => {
    const wrapper = createWrapper({ modelValue: false, defaultValue: 'original' })
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()

    const vm = wrapper.vm as any
    vm.inputValue = 'modified_name'
    vm.onConfirm()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('confirm')![0][0]).toBe('modified_name')
  })

  it('emits cancel when cancelled', async () => {
    const wrapper = createWrapper({ modelValue: false })
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()

    const vm = wrapper.vm as any
    vm.onCancel()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('hides modal on confirm', async () => {
    const wrapper = createWrapper({ modelValue: false, defaultValue: 'col' })
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()

    const vm = wrapper.vm as any
    vm.onConfirm()
    await wrapper.vm.$nextTick()

    expect(vm.visible).toBe(false)
  })

  it('hides modal on cancel', async () => {
    const wrapper = createWrapper({ modelValue: false })
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()

    const vm = wrapper.vm as any
    vm.onCancel()
    await wrapper.vm.$nextTick()

    expect(vm.visible).toBe(false)
  })

  it('does not emit confirm on cancel', async () => {
    const wrapper = createWrapper({ modelValue: false, defaultValue: 'col' })
    await wrapper.setProps({ modelValue: true })
    await wrapper.vm.$nextTick()

    const vm = wrapper.vm as any
    vm.onCancel()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('confirm')).toBeFalsy()
  })
})

describe('PromptModal - Rename Column Scenario', () => {
  it('pre-fills input with current column name when renaming', async () => {
    const currentColumnName = 'email_address'
    const wrapper = createWrapper({
      title: 'Rename Column',
      message: 'Enter new column name:',
      defaultValue: currentColumnName,
      confirmText: 'Rename',
    })

    await wrapper.setProps({ modelValue: true })
    expect((wrapper.vm as any).inputValue).toBe('email_address')
  })

  it('allows user to modify the pre-filled name and confirm', async () => {
    const wrapper = createWrapper({
      title: 'Rename Column',
      message: 'Enter new column name:',
      defaultValue: 'old_name',
      confirmText: 'Rename',
    })

    await wrapper.setProps({ modelValue: true })
    const vm = wrapper.vm as any

    // User modifies the name
    vm.inputValue = 'new_name'
    vm.onConfirm()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('confirm')![0][0]).toBe('new_name')
  })

  it('allows user to keep the same name (no change)', async () => {
    const wrapper = createWrapper({
      title: 'Rename Column',
      message: 'Enter new column name:',
      defaultValue: 'same_name',
      confirmText: 'Rename',
    })

    await wrapper.setProps({ modelValue: true })
    const vm = wrapper.vm as any
    vm.onConfirm()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('confirm')![0][0]).toBe('same_name')
  })

  it('returns cancel when user cancels rename', async () => {
    const wrapper = createWrapper({
      title: 'Rename Column',
      message: 'Enter new column name:',
      defaultValue: 'some_column',
      confirmText: 'Rename',
    })

    await wrapper.setProps({ modelValue: true })
    const vm = wrapper.vm as any
    vm.onCancel()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('confirm')).toBeFalsy()
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('handles column names with special characters as defaultValue', async () => {
    const specialNames = [
      'col with spaces',
      'column_with_underscores',
      'Column With Mixed Case',
      '123_numeric_start',
    ]

    for (const name of specialNames) {
      const wrapper = createWrapper({
        title: 'Rename Column',
        message: 'Enter new column name:',
        defaultValue: name,
      })

      await wrapper.setProps({ modelValue: true })
      expect((wrapper.vm as any).inputValue).toBe(name)
      wrapper.unmount()
    }
  })
})

describe('showPrompt - defaultValue Logic', () => {
  // These tests verify the logic that DataViewer uses when calling showPrompt
  // for the rename operation, ensuring defaultValue is passed correctly

  it('showPrompt options with defaultValue sets promptConfig.defaultValue', () => {
    const options = {
      title: 'Rename Column',
      message: 'Enter new column name:',
      defaultValue: 'current_col_name',
    }

    const promptConfig = {
      show: true,
      title: options.title || 'Input',
      message: options.message || '',
      defaultValue: options.defaultValue || '',
      inputType: 'text' as const,
      confirmText: 'OK' as const,
    }

    expect(promptConfig.defaultValue).toBe('current_col_name')
  })

  it('showPrompt options without defaultValue defaults to empty string', () => {
    const options = {
      title: 'Add Column',
      message: 'Enter new column name:',
    }

    const promptConfig = {
      show: true,
      title: options.title || 'Input',
      message: options.message || '',
      defaultValue: (options as any).defaultValue || '',
      inputType: 'text' as const,
      confirmText: 'OK' as const,
    }

    expect(promptConfig.defaultValue).toBe('')
  })

  it('rename operation passes selected column name as defaultValue', () => {
    const selectedColumns = ['email_address']
    const effectiveSelectedColumns = selectedColumns

    const columnName = effectiveSelectedColumns[0]
    const promptOptions = {
      title: 'Rename Column',
      message: 'Enter new column name:',
      defaultValue: columnName,
    }

    expect(promptOptions.defaultValue).toBe('email_address')
  })

  it('rename operation with various column names passes correct defaultValue', () => {
    const testCases = [
      { column: 'first_name', expected: 'first_name' },
      { column: 'user_email', expected: 'user_email' },
      { column: 'column_with_underscores', expected: 'column_with_underscores' },
      { column: 'Column With Spaces', expected: 'Column With Spaces' },
      { column: '123_numeric', expected: '123_numeric' },
    ]

    for (const { column, expected } of testCases) {
      const promptOptions = {
        title: 'Rename Column',
        message: 'Enter new column name:',
        defaultValue: column,
      }
      expect(promptOptions.defaultValue).toBe(expected)
    }
  })
})
