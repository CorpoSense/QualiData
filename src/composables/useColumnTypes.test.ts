import { describe, it, expect } from 'vitest'
import { classifyColumn, useColumnTypes } from './useColumnTypes'

describe('classifyColumn', () => {
  it('classifies int64 as numeric', () => {
    expect(classifyColumn('int64', 100)).toBe('numeric')
  })

  it('classifies float64 as numeric', () => {
    expect(classifyColumn('float64', 100)).toBe('numeric')
  })

  it('classifies int32 as numeric', () => {
    expect(classifyColumn('int32', 50)).toBe('numeric')
  })

  it('classifies datetime as datetime', () => {
    expect(classifyColumn('datetime', 100)).toBe('datetime')
  })

  it('classifies datetime64[ns] as datetime', () => {
    expect(classifyColumn('datetime64[ns]', 100)).toBe('datetime')
  })

  it('classifies boolean as boolean', () => {
    expect(classifyColumn('boolean', 2)).toBe('boolean')
  })

  it('classifies bool as boolean', () => {
    expect(classifyColumn('bool', 2)).toBe('boolean')
  })

  it('classifies string with few unique values as categorical', () => {
    expect(classifyColumn('string', 10)).toBe('categorical')
  })

  it('classifies string with many unique values as text', () => {
    expect(classifyColumn('string', 100)).toBe('text')
  })

  it('classifies object with few unique values as categorical', () => {
    expect(classifyColumn('object', 5)).toBe('categorical')
  })

  it('classifies object with many unique values as text', () => {
    expect(classifyColumn('object', 200)).toBe('text')
  })

  it('uses threshold of 50 for categorical/text boundary', () => {
    expect(classifyColumn('string', 49)).toBe('categorical')
    expect(classifyColumn('string', 50)).toBe('text')
  })

  it('falls back to categorical for unknown dtype with few unique values', () => {
    expect(classifyColumn('category', 10)).toBe('categorical')
  })

  it('falls back to text for unknown dtype with many unique values', () => {
    expect(classifyColumn('category', 100)).toBe('text')
  })
})

describe('useColumnTypes', () => {
  const { classifyColumns, getColumnsByType, getColumnNamesByType, isCompatibleWithAxis } = useColumnTypes()

  const profileColumns = [
    { name: 'age', dtype: 'int64', unique_count: 30, null_count: 0 },
    { name: 'salary', dtype: 'float64', unique_count: 50, null_count: 2 },
    { name: 'city', dtype: 'string', unique_count: 5, null_count: 0 },
    { name: 'description', dtype: 'string', unique_count: 200, null_count: 10 },
    { name: 'created_at', dtype: 'datetime64[ns]', unique_count: 100, null_count: 0 },
    { name: 'is_active', dtype: 'boolean', unique_count: 2, null_count: 0 },
  ]

  describe('classifyColumns', () => {
    it('classifies all columns from profiling data', () => {
      const result = classifyColumns(profileColumns)
      expect(result).toHaveLength(6)
    })

    it('maps profile fields to ColumnMeta fields', () => {
      const result = classifyColumns(profileColumns)
      expect(result[0]).toEqual({
        name: 'age',
        dtype: 'int64',
        uniqueCount: 30,
        nullCount: 0,
        columnType: 'numeric',
      })
    })

    it('returns empty array for null input', () => {
      expect(classifyColumns(null as any)).toEqual([])
    })

    it('returns empty array for undefined input', () => {
      expect(classifyColumns(undefined as any)).toEqual([])
    })

    it('correctly classifies each column type', () => {
      const result = classifyColumns(profileColumns)
      expect(result[0].columnType).toBe('numeric')   // age
      expect(result[1].columnType).toBe('numeric')   // salary
      expect(result[2].columnType).toBe('categorical') // city
      expect(result[3].columnType).toBe('text')       // description
      expect(result[4].columnType).toBe('datetime')   // created_at
      expect(result[5].columnType).toBe('boolean')    // is_active
    })
  })

  describe('getColumnsByType', () => {
    const columnMeta = classifyColumns(profileColumns)

    it('returns only numeric columns', () => {
      const numeric = getColumnsByType(columnMeta, 'numeric')
      expect(numeric).toHaveLength(2)
      expect(numeric.every(c => c.columnType === 'numeric')).toBe(true)
    })

    it('returns only categorical columns', () => {
      const categorical = getColumnsByType(columnMeta, 'categorical')
      expect(categorical).toHaveLength(1)
      expect(categorical[0].name).toBe('city')
    })

    it('returns empty array when no columns match', () => {
      const result = getColumnsByType([], 'numeric')
      expect(result).toEqual([])
    })
  })

  describe('getColumnNamesByType', () => {
    const columnMeta = classifyColumns(profileColumns)

    it('returns column names for numeric type', () => {
      expect(getColumnNamesByType(columnMeta, 'numeric')).toEqual(['age', 'salary'])
    })

    it('returns column names for categorical type', () => {
      expect(getColumnNamesByType(columnMeta, 'categorical')).toEqual(['city'])
    })

    it('returns column names for datetime type', () => {
      expect(getColumnNamesByType(columnMeta, 'datetime')).toEqual(['created_at'])
    })
  })

  describe('isCompatibleWithAxis', () => {
    it('allows categorical, datetime, numeric on X axis', () => {
      expect(isCompatibleWithAxis('categorical', 'x')).toBe(true)
      expect(isCompatibleWithAxis('datetime', 'x')).toBe(true)
      expect(isCompatibleWithAxis('numeric', 'x')).toBe(true)
      expect(isCompatibleWithAxis('boolean', 'x')).toBe(false)
      expect(isCompatibleWithAxis('text', 'x')).toBe(false)
    })

    it('allows only numeric on Y axis', () => {
      expect(isCompatibleWithAxis('numeric', 'y')).toBe(true)
      expect(isCompatibleWithAxis('categorical', 'y')).toBe(false)
      expect(isCompatibleWithAxis('datetime', 'y')).toBe(false)
      expect(isCompatibleWithAxis('boolean', 'y')).toBe(false)
      expect(isCompatibleWithAxis('text', 'y')).toBe(false)
    })

    it('allows categorical and boolean on group axis', () => {
      expect(isCompatibleWithAxis('categorical', 'group')).toBe(true)
      expect(isCompatibleWithAxis('boolean', 'group')).toBe(true)
      expect(isCompatibleWithAxis('numeric', 'group')).toBe(false)
      expect(isCompatibleWithAxis('datetime', 'group')).toBe(false)
      expect(isCompatibleWithAxis('text', 'group')).toBe(false)
    })
  })
})
