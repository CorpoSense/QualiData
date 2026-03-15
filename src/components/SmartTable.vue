<template>
 <div class="smart-table" :class="wrapperClass" :style="wrapperStyle">
 <slot name="top" v-bind="slotApi" />

 <div
 class="smart-table__viewport position-relative"
 :class="[responsiveClass, stickyHeader && 'smart-table__viewport--sticky']"
 :style="viewportStyle"
 >
 <table
 :class="tableClasses"
 :style="tableStyle"
 >
 <caption v-if="caption || $slots.caption" :class="captionTop && 'caption-top'">
 <slot name="caption" v-bind="slotApi">
 {{ caption }}
 </slot>
 </caption>

 <thead v-if="showHeader" :class="theadClass">
 <tr>
 <th
 v-if="hasRowSelection && rowSelectionColumnPosition === 'start'"
 scope="col"
 :class="rowSelectionColumnClass"
 :style="rowSelectionColumnStyle"
 >
 <slot
 name="selection-head"
 :allVisibleRowsSelected="allVisibleRowsSelected"
 :someVisibleRowsSelected="someVisibleRowsSelected"
 :toggleAllVisibleRows="toggleAllVisibleRows"
 :selectAllVisibleRows="selectAllVisibleRows"
 :clearSelectedRows="clearSelectedRows"
 >
 <div class="d-flex justify-content-center">
 <template v-if="rowSelectionMode === 'multiple'">
 <input
 ref="rowSelectAllRef"
 class="form-check-input m-0 smart-table__selection-control"
 type="checkbox"
 :aria-label="`Select all visible rows`"
 :checked="allVisibleRowsSelected"
 @click.stop
 @change="toggleAllVisibleRows(($event.target as HTMLInputElement).checked)"
 />
 </template>
 <span v-else class="visually-hidden">{{ selectionColumnLabel }}</span>
 </div>
 </slot>
 </th>

 <th
 v-for="(field, colIndex) in visibleFields"
 :key="field.key"
 scope="col"
 :class="getFieldThClass(field, colIndex)"
 :style="getFieldThStyle(field, colIndex)"
 :aria-sort="getAriaSort(field)"
 :tabindex="isHeaderFocusable(field) ? 0 : undefined"
 v-bind="getFieldThAttrs(field, colIndex)"
 @click="onHeaderClick(field, colIndex, $event)"
 @keydown.enter.prevent="onHeaderKeydown(field, colIndex, $event)"
 @keydown.space.prevent="onHeaderKeydown(field, colIndex, $event)"
 >
 <div
 class="smart-table__head-content"
 :class="field.sortable && 'smart-table__head-content--sortable'"
 >
 <template v-if="hasColumnSelection && isColumnSelectable(field, colIndex)">
 <input
 class="form-check-input m-0 smart-table__selection-control"
 :type="columnSelectionMode === 'single' ? 'radio' : 'checkbox'"
 :name="columnSelectionMode === 'single' ? `${uid}-column-select` : undefined"
 :checked="isColumnSelected(field.key)"
 :aria-label="`Select column ${field.label || field.key}`"
 @click="onColumnSelectControlClick(field, colIndex, $event)"
 @change="onColumnSelectControlChange(field, colIndex, $event)"
 />
 </template>

 <span class="smart-table__head-label flex-grow-1 text-truncate">
 <slot
 :name="`head(${field.key})`"
 :field="field"
 :index="colIndex"
 :selected="isColumnSelected(field.key)"
 :sortable="Boolean(field.sortable)"
 :sortBy="sortByState"
 :sortDesc="sortDescState"
 :toggleSort="() => toggleSortForField(field)"
 :toggleColumn="(force?: boolean) => toggleColumnSelection(field.key, force)"
 >
 <slot
 name="head"
 :field="field"
 :index="colIndex"
 :selected="isColumnSelected(field.key)"
 :sortable="Boolean(field.sortable)"
 :sortBy="sortByState"
 :sortDesc="sortDescState"
 :toggleSort="() => toggleSortForField(field)"
 :toggleColumn="(force?: boolean) => toggleColumnSelection(field.key, force)"
 >
 {{ field.label || startCase(field.key) }}
 </slot>
 </slot>
 </span>

 <span
 v-if="field.sortable"
 class="smart-table__sort-indicator"
 :class="sortByState === field.key ? 'text-primary' : 'text-body-secondary'"
 aria-hidden="true"
 >
 {{ getSortIndicator(field) }}
 </span>
 </div>
 </th>

 <th
 v-if="hasRowSelection && rowSelectionColumnPosition === 'end'"
 scope="col"
 :class="rowSelectionColumnClass"
 :style="rowSelectionColumnStyle"
 >
 <slot
 name="selection-head"
 :allVisibleRowsSelected="allVisibleRowsSelected"
 :someVisibleRowsSelected="someVisibleRowsSelected"
 :toggleAllVisibleRows="toggleAllVisibleRows"
 :selectAllVisibleRows="selectAllVisibleRows"
 :clearSelectedRows="clearSelectedRows"
 >
 <div class="d-flex justify-content-center">
 <template v-if="rowSelectionMode === 'multiple'">
 <input
 ref="rowSelectAllRef"
 class="form-check-input m-0 smart-table__selection-control"
 type="checkbox"
 :aria-label="`Select all visible rows`"
 :checked="allVisibleRowsSelected"
 @click.stop
 @change="toggleAllVisibleRows(($event.target as HTMLInputElement).checked)"
 />
 </template>
 <span v-else class="visually-hidden">{{ selectionColumnLabel }}</span>
 </div>
 </slot>
 </th>
 </tr>
 </thead>

 <tbody :class="tbodyClass">
 <template v-if="renderedItems.length > 0">
 <tr
 v-for="(row, localIndex) in renderedItems"
 :key="String(getRowKey(row, resolveRowIndex(localIndex)))"
 :class="getRowClass(row, resolveRowIndex(localIndex))"
 :style="getRowStyle(row, resolveRowIndex(localIndex))"
 :tabindex="isRowFocusable(row, resolveRowIndex(localIndex)) ? 0 : undefined"
 v-bind="getRowAttrs(row, resolveRowIndex(localIndex))"
 @click="onRowClick(row, resolveRowIndex(localIndex), $event)"
 @keydown.enter.prevent="onRowKeydown(row, resolveRowIndex(localIndex), $event)"
 @keydown.space.prevent="onRowKeydown(row, resolveRowIndex(localIndex), $event)"
 >
 <td
 v-if="hasRowSelection && rowSelectionColumnPosition === 'start'"
 :class="rowSelectionColumnClass"
 :style="rowSelectionColumnStyle"
 >
 <slot
 name="selection-cell"
 :item="row"
 :index="resolveRowIndex(localIndex)"
 :rowKey="getRowKey(row, resolveRowIndex(localIndex))"
 :selected="isRowSelected(row, resolveRowIndex(localIndex))"
 :disabled="!isRowSelectable(row, resolveRowIndex(localIndex))"
 :toggle="(force?: boolean) => toggleRowSelection(row, resolveRowIndex(localIndex), force)"
 >
 <div class="d-flex justify-content-center">
 <input
 class="form-check-input m-0 smart-table__selection-control"
 :type="rowSelectionMode === 'single' ? 'radio' : 'checkbox'"
 :name="rowSelectionMode === 'single' ? `${uid}-row-select` : undefined"
 :checked="isRowSelected(row, resolveRowIndex(localIndex))"
 :disabled="!isRowSelectable(row, resolveRowIndex(localIndex))"
 :aria-label="`Select row ${resolveRowIndex(localIndex) + 1}`"
 @click="onRowSelectControlClick(row, resolveRowIndex(localIndex), $event)"
 @change="onRowSelectControlChange(row, resolveRowIndex(localIndex), $event)"
 />
 </div>
 </slot>
 </td>

 <td
 v-for="(field, colIndex) in visibleFields"
 :key="field.key"
 :class="getFieldTdClass(field, row, resolveRowIndex(localIndex), colIndex)"
 :style="getFieldTdStyle(field, row, resolveRowIndex(localIndex), colIndex)"
 v-bind="getFieldTdAttrs(field, row, resolveRowIndex(localIndex), colIndex)"
 >
 <slot
 :name="`cell(${field.key})`"
 :item="row"
 :field="field"
 :index="resolveRowIndex(localIndex)"
 :value="getCellValue(row, field, resolveRowIndex(localIndex))"
 :formatted="formatCellValue(row, field, resolveRowIndex(localIndex))"
 :selectedRow="isRowSelected(row, resolveRowIndex(localIndex))"
 :selectedColumn="isColumnSelected(field.key)"
 :toggleRow="(force?: boolean) => toggleRowSelection(row, resolveRowIndex(localIndex), force)"
 :toggleColumn="(force?: boolean) => toggleColumnSelection(field.key, force)"
 >
 <slot
 name="cell"
 :item="row"
 :field="field"
 :index="resolveRowIndex(localIndex)"
 :value="getCellValue(row, field, resolveRowIndex(localIndex))"
 :formatted="formatCellValue(row, field, resolveRowIndex(localIndex))"
 :selectedRow="isRowSelected(row, resolveRowIndex(localIndex))"
 :selectedColumn="isColumnSelected(field.key)"
 :toggleRow="(force?: boolean) => toggleRowSelection(row, resolveRowIndex(localIndex), force)"
 :toggleColumn="(force?: boolean) => toggleColumnSelection(field.key, force)"
 >
 {{ formatCellValue(row, field, resolveRowIndex(localIndex)) }}
 </slot>
 </slot>
 </td>

 <td
 v-if="hasRowSelection && rowSelectionColumnPosition === 'end'"
 :class="rowSelectionColumnClass"
 :style="rowSelectionColumnStyle"
 >
 <slot
 name="selection-cell"
 :item="row"
 :index="resolveRowIndex(localIndex)"
 :rowKey="getRowKey(row, resolveRowIndex(localIndex))"
 :selected="isRowSelected(row, resolveRowIndex(localIndex))"
 :disabled="!isRowSelectable(row, resolveRowIndex(localIndex))"
 :toggle="(force?: boolean) => toggleRowSelection(row, resolveRowIndex(localIndex), force)"
 >
 <div class="d-flex justify-content-center">
 <input
 class="form-check-input m-0 smart-table__selection-control"
 :type="rowSelectionMode === 'single' ? 'radio' : 'checkbox'"
 :name="rowSelectionMode === 'single' ? `${uid}-row-select` : undefined"
 :checked="isRowSelected(row, resolveRowIndex(localIndex))"
 :disabled="!isRowSelectable(row, resolveRowIndex(localIndex))"
 :aria-label="`Select row ${resolveRowIndex(localIndex) + 1}`"
 @click="onRowSelectControlClick(row, resolveRowIndex(localIndex), $event)"
 @change="onRowSelectControlChange(row, resolveRowIndex(localIndex), $event)"
 />
 </div>
 </slot>
 </td>
 </tr>
 </template>

 <tr v-else-if="computedBusy && !showBusyOverlay">
 <td :colspan="colspan" class="text-center py-4">
 <slot name="busy" :busy="computedBusy" :text="busyText">
 <div class="d-inline-flex align-items-center gap-2 text-body-secondary">
 <div class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
 <span>{{ busyText }}</span>
 </div>
 </slot>
 </td>
 </tr>

 <tr v-else-if="providerError && !computedBusy">
 <td :colspan="colspan" class="text-center py-4 text-danger">
 <slot name="empty" v-bind="slotApi">
 {{ getProviderErrorMessage() }}
 </slot>
 </td>
 </tr>

 <tr v-else>
 <td :colspan="colspan" class="text-center py-4 text-body-secondary">
 <slot name="empty" v-bind="slotApi">
 {{ isFilterActive ? emptyFilteredText : emptyText }}
 </slot>
 </td>
 </tr>
 </tbody>
 </table>

 <div
 v-if="computedBusy && showBusyOverlay"
 class="smart-table__overlay"
 aria-live="polite"
 aria-busy="true"
 >
 <slot name="busy" :busy="computedBusy" :text="busyText">
 <div class="d-inline-flex align-items-center gap-2 bg-body border rounded px-3 py-2 shadow-sm">
 <div class="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
 <span>{{ busyText }}</span>
 </div>
 </slot>
 </div>
 </div>

 <div
 v-if="showPageInfo || showPaginationControls"
 class="smart-table__footer d-flex flex-wrap gap-3 align-items-center mt-2"
 >
 <div v-if="showPageInfo" class="small text-body-secondary">
 {{ pageInfoText }}
 </div>

 <nav
 v-if="showPaginationControls"
 :class="paginationNavClass"
 aria-label="Table pagination"
 >
 <ul class="pagination mb-0" :class="paginationSizeClass">
 <li class="page-item" :class="{ disabled: currentPageState <= 1 }">
 <button
 class="page-link"
 type="button"
 :disabled="currentPageState <= 1"
 @click="goToPage(1)"
 >
 «
 </button>
 </li>

 <li class="page-item" :class="{ disabled: currentPageState <= 1 }">
 <button
 class="page-link"
 type="button"
 :disabled="currentPageState <= 1"
 @click="prevPage()"
 >
 <<
 </button>
 </li>

 <template v-for="(page, index) in paginationItems" :key="`${page}-${index}`">
 <li v-if="typeof page === 'number'" class="page-item" :class="{ active: page === currentPageState }">
 <button class="page-link" type="button" @click="goToPage(page)">
 {{ page }}
 </button>
 </li>
 <li v-else class="page-item disabled">
 <span class="page-link">…</span>
 </li>
 </template>

 <li class="page-item" :class="{ disabled: currentPageState >= pageCount }">
 <button
 class="page-link"
 type="button"
 :disabled="currentPageState >= pageCount"
 @click="nextPage()"
 >
 ›
 </button>
 </li>

 <li class="page-item" :class="{ disabled: currentPageState >= pageCount }">
 <button
 class="page-link"
 type="button"
 :disabled="currentPageState >= pageCount"
 @click="goToPage(pageCount)"
 >>
 </button>
 </li>
 </ul>
 </nav>
 </div>

 <slot name="bottom" v-bind="slotApi" />
 </div>
</template>

<script lang="ts">
import {
 computed,
 defineComponent,
 getCurrentInstance,
 onBeforeUnmount,
 ref,
 watch,
 type PropType,
 type StyleValue,
} from 'vue'

export type SmartTableKey = string | number
export type SmartTableSelectionMode = 'none' | 'single' | 'multiple'
export type SmartTableItem = Record<string, unknown>

export interface SmartTableField<T extends SmartTableItem = SmartTableItem> {
 key: string
 label?: string
 visible?: boolean
 sortable?: boolean
 filterable?: boolean
 selectable?: boolean
 align?: 'start' | 'center' | 'end'
 class?: unknown
 thClass?: unknown | ((field: SmartTableField<T>, index: number) => unknown)
 tdClass?: unknown | ((value: unknown, item: T, index: number, field: SmartTableField<T>) => unknown)
 thStyle?: StyleValue | ((field: SmartTableField<T>, index: number) => StyleValue)
 tdStyle?: StyleValue | ((value: unknown, item: T, index: number, field: SmartTableField<T>) => StyleValue)
 thAttr?: Record<string, unknown> | ((field: SmartTableField<T>, index: number) => Record<string, unknown>)
 tdAttr?: Record<string, unknown> | ((value: unknown, item: T, index: number, field: SmartTableField<T>) => Record<string, unknown>)
 formatter?: (value: unknown, item: T, index: number, field: SmartTableField<T>) => unknown
 sortValue?: (item: T, index: number, field: SmartTableField<T>) => unknown
 sortCompare?: (
 aValue: unknown,
 bValue: unknown,
 aItem: T,
 bItem: T,
 sortDesc: boolean,
 field: SmartTableField<T>
 ) => number
 filterValue?: (item: T, index: number, field: SmartTableField<T>) => unknown
 [key: string]: unknown
}

export interface SmartTableQuery {
 currentPage: number
 perPage: number
 pageCount: number
 totalRows: number
 offset: number
 limit: number
 filter?: unknown
 sortBy?: string | null
 sortDesc: boolean
 selectedRowKeys: SmartTableKey[]
 selectedColumns: string[]
 extra?: Record<string, unknown>
 signal?: AbortSignal
}

export interface SmartTableProviderResult<T extends SmartTableItem = SmartTableItem> {
 items: T[]
 total?: number
}

export type SmartTableProvider<T extends SmartTableItem = SmartTableItem> =
 (query: SmartTableQuery) =>
 | T[]
 | SmartTableProviderResult<T>
 | Promise<T[] | SmartTableProviderResult<T>>

type PaginationToken = number | 'ellipsis'

function startCase(value: string): string {
 return value
 .replace(/\./g, ' ')
 .replace(/[_-]+/g, ' ')
 .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
 .replace(/\s+/g, ' ')
 .trim()
 .replace(/^./, (c) => c.toUpperCase())
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
 return Object.prototype.toString.call(value) === '[object Object]'
}

function resolveMaybe<T>(value: T | ((...args: any[]) => T), ...args: any[]): T {
 return typeof value === 'function' ? (value as (...args: any[]) => T)(...args) : value
}

function getByPath(record: unknown, path: string): unknown {
 if (!record || typeof record !== 'object') return undefined
 return path.split('.').reduce<unknown>((acc, part) => {
 if (acc == null || typeof acc !== 'object') return undefined
 return (acc as Record<string, unknown>)[part]
 }, record)
}

function normalizeProviderResult<T extends SmartTableItem>(
 result: T[] | SmartTableProviderResult<T>
): SmartTableProviderResult<T> {
 return Array.isArray(result) ? {items: result, total: result.length} : result
}

function compareValues(a: unknown, b: unknown): number {
 if (a == null && b == null) return 0
 if (a == null) return 1
 if (b == null) return -1

 if (a instanceof Date && b instanceof Date) return a.getTime() - b.getTime()
 if (typeof a === 'number' && typeof b === 'number') return a - b
 if (typeof a === 'boolean' && typeof b === 'boolean') return Number(a) - Number(b)

 return String(a).localeCompare(String(b), undefined, {
 numeric: true,
 sensitivity: 'base',
 })
}

function stringifyValue(value: unknown): string {
 if (value == null) return ''
 if (value instanceof Date) return value.toLocaleString()
 if (typeof value === 'string') return value
 if (typeof value === 'number' || typeof value === 'boolean' || typeof value === 'bigint') return String(value)
 if (Array.isArray(value)) return value.map(stringifyValue).join(', ')
 try {
 return JSON.stringify(value)
 } catch {
 return String(value)
 }
}

function isAbortError(error: unknown): boolean {
 return error instanceof DOMException
 ? error.name === 'AbortError'
 : (error as {name?: string})?.name === 'AbortError'
}

function arraysEqual<T>(a: T[], b: T[]): boolean {
 if (a === b) return true
 if (a.length !== b.length) return false
 for (let i = 0; i < a.length; i += 1) {
 if (a[i] !== b[i]) return false
 }
 return true
}

function hasActiveFilterValue(value: unknown): boolean {
 if (value == null) return false
 if (typeof value === 'string') return value.trim() !== ''
 if (Array.isArray(value)) return value.length > 0
 if (isPlainObject(value)) return Object.keys(value).length > 0
 return true
}

function toAttrs(value: unknown): Record<string, unknown> {
 return isPlainObject(value) ? value : {}
}

function buildPaginationTokens(page: number, pageCount: number, windowSize: number): PaginationToken[] {
 if (pageCount <= 1) return [1]

 const tokens: PaginationToken[] = []
 const start = Math.max(1, page - windowSize)
 const end = Math.min(pageCount, page + windowSize)

 if (start > 1) {
 tokens.push(1)
 if (start > 2) tokens.push('ellipsis')
 }

 for (let p = start; p <= end; p += 1) {
 tokens.push(p)
 }

 if (end < pageCount) {
 if (end < pageCount - 1) tokens.push('ellipsis')
 tokens.push(pageCount)
 }

 return tokens
}

export default defineComponent({
 name: 'SmartTable',
 props: {
 items: {
 type: Array as PropType<ReadonlyArray<SmartTableItem>>,
 default: () => [],
 },
 provider: {
 type: Function as PropType<SmartTableProvider | undefined>,
 default: undefined,
 },
 fields: {
 type: Array as PropType<Array<string | SmartTableField>>,
 default: () => [],
 },

 rowKey: {
 type: [String, Function] as PropType<string | ((item: SmartTableItem, index: number) => SmartTableKey)>,
 default: 'id',
 },

 rowSelectionMode: {
 type: String as PropType<SmartTableSelectionMode>,
 default: 'none',
 },
 columnSelectionMode: {
 type: String as PropType<SmartTableSelectionMode>,
 default: 'none',
 },

 selectedRowKeys: {
 type: Array as PropType<SmartTableKey[] | undefined>,
 default: undefined,
 },
 selectedColumns: {
 type: Array as PropType<string[] | undefined>,
 default: undefined,
 },

 selectableColumns: {
 type: Array as PropType<string[] | undefined>,
 default: undefined,
 },

 disableRowSelect: {
 type: Function as PropType<((item: SmartTableItem, index: number) => boolean) | undefined>,
 default: undefined,
 },
 disableColumnSelect: {
 type: Function as PropType<((field: SmartTableField, index: number) => boolean) | undefined>,
 default: undefined,
 },

 clickToSelectRow: {
 type: Boolean,
 default: true,
 },
 preserveSelectionOnRefresh: {
 type: Boolean,
 default: true,
 },
 refreshOnSelectionChange: {
 type: Boolean,
 default: false,
 },

 currentPage: {
 type: Number as PropType<number | undefined>,
 default: undefined,
 },
 perPage: {
 type: Number as PropType<number | undefined>,
 default: undefined,
 },
 serverTotal: {
 type: Number as PropType<number | undefined>,
 default: undefined,
 },
 filter: {
 type: null as unknown as PropType<unknown>,
 default: undefined,
 },
 sortBy: {
 type: String as PropType<string | null | undefined>,
 default: undefined,
 },
 sortDesc: {
 type: Boolean as PropType<boolean | undefined>,
 default: undefined,
 },
 allowSortClear: {
 type: Boolean,
 default: true,
 },

 providerDebounce: {
 type: Number,
 default: 120,
 },
 extraQuery: {
 type: Object as PropType<Record<string, unknown> | undefined>,
 default: undefined,
 },

 busy: {
 type: Boolean,
 default: false,
 },
 busyText: {
 type: String,
 default: 'Loading...',
 },
 emptyText: {
 type: String,
 default: 'No data available',
 },
 emptyFilteredText: {
 type: String,
 default: 'No matching records',
 },
 providerErrorText: {
 type: String,
 default: 'Failed to load data',
 },
 showBusyOverlay: {
 type: Boolean,
 default: true,
 },

 localFilterFn: {
 type: Function as PropType<
 | ((item: SmartTableItem, filter: unknown, fields: SmartTableField[]) => boolean)
 | undefined
 >,
 default: undefined,
 },
 localSortFn: {
 type: Function as PropType<
 | ((a: SmartTableItem, b: SmartTableItem, sortBy: string, sortDesc: boolean, field?: SmartTableField) => number)
 | undefined
 >,
 default: undefined,
 },

 bordered: {
 type: Boolean,
 default: false,
 },
 borderless: {
 type: Boolean,
 default: false,
 },
 striped: {
 type: Boolean,
 default: false,
 },
 stripedColumns: {
 type: Boolean,
 default: false,
 },
 hover: {
 type: Boolean,
 default: false,
 },
 small: {
 type: Boolean,
 default: false,
 },
 dark: {
 type: Boolean,
 default: false,
 },
 fixed: {
 type: Boolean,
 default: false,
 },
 responsive: {
 type: [Boolean, String] as PropType<boolean | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'>,
 default: false,
 },
 stickyHeader: {
 type: [Boolean, String] as PropType<boolean | string>,
 default: false,
 },
 showHeader: {
 type: Boolean,
 default: true,
 },
 caption: {
 type: String,
 default: '',
 },
 captionTop: {
 type: Boolean,
 default: false,
 },

 showPagination: {
 type: Boolean,
 default: false,
 },
 showPageInfo: {
 type: Boolean,
 default: false,
 },
 paginationWindow: {
 type: Number,
 default: 1,
 },
 paginationAlign: {
 type: String as PropType<'start' | 'center' | 'end'>,
 default: 'end',
 },
 paginationSize: {
 type: String as PropType<'' | 'sm' | 'lg'>,
 default: '',
 },

 rowSelectionColumnPosition: {
 type: String as PropType<'start' | 'end'>,
 default: 'start',
 },
 rowSelectionColumnClass: {
 type: [String, Array, Object] as PropType<unknown>,
 default: 'text-center align-middle',
 },
 rowSelectionColumnStyle: {
 type: [String, Object, Array] as PropType<StyleValue>,
 default: () => ({width: '44px'}),
 },
 selectionColumnLabel: {
 type: String,
 default: 'Select',
 },

 highlightSelectedRows: {
 type: Boolean,
 default: true,
 },
 highlightSelectedColumns: {
 type: Boolean,
 default: true,
 },

 wrapperClass: {
 type: [String, Array, Object] as PropType<unknown>,
 default: undefined,
 },
 wrapperStyle: {
 type: [String, Object, Array] as PropType<StyleValue>,
 default: undefined,
 },
 tableClass: {
 type: [String, Array, Object] as PropType<unknown>,
 default: undefined,
 },
 tableStyle: {
 type: [String, Object, Array] as PropType<StyleValue>,
 default: undefined,
 },
 theadClass: {
 type: [String, Array, Object] as PropType<unknown>,
 default: undefined,
 },
 tbodyClass: {
 type: [String, Array, Object] as PropType<unknown>,
 default: undefined,
 },

 rowClass: {
 type: [String, Array, Object, Function] as PropType<unknown | ((item: SmartTableItem, index: number) => unknown)>,
 default: undefined,
 },
 rowStyle: {
 type: [String, Object, Array, Function] as PropType<StyleValue | ((item: SmartTableItem, index: number) => StyleValue)>,
 default: undefined,
 },
 rowAttr: {
 type: [Object, Function] as PropType<Record<string, unknown> | ((item: SmartTableItem, index: number) => Record<string, unknown>)>,
 default: undefined,
 },
 },

 emits: [
 'update:selectedRowKeys',
 'update:selectedColumns',
 'update:currentPage',
 'update:perPage',
 'update:filter',
 'update:sortBy',
 'update:sortDesc',
 'row-selection-change',
 'column-selection-change',
 'sort-change',
 'row-click',
 'head-click',
 'provider-success',
 'provider-error',
 'refreshed',
 ],

 setup(props, {emit, expose}) {
 const uid = `smart-table-${getCurrentInstance()?.uid ?? Math.random().toString(36).slice(2)}`
 const objectKeyMap = new WeakMap<object, SmartTableKey>()
 const rowCache = new Map<SmartTableKey, SmartTableItem>()
 let autoKeySeed = 0

 const selectedRowKeysState = ref<SmartTableKey[]>(props.selectedRowKeys ? [...props.selectedRowKeys] : [])
 const selectedColumnsState = ref<string[]>(props.selectedColumns ? [...props.selectedColumns] : [])
 const currentPageState = ref<number>(Math.max(1, props.currentPage ?? 1))
 const perPageState = ref<number>(Math.max(1, props.perPage ?? 25))
 const filterState = ref<unknown>(props.filter)
 const sortByState = ref<string | null>(props.sortBy ?? null)
 const sortDescState = ref<boolean>(Boolean(props.sortDesc))
 const providerItems = ref<SmartTableItem[]>([])
 const providerTotal = ref(0)
 const providerBusy = ref(false)
 const providerError = ref<unknown>(null)
 const rowSelectAllRef = ref<HTMLInputElement | null>(null)

 let refreshTimer: ReturnType<typeof setTimeout> | null = null
 let requestId = 0
 let abortController: AbortController | null = null

 watch(() => props.selectedRowKeys, (value) => {
 if (value !== undefined) selectedRowKeysState.value = [...value]
 })

 watch(() => props.selectedColumns, (value) => {
 if (value !== undefined) selectedColumnsState.value = [...value]
 })

 watch(() => props.currentPage, (value) => {
 if (value !== undefined) currentPageState.value = Math.max(1, value)
 })

 watch(() => props.perPage, (value) => {
 if (value !== undefined) perPageState.value = Math.max(1, value)
 })

 watch(() => props.filter, (value) => {
 filterState.value = value
 })

 watch(() => props.sortBy, (value) => {
 if (value !== undefined) sortByState.value = value ?? null
 })

 watch(() => props.sortDesc, (value) => {
 if (value !== undefined) sortDescState.value = Boolean(value)
 })

 const isProviderMode = computed(() => typeof props.provider === 'function')
 const hasRowSelection = computed(() => props.rowSelectionMode !== 'none')
 const hasColumnSelection = computed(() => props.columnSelectionMode !== 'none')
 const isFilterActive = computed(() => hasActiveFilterValue(filterState.value))

 function getRowKey(item: SmartTableItem, index = -1): SmartTableKey {
 if (typeof props.rowKey === 'function') {
 return props.rowKey(item, index)
 }

 if (typeof props.rowKey === 'string' && props.rowKey) {
 const value = getByPath(item, props.rowKey)
 if (typeof value === 'string' || typeof value === 'number') return value
 }

 if (typeof item === 'object' && item !== null) {
 const existing = objectKeyMap.get(item)
 if (existing !== undefined) return existing
 const generated = `__smart_row_${++autoKeySeed}`
 objectKeyMap.set(item, generated)
 return generated
 }

 return `__smart_row_${++autoKeySeed}`
 }

 function normalizeField(field: string | SmartTableField): SmartTableField {
 if (typeof field === 'string') {
 return {
 key: field,
 label: startCase(field),
 visible: true,
 sortable: false,
 filterable: true,
 selectable: true,
 }
 }

 return {
 label: startCase(field.key),
 visible: true,
 sortable: false,
 filterable: true,
 selectable: true,
 ...field,
 }
 }

 const sourceItems = computed<SmartTableItem[]>(() => [...props.items])

 const normalizedFields = computed<SmartTableField[]>(() => {
 if (props.fields.length > 0) return props.fields.map(normalizeField)

 const sample = (isProviderMode.value ? providerItems.value : sourceItems.value)[0]
 if (!sample || typeof sample !== 'object') return []

 return Object.keys(sample).map((key) => normalizeField(key))
 })

 const visibleFields = computed<SmartTableField[]>(() =>
 normalizedFields.value.filter((field) => field.visible !== false)
 )

 function getCellValue(item: SmartTableItem, field: SmartTableField, index: number): unknown {
 return getByPath(item, field.key)
 }

 function formatCellValue(item: SmartTableItem, field: SmartTableField, index: number): string {
 const raw = getCellValue(item, field, index)
 const formatted = field.formatter ? field.formatter(raw, item, index, field) : raw
 return stringifyValue(formatted)
 }

 function defaultFilter(item: SmartTableItem, filter: unknown, fields: SmartTableField[]): boolean {
 if (!hasActiveFilterValue(filter)) return true

 const searchableFields = fields.filter((field) => field.filterable !== false)

 if (typeof filter === 'function') {
 return Boolean((filter as (row: SmartTableItem) => boolean)(item))
 }

 if (typeof filter === 'string') {
 const term = filter.trim().toLowerCase()
 return searchableFields.some((field, index) => {
 const value = field.filterValue
 ? field.filterValue(item, index, field)
 : getCellValue(item, field, index)
 return stringifyValue(value).toLowerCase().includes(term)
 })
 }

 if (isPlainObject(filter)) {
 return Object.entries(filter).every(([key, value]) => {
 const current = getByPath(item, key)
 return stringifyValue(current).toLowerCase().includes(stringifyValue(value).toLowerCase())
 })
 }

 return true
 }

 const filteredStaticItems = computed<SmartTableItem[]>(() => {
 if (isProviderMode.value) return providerItems.value
 if (!isFilterActive.value) return sourceItems.value

 const predicate = props.localFilterFn
 ? (item: SmartTableItem) => props.localFilterFn!(item, filterState.value, visibleFields.value)
 : (item: SmartTableItem) => defaultFilter(item, filterState.value, visibleFields.value)

 return sourceItems.value.filter(predicate)
 })

 const sortedStaticItems = computed<SmartTableItem[]>(() => {
 if (isProviderMode.value) return providerItems.value
 if (!sortByState.value) return filteredStaticItems.value

 const field = visibleFields.value.find((f) => f.key === sortByState.value)
 const rows = [...filteredStaticItems.value]

 const compare = props.localSortFn
 ? (a: SmartTableItem, b: SmartTableItem) =>
 props.localSortFn!(a, b, sortByState.value!, sortDescState.value, field)
 : (a: SmartTableItem, b: SmartTableItem) => {
 const aValue = field?.sortValue ? field.sortValue(a, 0, field) : getByPath(a, sortByState.value!)
 const bValue = field?.sortValue ? field.sortValue(b, 0, field) : getByPath(b, sortByState.value!)

 if (field?.sortCompare) {
 return field.sortCompare(aValue, bValue, a, b, sortDescState.value, field)
 }

 return compareValues(aValue, bValue)
 }

 rows.sort((a, b) => {
 const result = compare(a, b)
 return sortDescState.value ? -result : result
 })

 return rows
 })

 const isServerSide = computed(() => props.serverTotal !== undefined)

 const renderedItems = computed<SmartTableItem[]>(() => {
 if (isProviderMode.value) return providerItems.value
 // When serverTotal is provided, assume parent handles pagination - display all items
 if (isServerSide.value) return sortedStaticItems.value
 if (!perPageState.value || perPageState.value < 1) return sortedStaticItems.value

 const start = (currentPageState.value - 1) * perPageState.value
 return sortedStaticItems.value.slice(start, start + perPageState.value)
 })

 const totalRows = computed<number>(() => {
 if (props.serverTotal !== undefined) return props.serverTotal
 return isProviderMode.value ? providerTotal.value : filteredStaticItems.value.length
 })

 const pageCount = computed<number>(() => {
 if (!perPageState.value || perPageState.value < 1) return totalRows.value > 0 ? 1 : 1
 return Math.max(1, Math.ceil(totalRows.value / perPageState.value))
 })

 const colspan = computed<number>(() => visibleFields.value.length + (hasRowSelection.value ? 1 : 0))
 const computedBusy = computed<boolean>(() => props.busy || providerBusy.value)

 function setCurrentPage(page: number): void {
 const next = Math.min(Math.max(1, page), Math.max(1, pageCount.value))
 currentPageState.value = next
 emit('update:currentPage', next)
 }

 function setPerPage(perPage: number): void {
 const next = Math.max(0, perPage)
 perPageState.value = next
 emit('update:perPage', next)
 }

 function setFilter(value: unknown): void {
 filterState.value = value
 emit('update:filter', value)
 setCurrentPage(1)
 }

 function setSort(sortBy: string | null, sortDesc: boolean): void {
 sortByState.value = sortBy
 sortDescState.value = sortDesc
 emit('update:sortBy', sortBy)
 emit('update:sortDesc', sortDesc)
 emit('sort-change', {sortBy, sortDesc})
 }

 function clearSort(): void {
 setSort(null, false)
 }

 function toggleSortForField(field: SmartTableField): void {
 if (!field.sortable) return

 if (sortByState.value !== field.key) {
 setSort(field.key, false)
 return
 }

 if (!sortDescState.value) {
 setSort(field.key, true)
 return
 }

 if (props.allowSortClear) {
 clearSort()
 return
 }

 setSort(field.key, false)
 }

 watch(filterState, () => {
 if (currentPageState.value !== 1) setCurrentPage(1)
 }, {deep: true})

 watch([totalRows, perPageState], () => {
 if (currentPageState.value > pageCount.value) setCurrentPage(pageCount.value)
 }, {immediate: true})

 function normalizeSelectedRowKeys(keys: SmartTableKey[]): SmartTableKey[] {
 if (props.rowSelectionMode === 'none') return []
 const unique = [...new Set(keys)]
 return props.rowSelectionMode === 'single' ? unique.slice(0, 1) : unique
 }

 function isColumnSelectable(field: SmartTableField, index: number): boolean {
 if (props.columnSelectionMode === 'none') return false
 if (field.visible === false) return false
 if (field.selectable === false) return false
 if (props.selectableColumns && !props.selectableColumns.includes(field.key)) return false
 return !props.disableColumnSelect?.(field, index)
 }

 function normalizeSelectedColumns(keys: string[]): string[] {
 if (props.columnSelectionMode === 'none') return []

 const allowed = new Set(
 visibleFields.value
 .map((field, index) => ({field, index}))
 .filter(({field, index}) => isColumnSelectable(field, index))
 .map(({field}) => field.key)
 )

 const unique = [...new Set(keys)].filter((key) => allowed.has(key))
 return props.columnSelectionMode === 'single' ? unique.slice(0, 1) : unique
 }

 const selectedRowKeysSet = computed(() => new Set(selectedRowKeysState.value))
 const selectedColumnsSet = computed(() => new Set(selectedColumnsState.value))

 const selectedRows = computed<SmartTableItem[]>(() =>
 selectedRowKeysState.value
 .map((key) => rowCache.get(key))
 .filter((item): item is SmartTableItem => Boolean(item))
 )

 function emitRowSelectionChange(): void {
 emit('row-selection-change', {
 keys: [...selectedRowKeysState.value],
 rows: [...selectedRows.value],
 })
 }

 function emitColumnSelectionChange(): void {
 emit('column-selection-change', {
 columns: [...selectedColumnsState.value],
 fields: visibleFields.value.filter((field) => selectedColumnsSet.value.has(field.key)),
 })
 }

 function setSelectedRowKeys(keys: SmartTableKey[]): void {
 const next = normalizeSelectedRowKeys(keys)
 if (arraysEqual(next, selectedRowKeysState.value)) return
 selectedRowKeysState.value = next
 emit('update:selectedRowKeys', [...next])
 emitRowSelectionChange()
 }

 function setSelectedColumns(keys: string[]): void {
 const next = normalizeSelectedColumns(keys)
 if (arraysEqual(next, selectedColumnsState.value)) return
 selectedColumnsState.value = next
 emit('update:selectedColumns', [...next])
 emitColumnSelectionChange()
 }

 watch(() => props.rowSelectionMode, () => {
 setSelectedRowKeys(selectedRowKeysState.value)
 }, {immediate: true})

 watch([visibleFields, () => props.columnSelectionMode], () => {
 setSelectedColumns(selectedColumnsState.value)
 }, {immediate: true, deep: true})

 function isRowSelectable(item: SmartTableItem, index: number): boolean {
 if (props.rowSelectionMode === 'none') return false
 return !props.disableRowSelect?.(item, index)
 }

 function isRowSelected(item: SmartTableItem, index: number): boolean {
 return selectedRowKeysSet.value.has(getRowKey(item, index))
 }

 function isColumnSelected(key: string): boolean {
 return selectedColumnsSet.value.has(key)
 }

 function toggleRowSelection(item: SmartTableItem, index: number, force?: boolean): void {
 if (!isRowSelectable(item, index)) return

 const key = getRowKey(item, index)
 const isSelected = selectedRowKeysSet.value.has(key)
 const nextValue = force ?? !isSelected

 if (props.rowSelectionMode === 'single') {
 setSelectedRowKeys(nextValue ? [key] : [])
 return
 }

 const next = nextValue
 ? [...selectedRowKeysState.value, key]
 : selectedRowKeysState.value.filter((current) => current !== key)

 setSelectedRowKeys(next)
 }

 function toggleColumnSelection(key: string, force?: boolean): void {
 const fieldIndex = visibleFields.value.findIndex((field) => field.key === key)
 const field = visibleFields.value[fieldIndex]
 if (!field || !isColumnSelectable(field, fieldIndex)) return

 const isSelected = selectedColumnsSet.value.has(key)
 const nextValue = force ?? !isSelected

 if (props.columnSelectionMode === 'single') {
 setSelectedColumns(nextValue ? [key] : [])
 return
 }

 const next = nextValue
 ? [...selectedColumnsState.value, key]
 : selectedColumnsState.value.filter((current) => current !== key)

 setSelectedColumns(next)
 }

 function clearSelectedRows(): void {
 setSelectedRowKeys([])
 }

 function clearSelectedColumns(): void {
 setSelectedColumns([])
 }

 function selectAllColumns(): void {
 if (props.columnSelectionMode !== 'multiple') return
 setSelectedColumns(
 visibleFields.value
 .map((field, index) => ({field, index}))
 .filter(({field, index}) => isColumnSelectable(field, index))
 .map(({field}) => field.key)
 )
 }

 function resolveRowIndex(localIndex: number): number {
 if (!perPageState.value || perPageState.value < 1) return localIndex
 return (currentPageState.value - 1) * perPageState.value + localIndex
 }

 const visibleSelectableRowKeys = computed<SmartTableKey[]>(() =>
 renderedItems.value
 .map((item, localIndex) => ({item, index: resolveRowIndex(localIndex)}))
 .filter(({item, index}) => isRowSelectable(item, index))
 .map(({item, index}) => getRowKey(item, index))
 )

 const allVisibleRowsSelected = computed<boolean>(() =>
 visibleSelectableRowKeys.value.length > 0 &&
 visibleSelectableRowKeys.value.every((key) => selectedRowKeysSet.value.has(key))
 )

 const someVisibleRowsSelected = computed<boolean>(() =>
 visibleSelectableRowKeys.value.some((key) => selectedRowKeysSet.value.has(key)) &&
 !allVisibleRowsSelected.value
 )

 function selectAllVisibleRows(): void {
 if (props.rowSelectionMode !== 'multiple') return
 const next = [...new Set([...selectedRowKeysState.value, ...visibleSelectableRowKeys.value])]
 setSelectedRowKeys(next)
 }

 function clearVisibleRows(): void {
 if (props.rowSelectionMode !== 'multiple') return
 const visible = new Set(visibleSelectableRowKeys.value)
 setSelectedRowKeys(selectedRowKeysState.value.filter((key) => !visible.has(key)))
 }

 function toggleAllVisibleRows(force?: boolean): void {
 const next = force ?? !allVisibleRowsSelected.value
 if (next) selectAllVisibleRows()
 else clearVisibleRows()
 }

 watch([someVisibleRowsSelected, allVisibleRowsSelected], () => {
 if (rowSelectAllRef.value) {
 rowSelectAllRef.value.indeterminate = someVisibleRowsSelected.value
 }
 }, {immediate: true})

 function rebuildStaticCache(items: SmartTableItem[]): void {
 rowCache.clear()
 const validKeys = new Set<SmartTableKey>()

 items.forEach((item, index) => {
 const key = getRowKey(item, index)
 validKeys.add(key)
 rowCache.set(key, item)
 })

 const pruned = selectedRowKeysState.value.filter((key) => validKeys.has(key))
 if (!arraysEqual(pruned, selectedRowKeysState.value)) {
 setSelectedRowKeys(pruned)
 }
 }

 function updateProviderCache(items: SmartTableItem[]): void {
 if (!props.preserveSelectionOnRefresh) {
 rowCache.clear()
 clearSelectedRows()
 }

 items.forEach((item, index) => {
 rowCache.set(getRowKey(item, resolveRowIndex(index)), item)
 })
 }

 watch(sourceItems, (items) => {
 if (!isProviderMode.value) rebuildStaticCache(items)
 }, {immediate: true, deep: true})

 watch(providerItems, (items) => {
 if (isProviderMode.value) updateProviderCache(items)
 }, {immediate: true, deep: true})

 function buildQuery(): SmartTableQuery {
 const offset = perPageState.value > 0 ? (currentPageState.value - 1) * perPageState.value : 0
 return {
 currentPage: currentPageState.value,
 perPage: perPageState.value,
 pageCount: pageCount.value,
 totalRows: totalRows.value,
 offset,
 limit: perPageState.value,
 filter: filterState.value,
 sortBy: sortByState.value,
 sortDesc: sortDescState.value,
 selectedRowKeys: [...selectedRowKeysState.value],
 selectedColumns: [...selectedColumnsState.value],
 extra: props.extraQuery,
 signal: abortController?.signal,
 }
 }

 async function refresh(): Promise<SmartTableItem[]> {
 if (!props.provider) {
 emit('refreshed', {
 provider: false,
 items: [...renderedItems.value],
 total: totalRows.value,
 })
 return renderedItems.value
 }

 if (refreshTimer) {
 clearTimeout(refreshTimer)
 refreshTimer = null
 }

 requestId += 1
 const currentRequestId = requestId

 abortController?.abort()
 abortController = typeof AbortController !== 'undefined' ? new AbortController() : null

 providerBusy.value = true
 providerError.value = null

 const query = buildQuery()
 query.signal = abortController?.signal

 try {
 const result = normalizeProviderResult(await props.provider(query))
 if (currentRequestId !== requestId) return providerItems.value

 providerItems.value = result.items
 providerTotal.value = result.total ?? result.items.length

 emit('provider-success', {
 query,
 items: [...result.items],
 total: providerTotal.value,
 })

 emit('refreshed', {
 provider: true,
 query,
 items: [...result.items],
 total: providerTotal.value,
 })

 return result.items
 } catch (error) {
 if (isAbortError(error)) return providerItems.value
 if (currentRequestId !== requestId) return providerItems.value

 providerError.value = error
 emit('provider-error', error)
 throw error
 } finally {
 if (currentRequestId === requestId) {
 providerBusy.value = false
 }
 }
 }

 function scheduleRefresh(): void {
 if (!props.provider) return

 if (refreshTimer) clearTimeout(refreshTimer)

 if (props.providerDebounce <= 0) {
 void refresh()
 return
 }

 refreshTimer = setTimeout(() => {
 void refresh()
 }, props.providerDebounce)
 }

 const providerWatchState = computed(() => ({
 enabled: isProviderMode.value,
 provider: props.provider,
 currentPage: currentPageState.value,
 perPage: perPageState.value,
 filter: filterState.value,
 sortBy: sortByState.value,
 sortDesc: sortDescState.value,
 extraQuery: props.extraQuery,
 selectedRowKeys: props.refreshOnSelectionChange ? [...selectedRowKeysState.value] : undefined,
 selectedColumns: props.refreshOnSelectionChange ? [...selectedColumnsState.value] : undefined,
 }))

 watch(providerWatchState, (state) => {
 if (state.enabled) scheduleRefresh()
 }, {deep: true, immediate: true})

 watch(isProviderMode, (enabled) => {
 if (!enabled) {
 abortController?.abort()
 providerBusy.value = false
 providerError.value = null
 providerItems.value = []
 providerTotal.value = 0
 rebuildStaticCache(sourceItems.value)
 }
 }, {immediate: true})

 onBeforeUnmount(() => {
 if (refreshTimer) clearTimeout(refreshTimer)
 abortController?.abort()
 })

 function isInteractiveTarget(target: EventTarget | null): boolean {
 const el = target as HTMLElement | null
 return Boolean(
 el?.closest(
 'a,button,input,select,textarea,label,[role="button"],[contenteditable="true"],.dropdown-toggle,.dropdown-item'
 )
 )
 }

 function onRowClick(item: SmartTableItem, index: number, event: MouseEvent): void {
 if (props.clickToSelectRow && hasRowSelection.value && !isInteractiveTarget(event.target)) {
 toggleRowSelection(item, index)
 }
 emit('row-click', item, index, event)
 }

 function onRowKeydown(item: SmartTableItem, index: number, event: KeyboardEvent): void {
 if (!props.clickToSelectRow || !hasRowSelection.value) return
 if (isInteractiveTarget(event.target)) return
 toggleRowSelection(item, index)
 }

 function onHeaderClick(field: SmartTableField, index: number, event: MouseEvent): void {
 if (field.sortable && !isInteractiveTarget(event.target)) {
 toggleSortForField(field)
 }
 emit('head-click', field.key, field, index, event)
 }

 function onHeaderKeydown(field: SmartTableField, index: number, event: KeyboardEvent): void {
 if (!field.sortable) return
 toggleSortForField(field)
 emit('head-click', field.key, field, index, event)
 }

 function onRowSelectControlClick(item: SmartTableItem, index: number, event: MouseEvent): void {
 event.stopPropagation()
 if (props.rowSelectionMode === 'single' && isRowSelected(item, index)) {
 event.preventDefault()
 toggleRowSelection(item, index, false)
 }
 }

 function onRowSelectControlChange(item: SmartTableItem, index: number, event: Event): void {
 event.stopPropagation()
 toggleRowSelection(item, index, (event.target as HTMLInputElement).checked)
 }

 function onColumnSelectControlClick(field: SmartTableField, index: number, event: MouseEvent): void {
 event.stopPropagation()
 if (props.columnSelectionMode === 'single' && isColumnSelected(field.key)) {
 event.preventDefault()
 toggleColumnSelection(field.key, false)
 }
 }

 function onColumnSelectControlChange(field: SmartTableField, index: number, event: Event): void {
 event.stopPropagation()
 toggleColumnSelection(field.key, (event.target as HTMLInputElement).checked)
 }

 function getSortIndicator(field: SmartTableField): string {
 if (!field.sortable) return ''
 if (sortByState.value !== field.key) return '↕'
 return sortDescState.value ? '↓' : '↑'
 }

 function getAriaSort(field: SmartTableField): 'ascending' | 'descending' | 'none' | undefined {
 if (!field.sortable) return undefined
 if (sortByState.value !== field.key) return 'none'
 return sortDescState.value ? 'descending' : 'ascending'
 }

 function isHeaderFocusable(field: SmartTableField): boolean {
 return Boolean(field.sortable)
 }

 function isRowFocusable(item: SmartTableItem, index: number): boolean {
 return Boolean(props.clickToSelectRow && isRowSelectable(item, index))
 }

 function alignClass(align?: 'start' | 'center' | 'end'): string | undefined {
 return align ? `text-${align}` : undefined
 }

 function getFieldThClass(field: SmartTableField, index: number): unknown[] {
 return [
 field.class,
 resolveMaybe(field.thClass as any, field, index),
 alignClass(field.align),
 props.highlightSelectedColumns && isColumnSelected(field.key) && 'smart-table__column--selected',
 ]
 }

 function getFieldTdClass(field: SmartTableField, item: SmartTableItem, index: number, colIndex: number): unknown[] {
 const value = getCellValue(item, field, index)
 return [
 field.class,
 resolveMaybe(field.tdClass as any, value, item, index, field),
 alignClass(field.align),
 props.highlightSelectedColumns && isColumnSelected(field.key) && 'smart-table__column--selected',
 ]
 }

 function getFieldThStyle(field: SmartTableField, index: number): StyleValue {
 return resolveMaybe(field.thStyle as any, field, index)
 }

 function getFieldTdStyle(field: SmartTableField, item: SmartTableItem, index: number, colIndex: number): StyleValue {
 const value = getCellValue(item, field, index)
 return resolveMaybe(field.tdStyle as any, value, item, index, field)
 }

 function getFieldThAttrs(field: SmartTableField, index: number): Record<string, unknown> {
 return toAttrs(resolveMaybe(field.thAttr as any, field, index))
 }

 function getFieldTdAttrs(field: SmartTableField, item: SmartTableItem, index: number, colIndex: number): Record<string, unknown> {
 const value = getCellValue(item, field, index)
 return toAttrs(resolveMaybe(field.tdAttr as any, value, item, index, field))
 }

 function getRowClass(item: SmartTableItem, index: number): unknown[] {
 return [
 resolveMaybe(props.rowClass as any, item, index),
 props.highlightSelectedRows && isRowSelected(item, index) && 'smart-table__row--selected',
 ]
 }

 function getRowStyle(item: SmartTableItem, index: number): StyleValue {
 return resolveMaybe(props.rowStyle as any, item, index)
 }

 function getRowAttrs(item: SmartTableItem, index: number): Record<string, unknown> {
 return {
 ...toAttrs(resolveMaybe(props.rowAttr as any, item, index)),
 ...(hasRowSelection.value ? {'aria-selected': String(isRowSelected(item, index))} : {}),
 'data-row-key': String(getRowKey(item, index)),
 }
 }

 function getProviderErrorMessage(): string {
 const message = (providerError.value as {message?: string} | null)?.message
 return message || props.providerErrorText
 }

 const responsiveClass = computed<string | null>(() => {
 if (props.responsive === true) return 'table-responsive'
 if (typeof props.responsive === 'string' && props.responsive) return `table-responsive-${props.responsive}`
 return null
 })

 const viewportStyle = computed<StyleValue>(() => {
 if (!props.stickyHeader) return undefined
 return {
 maxHeight: typeof props.stickyHeader === 'string' ? props.stickyHeader : '60vh',
 }
 })

 const tableClasses = computed(() => [
 'table',
 props.bordered && 'table-bordered',
 props.borderless && 'table-borderless',
 props.striped && 'table-striped',
 props.stripedColumns && 'table-striped-columns',
 props.hover && 'table-hover',
 props.small && 'table-sm',
 props.dark && 'table-dark',
 props.fixed && 'smart-table__table--fixed',
 props.tableClass,
 ])

 const pageInfoText = computed(() => {
 if (totalRows.value === 0) return '0 rows'

 // When server-side pagination is active, use actual rendered items count
 if (isServerSide.value) {
 return `Showing 1-${renderedItems.value.length} of ${totalRows.value}`
 }

 if (!perPageState.value || perPageState.value < 1) {
 return `Showing 1-${renderedItems.value.length} of ${totalRows.value}`
 }

 const start = (currentPageState.value - 1) * perPageState.value + 1
 const end = Math.min(start + renderedItems.value.length - 1, totalRows.value)
 return `Showing ${start}-${end} of ${totalRows.value}`
 })

 const showPaginationControls = computed(() =>
 props.showPagination &&
 perPageState.value > 0 &&
 pageCount.value > 1
 )

 const paginationItems = computed<PaginationToken[]>(() =>
 buildPaginationTokens(currentPageState.value, pageCount.value, Math.max(0, props.paginationWindow))
 )

 const paginationSizeClass = computed(() =>
 props.paginationSize ? `pagination-${props.paginationSize}` : null
 )

 const paginationNavClass = computed(() => ({
 'ms-auto': props.paginationAlign === 'end',
 'me-auto': props.paginationAlign === 'start',
 'mx-auto': props.paginationAlign === 'center',
 }))

 function goToPage(page: number): void {
 setCurrentPage(page)
 }

 function nextPage(): void {
 goToPage(currentPageState.value + 1)
 }

 function prevPage(): void {
 goToPage(currentPageState.value - 1)
 }

 const slotApi = computed(() => ({
 items: [...renderedItems.value],
 rawItems: isProviderMode.value ? [...providerItems.value] : [...sourceItems.value],
 fields: [...visibleFields.value],
 busy: computedBusy.value,
 error: providerError.value,
 currentPage: currentPageState.value,
 perPage: perPageState.value,
 pageCount: pageCount.value,
 totalRows: totalRows.value,
 filter: filterState.value,
 sortBy: sortByState.value,
 sortDesc: sortDescState.value,
 selectedRowKeys: [...selectedRowKeysState.value],
 selectedColumns: [...selectedColumnsState.value],
 selectedRows: [...selectedRows.value],
 isProviderMode: isProviderMode.value,
 refresh,
 clearSort,
 setSort,
 setFilter,
 setCurrentPage,
 setPerPage,
 goToPage,
 nextPage,
 prevPage,
 clearSelectedRows,
 clearSelectedColumns,
 selectAllVisibleRows,
 toggleAllVisibleRows,
 selectAllColumns,
 toggleRowSelection,
 toggleColumnSelection,
 }))

 expose({
 refresh,
 clearSort,
 setSort,
 setFilter,
 setCurrentPage,
 setPerPage,
 goToPage,
 nextPage,
 prevPage,
 clearSelectedRows,
 clearSelectedColumns,
 selectAllVisibleRows,
 toggleAllVisibleRows,
 selectAllColumns,
 toggleRowSelection,
 toggleColumnSelection,
 selectedRowKeys: selectedRowKeysState,
 selectedColumns: selectedColumnsState,
 selectedRows,
 busy: computedBusy,
 error: providerError,
 totalRows,
 pageCount,
 })

 return {
 uid,
 providerError,
 rowSelectAllRef,

 selectedRowKeysState,
 selectedColumnsState,
 currentPageState,
 perPageState,
 filterState,
 sortByState,
 sortDescState,

 visibleFields,
 renderedItems,
 totalRows,
 pageCount,
 colspan,
 computedBusy,
 isFilterActive,

 hasRowSelection,
 hasColumnSelection,

 responsiveClass,
 viewportStyle,
 tableClasses,

 pageInfoText,
 showPaginationControls,
 paginationItems,
 paginationSizeClass,
 paginationNavClass,

 slotApi,

 startCase,
 getRowKey,
 getCellValue,
 formatCellValue,
 resolveRowIndex,

 setCurrentPage,
 setPerPage,
 setFilter,
 setSort,
 clearSort,
 toggleSortForField,
 goToPage,
 nextPage,
 prevPage,

 isRowSelectable,
 isRowSelected,
 isColumnSelectable,
 isColumnSelected,
 toggleRowSelection,
 toggleColumnSelection,
 clearSelectedRows,
 clearSelectedColumns,
 selectAllVisibleRows,
 toggleAllVisibleRows,
 allVisibleRowsSelected,
 someVisibleRowsSelected,
 selectAllColumns,

 onRowClick,
 onRowKeydown,
 onHeaderClick,
 onHeaderKeydown,
 onRowSelectControlClick,
 onRowSelectControlChange,
 onColumnSelectControlClick,
 onColumnSelectControlChange,

 getSortIndicator,
 getAriaSort,
 isHeaderFocusable,
 isRowFocusable,
 getFieldThClass,
 getFieldTdClass,
 getFieldThStyle,
 getFieldTdStyle,
 getFieldThAttrs,
 getFieldTdAttrs,
 getRowClass,
 getRowStyle,
 getRowAttrs,
 getProviderErrorMessage,
 }
 },
})
</script>

<style scoped>
.smart-table__viewport.table-responsive,
.smart-table__viewport[class*='table-responsive-'] {
 overflow-x: auto;
}

.smart-table__viewport--sticky {
 overflow-y: auto;
}

.smart-table__table--fixed {
 table-layout: fixed;
}

.smart-table thead th {
 vertical-align: middle;
}

.smart-table__viewport--sticky thead th {
 position: sticky;
 top: 0;
 z-index: 2;
 background: var(--bs-table-bg, var(--bs-body-bg));
}

.smart-table__head-content {
 display: flex;
 align-items: center;
 gap: 0.5rem;
 min-width: 0;
}

.smart-table__head-content--sortable {
 user-select: none;
 cursor: pointer;
}

.smart-table__head-label {
 min-width: 0;
}

.smart-table__sort-indicator {
 font-size: 0.75rem;
 line-height: 1;
 flex: 0 0 auto;
}

.smart-table__selection-control {
 cursor: pointer;
}

.smart-table__overlay {
 position: absolute;
 inset: 0;
 z-index: 4;
 display: flex;
 align-items: center;
 justify-content: center;
 background: rgba(var(--bs-body-bg-rgb, 255, 255, 255), 0.45);
 backdrop-filter: blur(1px);
}

.smart-table__row--selected > * {
 background-color: var(--bs-table-active-bg);
 color: var(--bs-table-active-color);
}

.smart-table__column--selected {
 background-color: var(--bs-table-active-bg);
}

.smart-table .page-link {
 user-select: none;
}
</style>
