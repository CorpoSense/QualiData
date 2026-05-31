import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  buildChartSuggestionPrompt,
  parseAiChartResponse,
  validateChartConfig,
  useChartAiSuggestion,
} from '@/composables/useChartAiSuggestion'
import type { ColumnMeta } from '@/composables/useColumnTypes'
import type { ChartType } from '@/composables/useChartConfig'

// Helper to create ColumnMeta objects
function makeCol(
  name: string,
  columnType: ColumnMeta['columnType'],
  uniqueCount = 10,
  nullCount = 0,
): ColumnMeta {
  return { name, dtype: '', uniqueCount, nullCount, columnType }
}

describe('buildChartSuggestionPrompt', () => {
  const cols: ColumnMeta[] = [
    makeCol('city', 'categorical', 5),
    makeCol('revenue', 'numeric'),
    makeCol('date', 'datetime'),
  ]

  it('returns a string containing all column names', () => {
    const prompt = buildChartSuggestionPrompt(cols)
    expect(prompt).toContain('city')
    expect(prompt).toContain('revenue')
    expect(prompt).toContain('date')
  })

  it('includes column type information', () => {
    const prompt = buildChartSuggestionPrompt(cols)
    expect(prompt).toContain('categorical')
    expect(prompt).toContain('numeric')
    expect(prompt).toContain('datetime')
  })

  it('includes selected columns info when provided', () => {
    const prompt = buildChartSuggestionPrompt(cols, ['city', 'revenue'])
    expect(prompt).toContain('city')
    expect(prompt).toContain('revenue')
    expect(prompt).toContain('selected')
  })

  it('includes JSON structure instructions', () => {
    const prompt = buildChartSuggestionPrompt(cols)
    expect(prompt).toContain('chartType')
    expect(prompt).toContain('xAxis')
    expect(prompt).toContain('yAxis')
    expect(prompt).toContain('JSON')
  })

  it('includes aggregation methods in prompt', () => {
    const prompt = buildChartSuggestionPrompt(cols)
    expect(prompt).toContain('sum')
    expect(prompt).toContain('avg')
    expect(prompt).toContain('count')
  })

  it('handles empty column meta', () => {
    const prompt = buildChartSuggestionPrompt([])
    expect(prompt).toContain('chartType')
    expect(typeof prompt).toBe('string')
  })

  it('includes custom instruction when provided', () => {
    const prompt = buildChartSuggestionPrompt(cols, [], 'Show top 5 cities')
    expect(prompt).toContain('Show top 5 cities')
  })
})

describe('parseAiChartResponse', () => {
  const validJson = JSON.stringify({
    chartType: 'bar',
    xAxis: 'city',
    yAxis: 'revenue',
    groupBy: '',
    aggregation: 'sum',
    title: 'Revenue by City',
    showLegend: true,
    showGrid: true,
    colorPalette: 'default',
    explanation: 'Bar chart showing total revenue per city.',
  })

  it('extracts plain JSON', () => {
    const result = parseAiChartResponse(validJson)
    expect(result).not.toBeNull()
    expect(result!.chartType).toBe('bar')
    expect(result!.xAxis).toBe('city')
    expect(result!.yAxis).toBe('revenue')
  })

  it('extracts JSON from markdown code fence', () => {
    const response = `Here is the suggested chart:\n\`\`\`json\n${validJson}\n\`\`\`\nLet me know if you need changes.`
    const result = parseAiChartResponse(response)
    expect(result).not.toBeNull()
    expect(result!.chartType).toBe('bar')
    expect(result!.xAxis).toBe('city')
  })

  it('extracts JSON from generic code fence', () => {
    const response = `Sure!\n\`\`\`\n${validJson}\n\`\`\``
    const result = parseAiChartResponse(response)
    expect(result).not.toBeNull()
    expect(result!.chartType).toBe('bar')
  })

  it('extracts JSON with extra text around it', () => {
    const response = `I recommend this chart configuration:\n${validJson}\nThis should work well.`
    const result = parseAiChartResponse(response)
    expect(result).not.toBeNull()
    expect(result!.chartType).toBe('bar')
  })

  it('returns null for non-JSON response', () => {
    const result = parseAiChartResponse('I cannot suggest a chart for this data.')
    expect(result).toBeNull()
  })

  it('returns null for empty string', () => {
    const result = parseAiChartResponse('')
    expect(result).toBeNull()
  })

  it('returns null for array instead of object', () => {
    const result = parseAiChartResponse('[1, 2, 3]')
    expect(result).toBeNull()
  })

  it('extracts JSON wrapped in markdown with leading/trailing text', () => {
    const response = `Based on the data analysis, I suggest:\n\n\`\`\`json\n${validJson}\n\`\`\`\n\nThis visualization highlights the key trends.`
    const result = parseAiChartResponse(response)
    expect(result).not.toBeNull()
    expect(result!.chartType).toBe('bar')
    expect(result!.title).toBe('Revenue by City')
  })

  it('handles JSON with explanation field', () => {
    const result = parseAiChartResponse(validJson)
    expect(result).not.toBeNull()
    expect(result!.explanation).toBe('Bar chart showing total revenue per city.')
  })
})

describe('validateChartConfig', () => {
  const validConfig = {
    chartType: 'bar',
    xAxis: 'city',
    yAxis: 'revenue',
    groupBy: '',
    aggregation: 'sum',
    title: 'Revenue by City',
    showLegend: true,
    showGrid: true,
    colorPalette: 'default',
  }

  it('accepts a valid config', () => {
    const result = validateChartConfig(validConfig)
    expect(result.valid).toBe(true)
    expect(result.config).toBeDefined()
    expect(result.config!.chartType).toBe('bar')
  })

  it('rejects invalid chartType', () => {
    const result = validateChartConfig({ ...validConfig, chartType: 'waterfall' })
    expect(result.valid).toBe(false)
    expect(result.error).toContain('chartType')
  })

  it('rejects missing xAxis', () => {
    const result = validateChartConfig({ ...validConfig, xAxis: '' })
    expect(result.valid).toBe(false)
    expect(result.error).toContain('xAxis')
  })

  it('rejects missing xAxis (undefined)', () => {
    const config = { ...validConfig }
    delete (config as any).xAxis
    const result = validateChartConfig(config)
    expect(result.valid).toBe(false)
    expect(result.error).toContain('xAxis')
  })

  it('accepts all valid chart types', () => {
    const types: ChartType[] = ['bar', 'line', 'pie', 'scatter', 'histogram', 'area']
    for (const t of types) {
      const config = { ...validConfig, chartType: t }
      if (t === 'histogram') {
        config.yAxis = ''
      }
      const result = validateChartConfig(config)
      expect(result.valid).toBe(true)
    }
  })

  it('applies defaults for missing optional fields', () => {
    const minimal = {
      chartType: 'bar',
      xAxis: 'city',
      yAxis: 'revenue',
    }
    const result = validateChartConfig(minimal)
    expect(result.valid).toBe(true)
    expect(result.config!.aggregation).toBe('sum')
    expect(result.config!.showLegend).toBe(true)
    expect(result.config!.showGrid).toBe(true)
    expect(result.config!.colorPalette).toBe('default')
    expect(result.config!.title).toBe('')
  })

  it('rejects null input', () => {
    const result = validateChartConfig(null)
    expect(result.valid).toBe(false)
  })

  it('rejects non-object input', () => {
    const result = validateChartConfig('not an object')
    expect(result.valid).toBe(false)
  })
})

describe('useChartAiSuggestion', () => {
  let composable: ReturnType<typeof useChartAiSuggestion>

  beforeEach(() => {
    composable = useChartAiSuggestion()
  })

  it('initializes with loading=false and no result', () => {
    expect(composable.loading.value).toBe(false)
    expect(composable.result.value).toBeNull()
    expect(composable.error.value).toBe('')
  })

  it('clears previous result and error', () => {
    composable.error.value = 'previous error'
    composable.clearResult()
    expect(composable.result.value).toBeNull()
    expect(composable.error.value).toBe('')
  })

  it('requestAiSuggestion returns error when no agent selected', async () => {
    await composable.requestAiSuggestion({
      agentId: null as any,
      datasetId: 'ds-1',
      columnMeta: [makeCol('city', 'categorical')],
    })
    expect(composable.error.value).toContain('agent')
    expect(composable.loading.value).toBe(false)
  })

  it('requestAiSuggestion returns error when no datasetId', async () => {
    await composable.requestAiSuggestion({
      agentId: 'agent-1',
      datasetId: '',
      columnMeta: [makeCol('city', 'categorical')],
    })
    expect(composable.error.value).toContain('dataset')
    expect(composable.loading.value).toBe(false)
  })

  it('requestAiSuggestion calls API and parses response', async () => {
    const mockConfig = {
      chartType: 'bar',
      xAxis: 'city',
      yAxis: 'revenue',
      aggregation: 'sum',
      title: 'Revenue by City',
      explanation: 'Bar chart showing revenue per city.',
    }

    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: `Here is my suggestion:\n\`\`\`json\n${JSON.stringify(mockConfig)}\n\`\`\``,
        provider: 'openai',
        model: 'gpt-4',
      }),
    } as Response)

    await composable.requestAiSuggestion({
      agentId: 'agent-1',
      datasetId: 'ds-1',
      columnMeta: [makeCol('city', 'categorical'), makeCol('revenue', 'numeric')],
    })

    expect(fetchSpy).toHaveBeenCalled()
    expect(composable.loading.value).toBe(false)
    expect(composable.result.value).not.toBeNull()
    expect(composable.result.value!.config.chartType).toBe('bar')
    expect(composable.result.value!.config.xAxis).toBe('city')
    expect(composable.result.value!.explanation).toContain('revenue')

    fetchSpy.mockRestore()
  })

  it('requestAiSuggestion handles API failure', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Agent not found' }),
    } as Response)

    await composable.requestAiSuggestion({
      agentId: 'bad-agent',
      datasetId: 'ds-1',
      columnMeta: [makeCol('city', 'categorical')],
    })

    expect(composable.error.value).toContain('Agent not found')
    expect(composable.loading.value).toBe(false)

    fetchSpy.mockRestore()
  })

  it('requestAiSuggestion handles invalid AI response (no JSON)', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'I cannot suggest a chart for this data.',
        provider: 'openai',
        model: 'gpt-4',
      }),
    } as Response)

    await composable.requestAiSuggestion({
      agentId: 'agent-1',
      datasetId: 'ds-1',
      columnMeta: [makeCol('city', 'categorical')],
    })

    expect(composable.error.value).toContain('parse')
    expect(composable.loading.value).toBe(false)

    fetchSpy.mockRestore()
  })

  it('requestAiSuggestion handles invalid AI config (bad chartType)', async () => {
    const badConfig = {
      chartType: 'waterfall',
      xAxis: 'city',
      yAxis: 'revenue',
    }

    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: `\`\`\`json\n${JSON.stringify(badConfig)}\n\`\`\``,
        provider: 'openai',
        model: 'gpt-4',
      }),
    } as Response)

    await composable.requestAiSuggestion({
      agentId: 'agent-1',
      datasetId: 'ds-1',
      columnMeta: [makeCol('city', 'categorical'), makeCol('revenue', 'numeric')],
    })

    expect(composable.error.value).toContain('chartType')
    expect(composable.loading.value).toBe(false)

    fetchSpy.mockRestore()
  })

  it('requestAiSuggestion sends custom instruction in message', async () => {
    const mockConfig = {
      chartType: 'pie',
      xAxis: 'city',
      yAxis: 'revenue',
      aggregation: 'sum',
      title: 'Top Cities',
      explanation: 'Pie chart.',
    }

    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: `\`\`\`json\n${JSON.stringify(mockConfig)}\n\`\`\``,
        provider: 'openai',
        model: 'gpt-4',
      }),
    } as Response)

    await composable.requestAiSuggestion({
      agentId: 'agent-1',
      datasetId: 'ds-1',
      columnMeta: [makeCol('city', 'categorical'), makeCol('revenue', 'numeric')],
      customInstruction: 'Show top 5 cities as a pie chart',
    })

    const fetchCall = fetchSpy.mock.calls[0][0] as string
    const fetchBody = JSON.parse((fetchSpy.mock.calls[0][1] as any).body)
    expect(fetchBody.message).toContain('Show top 5 cities as a pie chart')

    fetchSpy.mockRestore()
  })
})