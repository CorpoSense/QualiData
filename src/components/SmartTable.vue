<script lang="ts">
import {BTable} from 'bootstrap-vue-next'
import {
 computed,
 defineComponent,
 getCurrentInstance,
 h,
 mergeProps,
 onBeforeUnmount,
 ref,
 watch,
 type PropType,
 type VNodeChild,
} from 'vue'

export type SmartTableKey = string | number
export type SmartTableSelectionMode = 'none' | 'single' | 'multiple'
export type SmartTableItem = Record<string, unknown>

export interface SmartTableField<T extends SmartTableItem = SmartTableItem> {
 key: string
 label?: string
 sortable?: boolean
 selectable?: boolean
 visible?: boolean
 class?: unknown
 thClass?: unknown
 tdClass?: unknown
 thStyle?: string | Record<string, string>
 tdStyle?: string | Record<string, string>
 formatter?: (value: unknown, key: string, item: T) => unknown
 [key: string]: unknown
}

export interface SmartTableQuery {
 currentPage: number
 perPage: number
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
 (ctx: SmartTableQuery) =>
 | T[]
 | SmartTableProviderResult<T>
 | Promise<T[] | SmartTableProviderResult<T>>

const INTERNAL_SELECTION_FIELD = '__smart_table_select__'

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

function shallowEqualArray<T>(a: T[], b: T[]): boolean {
 if (a === b) return true
 if (a.length !== b.length) return false
 for (let i = 0; i < a.length; i++) {
 if (a[i] !== b[i]) return false
 }
 return true
}

function mergeMaybeCallableClass(base: unknown, extra: unknown): unknown {
 if (!extra) return base
 if (typeof base === 'function') {
 return (...args: unknown[]) => [base(...args), extra]
 }
 return [base, extra]
}

function getByPath(record: unknown, path: string): unknown {
 if (!record || typeof record !== 'object') return undefined
 return path.split('.').reduce<unknown>((acc, segment) => {
 if (acc == null || typeof acc !== 'object') return undefined
 return (acc as Record<string, unknown>)[segment]
 }, record)
}

function compareValues(a: unknown, b: unknown): number {
 if (a == null && b == null) return 0
 if (a == null) return 1
 if (b == null) return -1

 if (a instanceof Date && b instanceof Date) {
 return a.getTime() - b.getTime()
 }

 if (typeof a === 'number' && typeof b === 'number') {
 return a - b
 }

 if (typeof a === 'boolean' && typeof b === 'boolean') {
 return Number(a) - Number(b)
 }

 return String(a).localeCompare(String(b), undefined, {
 numeric: true,
 sensitivity: 'base',
 })
}

function normalizeProviderResult<T extends SmartTableItem>(
 result: T[] | SmartTableProviderResult<T>
): SmartTableProviderResult<T> {
 return Array.isArray(result) ? {items: result, total: result.length} : result
}

function isAbortError(error: unknown): boolean {
 return error instanceof DOMException
 ? error.name === 'AbortError'
 : (error as {name?: string})?.name === 'AbortError'
}

export default defineComponent({
 name: 'SmartTable',
 inheritAttrs: false,
 props: {
 items: {
 type: [Array, Function] as PropType<ReadonlyArray<SmartTableItem> | SmartTableProvider>,
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

 currentPage: {
 type: Number as PropType<number | undefined>,
 default: undefined,
 },
 perPage: {
 type: Number as PropType<number | undefined>,
 default: undefined,
 },
 filter: {
 type: null as PropType<unknown>,
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

 rowSelectionColumnPosition: {
 type: String as PropType<'start' | 'end'>,
 default: 'start',
 },
 rowSelectionFieldKey: {
 type: String,
 default: INTERNAL_SELECTION_FIELD,
 },
 rowSelectionColumnStyle: {
 type: [String, Object] as PropType<string | Record<string, string>>,
 default: () => ({width: '44px'}),
 },
 rowSelectionColumnClass: {
 type: [String, Array, Object] as PropType<unknown>,
 default: 'text-center align-middle',
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
 | ((a: SmartTableItem, b: SmartTableItem, sortBy: string, sortDesc: boolean) => number)
 | undefined
 >,
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
 'sort-changed',

 'row-clicked',
 'head-clicked',

 'provider-success',
 'provider-error',
 'refreshed',
 ],

 setup(props, {attrs, slots, emit, expose}) {
 const uid = `smart-table-${getCurrentInstance()?.uid ?? Math.random().toString(36).slice(2)}`
 const rowCache = new Map<SmartTableKey, SmartTableItem>()

 const selectedRowKeysState = ref<SmartTableKey[]>(props.selectedRowKeys ? [...props.selectedRowKeys] : [])
 const selectedColumnsState = ref<string[]>(props.selectedColumns ? [...props.selectedColumns] : [])
 const currentPageState = ref<number>(props.currentPage ?? 1)
 const perPageState = ref<number>(props.perPage ?? 0)
 const filterState = ref<unknown>(props.filter)
 const sortByState = ref<string | null>(props.sortBy ?? null)
 const sortDescState = ref<boolean>(props.sortDesc ?? false)

 watch(() => props.selectedRowKeys, (v) => {
 if (v !== undefined) selectedRowKeysState.value = [...v]
 })
 watch(() => props.selectedColumns, (v) => {
 if (v !== undefined) selectedColumnsState.value = [...v]
 })
 watch(() => props.currentPage, (v) => {
 if (v !== undefined) currentPageState.value = Math.max(1, v)
 })
 watch(() => props.perPage, (v) => {
 if (v !== undefined) perPageState.value = Math.max(0, v)
 })
 watch(() => props.filter, (v) => {
 filterState.value = v
 })
 watch(() => props.sortBy, (v) => {
 if (v !== undefined) sortByState.value = v ?? null
 })
 watch(() => props.sortDesc, (v) => {
 if (v !== undefined) sortDescState.value = Boolean(v)
 })

 function setCurrentPage(value: number): void {
 const next = Math.max(1, Number.isFinite(value) ? value : 1)
 currentPageState.value = next
 emit('update:currentPage', next)
 }

 function setPerPage(value: number): void {
 const next = Math.max(0, Number.isFinite(value) ? value : 0)
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
 emit('sort-changed', {sortBy, sortDesc})
 }

 watch(filterState, () => {
 if (currentPageState.value !== 1) setCurrentPage(1)
 }, {deep: true})

 const providerFn = computed<SmartTableProvider | null>(() => {
 if (typeof props.provider === 'function') return props.provider
 if (typeof props.items === 'function') return props.items as SmartTableProvider
 return null
 })

 const providerItems = ref<SmartTableItem[]>([])
 const providerTotal = ref(0)
 const providerBusy = ref(false)
 const providerError = ref<unknown>(null)

 let refreshTimer: ReturnType<typeof setTimeout> | null = null
 let requestId = 0
 let abortController: AbortController | null = null

 const isProviderMode = computed(() => providerFn.value !== null)

 function getRowKey(item: SmartTableItem, index = -1): SmartTableKey {
 if (typeof props.rowKey === 'function') {
 return props.rowKey(item, index)
 }

 if (typeof props.rowKey === 'string' && props.rowKey) {
 const value = getByPath(item, props.rowKey)
 if (typeof value === 'string' || typeof value === 'number') return value
 }

 const id = item.id
 if (typeof id === 'string' || typeof id === 'number') return id

 const _id = item._id
 if (typeof _id === 'string' || typeof _id === 'number') return _id

 if (index >= 0) return index

 return JSON.stringify(item)
 }

 function normalizeField(raw: string | SmartTableField): SmartTableField {
 if (typeof raw === 'string') {
 return {
 key: raw,
 label: startCase(raw),
 sortable: false,
 selectable: true,
 visible: true,
 }
 }

 return {
 label: startCase(raw.key),
 sortable: false,
 selectable: true,
 visible: true,
 ...raw,
 }
 }

 const sourceItems = computed<SmartTableItem[]>(() => {
 return Array.isArray(props.items) ? [...props.items] : []
 })

 const inferredFields = computed<SmartTableField[]>(() => {
 if (props.fields.length > 0) {
 return props.fields.map(normalizeField)
 }

 const sample = (isProviderMode.value ? providerItems.value : sourceItems.value)[0]
 if (!sample || typeof sample !== 'object') return []

 return Object.keys(sample).map((key) => normalizeField(key))
 })

 function isRowSelectable(item: SmartTableItem, index: number): boolean {
 if (props.rowSelectionMode === 'none') return false
 return !props.disableRowSelect?.(item, index)
 }

 function isColumnSelectable(field: SmartTableField, index: number): boolean {
 if (props.columnSelectionMode === 'none') return false
 if (field.key === props.rowSelectionFieldKey) return false
 if (field.visible === false) return false
 if (field.selectable === false) return false
 if (props.selectableColumns && !props.selectableColumns.includes(field.key)) return false
 return !props.disableColumnSelect?.(field, index)
 }

 const visibleDataFields = computed<SmartTableField[]>(() => {
 return inferredFields.value.filter((field) => field.visible !== false)
 })

 function defaultMatchesFilter(item: SmartTableItem, filter: unknown, fields: SmartTableField[]): boolean {
 if (filter == null || filter === '') return true

 if (typeof filter === 'function') {
 return Boolean((filter as (row: SmartTableItem) => boolean)(item))
 }

 if (typeof filter === 'string') {
 const term = filter.trim().toLowerCase()
 if (!term) return true
 return fields.some((field) => String(getByPath(item, field.key) ?? '').toLowerCase().includes(term))
 }

 if (isPlainObject(filter)) {
 return Object.entries(filter).every(([key, value]) => {
 const current = getByPath(item, key)
 return String(current ?? '').toLowerCase().includes(String(value ?? '').toLowerCase())
 })
 }

 return true
 }

 const filteredStaticItems = computed<SmartTableItem[]>(() => {
 if (isProviderMode.value) return providerItems.value

 const rows = sourceItems.value
 if (filterState.value == null || filterState.value === '') return rows

 const predicate = props.localFilterFn
 ? (item: SmartTableItem) => props.localFilterFn!(item, filterState.value, visibleDataFields.value)
 : (item: SmartTableItem) => defaultMatchesFilter(item, filterState.value, visibleDataFields.value)

 return rows.filter(predicate)
 })

 const sortedStaticItems = computed<SmartTableItem[]>(() => {
 if (isProviderMode.value) return providerItems.value

 const rows = [...filteredStaticItems.value]
 if (!sortByState.value) return rows

 const compare = props.localSortFn
 ? (a: SmartTableItem, b: SmartTableItem) => props.localSortFn!(a, b, sortByState.value!, sortDescState.value)
 : (a: SmartTableItem, b: SmartTableItem) => {
 const result = compareValues(getByPath(a, sortByState.value!), getByPath(b, sortByState.value!))
 return sortDescState.value ? -result : result
 }

 return rows.sort(compare)
 })

 const displayedItems = computed<SmartTableItem[]>(() => {
 if (isProviderMode.value) return providerItems.value

 const page = currentPageState.value
 const perPage = perPageState.value
 if (!perPage || perPage < 1) return sortedStaticItems.value

 const start = (page - 1) * perPage
 return sortedStaticItems.value.slice(start, start + perPage)
 })

 const totalRows = computed<number>(() => {
 return isProviderMode.value ? providerTotal.value : filteredStaticItems.value.length
 })

 watch([totalRows, perPageState], () => {
 if (perPageState.value > 0) {
 const maxPage = Math.max(1, Math.ceil(totalRows.value / perPageState.value))
 if (currentPageState.value > maxPage) setCurrentPage(maxPage)
 }
 }, {immediate: true})

 function normalizeSelectedRowKeys(keys: SmartTableKey[]): SmartTableKey[] {
 if (props.rowSelectionMode === 'none') return []
 const unique = [...new Set(keys)]
 return props.rowSelectionMode === 'single' ? unique.slice(0, 1) : unique
 }

 function normalizeSelectedColumns(keys: string[]): string[] {
 if (props.columnSelectionMode === 'none') return []

 const allowed = new Set(
 visibleDataFields.value
 .filter((field, index) => isColumnSelectable(field, index))
 .map((field) => field.key)
 )

 const unique = [...new Set(keys)].filter((key) => allowed.has(key))
 return props.columnSelectionMode === 'single' ? unique.slice(0, 1) : unique
 }

 const selectedRowKeysSet = computed(() => new Set(selectedRowKeysState.value))
 const selectedColumnsSet = computed(() => new Set(selectedColumnsState.value))

 const selectedRows = computed<SmartTableItem[]>(() =>
 selectedRowKeysState.value
 .map((key) => rowCache.get(key))
 .filter((row): row is SmartTableItem => Boolean(row))
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
 fields: visibleDataFields.value.filter((field) => selectedColumnsSet.value.has(field.key)),
 })
 }

 function setSelectedRowKeys(keys: SmartTableKey[]): void {
 const next = normalizeSelectedRowKeys(keys)
 if (shallowEqualArray(next, selectedRowKeysState.value)) {
 emitRowSelectionChange()
 return
 }
 selectedRowKeysState.value = next
 emit('update:selectedRowKeys', [...next])
 emitRowSelectionChange()
 }

 function setSelectedColumns(keys: string[]): void {
 const next = normalizeSelectedColumns(keys)
 if (shallowEqualArray(next, selectedColumnsState.value)) {
 emitColumnSelectionChange()
 return
 }
 selectedColumnsState.value = next
 emit('update:selectedColumns', [...next])
 emitColumnSelectionChange()
 }

 watch(() => props.rowSelectionMode, () => {
 setSelectedRowKeys(selectedRowKeysState.value)
 }, {immediate: true})

 watch([visibleDataFields, () => props.columnSelectionMode], () => {
 setSelectedColumns(selectedColumnsState.value)
 }, {immediate: true, deep: true})

 function isRowSelected(item: SmartTableItem, index: number): boolean {
 return selectedRowKeysSet.value.has(getRowKey(item, index))
 }

 function isColumnSelected(key: string): boolean {
 return selectedColumnsSet.value.has(key)
 }

 function toggleRowSelection(item: SmartTableItem, index: number, force?: boolean): void {
 if (!isRowSelectable(item, index)) return

 const key = getRowKey(item, index)
 const exists = selectedRowKeysSet.value.has(key)
 const nextValue = force ?? !exists

 if (props.rowSelectionMode === 'single') {
 setSelectedRowKeys(nextValue ? [key] : [])
 return
 }

 const next = nextValue
 ? [...selectedRowKeysState.value, key]
 : selectedRowKeysState.value.filter((k) => k !== key)

 setSelectedRowKeys(next)
 }

 function clearSelectedRows(): void {
 setSelectedRowKeys([])
 }

 function toggleColumnSelection(key: string, force?: boolean): void {
 const fieldIndex = visibleDataFields.value.findIndex((field) => field.key === key)
 const field = visibleDataFields.value[fieldIndex]
 if (!field || !isColumnSelectable(field, fieldIndex)) return

 const exists = selectedColumnsSet.value.has(key)
 const nextValue = force ?? !exists

 if (props.columnSelectionMode === 'single') {
 setSelectedColumns(nextValue ? [key] : [])
 return
 }

 const next = nextValue
 ? [...selectedColumnsState.value, key]
 : selectedColumnsState.value.filter((k) => k !== key)

 setSelectedColumns(next)
 }

 function clearSelectedColumns(): void {
 setSelectedColumns([])
 }

 function selectAllColumns(): void {
 if (props.columnSelectionMode !== 'multiple') return
 setSelectedColumns(
 visibleDataFields.value
 .filter((field, index) => isColumnSelectable(field, index))
 .map((field) => field.key)
 )
 }

 const visibleSelectableRowKeys = computed<SmartTableKey[]>(() => {
 return displayedItems.value
 .map((item, index) => ({item, index}))
 .filter(({item, index}) => isRowSelectable(item, index))
 .map(({item, index}) => getRowKey(item, index))
 })

 const allVisibleRowsSelected = computed<boolean>(() => {
 return (
 visibleSelectableRowKeys.value.length > 0 &&
 visibleSelectableRowKeys.value.every((key) => selectedRowKeysSet.value.has(key))
 )
 })

 const someVisibleRowsSelected = computed<boolean>(() => {
 return (
 visibleSelectableRowKeys.value.some((key) => selectedRowKeysSet.value.has(key)) &&
 !allVisibleRowsSelected.value
 )
 })

 function selectAllVisibleRows(): void {
 if (props.rowSelectionMode !== 'multiple') return
 const merged = [...new Set([...selectedRowKeysState.value, ...visibleSelectableRowKeys.value])]
 setSelectedRowKeys(merged)
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

 function rebuildStaticCache(items: SmartTableItem[]): void {
 rowCache.clear()

 const keys = new Set<SmartTableKey>()
 items.forEach((item, index) => {
 const key = getRowKey(item, index)
 keys.add(key)
 rowCache.set(key, item)
 })

 const pruned = selectedRowKeysState.value.filter((key) => keys.has(key))
 if (!shallowEqualArray(pruned, selectedRowKeysState.value)) {
 setSelectedRowKeys(pruned)
 } else {
 emitRowSelectionChange()
 }
 }

 function updateProviderCache(items: SmartTableItem[]): void {
 items.forEach((item, index) => {
 rowCache.set(getRowKey(item, index), item)
 })

 if (!props.preserveSelectionOnRefresh) {
 clearSelectedRows()
 } else {
 emitRowSelectionChange()
 }
 }

 watch(sourceItems, (items) => {
 if (!isProviderMode.value) rebuildStaticCache(items)
 }, {immediate: true, deep: true})

 watch(providerItems, (items) => {
 if (isProviderMode.value) updateProviderCache(items)
 }, {immediate: true, deep: true})

 async function refresh(): Promise<SmartTableItem[]> {
 if (!providerFn.value) {
 emit('refreshed', {
 items: [...displayedItems.value],
 total: totalRows.value,
 provider: false,
 })
 return displayedItems.value
 }

 if (refreshTimer) {
 clearTimeout(refreshTimer)
 refreshTimer = null
 }

 requestId += 1
 abortController?.abort()
 abortController = typeof AbortController !== 'undefined' ? new AbortController() : null

 providerBusy.value = true
 providerError.value = null

 const query: SmartTableQuery = {
 currentPage: currentPageState.value,
 perPage: perPageState.value,
 filter: filterState.value,
 sortBy: sortByState.value,
 sortDesc: sortDescState.value,
 selectedRowKeys: [...selectedRowKeysState.value],
 selectedColumns: [...selectedColumnsState.value],
 extra: props.extraQuery,
 signal: abortController?.signal,
 }

 try {
 const result = normalizeProviderResult(await providerFn.value(query))
 if (currentRequest !== requestId) return providerItems.value

 providerItems.value = result.items
 providerTotal.value = result.total ?? result.items.length

 emit('provider-success', {
 items: [...result.items],
 total: providerTotal.value,
 query,
 })
 emit('refreshed', {
 items: [...result.items],
 total: providerTotal.value,
 provider: true,
 query,
 })

 return result.items
 } catch (error) {
 if (isAbortError(error)) return providerItems.value
 if (currentRequest !== requestId) return providerItems.value

 providerError.value = error
 emit('provider-error', error)
 throw error
 } finally {
 if (currentRequest === requestId) {
 providerBusy.value = false
 }
 }
 }

 function scheduleRefresh(): void {
 if (!providerFn.value) return
 if (refreshTimer) clearTimeout(refreshTimer)

 if (props.providerDebounce <= 0) {
 void refresh()
 return
 }

 refreshTimer = setTimeout(() => {
 void refresh()
 }, props.providerDebounce)
 }

 watch(
 [
 providerFn,
 currentPageState,
 perPageState,
 filterState,
 sortByState,
 sortDescState,
 selectedColumnsState,
 () => props.extraQuery,
 ],
 () => {
 if (isProviderMode.value) scheduleRefresh()
 },
 {immediate: true, deep: true}
 )

 watch(isProviderMode, (enabled) => {
 if (!enabled) {
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
 setSort(null, false)
 return
 }

 setSort(field.key, false)
 }

 function isInteractiveTarget(target: EventTarget | null): boolean {
 const el = target as HTMLElement | null
 return Boolean(
 el?.closest(
 'a,button,input,select,textarea,label,[role="button"],[contenteditable="true"],.dropdown-toggle,.dropdown-item'
 )
 )
 }

 function handleRowClicked(item: SmartTableItem, index: number, event: MouseEvent, ...rest: unknown[]): void {
 if (props.clickToSelectRow && props.rowSelectionMode !== 'none' && !isInteractiveTarget(event.target)) {
 toggleRowSelection(item, index)
 }
 emit('row-clicked', item, index, event, ...rest)
 }

 function handleHeadClicked(key: string, field: SmartTableField, event: MouseEvent, isFooter = false, ...rest: unknown[]): void {
 if (!isFooter && !isInteractiveTarget(event.target)) {
 const candidate = visibleDataFields.value.find((f) => f.key === key)
 if (candidate?.sortable) toggleSortForField(candidate)
 }
 emit('head-clicked', key, field, event, isFooter, ...rest)
 }

 function renderSortIndicator(field: SmartTableField): VNodeChild {
 if (!field.sortable) return null

 const active = sortByState.value === field.key
 const glyph = !active ? '↕' : sortDescState.value ? '↓' : '↑'

 return h(
 'span',
 {
 class: [
 'smart-table__sort-indicator',
 active ? 'text-primary' : 'text-body-secondary',
 ],
 'aria-hidden': 'true',
 },
 glyph
 )
 }

 function renderDefaultHeadContent(field: SmartTableField, scope: Record<string, unknown>): VNodeChild {
 const exact = slots[`head(${field.key})` as keyof typeof slots] as ((arg: Record<string, unknown>) => VNodeChild) | undefined
 const generic = slots.head as ((arg: Record<string, unknown>) => VNodeChild) | undefined

 const slotScope = {
 ...scope,
 field,
 key: field.key,
 label: field.label ?? startCase(field.key),
 selected: isColumnSelected(field.key),
 }

 if (exact) return exact(slotScope)
 if (generic) return generic(slotScope)

 return h('span', field.label ?? startCase(field.key))
 }

 function renderColumnSelectControl(field: SmartTableField, index: number): VNodeChild {
 if (!isColumnSelectable(field, index)) return null

 const checked = isColumnSelected(field.key)
 const inputType = props.columnSelectionMode === 'single' ? 'radio' : 'checkbox'

 return h('input', {
 class: 'form-check-input m-0 smart-table__selection-control',
 type: inputType,
 name: props.columnSelectionMode === 'single' ? `${uid}-column-select` : undefined,
 checked,
 disabled: !isColumnSelectable(field, index),
 'aria-label': `Select column ${field.label ?? field.key}`,
 onClick: (e: Event) => e.stopPropagation(),
 onChange: (e: Event) => {
 e.stopPropagation()
 toggleColumnSelection(field.key, (e.target as HTMLInputElement).checked)
 },
 })
 }

 function renderColumnHeader(field: SmartTableField, index: number, scope: Record<string, unknown>): VNodeChild {
 return h(
 'div',
 {
 class: [
 'smart-table__head-content',
 field.sortable && 'smart-table__head-content--sortable',
 ],
 },
 [
 props.columnSelectionMode !== 'none' ? renderColumnSelectControl(field, index) : null,
 h('span', {class: 'smart-table__head-label flex-grow-1'}, renderDefaultHeadContent(field, scope)),
 renderSortIndicator(field),
 ]
 )
 }

 function renderRowSelectionHeader(): VNodeChild {
 const custom = slots['selection-head'] as ((arg: Record<string, unknown>) => VNodeChild) | undefined
 const slotScope = {
 allVisibleRowsSelected: allVisibleRowsSelected.value,
 someVisibleRowsSelected: someVisibleRowsSelected.value,
 toggleAllVisibleRows,
 selectAllVisibleRows,
 clearSelectedRows,
 }

 if (custom) return custom(slotScope)

 if (props.rowSelectionMode !== 'multiple') {
 return h('span', {class: 'visually-hidden'}, 'Row selection')
 }

 return h('div', {class: 'd-flex justify-content-center'}, [
 h('input', {
 class: 'form-check-input m-0 smart-table__selection-control',
 type: 'checkbox',
 checked: allVisibleRowsSelected.value,
 ref: (el: Element | null) => {
 if (el instanceof HTMLInputElement) {
 el.indeterminate = someVisibleRowsSelected.value
 }
 },
 'aria-label': 'Select all visible rows',
 onClick: (e: Event) => e.stopPropagation(),
 onChange: (e: Event) => {
 e.stopPropagation()
 toggleAllVisibleRows((e.target as HTMLInputElement).checked)
 },
 }),
 ])
 }

 function renderRowSelectionCell(item: SmartTableItem, index: number): VNodeChild {
 const key = getRowKey(item, index)
 const checked = isRowSelected(item, index)
 const disabled = !isRowSelectable(item, index)

 const custom = slots['selection-cell'] as ((arg: Record<string, unknown>) => VNodeChild) | undefined
 if (custom) {
 return custom({
 item,
 index,
 rowKey: key,
 selected: checked,
 disabled,
 toggle: (force?: boolean) => toggleRowSelection(item, index, force),
 })
 }

 return h('div', {class: 'd-flex justify-content-center'}, [
 h('input', {
 class: 'form-check-input m-0 smart-table__selection-control',
 type: props.rowSelectionMode === 'single' ? 'radio' : 'checkbox',
 name: props.rowSelectionMode === 'single' ? `${uid}-row-select` : undefined,
 checked,
 disabled,
 'aria-label': `Select row ${index + 1}`,
 onClick: (e: Event) => e.stopPropagation(),
 onChange: (e: Event) => {
 e.stopPropagation()
 toggleRowSelection(item, index, (e.target as HTMLInputElement).checked)
 },
 }),
 ])
 }

 const tableFields = computed<SmartTableField[]>(() => {
 const dataFields = visibleDataFields.value.map((field) => {
 const isSelected = isColumnSelected(field.key)

 return {
 ...field,
 sortable: false,
 thClass: mergeMaybeCallableClass(field.thClass, isSelected ? 'smart-table__column--selected' : null),
 tdClass: mergeMaybeCallableClass(field.tdClass, isSelected ? 'smart-table__column--selected' : null),
 }
 })

 if (props.rowSelectionMode === 'none') return dataFields

 const selectionField: SmartTableField = {
 key: props.rowSelectionFieldKey,
 label: '',
 sortable: false,
 selectable: false,
 class: props.rowSelectionColumnClass,
 thClass: props.rowSelectionColumnClass,
 tdClass: props.rowSelectionColumnClass,
 thStyle: props.rowSelectionColumnStyle,
 tdStyle: props.rowSelectionColumnStyle,
 }

 return props.rowSelectionColumnPosition === 'start'
 ? [selectionField, ...dataFields]
 : [...dataFields, selectionField]
 })

 function mergedTbodyTrClass(item: SmartTableItem, type?: unknown, ...rest: unknown[]): unknown {
 const user = (attrs.tbodyTrClass ?? attrs['tbody-tr-class']) as unknown
 const userValue = typeof user === 'function' ? (user as (...args: unknown[]) => unknown)(item, type, ...rest) : user

 return [
 userValue,
 item && props.rowSelectionMode !== 'none' && selectedRowKeysSet.value.has(getRowKey(item))
 ? 'smart-table__row--selected'
 : null,
 ]
 }

 function mergedTbodyTrAttr(item: SmartTableItem, type?: unknown, ...rest: unknown[]): Record<string, unknown> {
 const user = (attrs.tbodyTrAttr ?? attrs['tbody-tr-attr']) as unknown
 const userValue = typeof user === 'function' ? (user as (...args: unknown[]) => unknown)(item, type, ...rest) : user
 const base = isPlainObject(userValue) ? userValue : {}

 if (!item) return base

 return {
 ...base,
 ...(props.rowSelectionMode !== 'none'
 ? {'aria-selected': String(selectedRowKeysSet.value.has(getRowKey(item)))}
 : {}),
 }
 }

 function buildSlots(): Record<string, (scope?: Record<string, unknown>) => VNodeChild> {
 const out: Record<string, (scope?: Record<string, unknown>) => VNodeChild> = {}

 for (const name of Object.keys(slots)) {
 if (name === 'selection-head' || name === 'selection-cell') continue
 out[name] = (scope?: Record<string, unknown>) => slots[name]?.(scope ?? {})
 }

 if (!slots.empty && providerError.value && displayedItems.value.length === 0) {
 out.empty = () =>
 h('div', {class: 'text-danger small py-3 px-2'}, String((providerError.value as Error)?.message ?? 'Failed to load data'))
 }

 if (props.rowSelectionMode !== 'none') {
 out[`head(${props.rowSelectionFieldKey})`] = () => renderRowSelectionHeader()
 out[`cell(${props.rowSelectionFieldKey})`] = (scope?: Record<string, unknown>) =>
 renderRowSelectionCell(
 (scope?.item ?? {}) as SmartTableItem,
 Number(scope?.index ?? -1)
 )
 }

 visibleDataFields.value.forEach((field, index) => {
 out[`head(${field.key})`] = (scope?: Record<string, unknown>) =>
 renderColumnHeader(field, index, scope ?? {})
 })

 return out
 }

 const computedBusy = computed<boolean>(() => props.busy || providerBusy.value)

 expose({
 refresh,
 clearSelectedRows,
 clearSelectedColumns,
 selectAllVisibleRows,
 selectAllColumns,
 setSelectedRowKeys,
 setSelectedColumns,
 setCurrentPage,
 setPerPage,
 setFilter,
 setSort,
 selectedRowKeys: selectedRowKeysState,
 selectedColumns: selectedColumnsState,
 selectedRows,
 totalRows,
 busy: computedBusy,
 error: providerError,
 })

 return () => {
 const passthrough = {...attrs} as Record<string, unknown>

 delete passthrough.items
 delete passthrough.fields
 delete passthrough.busy
 delete passthrough.tbodyTrClass
 delete passthrough['tbody-tr-class']
 delete passthrough.tbodyTrAttr
 delete passthrough['tbody-tr-attr']

 return h(
 BTable as never,
 mergeProps(passthrough, {
 class: 'smart-table',
 items: displayedItems.value,
 fields: tableFields.value,
 busy: computedBusy.value,
 primaryKey: typeof props.rowKey === 'string' ? props.rowKey : undefined,
 tbodyTrClass: mergedTbodyTrClass,
 tbodyTrAttr: mergedTbodyTrAttr,
 onRowClicked: handleRowClicked,
 onHeadClicked: handleHeadClicked,
 }),
 buildSlots()
 )
 }
},
})
</script>

<style scoped>
.smart-table__selection-control {
 cursor: pointer;
}

.smart-table__head-content {
 display: flex;
 align-items: center;
 gap: 0.5rem;
 min-width: 0;
}

.smart-table__head-content--sortable {
 user-select: none;
}

.smart-table__head-label {
 min-width: 0;
}

.smart-table__sort-indicator {
 font-size: 0.75rem;
 line-height: 1;
 opacity: 0.9;
}

.smart-table :deep(.smart-table__column--selected) {
 background-color: var(--bs-table-active-bg);
}

.smart-table :deep(tbody tr.smart-table__row--selected > *) {
 --bs-table-bg-type: var(--bs-table-active-bg);
 --bs-table-color-type: var(--bs-table-active-color);
}
</style>
