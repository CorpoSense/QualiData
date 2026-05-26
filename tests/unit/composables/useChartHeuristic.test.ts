import { describe, it, expect } from 'vitest'
import { suggestChart, getRecommendedChartTypes, useChartHeuristic } from '@/composables/useChartHeuristic'
import type { ColumnMeta } from '@/composables/useColumnTypes'

// Helper to create ColumnMeta objects
function makeCol(name: string, columnType: ColumnMeta['columnType'], uniqueCount = 10, nullCount = 0): ColumnMeta {
  return { name, dtype: '', uniqueCount, nullCount, columnType }
}

describe('suggestChart', () => {
  it('returns default bar chart for empty column meta', () => {
    const result = suggestChart([])
    expect(result.chartType).toBe('bar')
    expect(result.xAxis).toBe('')
    expect(result.yAxis).toBe('')
  })

  it('suggests scatter for two numeric columns', () => {
    const cols = [makeCol('age', 'numeric'), makeCol('salary', 'numeric')]
    const result = suggestChart(cols)
    expect(result.chartType).toBe('scatter')
    expect(result.xAxis).toBe('age')
    expect(result.yAxis).toBe('salary')
  })

  it('suggests histogram for single numeric column', () => {
    const cols = [makeCol('age', 'numeric')]
    const result = suggestChart(cols)
    expect(result.chartType).toBe('histogram')
    expect(result.xAxis).toBe('age')
    expect(result.yAxis).toBe('')
    expect(result.aggregation).toBe('count')
  })

  it('suggests bar for categorical + numeric columns', () => {
    const cols = [makeCol('city', 'categorical', 5), makeCol('revenue', 'numeric')]
    const result = suggestChart(cols)
    expect(result.chartType).toBe('bar')
    expect(result.xAxis).toBe('city')
    expect(result.yAxis).toBe('revenue')
  })

  it('suggests line for datetime + numeric columns', () => {
    const cols = [makeCol('date', 'datetime'), makeCol('revenue', 'numeric')]
    const result = suggestChart(cols)
    expect(result.chartType).toBe('line')
    expect(result.xAxis).toBe('date')
    expect(result.yAxis).toBe('revenue')
  })

  it('prefers line when both categorical and datetime are available', () => {
    const cols = [
      makeCol('city', 'categorical', 5),
      makeCol('date', 'datetime'),
      makeCol('revenue', 'numeric'),
    ]
    const result = suggestChart(cols, ['city', 'date', 'revenue'])
    expect(result.chartType).toBe('line')
    expect(result.xAxis).toBe('date')
  })

  it('suggests bar with count for only categorical columns', () => {
    const cols = [makeCol('city', 'categorical', 5)]
    const result = suggestChart(cols)
    expect(result.chartType).toBe('bar')
    expect(result.aggregation).toBe('count')
    expect(result.warning).toContain('No numeric column')
  })

  it('suggests histogram for boolean + numeric when no categorical columns (numeric takes priority)', () => {
    const cols = [makeCol('is_active', 'boolean'), makeCol('score', 'numeric')]
    const result = suggestChart(cols, ['is_active', 'score'])
    // The heuristic checks numeric count first, so single numeric → histogram
    expect(result.chartType).toBe('histogram')
    expect(result.xAxis).toBe('score')
  })

  it('uses selected columns when provided', () => {
    const allCols = [
      makeCol('city', 'categorical', 5),
      makeCol('age', 'numeric'),
      makeCol('salary', 'numeric'),
    ]
    // Select only numeric columns → should suggest scatter
    const result = suggestChart(allCols, ['age', 'salary'])
    expect(result.chartType).toBe('scatter')
  })

  it('falls back to first column when no good match', () => {
    const cols = [makeCol('description', 'text', 200)]
    const result = suggestChart(cols)
    expect(result.xAxis).toBe('description')
    expect(result.warning).toContain('No numeric column')
  })

  it('adds warning for scatter with non-numeric selected columns', () => {
    const cols = [makeCol('city', 'categorical', 5), makeCol('name', 'text', 200)]
    const result = suggestChart(cols, ['city', 'name'])
    // Since no numeric columns, it should fall back with a warning
    expect(result.warning).toBeDefined()
  })
})

describe('getRecommendedChartTypes', () => {
  it('recommends bar for categorical + numeric', () => {
    const cols = [makeCol('city', 'categorical', 5), makeCol('revenue', 'numeric')]
    const result = getRecommendedChartTypes(cols)
    const bar = result.find(r => r.type === 'bar')
    expect(bar?.recommended).toBe(true)
  })

  it('recommends line for datetime + numeric', () => {
    const cols = [makeCol('date', 'datetime'), makeCol('revenue', 'numeric')]
    const result = getRecommendedChartTypes(cols)
    const line = result.find(r => r.type === 'line')
    expect(line?.recommended).toBe(true)
  })

  it('recommends scatter for 2+ numeric columns', () => {
    const cols = [makeCol('age', 'numeric'), makeCol('salary', 'numeric')]
    const result = getRecommendedChartTypes(cols)
    const scatter = result.find(r => r.type === 'scatter')
    expect(scatter?.recommended).toBe(true)
  })

  it('recommends histogram for single numeric column', () => {
    const cols = [makeCol('age', 'numeric')]
    const result = getRecommendedChartTypes(cols)
    const histogram = result.find(r => r.type === 'histogram')
    expect(histogram?.recommended).toBe(true)
  })

  it('recommends area for datetime + numeric', () => {
    const cols = [makeCol('date', 'datetime'), makeCol('revenue', 'numeric')]
    const result = getRecommendedChartTypes(cols)
    const area = result.find(r => r.type === 'area')
    expect(area?.recommended).toBe(true)
  })

  it('does not recommend bar when no categorical columns', () => {
    const cols = [makeCol('age', 'numeric'), makeCol('salary', 'numeric')]
    const result = getRecommendedChartTypes(cols)
    const bar = result.find(r => r.type === 'bar')
    expect(bar?.recommended).toBe(false)
  })

  it('does not recommend scatter with only 1 numeric column', () => {
    const cols = [makeCol('age', 'numeric'), makeCol('city', 'categorical', 5)]
    const result = getRecommendedChartTypes(cols)
    const scatter = result.find(r => r.type === 'scatter')
    expect(scatter?.recommended).toBe(false)
  })

  it('returns all 6 chart types', () => {
    const result = getRecommendedChartTypes([])
    expect(result).toHaveLength(6)
  })

  it('uses selected columns when provided', () => {
    const allCols = [
      makeCol('city', 'categorical', 5),
      makeCol('age', 'numeric'),
      makeCol('salary', 'numeric'),
    ]
    // Only select numeric columns
    const result = getRecommendedChartTypes(allCols, ['age', 'salary'])
    const scatter = result.find(r => r.type === 'scatter')
    expect(scatter?.recommended).toBe(true)
    const bar = result.find(r => r.type === 'bar')
    expect(bar?.recommended).toBe(false)
  })

  it('provides reason strings', () => {
    const result = getRecommendedChartTypes([])
    for (const r of result) {
      expect(r.reason).toBeTruthy()
    }
  })
})

describe('useChartHeuristic composable', () => {
  it('exposes suggestChart and getRecommendedChartTypes', () => {
    const { suggestChart, getRecommendedChartTypes } = useChartHeuristic()
    expect(typeof suggestChart).toBe('function')
    expect(typeof getRecommendedChartTypes).toBe('function')
  })
})
