/**
 * Tests for resolveAbsoluteRowIndex logic — the fix for the bug where
 * cell editing updates the wrong row when multi-column filtering is active.
 *
 * Bug: When filters are active, the /filtered endpoint returns non-contiguous
 * rows (e.g., original indices [2, 5, 8, 15]). The old code used arithmetic
 * (page-1)*limit + displayIndex to compute the absolute row index, which
 * assumed contiguous data. This caused the wrong cell to be updated.
 *
 * Fix: Use filteredMatchingIndices to map display position → original index.
 */
import { describe, it, expect } from 'vitest'

/**
 * Pure-function replica of the resolveAbsoluteRowIndex logic from DataViewer.vue.
 * This mirrors the exact implementation so we can test it in isolation.
 */
function resolveAbsoluteRowIndex(params: {
  displayRowIndex: number
  page: number
  limit: number
  filteredMatchingIndices: number[] | null
}): number {
  const { displayRowIndex, page, limit, filteredMatchingIndices } = params

  if (filteredMatchingIndices && filteredMatchingIndices.length > 0) {
    const pageOffset = (page - 1) * limit
    const indexInMatching = pageOffset + displayRowIndex
    if (indexInMatching < filteredMatchingIndices.length) {
      return filteredMatchingIndices[indexInMatching]
    }
  }

  return (page - 1) * limit + displayRowIndex
}

describe('resolveAbsoluteRowIndex', () => {
  describe('without filters (no filteredMatchingIndices)', () => {
    it('computes absolute index using arithmetic offset on page 1', () => {
      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 1, limit: 10, filteredMatchingIndices: null,
      })).toBe(0)

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 5, page: 1, limit: 10, filteredMatchingIndices: null,
      })).toBe(5)
    })

    it('computes absolute index using arithmetic offset on page 2', () => {
      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 2, limit: 10, filteredMatchingIndices: null,
      })).toBe(10)

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 3, page: 2, limit: 10, filteredMatchingIndices: null,
      })).toBe(13)
    })

    it('computes absolute index with different limit values', () => {
      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 3, limit: 25, filteredMatchingIndices: null,
      })).toBe(50)

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 7, page: 1, limit: 100, filteredMatchingIndices: null,
      })).toBe(7)
    })
  })

  describe('with filters (filteredMatchingIndices present)', () => {
    it('maps display position 0 to the first matching original index', () => {
      // Dataset has 100 rows; filter matches rows at original indices [17, 24, 26, 27, 44, 50]
      const matchingIndices = [17, 24, 26, 27, 44, 50]

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(17)
    })

    it('maps display position 3 to the fourth matching original index', () => {
      const matchingIndices = [17, 24, 26, 27, 44, 50]

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 3, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(27)
    })

    it('maps all display positions correctly for a filtered view', () => {
      const matchingIndices = [17, 24, 26, 27, 44, 50]

      const expected = [17, 24, 26, 27, 44, 50]
      for (let i = 0; i < matchingIndices.length; i++) {
        expect(resolveAbsoluteRowIndex({
          displayRowIndex: i, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
        })).toBe(expected[i])
      }
    })

    it('handles pagination: page 2 with filtered results', () => {
      // 15 matching rows, limit 10 → page 1 has display 0-9, page 2 has display 0-4
      const matchingIndices = [2, 5, 8, 15, 23, 42, 67, 89, 91, 95, 96, 97, 98, 99, 100]

      // Page 2, display position 0 → matchingIndices[10] = 96
      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 2, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(96)

      // Page 2, display position 4 → matchingIndices[14] = 100
      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 4, page: 2, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(100)
    })

    it('handles sparse matching indices (non-contiguous rows)', () => {
      // Filter matches only rows at indices 0, 50, 99 in a 100-row dataset
      const matchingIndices = [0, 50, 99]

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(0)

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 1, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(50)

      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 2, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(99)
    })

    it('falls back to arithmetic when displayRowIndex exceeds matching indices', () => {
      // Edge case: if somehow the display row exceeds the matching indices array
      const matchingIndices = [5, 10]

      // displayRowIndex=2 with page=1, limit=10 → indexInMatching=2 >= length=2
      // Falls back to arithmetic: (1-1)*10 + 2 = 2
      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 2, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })).toBe(2)
    })

    it('handles empty matching indices array by falling back to arithmetic', () => {
      expect(resolveAbsoluteRowIndex({
        displayRowIndex: 5, page: 1, limit: 10, filteredMatchingIndices: [],
      })).toBe(5)
    })
  })

  describe('regression: the original bug scenario', () => {
    it('BUG: arithmetic calculation gives wrong index for filtered data', () => {
      // Scenario: dataset with 51 rows, filter matches 6 rows at indices [17, 24, 26, 27, 44, 50]
      const matchingIndices = [17, 24, 26, 27, 44, 50]

      // User double-clicks the first visible row (display position 0)
      // OLD (buggy) calculation: (1-1)*10 + 0 = 0 → updates row 0 (WRONG!)
      const buggyResult = (1 - 1) * 10 + 0
      expect(buggyResult).toBe(0) // This is WRONG - row 0 is not even in the filtered results

      // NEW (fixed) calculation: matchingIndices[0] = 17 → updates row 17 (CORRECT!)
      const fixedResult = resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })
      expect(fixedResult).toBe(17) // This is CORRECT
      expect(fixedResult).not.toBe(buggyResult) // Proves the fix changes behavior
    })

    it('BUG: clicking 4th filtered row updates wrong row with arithmetic', () => {
      const matchingIndices = [17, 24, 26, 27, 44, 50]

      // User clicks display position 3 (which shows original row 27)
      // OLD: (1-1)*10 + 3 = 3 → updates row 3 (WRONG - that's a completely different row)
      const buggyResult = (1 - 1) * 10 + 3
      expect(buggyResult).toBe(3)

      // NEW: matchingIndices[3] = 27 → updates row 27 (CORRECT)
      const fixedResult = resolveAbsoluteRowIndex({
        displayRowIndex: 3, page: 1, limit: 10, filteredMatchingIndices: matchingIndices,
      })
      expect(fixedResult).toBe(27)
      expect(fixedResult).not.toBe(buggyResult)
    })

    it('verifies that without filters, arithmetic is still correct', () => {
      // Without filters, data is contiguous, so arithmetic is correct
      // Display position 5 on page 1 with limit 10 → row 5
      const result = resolveAbsoluteRowIndex({
        displayRowIndex: 5, page: 1, limit: 10, filteredMatchingIndices: null,
      })
      expect(result).toBe(5)

      // Display position 0 on page 2 with limit 10 → row 10
      const result2 = resolveAbsoluteRowIndex({
        displayRowIndex: 0, page: 2, limit: 10, filteredMatchingIndices: null,
      })
      expect(result2).toBe(10)
    })
  })
})

