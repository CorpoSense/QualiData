/**
 * Chart config state management composable.
 * Manages chart type, axis mappings, aggregation, and options.
 * Computes chartData and chartOptions for Chart.js from raw data.
 * Also provides fetchChartData() for server-side aggregation on full dataset.
 */

import { ref } from 'vue'
import type { ChartData, ChartOptions } from 'chart.js'
import type { ColumnMeta } from './useColumnTypes'
import { getApiUrl } from '@/utils/api'

export type ChartType = 'bar' | 'line' | 'pie' | 'scatter' | 'histogram' | 'area' | 'boxplot' | 'violin' | 'doughnut' | 'bubble' | 'radar' | 'polarArea'
export type AggregationMethod = 'sum' | 'avg' | 'count' | 'min' | 'max'

export interface ChartConfig {
  chartType: ChartType
  xAxis: string
  yAxis: string
  groupBy: string
  aggregation: AggregationMethod
  showLegend: boolean
  showGrid: boolean
  colorPalette: string
  title: string
  nullHandling: 'exclude' | 'category' | 'zero'
  sizeColumn: string
}

export const CHART_TYPE_OPTIONS: Array<{ value: ChartType; label: string; icon: string }> = [
  { value: 'bar', label: 'Bar Chart', icon: 'bi-bar-chart' },
  { value: 'line', label: 'Line Chart', icon: 'bi-graph-up' },
  { value: 'pie', label: 'Pie Chart', icon: 'bi-pie-chart' },
  { value: 'doughnut', label: 'Doughnut Chart', icon: 'bi-circle' },
  { value: 'scatter', label: 'Scatter Plot', icon: 'bi-diagram-3' },
  { value: 'bubble', label: 'Bubble Chart', icon: 'bi-bullseye' },
  { value: 'radar', label: 'Radar Chart', icon: 'bi-broadcast' },
  { value: 'polarArea', label: 'Polar Area', icon: 'bi-record-circle' },
  { value: 'histogram', label: 'Histogram', icon: 'bi-bar-chart-steps' },
  { value: 'area', label: 'Area Chart', icon: 'bi-graph-up-arrow' },
  { value: 'boxplot', label: 'Box Plot', icon: 'bi-box-seam' },
  { value: 'violin', label: 'Violin Plot', icon: 'bi-music-note-beamed' },
]

export const AGGREGATION_OPTIONS: Array<{ value: AggregationMethod; label: string }> = [
  { value: 'sum', label: 'Sum' },
  { value: 'avg', label: 'Average' },
  { value: 'count', label: 'Count' },
  { value: 'min', label: 'Min' },
  { value: 'max', label: 'Max' },
]

export const COLOR_PALETTES: Record<string, string[]> = {
  default: ['#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236', '#166a8f', '#00a950', '#58595b', '#8549ba'],
  pastel: ['#a1c9f4', '#ffb482', '#8de5a1', '#ff9c9c', '#b9f2f0', '#d0bbff', '#ffda9c', '#fab4d4', '#cfcfcf'],
  vivid: ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45'],
  cool: ['#4dc9f6', '#537bc4', '#166a8f', '#00a950', '#acc236', '#58595b', '#8549ba', '#a1c9f4', '#b9f2f0'],
  warm: ['#f67019', '#f53794', '#ff9c9c', '#ffb482', '#ffda9c', '#fab4d4', '#f032e6', '#ffe119', '#bfef45'],
}

const DEFAULT_CONFIG: ChartConfig = {
  chartType: 'bar',
  xAxis: '',
  yAxis: '',
  groupBy: '',
  aggregation: 'sum',
  showLegend: true,
  showGrid: true,
  colorPalette: 'default',
  title: '',
  nullHandling: 'exclude',
  sizeColumn: '',
}

/**
 * Aggregate data for chart rendering.
 * Groups rows by xColumn, applies aggregation to yColumn.
 */
export function aggregateData(
  data: Record<string, any>[],
  xColumn: string,
  yColumn: string,
  method: AggregationMethod,
  groupColumn?: string,
): { labels: string[]; datasets: Array<{ label: string; data: number[] }> } {
  if (!data.length || !xColumn) {
    return { labels: [], datasets: [{ label: yColumn || 'Count', data: [] }] }
  }

  // For count without yColumn, just count occurrences
  if (method === 'count' && !yColumn) {
    const counts: Record<string, number> = {}
    for (const row of data) {
      const key = String(row[xColumn] ?? '(null)')
      counts[key] = (counts[key] || 0) + 1
    }
    const labels = Object.keys(counts).sort()
    return {
      labels,
      datasets: [{ label: `Count of ${xColumn}`, data: labels.map(l => counts[l]) }],
    }
  }

  if (groupColumn) {
    // Grouped aggregation
    const groups: Record<string, Record<string, number[]>> = {}
    const xValues = new Set<string>()

    for (const row of data) {
      const x = String(row[xColumn] ?? '(null)')
      const g = String(row[groupColumn] ?? '(null)')
      const y = yColumn ? Number(row[yColumn]) : 1
      if (isNaN(y)) continue

      xValues.add(x)
      if (!groups[g]) groups[g] = {}
      if (!groups[g][x]) groups[g][x] = []
      groups[g][x].push(y)
    }

    const labels = Array.from(xValues).sort()
    const datasets = Object.entries(groups).map(([group, xData]) => ({
      label: group,
      data: labels.map(x => applyAgg(xData[x] || [], method)),
    }))

    return { labels, datasets }
  }

  // Simple aggregation (no grouping)
  const groups: Record<string, number[]> = {}
  for (const row of data) {
    const x = String(row[xColumn] ?? '(null)')
    const y = yColumn ? Number(row[yColumn]) : 1
    if (isNaN(y)) continue

    if (!groups[x]) groups[x] = []
    groups[x].push(y)
  }

  const labels = Object.keys(groups).sort()
  return {
    labels,
    datasets: [{ label: yColumn || 'Count', data: labels.map(l => applyAgg(groups[l], method)) }],
  }
}

/**
 * Apply aggregation method to an array of numbers.
 */
export function applyAgg(values: number[], method: AggregationMethod): number {
  if (!values.length) return 0
  switch (method) {
    case 'sum': return values.reduce((a, b) => a + b, 0)
    case 'avg': return values.reduce((a, b) => a + b, 0) / values.length
    case 'count': return values.length
    case 'min': return Math.min(...values)
    case 'max': return Math.max(...values)
    default: return values.reduce((a, b) => a + b, 0)
  }
}

/**
 * Compute boxplot data: groups rows by xColumn, collects raw numeric arrays per group.
 * The chartjs-chart-boxplot library computes stats (median, q1, q3, whiskers, outliers) from raw values.
 */
export function computeBoxPlotData(
  data: Record<string, any>[],
  xColumn: string,
  yColumn: string,
): { labels: string[]; datasets: Array<{ label: string; data: number[][] }> } {
  if (!data.length || !xColumn || !yColumn) {
    return { labels: [], datasets: [{ label: yColumn || 'Value', data: [] }] }
  }

  const groups: Record<string, number[]> = {}
  for (const row of data) {
    const x = String(row[xColumn] ?? '(null)')
    const raw = row[yColumn]
    if (raw === null || raw === '' || raw === undefined) continue
    const y = Number(raw)
    if (isNaN(y)) continue
    if (!groups[x]) groups[x] = []
    groups[x].push(y)
  }

  const labels = Object.keys(groups).sort()
  return {
    labels,
    datasets: [{ label: yColumn, data: labels.map(l => groups[l]) }],
  }
}

/**
 * Compute violin data: same format as boxplot (raw numeric arrays per group).
 * The chartjs-chart-boxplot library computes KDE (kernel density estimation) from raw values.
 */
export function computeViolinData(
  data: Record<string, any>[],
  xColumn: string,
  yColumn: string,
): { labels: string[]; datasets: Array<{ label: string; data: number[][] }> } {
  return computeBoxPlotData(data, xColumn, yColumn)
}

/**
 * Compute bubble chart data: x, y, and radius from size column.
 * Normalizes radius values to a reasonable range (5–30).
 */
export function computeBubbleData(
  data: Record<string, any>[],
  xColumn: string,
  yColumn: string,
  sizeColumn?: string,
): { datasets: Array<{ label: string; data: Array<{ x: number; y: number; r: number }> }> } {
  if (!data.length || !xColumn || !yColumn) {
    return { datasets: [{ label: `${xColumn || 'X'} vs ${yColumn || 'Y'}`, data: [] }] }
  }

  const points: Array<{ x: number; y: number; r: number }> = []
  const rawSizes: number[] = []

  for (const row of data) {
    const x = Number(row[xColumn])
    const y = Number(row[yColumn])
    if (isNaN(x) || isNaN(y)) continue

    let r = 8
    if (sizeColumn && row[sizeColumn] != null) {
      const s = Number(row[sizeColumn])
      if (!isNaN(s)) {
        rawSizes.push(s)
        r = s
      }
    }
    points.push({ x, y, r })
  }

  // Normalize radius to 5–30 range
  if (sizeColumn && rawSizes.length > 0) {
    const minR = Math.min(...rawSizes)
    const maxR = Math.max(...rawSizes)
    const range = maxR - minR || 1
    for (const pt of points) {
      pt.r = 5 + ((pt.r - minR) / range) * 25
    }
  }

  return { datasets: [{ label: sizeColumn ? `${xColumn} vs ${yColumn} (size: ${sizeColumn})` : `${xColumn} vs ${yColumn}`, data: points }] }
}

/**
 * Compute histogram bins from numeric data.
 */
export function computeHistogramBins(
  data: Record<string, any>[],
  column: string,
  numBins: number = 10,
): { labels: string[]; data: number[] } {
  if (!data.length || !column) return { labels: [], data: [] }

  const values = data
    .map(row => Number(row[column]))
    .filter(v => !isNaN(v))

  if (!values.length) return { labels: [], data: [] }

  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const binWidth = range / numBins

  const bins = new Array(numBins).fill(0)
  const labels: string[] = []

  for (let i = 0; i < numBins; i++) {
    const lo = min + i * binWidth
    const hi = lo + binWidth
    labels.push(`${lo.toFixed(1)}–${hi.toFixed(1)}`)
  }

  for (const v of values) {
    let idx = Math.floor((v - min) / binWidth)
    if (idx >= numBins) idx = numBins - 1
    if (idx < 0) idx = 0
    bins[idx]++
  }

  return { labels, data: bins }
}

/**
 * Composable for chart configuration and computed chart data.
 */
export function useChartConfig() {
  const config = ref<ChartConfig>({ ...DEFAULT_CONFIG })

  /**
   * Filter nulls from data based on nullHandling setting.
   */
  function filterNulls(data: Record<string, any>[], columns: string[]): Record<string, any>[] {
    if (config.value.nullHandling === 'exclude') {
      return data.filter(row => columns.every(c => row[c] != null && row[c] !== ''))
    }
    return data
  }

  /**
   * Compute chartData for Chart.js based on current config and data.
   */
  function computeChartData(data: Record<string, any>[], _columnMeta: ColumnMeta[]): ChartData {
    const cfg = config.value
    const colors = COLOR_PALETTES[cfg.colorPalette] || COLOR_PALETTES.default

    // Filter nulls
    const relevantCols = [cfg.xAxis, cfg.yAxis, cfg.groupBy, cfg.sizeColumn].filter(Boolean)
    const filteredData = filterNulls(data, relevantCols)

    if (cfg.chartType === 'histogram') {
      const { labels, data: bins } = computeHistogramBins(filteredData, cfg.xAxis)
      return {
        labels,
        datasets: [{
          label: `Histogram of ${cfg.xAxis}`,
          data: bins,
          backgroundColor: colors[0] + '80',
          borderColor: colors[0],
          borderWidth: 1,
        }],
      }
    }

    if (cfg.chartType === 'boxplot') {
      const boxResult = computeBoxPlotData(filteredData, cfg.xAxis, cfg.yAxis)
      return {
        labels: boxResult.labels,
        datasets: boxResult.datasets.map((ds, i) => ({
          ...ds,
          backgroundColor: colors[i % colors.length] + '80',
          borderColor: colors[i % colors.length],
          borderWidth: 2,
        })),
      } as ChartData
    }

    if (cfg.chartType === 'violin') {
      const violinResult = computeViolinData(filteredData, cfg.xAxis, cfg.yAxis)
      return {
        labels: violinResult.labels,
        datasets: violinResult.datasets.map((ds, i) => ({
          ...ds,
          backgroundColor: colors[i % colors.length] + '80',
          borderColor: colors[i % colors.length],
          borderWidth: 2,
        })),
      } as ChartData
    }

    if (cfg.chartType === 'scatter') {
      // Scatter: raw x,y pairs
      const points = filteredData
        .map(row => ({
          x: Number(row[cfg.xAxis]),
          y: Number(row[cfg.yAxis]),
        }))
        .filter(p => !isNaN(p.x) && !isNaN(p.y))

      return {
        datasets: [{
          label: `${cfg.xAxis} vs ${cfg.yAxis}`,
          data: points,
          backgroundColor: colors[0] + '80',
          borderColor: colors[0],
          pointRadius: 4,
        }],
      }
    }

    if (cfg.chartType === 'bubble') {
      const bubbleResult = computeBubbleData(filteredData, cfg.xAxis, cfg.yAxis, cfg.sizeColumn || undefined)
      return {
        datasets: bubbleResult.datasets.map((ds, i) => ({
          ...ds,
          backgroundColor: colors[i % colors.length] + '60',
          borderColor: colors[i % colors.length],
          borderWidth: 1,
        })),
      } as ChartData
    }

    // Aggregated charts (bar, line, pie, area, doughnut, radar, polarArea)
    const aggResult = aggregateData(
      filteredData,
      cfg.xAxis,
      cfg.yAxis,
      cfg.aggregation,
      cfg.groupBy || undefined,
    )

    const isPieLike = cfg.chartType === 'pie' || cfg.chartType === 'doughnut' || cfg.chartType === 'polarArea'
    const isArea = cfg.chartType === 'area'

    const datasets = aggResult.datasets.map((ds, i) => ({
      ...ds,
      backgroundColor: isPieLike
        ? aggResult.labels.map((_, j) => colors[j % colors.length] + '80')
        : cfg.groupBy
          ? colors[i % colors.length] + '80'
          : colors[0] + '80',
      borderColor: isPieLike
        ? aggResult.labels.map((_, j) => colors[j % colors.length])
        : cfg.groupBy
          ? colors[i % colors.length]
          : colors[0],
      borderWidth: isPieLike ? 1 : 2,
      fill: isArea ? 'origin' : false,
      tension: (cfg.chartType === 'line' || isArea) ? 0.3 : 0,
    }))

    return {
      labels: aggResult.labels,
      datasets,
    }
  }

  /**
   * Compute chart options for Chart.js based on current config.
   */
  function computeChartOptions(): ChartOptions {
    const cfg = config.value
    const isPieLike = cfg.chartType === 'pie' || cfg.chartType === 'doughnut'
    const isBoxPlot = cfg.chartType === 'boxplot' || cfg.chartType === 'violin'
    const isHistogram = cfg.chartType === 'histogram'
    const isRadar = cfg.chartType === 'radar'
    const isPolarArea = cfg.chartType === 'polarArea'
    const noCartesianScales = isPieLike || isPolarArea

    if (isRadar) {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: cfg.showLegend,
            position: 'top',
          },
          title: {
            display: !!cfg.title,
            text: cfg.title,
          },
        },
        scales: {
          r: {
            grid: { display: cfg.showGrid },
            pointLabels: { display: true },
          },
        },
      } as ChartOptions
    }

    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: cfg.showLegend,
          position: noCartesianScales ? 'right' : 'top',
        },
        title: {
          display: !!cfg.title,
          text: cfg.title,
        },
      },
      ...(cfg.chartType === 'doughnut' ? { cutout: '50%' } : {}),
      scales: noCartesianScales ? {} : {
        x: {
          display: true,
          title: {
            display: !isHistogram,
            text: isHistogram ? '' : cfg.xAxis,
          },
          grid: { display: cfg.showGrid },
        },
        y: {
          display: true,
          title: {
            display: !(isHistogram || isBoxPlot),
            text: isHistogram ? 'Frequency' : isBoxPlot ? 'Values' : cfg.yAxis,
          },
          grid: { display: cfg.showGrid },
          beginAtZero: false,
        },
      },
    } as ChartOptions
  }

  /**
   * Reset config to defaults.
   */
  function resetConfig() {
    config.value = { ...DEFAULT_CONFIG }
  }

  /**
   * Set config from a preset (e.g., from quick chart type selection).
   */
  function setPreset(chartType: ChartType, xAxis?: string, yAxis?: string) {
    config.value.chartType = chartType
    if (xAxis) config.value.xAxis = xAxis
    if (yAxis) config.value.yAxis = yAxis
    // Set sensible defaults per chart type
    if (chartType === 'histogram') {
      config.value.yAxis = ''
      config.value.groupBy = ''
    }
    if (chartType === 'pie' || chartType === 'doughnut' || chartType === 'polarArea') {
      config.value.groupBy = ''
    }
    if (chartType === 'scatter' || chartType === 'bubble') {
      config.value.aggregation = 'sum'
      config.value.groupBy = ''
    }
    if (chartType === 'bubble') {
      config.value.sizeColumn = ''
    }
    if (chartType === 'boxplot' || chartType === 'violin') {
      config.value.groupBy = ''
    }
  }

  return {
    config,
    computeChartData,
    computeChartOptions,
    resetConfig,
    setPreset,
    filterNulls,
  }
}

/**
 * Transform server chart-data response into Chart.js compatible format.
 * Server returns: { labels, datasets: [{ label, data }] }
 * Chart.js needs: { labels, datasets: [{ label, data, backgroundColor, borderColor, ... }] }
 */
export function transformServerChartData(
  serverData: {
    chart_type: string
    labels: string[]
    datasets: Array<{ label: string; data: number[] | Array<{ x: number; y: number }> }>
    warning?: string
  },
  colorPalette: string = 'default',
): ChartData {
  const colors = COLOR_PALETTES[colorPalette] || COLOR_PALETTES.default
  const isPieLike = serverData.chart_type === 'pie' || serverData.chart_type === 'doughnut' || serverData.chart_type === 'polarArea'
  const isArea = serverData.chart_type === 'area'
  const isBubble = serverData.chart_type === 'bubble'

  const datasets = serverData.datasets.map((ds, i) => ({
    ...ds,
    backgroundColor: isBubble
      ? (colors[i % colors.length] || colors[0]) + '60'
      : isPieLike
        ? serverData.labels.map((_, j) => colors[j % colors.length] + '80')
        : serverData.datasets.length > 1
          ? colors[i % colors.length] + '80'
          : colors[0] + '80',
    borderColor: isBubble
      ? colors[i % colors.length] || colors[0]
      : isPieLike
        ? serverData.labels.map((_, j) => colors[j % colors.length])
        : serverData.datasets.length > 1
          ? colors[i % colors.length]
          : colors[0],
    borderWidth: isPieLike ? 1 : 2,
    fill: isArea ? 'origin' : false,
    tension: (serverData.chart_type === 'line' || isArea) ? 0.3 : 0,
  }))

  return {
    labels: serverData.labels,
    datasets,
  }
}

/**
 * Fetch chart data from the backend chart-data endpoint.
 * Operates on the full dataset (not just the preview page).
 */
export async function fetchChartData(
  datasetId: string,
  config: ChartConfig,
  filters?: Record<string, any>,
): Promise<{ chartData: ChartData; warning?: string; rowCount: number; filteredCount: number }> {
  const apiUrl = getApiUrl()
  const token = localStorage.getItem('token')

  const body: Record<string, any> = {
    chart_type: config.chartType,
    x_column: config.xAxis,
    y_column: config.yAxis || '',
    aggregation: config.aggregation,
    group_by: config.groupBy || '',
    null_handling: config.nullHandling,
    histogram_bins: 10,
    size_column: config.sizeColumn || '',
  }

  if (filters && Object.keys(filters).length > 0) {
    body.filters = filters
  }

  const res = await fetch(`${apiUrl}/api/datasets/${datasetId}/chart-data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to fetch chart data' }))
    throw new Error(err.detail || 'Failed to fetch chart data')
  }

  const serverData = await res.json()
  const chartData = transformServerChartData(serverData, config.colorPalette)

  return {
    chartData,
    warning: serverData.warning,
    rowCount: serverData.row_count || 0,
    filteredCount: serverData.filtered_count || 0,
  }
}
