/**
 * Column type classification composable for chart visualization.
 * Classifies columns as numeric, categorical, datetime, boolean, or text
 * based on dtype and unique_count from profiling data.
 */

export type ColumnType = 'numeric' | 'categorical' | 'datetime' | 'boolean' | 'text'

export interface ColumnMeta {
  name: string
  dtype: string
  uniqueCount: number
  nullCount: number
  columnType: ColumnType
}

const CATEGORICAL_THRESHOLD = 50

/**
 * Classify a single column based on its dtype and unique count.
 */
export function classifyColumn(dtype: string, uniqueCount: number): ColumnType {
  if (dtype.startsWith('int') || dtype.startsWith('float')) return 'numeric'
  if (dtype === 'datetime' || dtype.startsWith('datetime')) return 'datetime'
  if (dtype === 'boolean' || dtype === 'bool') return 'boolean'
  if (dtype === 'string' || dtype === 'object') {
    return uniqueCount < CATEGORICAL_THRESHOLD ? 'categorical' : 'text'
  }
  // Fallback: treat as categorical if few unique values, else text
  return uniqueCount < CATEGORICAL_THRESHOLD ? 'categorical' : 'text'
}

/**
 * Composable that provides column type classification utilities.
 */
export function useColumnTypes() {
  /**
   * Build column metadata from profiling data.
   * @param profileColumns - Array of column profile objects from /api/datasets/{id}/profile
   * @returns Array of ColumnMeta with classified types
   */
  function classifyColumns(profileColumns: Array<{ name: string; dtype: string; unique_count: number; null_count: number }>): ColumnMeta[] {
    if (!profileColumns) return []
    return profileColumns.map(col => ({
      name: col.name,
      dtype: col.dtype,
      uniqueCount: col.unique_count,
      nullCount: col.null_count,
      columnType: classifyColumn(col.dtype, col.unique_count),
    }))
  }

  /**
   * Get columns of a specific type.
   */
  function getColumnsByType(columns: ColumnMeta[], type: ColumnType): ColumnMeta[] {
    return columns.filter(c => c.columnType === type)
  }

  /**
   * Get column names of a specific type.
   */
  function getColumnNamesByType(columns: ColumnMeta[], type: ColumnType): string[] {
    return getColumnsByType(columns, type).map(c => c.name)
  }

  /**
   * Check if a column type is compatible with an axis role.
   */
  function isCompatibleWithAxis(columnType: ColumnType, axisRole: 'x' | 'y' | 'group'): boolean {
    if (axisRole === 'x') {
      return ['categorical', 'datetime', 'numeric'].includes(columnType)
    }
    if (axisRole === 'y') {
      return columnType === 'numeric'
    }
    if (axisRole === 'group') {
      return ['categorical', 'boolean'].includes(columnType)
    }
    return false
  }

  return {
    classifyColumn,
    classifyColumns,
    getColumnsByType,
    getColumnNamesByType,
    isCompatibleWithAxis,
  }
}
