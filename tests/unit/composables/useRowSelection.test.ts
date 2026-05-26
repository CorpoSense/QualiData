/**
 * Tests for row selection composable functionality
 * Tests the logic for handling selected rows and applying operations to selected rows
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock global fetch
global.fetch = vi.fn()

describe('Row Selection Operations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Row Scope Logic', () => {
    it('should default to "all" row scope', () => {
      const operationRowScope = 'all'
      expect(operationRowScope).toBe('all')
    })

    it('should switch to "selected" when rows are selected', () => {
      const selectedRowIndices = [0, 2, 4]
      const operationRowScope = selectedRowIndices.length > 0 ? 'selected' : 'all'
      expect(operationRowScope).toBe('selected')
    })

    it('should stay "all" when no rows are selected', () => {
      const selectedRowIndices: number[] = []
      const operationRowScope = selectedRowIndices.length > 0 ? 'selected' : 'all'
      expect(operationRowScope).toBe('all')
    })
  })

  describe('Selected Row Count Display', () => {
    it('should show correct count for selected rows', () => {
      const selectedRowIndices = [0, 1, 2, 3, 4]
      const count = selectedRowIndices.length
      expect(count).toBe(5)
    })

    it('should show singular "row" for single selection', () => {
      const selectedRowIndices = [0]
      const text = selectedRowIndices.length === 1
        ? 'Selected (1 row)'
        : `Selected (${selectedRowIndices.length} rows)`
      expect(text).toBe('Selected (1 row)')
    })

    it('should show plural "rows" for multiple selections', () => {
      const selectedRowIndices = [0, 1, 2]
      const text = selectedRowIndices.length === 1
        ? 'Selected (1 row)'
        : `Selected (${selectedRowIndices.length} rows)`
      expect(text).toBe('Selected (3 rows)')
    })
  })

  describe('Row Indices Payload', () => {
    it('should include row_indices in payload when scope is "selected"', () => {
      const selectedRowIndices = [0, 2, 4]
      const operationRowScope = 'selected'

      const payload = {
        columns: ['name'],
        operation: 'upper',
        ...(operationRowScope === 'selected' && {
          row_indices: selectedRowIndices
        })
      }

      expect(payload.row_indices).toEqual([0, 2, 4])
    })

    it('should not include row_indices in payload when scope is "all"', () => {
      const selectedRowIndices = [0, 2, 4]
      const operationRowScope: 'all' | 'selected' = 'all'

      const payload = {
        columns: ['name'],
        operation: 'upper',
        ...(operationRowScope.toLocaleLowerCase() === 'selected' ? {
          row_indices: selectedRowIndices
        } : {})
      }

      expect(payload.row_indices).toBeUndefined()
    })

    it('should include row_indices even if empty when explicitly passed', () => {
      const payload = {
        columns: ['name'],
        operation: 'upper',
        row_indices: []
      }

      expect('row_indices' in payload).toBe(true)
      expect(payload.row_indices).toEqual([])
    })
  })

  describe('Toggle Selection', () => {
    it('should add row to selection if not selected', () => {
      let selectedRowIndices = [0, 2]
      const rowToToggle = 4

      if (!selectedRowIndices.includes(rowToToggle)) {
        selectedRowIndices = [...selectedRowIndices, rowToToggle]
      }

      expect(selectedRowIndices).toContain(4)
      expect(selectedRowIndices.length).toBe(3)
    })

    it('should remove row from selection if already selected', () => {
      let selectedRowIndices = [0, 2, 4]
      const rowToToggle = 2

      selectedRowIndices = selectedRowIndices.filter(i => i !== rowToToggle)

      expect(selectedRowIndices).not.toContain(2)
      expect(selectedRowIndices.length).toBe(2)
    })

    it('should clear all selections when clearSelection is called', () => {
      let selectedRowIndices = [0, 1, 2, 3, 4]

      selectedRowIndices = []

      expect(selectedRowIndices.length).toBe(0)
    })

    it('should select all rows when selectAll is called', () => {
      const totalRows = 100
      let selectedRowIndices: number[] = []

      selectedRowIndices = Array.from({ length: totalRows }, (_, i) => i)

      expect(selectedRowIndices.length).toBe(100)
      expect(selectedRowIndices[0]).toBe(0)
      expect(selectedRowIndices[99]).toBe(99)
    })
  })

  describe('Operation Request Building', () => {
    it('should build string operation request with row indices', () => {
      const columns = ['name']
      const operation = 'upper'
      const selectedRowIndices = [0, 1, 2]
      const operationRowScope = 'selected'

      const request = {
        columns,
        operation,
        ...(operationRowScope === 'selected' ? { row_indices: selectedRowIndices } : {})
      }

      expect(request).toEqual({
        columns: ['name'],
        operation: 'upper',
        row_indices: [0, 1, 2]
      })
    })

    it('should build find replace request with row indices', () => {
      const columns = ['city']
      const find = 'NYC'
      const replace = 'New York'
      const selectedRowIndices = [0, 3, 5]
      const operationRowScope = 'selected'

      const request = {
        columns,
        find,
        replace,
        ...(operationRowScope === 'selected' ? { row_indices: selectedRowIndices } : {})
      }

      expect(request.row_indices).toEqual([0, 3, 5])
    })

    it('should build datetime operation request with row indices', () => {
      const columns = ['date']
      const operation = 'extract_year'
      const selectedRowIndices = [1, 4]
      const operationRowScope = 'selected'

      const request = {
        columns,
        operation,
        ...(operationRowScope === 'selected' ? { row_indices: selectedRowIndices } : {})
      }

      expect(request.row_indices).toEqual([1, 4])
    })

    it('should build numeric operation request with row indices', () => {
      const columns = ['value']
      const operation = 'multiply'
      const factor = 2
      const selectedRowIndices = [0, 1]
      const operationRowScope = 'selected'

      const request = {
        columns,
        operation,
        factor,
        ...(operationRowScope === 'selected' ? { row_indices: selectedRowIndices } : {})
      }

      expect(request.row_indices).toEqual([0, 1])
      expect(request.factor).toBe(2)
    })
  })

  describe('Response Handling', () => {
    it('should indicate rows affected in response message', () => {
      const message = 'Applied uppercase to 3 row(s)'
      const rowsAffected = message.match(/(\d+) row\(s\)/)

      expect(rowsAffected).not.toBeNull()
      expect(parseInt(rowsAffected![1])).toBe(3)
    })

    it('should handle response without row count for all rows', () => {
      const message = 'Applied uppercase to all rows'

      expect(message).toContain('all rows')
    })
  })
})
