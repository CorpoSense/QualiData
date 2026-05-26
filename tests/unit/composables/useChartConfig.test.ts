import { describe, it, expect } from 'vitest'
import { aggregateData, applyAgg, computeHistogramBins, useChartConfig, COLOR_PALETTES, CHART_TYPE_OPTIONS, AGGREGATION_OPTIONS, transformServerChartData } from '@/composables/useChartConfig'

describe('applyAgg', () => {
  it('sums values', () => {
    expect(applyAgg([1, 2, 3, 4], 'sum')).toBe(10)
  })

  it('averages values', () => {
    expect(applyAgg([1, 2, 3, 4], 'avg')).toBe(2.5)
  })

  it('counts values', () => {
    expect(applyAgg([1, 2, 3, 4], 'count')).toBe(4)
  })

  it('finds min', () => {
    expect(applyAgg([5, 2, 8, 1], 'min')).toBe(1)
  })

  it('finds max', () => {
    expect(applyAgg([5, 2, 8, 1], 'max')).toBe(8)
  })

  it('returns 0 for empty array', () => {
    expect(applyAgg([], 'sum')).toBe(0)
    expect(applyAgg([], 'avg')).toBe(0)
    expect(applyAgg([], 'count')).toBe(0)
    expect(applyAgg([], 'min')).toBe(0)
    expect(applyAgg([], 'max')).toBe(0)
  })
})

describe('aggregateData', () => {
  const sampleData = [
    { city: 'NYC', revenue: 100, category: 'A' },
    { city: 'NYC', revenue: 200, category: 'B' },
    { city: 'LA', revenue: 150, category: 'A' },
    { city: 'LA', revenue: 50, category: 'B' },
    { city: 'Chicago', revenue: 300, category: 'A' },
  ]

  it('returns empty result for empty data', () => {
    const result = aggregateData([], 'city', 'revenue', 'sum')
    expect(result.labels).toEqual([])
    expect(result.datasets).toHaveLength(1)
    expect(result.datasets[0].data).toEqual([])
  })

  it('returns empty result when xColumn is empty', () => {
    const result = aggregateData(sampleData, '', 'revenue', 'sum')
    expect(result.labels).toEqual([])
  })

  it('aggregates with sum', () => {
    const result = aggregateData(sampleData, 'city', 'revenue', 'sum')
    expect(result.labels).toContain('NYC')
    expect(result.labels).toContain('LA')
    expect(result.labels).toContain('Chicago')
    const nycIdx = result.labels.indexOf('NYC')
    const laIdx = result.labels.indexOf('LA')
    const chiIdx = result.labels.indexOf('Chicago')
    expect(result.datasets[0].data[nycIdx]).toBe(300) // 100 + 200
    expect(result.datasets[0].data[laIdx]).toBe(200) // 150 + 50
    expect(result.datasets[0].data[chiIdx]).toBe(300)
  })

  it('aggregates with avg', () => {
    const result = aggregateData(sampleData, 'city', 'revenue', 'avg')
    const nycIdx = result.labels.indexOf('NYC')
    expect(result.datasets[0].data[nycIdx]).toBe(150) // (100+200)/2
  })

  it('aggregates with count', () => {
    const result = aggregateData(sampleData, 'city', 'revenue', 'count')
    const nycIdx = result.labels.indexOf('NYC')
    expect(result.datasets[0].data[nycIdx]).toBe(2)
  })

  it('aggregates with min', () => {
    const result = aggregateData(sampleData, 'city', 'revenue', 'min')
    const nycIdx = result.labels.indexOf('NYC')
    expect(result.datasets[0].data[nycIdx]).toBe(100)
  })

  it('aggregates with max', () => {
    const result = aggregateData(sampleData, 'city', 'revenue', 'max')
    const nycIdx = result.labels.indexOf('NYC')
    expect(result.datasets[0].data[nycIdx]).toBe(200)
  })

  it('counts without yColumn', () => {
    const result = aggregateData(sampleData, 'city', '', 'count')
    const nycIdx = result.labels.indexOf('NYC')
    expect(result.datasets[0].data[nycIdx]).toBe(2)
  })

  it('handles grouped aggregation', () => {
    const result = aggregateData(sampleData, 'city', 'revenue', 'sum', 'category')
    expect(result.datasets.length).toBe(2) // A and B
    const catADataset = result.datasets.find(ds => ds.label === 'A')
    const catBDataset = result.datasets.find(ds => ds.label === 'B')
    expect(catADataset).toBeDefined()
    expect(catBDataset).toBeDefined()
  })

  it('handles null values in data', () => {
    const dataWithNulls = [
      { city: 'NYC', revenue: 100 },
      { city: 'NYC', revenue: null },
      { city: 'LA', revenue: 200 },
    ]
    const result = aggregateData(dataWithNulls, 'city', 'revenue', 'sum')
    const nycIdx = result.labels.indexOf('NYC')
    // null becomes NaN which is skipped
    expect(result.datasets[0].data[nycIdx]).toBe(100)
  })
})

describe('computeHistogramBins', () => {
  it('returns empty for empty data', () => {
    const result = computeHistogramBins([], 'age')
    expect(result.labels).toEqual([])
    expect(result.data).toEqual([])
  })

  it('returns empty for missing column', () => {
    const result = computeHistogramBins([{ name: 'Alice' }], 'age')
    expect(result.labels).toEqual([])
    expect(result.data).toEqual([])
  })

  it('computes histogram bins correctly', () => {
    const data = [
      { age: 10 }, { age: 15 }, { age: 20 }, { age: 25 }, { age: 30 },
    ]
    const result = computeHistogramBins(data, 'age', 5)
    expect(result.labels).toHaveLength(5)
    expect(result.data).toHaveLength(5)
    // Total count should equal data length
    const total = result.data.reduce((a, b) => a + b, 0)
    expect(total).toBe(5)
  })

  it('handles single value data', () => {
    const data = [{ age: 25 }, { age: 25 }, { age: 25 }]
    const result = computeHistogramBins(data, 'age', 5)
    const total = result.data.reduce((a, b) => a + b, 0)
    expect(total).toBe(3)
  })

  it('filters out NaN values', () => {
    const data = [{ age: 10 }, { age: NaN }, { age: 20 }]
    const result = computeHistogramBins(data, 'age', 5)
    const total = result.data.reduce((a, b) => a + b, 0)
    expect(total).toBe(2)
  })
})

describe('useChartConfig', () => {
  it('initializes with default config', () => {
    const { config } = useChartConfig()
    expect(config.value.chartType).toBe('bar')
    expect(config.value.xAxis).toBe('')
    expect(config.value.yAxis).toBe('')
    expect(config.value.aggregation).toBe('sum')
    expect(config.value.showLegend).toBe(true)
    expect(config.value.showGrid).toBe(true)
  })

  it('resets config to defaults', () => {
    const { config, resetConfig } = useChartConfig()
    config.value.chartType = 'scatter'
    config.value.xAxis = 'test'
    resetConfig()
    expect(config.value.chartType).toBe('bar')
    expect(config.value.xAxis).toBe('')
  })

  it('sets preset for histogram', () => {
    const { config, setPreset } = useChartConfig()
    setPreset('histogram', 'age')
    expect(config.value.chartType).toBe('histogram')
    expect(config.value.xAxis).toBe('age')
    expect(config.value.yAxis).toBe('')
    expect(config.value.groupBy).toBe('')
  })

  it('sets preset for scatter', () => {
    const { config, setPreset } = useChartConfig()
    setPreset('scatter', 'x_col', 'y_col')
    expect(config.value.chartType).toBe('scatter')
    expect(config.value.xAxis).toBe('x_col')
    expect(config.value.yAxis).toBe('y_col')
    expect(config.value.groupBy).toBe('')
  })

  it('sets preset for pie', () => {
    const { config, setPreset } = useChartConfig()
    setPreset('pie', 'category', 'value')
    expect(config.value.chartType).toBe('pie')
    expect(config.value.groupBy).toBe('')
  })

  it('filters nulls when nullHandling is exclude', () => {
    const { config, filterNulls } = useChartConfig()
    config.value.nullHandling = 'exclude'
    const data = [
      { a: 1, b: 'x' },
      { a: null, b: 'y' },
      { a: 3, b: '' },
    ]
    const result = filterNulls(data, ['a', 'b'])
    expect(result).toHaveLength(1)
    expect(result[0].a).toBe(1)
  })

  it('does not filter nulls when nullHandling is not exclude', () => {
    const { config, filterNulls } = useChartConfig()
    config.value.nullHandling = 'zero'
    const data = [
      { a: 1, b: 'x' },
      { a: null, b: 'y' },
    ]
    const result = filterNulls(data, ['a', 'b'])
    expect(result).toHaveLength(2)
  })

  it('computeChartData returns empty result for empty data', () => {
    const { config, computeChartData } = useChartConfig()
    config.value.xAxis = 'test'
    const result = computeChartData([], [])
    // Returns empty chart data object, not null (the composable handles empty data gracefully)
    expect(result).toBeTruthy()
    expect(result.labels).toEqual([])
  })

  it('computeChartData returns empty result when xAxis is not set', () => {
    const { computeChartData } = useChartConfig()
    const result = computeChartData([{ a: 1 }], [])
    // Returns empty chart data object when xAxis is empty
    expect(result).toBeTruthy()
    expect(result.labels).toEqual([])
  })

  it('computeChartOptions returns responsive options', () => {
    const { computeChartOptions } = useChartConfig()
    const options = computeChartOptions()
    expect(options.responsive).toBe(true)
    expect(options.maintainAspectRatio).toBe(false)
  })
})

describe('Constants', () => {
  it('CHART_TYPE_OPTIONS has 6 types', () => {
    expect(CHART_TYPE_OPTIONS).toHaveLength(6)
  })

  it('AGGREGATION_OPTIONS has 5 methods', () => {
    expect(AGGREGATION_OPTIONS).toHaveLength(5)
  })

  it('COLOR_PALETTES has 5 palettes', () => {
    expect(Object.keys(COLOR_PALETTES)).toHaveLength(5)
  })

  it('each palette has at least 5 colors', () => {
    for (const [name, colors] of Object.entries(COLOR_PALETTES)) {
      expect(colors.length).toBeGreaterThanOrEqual(5)
      expect(name).not.toBeNull();
    }
  })
})

describe('transformServerChartData', () => {
  it('transforms bar chart server data', () => {
    const serverData = {
      chart_type: 'bar',
      labels: ['NYC', 'LA', 'Chicago'],
      datasets: [{ label: 'Sum of revenue', data: [300, 200, 300] }],
    }
    const result = transformServerChartData(serverData)
    expect(result.labels).toEqual(['NYC', 'LA', 'Chicago'])
    expect(result.datasets).toHaveLength(1)
    expect(result.datasets[0].data).toEqual([300, 200, 300])
    expect(result.datasets[0].backgroundColor).toBeDefined()
    expect(result.datasets[0].borderColor).toBeDefined()
  })

  it('transforms pie chart server data with per-label colors', () => {
    const serverData = {
      chart_type: 'pie',
      labels: ['A', 'B', 'C'],
      datasets: [{ label: 'Values', data: [10, 20, 30] }],
    }
    const result = transformServerChartData(serverData)
    expect(result.datasets[0].backgroundColor).toHaveLength(3)
    expect(result.datasets[0].borderColor).toHaveLength(3)
  })

  it('transforms scatter chart server data', () => {
    const serverData = {
      chart_type: 'scatter',
      labels: [],
      datasets: [{ label: 'x vs y', data: [{ x: 1, y: 10 }, { x: 2, y: 20 }] }],
    }
    const result = transformServerChartData(serverData)
    expect(result.datasets[0].data).toHaveLength(2)
  })

  it('transforms area chart with fill origin', () => {
    const serverData = {
      chart_type: 'area',
      labels: ['Jan', 'Feb', 'Mar'],
      datasets: [{ label: 'Sales', data: [100, 200, 150] }],
    }
    const result = transformServerChartData(serverData)
    expect((result.datasets[0] as any).fill).toBe('origin')
    expect((result.datasets[0] as any).tension).toBe(0.3)
  })

  it('transforms grouped datasets with different colors', () => {
    const serverData = {
      chart_type: 'bar',
      labels: ['NYC', 'LA'],
      datasets: [
        { label: 'A', data: [100, 200] },
        { label: 'B', data: [50, 75] },
      ],
    }
    const result = transformServerChartData(serverData)
    expect(result.datasets).toHaveLength(2)
    expect(result.datasets[0].backgroundColor).not.toBe(result.datasets[1].backgroundColor)
  })

  it('uses default palette when invalid palette specified', () => {
    const serverData = {
      chart_type: 'bar',
      labels: ['A'],
      datasets: [{ label: 'Test', data: [1] }],
    }
    const result = transformServerChartData(serverData, 'nonexistent')
    expect(result.datasets[0].backgroundColor).toBeDefined()
  })
})
