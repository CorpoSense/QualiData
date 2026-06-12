/**
 * Smart chart type + axis suggestion composable.
 * Analyzes column types and selected columns to suggest
 * the best chart type and axis mappings.
 */

import type { ColumnMeta } from './useColumnTypes'
import type { ChartType } from './useChartConfig'

export interface ChartSuggestion {
  chartType: ChartType
  xAxis: string
  yAxis: string
  groupBy: string
  aggregation: 'sum' | 'avg' | 'count' | 'min' | 'max'
  warning?: string
}

/**
 * Determine the best chart type and axis mapping from column metadata.
 * @param columnMeta - Classified column metadata
 * @param selectedColumns - Currently selected column names (from DataViewer)
 * @returns Suggested chart configuration
 */
export function suggestChart(
  columnMeta: ColumnMeta[],
  selectedColumns: string[] = [],
): ChartSuggestion {
  const result: ChartSuggestion = {
    chartType: 'bar',
    xAxis: '',
    yAxis: '',
    groupBy: '',
    aggregation: 'sum',
  }

  if (!columnMeta.length) return result

  // Get selected column metadata, or fall back to all columns
  const relevantCols = selectedColumns.length > 0
    ? columnMeta.filter(c => selectedColumns.includes(c.name))
    : columnMeta

  const numericCols = relevantCols.filter(c => c.columnType === 'numeric')
  const categoricalCols = relevantCols.filter(c => c.columnType === 'categorical')
  const datetimeCols = relevantCols.filter(c => c.columnType === 'datetime')
  const booleanCols = relevantCols.filter(c => c.columnType === 'boolean')

  // Also consider all columns for fallback
  const allNumeric = columnMeta.filter(c => c.columnType === 'numeric')
  // Unused
//   const allCategorical = columnMeta.filter(c => c.columnType === 'categorical')
//   const allDatetime = columnMeta.filter(c => c.columnType === 'datetime')

  // Decision logic based on available column types
  if (numericCols.length >= 3 && categoricalCols.length === 0 && datetimeCols.length === 0) {
    // Three numeric columns → Bubble (x, y, size)
    result.chartType = 'bubble'
    result.xAxis = numericCols[0].name
    result.yAxis = numericCols[1].name
    result.aggregation = 'sum'
  } else if (numericCols.length >= 2 && categoricalCols.length === 0 && datetimeCols.length === 0) {
    // Two numeric columns → Scatter
    result.chartType = 'scatter'
    result.xAxis = numericCols[0].name
    result.yAxis = numericCols[1].name
    result.aggregation = 'sum'
  } else if (numericCols.length === 1 && categoricalCols.length === 0 && datetimeCols.length === 0) {
    // Single numeric column → Histogram
    result.chartType = 'histogram'
    result.xAxis = numericCols[0].name
    result.yAxis = ''
    result.aggregation = 'count'
  } else if (categoricalCols.length >= 1 && numericCols.length >= 1) {
    // Categorical + Numeric → Bar (default)
    result.chartType = 'bar'
    result.xAxis = categoricalCols[0].name
    result.yAxis = numericCols[0].name
    result.aggregation = 'sum'

    // If datetime is available, prefer line chart
    if (datetimeCols.length > 0) {
      result.chartType = 'line'
      result.xAxis = datetimeCols[0].name
      result.yAxis = numericCols[0].name
    }

    // If categorical has few unique values and no datetime, suggest pie/doughnut
    if (categoricalCols[0].uniqueCount <= 12 && datetimeCols.length === 0) {
      // Pie/Doughnut are good alternatives but bar is the default
    }
  } else if (datetimeCols.length >= 1 && numericCols.length >= 1) {
    // Datetime + Numeric → Line
    result.chartType = 'line'
    result.xAxis = datetimeCols[0].name
    result.yAxis = numericCols[0].name
    result.aggregation = 'sum'
  } else if (categoricalCols.length >= 1 && numericCols.length === 0) {
    // Only categorical → Bar with count
    result.chartType = 'bar'
    result.xAxis = categoricalCols[0].name
    result.yAxis = ''
    result.aggregation = 'count'
    result.warning = 'No numeric column found. Using count aggregation.'
  } else if (booleanCols.length >= 1 && numericCols.length >= 1) {
    // Boolean + Numeric → Bar
    result.chartType = 'bar'
    result.xAxis = booleanCols[0].name
    result.yAxis = numericCols[0].name
    result.aggregation = 'avg'
  } else {
    // Fallback: use first column as X, try to find numeric for Y
    const firstCol = relevantCols[0] || columnMeta[0]
    result.xAxis = firstCol.name
    if (allNumeric.length > 0) {
      result.yAxis = allNumeric[0].name
    } else {
      result.aggregation = 'count'
      result.warning = 'No numeric column found. Using count aggregation.'
    }
  }

  // If selected columns don't match the suggested chart type well, add warning
  if (selectedColumns.length > 0) {
    const selectedMeta = columnMeta.filter(c => selectedColumns.includes(c.name))
    const selectedTypes = selectedMeta.map(c => c.columnType)
    if (result.chartType === 'scatter' && !selectedTypes.includes('numeric')) {
      result.warning = 'Scatter plot works best with numeric columns on both axes.'
    }
    if (result.chartType === 'histogram' && !selectedTypes.includes('numeric')) {
      result.warning = 'Histogram requires a numeric column.'
    }
  }

  return result
}

/**
 * Get recommended chart types for given column types.
 * Returns array of chart types with whether they're recommended.
 */
export function getRecommendedChartTypes(
  columnMeta: ColumnMeta[],
  selectedColumns: string[] = [],
): Array<{ type: ChartType; recommended: boolean; reason: string }> {
  const relevantCols = selectedColumns.length > 0
    ? columnMeta.filter(c => selectedColumns.includes(c.name))
    : columnMeta

  const hasNumeric = relevantCols.some(c => c.columnType === 'numeric')
  const hasCategorical = relevantCols.some(c => c.columnType === 'categorical')
  const hasDatetime = relevantCols.some(c => c.columnType === 'datetime')
  const numericCount = relevantCols.filter(c => c.columnType === 'numeric').length
  const categoricalCount = relevantCols.filter(c => c.columnType === 'categorical').length

  return [
    {
      type: 'bar',
      recommended: hasCategorical && hasNumeric,
      reason: hasCategorical && hasNumeric ? 'Categorical + numeric data' : 'Needs categorical + numeric',
    },
    {
      type: 'line',
      recommended: hasDatetime && hasNumeric,
      reason: hasDatetime && hasNumeric ? 'Time series data' : 'Needs datetime + numeric',
    },
    {
      type: 'pie',
      recommended: hasCategorical && hasNumeric && categoricalCount <= 12,
      reason: hasCategorical && hasNumeric ? 'Few categories' : 'Needs categorical + numeric (≤12 categories)',
    },
    {
      type: 'doughnut',
      recommended: hasCategorical && hasNumeric && categoricalCount <= 12,
      reason: hasCategorical && hasNumeric ? 'Few categories (ring style)' : 'Needs categorical + numeric (≤12 categories)',
    },
    {
      type: 'scatter',
      recommended: numericCount >= 2,
      reason: numericCount >= 2 ? 'Two numeric columns' : 'Needs 2 numeric columns',
    },
    {
      type: 'bubble',
      recommended: numericCount >= 3,
      reason: numericCount >= 3 ? 'Three numeric columns (x, y, size)' : 'Needs 3 numeric columns',
    },
    {
      type: 'radar',
      recommended: hasCategorical && hasNumeric,
      reason: hasCategorical && hasNumeric ? 'Multi-variable comparison' : 'Needs categorical + numeric',
    },
    {
      type: 'polarArea',
      recommended: hasCategorical && hasNumeric && categoricalCount <= 12,
      reason: hasCategorical && hasNumeric ? 'Category magnitude comparison' : 'Needs categorical + numeric (≤12 categories)',
    },
    {
      type: 'histogram',
      recommended: hasNumeric && numericCount === 1,
      reason: hasNumeric ? 'Single numeric column' : 'Needs a numeric column',
    },
    {
      type: 'area',
      recommended: hasDatetime && hasNumeric,
      reason: hasDatetime && hasNumeric ? 'Time series with area' : 'Needs datetime + numeric',
    },
    {
      type: 'boxplot',
      recommended: hasCategorical && hasNumeric,
      reason: hasCategorical && hasNumeric ? 'Distribution & outlier detection' : 'Needs categorical + numeric',
    },
    {
      type: 'violin',
      recommended: hasCategorical && hasNumeric,
      reason: hasCategorical && hasNumeric ? 'Density distribution & outlier detection' : 'Needs categorical + numeric',
    },
  ]
}

/**
 * Composable for chart heuristic functions.
 */
export function useChartHeuristic() {
  return {
    suggestChart,
    getRecommendedChartTypes,
  }
}
