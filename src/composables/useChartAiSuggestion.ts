/**
 * AI-assisted chart suggestion composable.
 * Sends dataset context + column metadata to an AI agent via /api/ai/chat,
 * parses the structured JSON response into a chart configuration.
 */

import { ref } from 'vue'
import type { ChartType } from './useChartConfig'
import type { ColumnMeta } from './useColumnTypes'
import { getApiUrl } from '@/utils/api'

const VALID_CHART_TYPES: ChartType[] = ['bar', 'line', 'pie', 'scatter', 'histogram', 'area']
const VALID_AGGREGATIONS = ['sum', 'avg', 'count', 'min', 'max']
const VALID_PALETTES = ['default', 'pastel', 'vivid', 'cool', 'warm']

/** Human-readable labels for chart types. */
export const CHART_TYPE_LABELS: Record<ChartType, string> = {
  bar: 'Bar Chart',
  line: 'Line Chart',
  pie: 'Pie Chart',
  scatter: 'Scatter Plot',
  histogram: 'Histogram',
  area: 'Area Chart',
}

export interface AiChartConfig {
  chartType: ChartType
  xAxis: string
  yAxis: string
  groupBy: string
  aggregation: string
  title: string
  showLegend: boolean
  showGrid: boolean
  colorPalette: string
  explanation: string
}

export interface AiSuggestionResult {
  config: AiChartConfig | null
  explanation: string
}

export interface ValidateResult {
  valid: boolean
  config?: AiChartConfig
  error?: string
}

/**
 * Build the prompt message to send to the AI agent for chart suggestion.
 */
export function buildChartSuggestionPrompt(
  columnMeta: ColumnMeta[],
  selectedColumns: string[] = [],
  customInstruction?: string,
): string {
  const columnDescriptions = columnMeta.map((col) => {
    const parts = [`  - ${col.name} (type: ${col.columnType}, dtype: ${col.dtype})`]
    if (col.uniqueCount > 0) parts.push(`, unique: ${col.uniqueCount}`)
    if (col.nullCount > 0) parts.push(`, nulls: ${col.nullCount}`)
    return parts.join('')
  })

  let prompt = `I need you to suggest the best chart configuration for visualizing this dataset.\n\n`

  prompt += `Available columns:\n${columnDescriptions.join('\n')}\n\n`

  if (selectedColumns.length > 0) {
    prompt += `The user has selected these columns for visualization: ${selectedColumns.join(', ')}.\n`
    prompt += `Prefer using these columns in the chart if appropriate.\n\n`
  }

  prompt += `Return ONLY a JSON block with this exact structure:\n`
  prompt += `{
  "chartType": "<bar|line|pie|scatter|histogram|area>",
  "xAxis": "<column name>",
  "yAxis": "<column name or empty string for histogram>",
  "groupBy": "<column name or empty string>",
  "aggregation": "<sum|avg|count|min|max>",
  "title": "<descriptive chart title>",
  "showLegend": true,
  "showGrid": true,
  "colorPalette": "<default|pastel|vivid|cool|warm>",
  "explanation": "<1-3 sentences explaining why this chart is recommended>"
}\n\n`

  prompt += `Rules:\n`
  prompt += `- chartType must be one of: bar, line, pie, scatter, histogram, area\n`
  prompt += `- xAxis must be an existing column name\n`
  prompt += `- yAxis must be an existing numeric column (empty string for histogram)\n`
  prompt += `- aggregation is required for bar, line, pie, and area (not for scatter/histogram)\n`
  prompt += `- Choose the chart type that best reveals patterns in this data\n`
  prompt += `- Consider column types: numeric for Y axis, categorical/datetime for X axis\n`
  prompt += `- Return ONLY the JSON block, no other text outside the JSON\n`

  if (customInstruction) {
    prompt += `\nAdditional user instruction: ${customInstruction}\n`
  }

  return prompt
}

/**
 * Parse the AI response text to extract a chart configuration JSON block.
 * Handles: plain JSON, markdown code fences (```json or ```), mixed text+JSON.
 */
export function parseAiChartResponse(responseText: string): AiChartConfig | null {
  if (!responseText || typeof responseText !== 'string') return null

  // Try to extract JSON from markdown code fences first
  const fenceRegex = /```(?:json)?\s*\n?([\s\S]*?)\n?\s*```/
  const fenceMatch = responseText.match(fenceRegex)
  if (fenceMatch) {
    try {
      const parsed = JSON.parse(fenceMatch[1].trim())
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        return parsed as AiChartConfig
      }
    } catch {
      // Fall through to other strategies
    }
  }

  // Try to find raw JSON object in the text
  const jsonRegex = /\{[\s\S]*\}/
  const jsonMatch = responseText.match(jsonRegex)
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[0])
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        return parsed as AiChartConfig
      }
    } catch {
      // Not valid JSON
    }
  }

  return null
}

/**
 * Validate and normalize a parsed chart configuration.
 */
export function validateChartConfig(raw: any): ValidateResult {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    return { valid: false, error: 'Invalid input: expected a JSON object.' }
  }

  // Validate chartType
  if (!raw.chartType || !VALID_CHART_TYPES.includes(raw.chartType)) {
    return {
      valid: false,
      error: `Invalid chartType "${raw.chartType}". Must be one of: ${VALID_CHART_TYPES.join(', ')}.`,
    }
  }

  // Validate xAxis
  if (!raw.xAxis || typeof raw.xAxis !== 'string' || raw.xAxis.trim() === '') {
    return { valid: false, error: 'xAxis is required and must be a non-empty column name.' }
  }

  // Build validated config with defaults
  const config: AiChartConfig = {
    chartType: raw.chartType,
    yAxis: raw.yAxis || '',
    xAxis: raw.xAxis,
    groupBy: raw.groupBy || '',
    aggregation: VALID_AGGREGATIONS.includes(raw.aggregation) ? raw.aggregation : 'sum',
    title: raw.title || '',
    showLegend: typeof raw.showLegend === 'boolean' ? raw.showLegend : true,
    showGrid: typeof raw.showGrid === 'boolean' ? raw.showGrid : true,
    colorPalette: VALID_PALETTES.includes(raw.colorPalette) ? raw.colorPalette : 'default',
    explanation: raw.explanation || '',
  }

  return { valid: true, config }
}

export interface RequestSuggestionParams {
  agentId: string | null
  datasetId: string
  columnMeta: ColumnMeta[]
  selectedColumns?: string[]
  customInstruction?: string
  contextRows?: number
}

/**
 * Composable for AI-assisted chart suggestion.
 */
export function useChartAiSuggestion() {
  const loading = ref(false)
  const result = ref<AiSuggestionResult | null>(null)
  const error = ref('')

  function clearResult() {
    result.value = null
    error.value = ''
  }

  async function requestAiSuggestion(params: RequestSuggestionParams): Promise<void> {
    const { agentId, datasetId, columnMeta, selectedColumns = [], customInstruction, contextRows = 15 } = params

    // Validation
    if (!agentId) {
      error.value = 'Please select an AI agent first.'
      return
    }
    if (!datasetId) {
      error.value = 'No dataset loaded. Please open a dataset first.'
      return
    }

    loading.value = true
    error.value = ''
    result.value = null

    try {
      const message = buildChartSuggestionPrompt(columnMeta, selectedColumns, customInstruction)

      const apiUrl = getApiUrl()
      const token = localStorage.getItem('token')

      const res = await fetch(`${apiUrl}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          agent_id: agentId,
          message,
          dataset_id: datasetId,
          dataset_context_rows: contextRows,
        }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'AI request failed' }))
        throw new Error(errData.detail || 'AI request failed')
      }

      const data = await res.json()
      const responseText = data.response || ''

      // Parse the AI response
      const parsed = parseAiChartResponse(responseText)
      if (!parsed) {
        throw new Error(
          'Could not parse chart configuration from AI response. The AI may not have returned valid JSON.',
        )
      }

      // Validate the config
      const validation = validateChartConfig(parsed)
      if (!validation.valid) {
        throw new Error(`Invalid AI suggestion: ${validation.error}`)
      }

      result.value = {
        config: validation.config!,
        explanation: validation.config!.explanation || '',
      }
    } catch (e: any) {
      error.value = e.message || 'An unexpected error occurred'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    result,
    error,
    clearResult,
    requestAiSuggestion,
  }
}