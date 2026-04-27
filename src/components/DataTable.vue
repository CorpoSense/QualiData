<template>
  <div class="data-table-wrapper" ref="wrapperRef">


  <!-- Table -->
  <div class="table-responsive">
    <table class="table table-hover table-striped table-sm">
      <thead>
        <tr>
          <th v-if="showIndex" style="width: 50px;" class="text-center text-muted">#</th>
          <th v-if="selectable" style="width: 40px;" class="text-center">
            <input
              class="form-check-input"
              type="checkbox"
              :checked="allSelected"
              :indeterminate="someSelected && !allSelected"
              @change="$emit('toggle-all')"
            >
          </th>
          <th
            v-for="(field, index) in visibleFields"
            :key="field.key"
            :class="{ 'table-primary': isSelected(field), 'has-column-filter': enableColumnFilter }"
            :style="{ width: columnWidths[field.key] ? columnWidths[field.key] + 'px' : 'auto', minWidth: '50px', position: 'relative' }"
            @click="$emit('head-clicked', field)"
            style="cursor: pointer"
          >
            <span class="d-flex align-items-center justify-content-between">
              {{ field.label }}
              <div class="d-flex align-items-center gap-1">
                <!-- Column filter button -->
                <button
                  v-if="enableColumnFilter"
                  class="btn btn-sm btn-outline-secondary border-0 py-0 px-1 filter-btn"
                  :class="{ active: hasColumnFilter(field.key) }"
                  @click.stop="toggleFilterDropdown(field.key)"
                  :title="hasColumnFilter(field.key) ? `Filtered (${columnFilterState[field.key]?.length || 0} values)` : 'Filter column'"
                >
                  <i :class="hasColumnFilter(field.key) ? 'bi bi-funnel-fill' : 'bi bi-funnel'" style="font-size: 0.65rem;"></i>
                </button>
                <button
                  class="btn btn-sm btn-outline-secondary border-0 py-0 px-1"
                  @click.stop="toggleVisibility(field.key)"
                  :title="isHidden(field.key) ? 'Show column' : 'Hide column'"
                >
                  <i :class="isHidden(field.key) ? 'bi bi-eye-slash text-muted' : 'bi bi-eye-slash'" style="opacity: 0.4; font-size: 0.65rem;"></i>
                </button>
                <button
                  class="btn btn-sm btn-outline-secondary border-0 py-0 px-1 sort-btn"
                  :class="{ active: getSortIndex(field.key) >= 0 }"
                  @click.stop="toggleSort(field.key)"
                  :title="sortTitle(field.key)"
                >
                  <template v-if="getSortIndex(field.key) >= 0">
                    <i :class="getSortDir(field.key) === 'asc' ? 'bi bi-arrow-up' : 'bi bi-arrow-down'"></i>
                    <small v-if="multiSort && sortKeys.length > 1" class="ms-0 sort-badge">{{ getSortIndex(field.key) + 1 }}</small>
                  </template>
                  <i v-else class="bi bi-arrow-down-up text-muted"></i>
                </button>
              </div>
            </span>
            <!-- Column Filter Dropdown -->
            <ColumnFilterDropdown
              v-if="enableColumnFilter && openFilterColumn === field.key"
              :field="field"
              :values="columnUniqueValues[field.key] || []"
              :selected-values="columnFilterState[field.key] || []"
              :loading="!!fetchingUniqueValues[field.key]"
              :total-unique="columnUniqueCounts[field.key] || 0"
              @apply="onColumnFilterApply(field.key, $event)"
              @close="closeFilterDropdown"
            />
            <div
              class="resize-handle"
              @mousedown.prevent="startResize($event, field.key)"
              @dblclick.stop="autoFitColumn(field.key)"
              title="Drag to resize, double-click to auto-fit"
            ></div>
          </th>
          <!-- Column visibility button in last header column -->
          <th v-if="visibleFields.length > 0" style="width: 50px; min-width: 50px; position: relative;" class="text-center">
            <BButton
              size="sm"
              variant="outline-secondary"
              @click.stop="showColumnMenu = !showColumnMenu"
              title="Column visibility"
              class="border-0 p-1"
            >
              <i class="bi bi-eye"></i>
              <span v-if="hiddenColumns.length > 0" class="badge bg-warning ms-1" style="font-size: 0.6rem;">{{ hiddenColumns.length }}</span>
            </BButton>
            <div v-if="showColumnMenu" class="column-menu" style="right: 0;">
              <div class="column-menu-header">
                <span class="fw-bold small">Show/Hide Columns</span>
                <button class="btn-close btn-close-sm" @click.stop="showColumnMenu = false"></button>
              </div>
              <div class="column-menu-list">
                <div
                  v-for="field in allFields"
                  :key="field.key"
                  class="column-menu-item"
                  :class="{ 'text-muted': isHidden(field.key) }"
                  @click.stop="toggleVisibility(field.key)"
                >
                  <i :class="isHidden(field.key) ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  <span class="column-name">{{ field.label }}</span>
                </div>
              </div>
              <div class="column-menu-footer">
                <button class="btn btn-sm btn-outline-secondary w-100" @click.stop="showAllColumns">
                  Show All
                </button>
              </div>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, index) in sortedItems"
          :key="index"
          @click="!selectable && $emit('row-clicked', { item: row, index })"
        >
          <td v-if="showIndex" class="text-center text-muted small">{{ index + 1 }}</td>
          <td v-if="selectable" class="text-center" @click.stop>
            <input
              class="form-check-input"
              type="checkbox"
              :checked="selectedRows.includes(index)"
              @change="$emit('row-selected', index)"
            >
          </td>
          <td v-for="field in visibleFields" :key="field.key" @click="selectable && $emit('row-clicked', { item: row, index })" @dblclick="$emit('cell-dblclick', { row: index, column: field.key, value: row[field.key] })">
            {{ row[field.key] }}
          </td>
        </tr>
        <tr v-if="sortedItems.length === 0">
          <td :colspan="visibleFields.length + 1 + (selectable ? 1 : 0) + (showIndex ? 1 : 0)" class="text-center text-muted py-4">
            No data to display
          </td>
        </tr>
      </tbody>
      <!-- Smart Footer -->
      <tfoot v-if="showFooter" class="smart-footer">
        <tr>
          <td v-if="showIndex" class="text-muted small text-center"></td>
          <td v-if="selectable"></td>
          <td v-for="field in visibleFields" :key="field.key" class="footer-cell">
            <div class="d-flex align-items-center justify-content-between">
              <div class="footer-stats">
                <template v-if="getColumnStats(field.key)">
                  <!-- Numeric stats -->
                  <template v-if="getColumnStats(field.key).is_numeric">
                    <span class="footer-stat">
                      <span class="stat-label">null:</span> {{ getColumnStats(field.key).stats.null_count ?? 0 }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">min:</span> {{ getColumnStats(field.key).stats.min ?? '-' }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">max:</span> {{ getColumnStats(field.key).stats.max ?? '-' }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">mean:</span> {{ getColumnStats(field.key).stats.mean?.toFixed(2) ?? '-' }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">median:</span> {{ getColumnStats(field.key).stats.median?.toFixed(2) ?? '-' }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">std:</span> {{ getColumnStats(field.key).stats.std?.toFixed(2) ?? '-' }}
                    </span>
                  </template>
                  <!-- Non-numeric stats -->
                  <template v-else>
                    <span class="footer-stat">
                      <span class="stat-label">null:</span> {{ getColumnStats(field.key).stats.null_count ?? 0 }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">unique:</span> {{ getColumnStats(field.key).stats.unique ?? '-' }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">min:</span> {{ getColumnStats(field.key).stats.min_length ?? '-' }}
                    </span>
                    <span class="footer-stat">
                      <span class="stat-label">max:</span> {{ getColumnStats(field.key).stats.max_length ?? '-' }}
                    </span>
                  </template>
                </template>
              </div>
            </div>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import ColumnFilterDropdown from './ColumnFilterDropdown.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  fields: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] },
  selectable: { type: Boolean, default: false },
  selectedRows: { type: Array, default: () => [] },
  showIndex: { type: Boolean, default: false },
  multiSort: { type: Boolean, default: false },
  // Server-side sort: when provided, sort state is controlled externally
  // Data is already sorted by the server; this prop only controls the sort UI indicators
  serverSort: { type: Array, default: null }, // [{ key: 'name', dir: 'asc' }, ...] or null
  // Footer props
  showFooter: { type: Boolean, default: false },
  footerStats: { type: Object, default: () => ({}) },
  // Column filter props
  enableColumnFilter: { type: Boolean, default: false },
  columnUniqueValues: { type: Object, default: () => ({}) },
  columnFilterState: { type: Object, default: () => ({}) },
  fetchingUniqueValues: { type: Object, default: () => ({}) },
  columnUniqueCounts: { type: Object, default: () => ({}) },
})

const emit = defineEmits([
  'row-clicked', 'head-clicked', 'row-selected', 'toggle-all',
  'sort-changed', 'cell-dblclick', 'footer-config-changed',
  'hidden-columns-changed', 'column-filter-changed', 'request-unique-values'
])

// Sort state: array of { key, dir } for multi-sort
const sortKeys = ref([]) // [{ key: 'name', dir: 'asc' }, ...]

// Sync sort state with serverSort prop when provided (server-side sort mode)
watch(() => props.serverSort, (newVal) => {
  if (newVal !== null && newVal !== undefined) {
    sortKeys.value = [...newVal]
  }
}, { immediate: true, deep: true })

// Hidden columns state
const hiddenColumns = ref([])
const showColumnMenu = ref(false)

// Column filter dropdown state
const openFilterColumn = ref(null)

// Column resizing state
const columnWidths = ref({}) // { key: width }
const resizing = ref(null) // { key, startX, startWidth }

// Wrapper ref for click-outside detection
const wrapperRef = ref(null)

const allSelected = computed(() =>
  props.items.length > 0 && props.selectedRows.length === props.items.length
)
const someSelected = computed(() => props.selectedRows.length > 0)

function getSortIndex(key) {
  return sortKeys.value.findIndex(s => s.key === key)
}

function getSortDir(key) {
  const entry = sortKeys.value.find(s => s.key === key)
  return entry ? entry.dir : null
}

function toggleSort(key) {
  const idx = getSortIndex(key)
  if (idx >= 0) {
    const current = sortKeys.value[idx]
    if (current.dir === 'asc') {
      // asc → desc
      sortKeys.value[idx] = { key, dir: 'desc' }
    } else {
      // desc → remove
      sortKeys.value.splice(idx, 1)
    }
  } else {
    // Add new sort
    if (props.multiSort) {
      sortKeys.value.push({ key, dir: 'asc' })
    } else {
      sortKeys.value = [{ key, dir: 'asc' }]
    }
  }
  sortKeys.value = [...sortKeys.value] // trigger reactivity
  emit('sort-changed', sortKeys.value)
}

function sortTitle(key) {
  const idx = getSortIndex(key)
  if (idx < 0) return 'Sort'
  const dir = getSortDir(key)
  const suffix = props.multiSort && sortKeys.value.length > 1 ? ` (${idx + 1})` : ''
  return dir === 'asc' ? `Sorted ascending${suffix}` : `Sorted descending${suffix}`
}

const sortedItems = computed(() => {
  // When serverSort is provided, data is already sorted server-side
  if (props.serverSort !== null && props.serverSort !== undefined) {
    return props.items
  }
  // Client-side sort (default behavior)
  if (!sortKeys.value.length) return props.items
  return [...props.items].sort((a, b) => {
    for (const { key, dir } of sortKeys.value) {
      const multiplier = dir === 'asc' ? 1 : -1
      const va = a[key]
      const vb = b[key]
      if (va == null && vb == null) continue
      if (va == null) return multiplier
      if (vb == null) return -multiplier
      const na = Number(va)
      const nb = Number(vb)
      if (!isNaN(na) && !isNaN(nb)) {
        if (na !== nb) return (na - nb) * multiplier
      } else {
        const cmp = String(va).localeCompare(String(vb))
        if (cmp !== 0) return cmp * multiplier
      }
    }
    return 0
  })
})

function isSelected(field) {
  const fieldKey = field.key || field.field
  return props.selectedColumns.includes(fieldKey)
}

// Hidden columns functions
function isHidden(key) {
  return hiddenColumns.value.includes(key)
}

function toggleVisibility(key) {
  const idx = hiddenColumns.value.indexOf(key)
  if (idx >= 0) {
    hiddenColumns.value.splice(idx, 1)
  } else {
    hiddenColumns.value.push(key)
  }
  emit('hidden-columns-changed', hiddenColumns.value)
}

function showAllColumns() {
  hiddenColumns.value = []
  emit('hidden-columns-changed', hiddenColumns.value)
}

function hideColumn(key) {
  if (!isHidden(key)) {
    hiddenColumns.value.push(key)
    emit('hidden-columns-changed', hiddenColumns.value)
  }
}

function unhideColumn(key) {
  const idx = hiddenColumns.value.indexOf(key)
  if (idx >= 0) {
    hiddenColumns.value.splice(idx, 1)
    emit('hidden-columns-changed', hiddenColumns.value)
  }
}

// All fields (including hidden)
const allFields = computed(() => props.fields)

// Visible fields (excluding hidden)
const visibleFields = computed(() => {
  const result = props.fields.filter(f => !hiddenColumns.value.includes(f.key))
  return result
})

// Column filter functions
function hasColumnFilter(key) {
  return props.columnFilterState[key] && props.columnFilterState[key].length > 0
}

function toggleFilterDropdown(key) {
  if (openFilterColumn.value === key) {
    openFilterColumn.value = null
  } else {
    openFilterColumn.value = key
    // Request unique values from parent if not cached
    if (!props.columnUniqueValues[key] && !props.fetchingUniqueValues[key]) {
      emit('request-unique-values', key)
    }
  }
}

function closeFilterDropdown() {
  openFilterColumn.value = null
}

function onColumnFilterApply(column, selectedValues) {
  emit('column-filter-changed', { column, selectedValues })
  openFilterColumn.value = null
}

// Click outside handler to close filter dropdown
function handleClickOutside(event) {
  if (openFilterColumn.value && wrapperRef.value) {
    // Check if click is inside the filter dropdown
    const filterDropdown = wrapperRef.value.querySelector('.column-filter-dropdown')
    if (filterDropdown && filterDropdown.contains(event.target)) {
      return
    }
    // Check if click is on a filter button (don't close, toggle will handle it)
    const filterBtns = wrapperRef.value.querySelectorAll('.filter-btn')
    for (const btn of filterBtns) {
      if (btn.contains(event.target)) {
        return
      }
    }
    openFilterColumn.value = null
  }
}

// Footer functions
function getColumnStats(key) {
  if (props.footerStats) {
    return props.footerStats[key] || null
  }
  return null
}

// Column resizing functions
function startResize(event, key) {
  const th = event.target.closest('th')
  if (!th) return

  resizing.value = {
    key,
    startX: event.clientX,
    startWidth: th.offsetWidth
  }

  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function handleResize(event) {
  if (!resizing.value) return

  const diff = event.clientX - resizing.value.startX
  const newWidth = Math.max(50, resizing.value.startWidth + diff)
  columnWidths.value[resizing.value.key] = newWidth
}

function stopResize() {
  resizing.value = null
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

function autoFitColumn(key) {
  // Find the column index
  const fieldIndex = props.fields.findIndex(f => f.key === key)
  if (fieldIndex === -1) return

  // Create a temporary element to measure text width
  const tempSpan = document.createElement('span')
  tempSpan.style.visibility = 'hidden'
  tempSpan.style.position = 'absolute'
  tempSpan.style.whiteSpace = 'nowrap'
  tempSpan.style.font = '0.875rem system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  document.body.appendChild(tempSpan)

  // Measure header text
  const field = props.fields[fieldIndex]
  tempSpan.textContent = field.label
  let maxWidth = tempSpan.offsetWidth + 60 // Add padding for sort button and handle

  // Measure cell contents
  const items = props.items || []
  for (const row of items) {
    const value = row[key]
    if (value != null) {
      tempSpan.textContent = String(value)
      const cellWidth = tempSpan.offsetWidth + 32 // Add cell padding
      maxWidth = Math.max(maxWidth, cellWidth)
    }
  }

  document.body.removeChild(tempSpan)

  // Set the column width with min/max constraints
  columnWidths.value[key] = Math.min(500, Math.max(50, maxWidth))
}

// Add click outside listener on mount
onMounted(() => {
  document.addEventListener('click', handleClickOutside, true)
})

// Cleanup event listeners on unmount
onUnmounted(() => {
  if (resizing.value) {
    document.removeEventListener('mousemove', handleResize)
    document.removeEventListener('mouseup', stopResize)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }
  document.removeEventListener('click', handleClickOutside, true)
})

// Expose methods and state to parent
defineExpose({
  hiddenColumns,
  hideColumn,
  unhideColumn,
  showAllColumns,
  isHidden,
  openFilterColumn,
  closeFilterDropdown
})
</script>

<style scoped>
.data-table-wrapper {
  width: 100%;
  position: relative;
}
.table-responsive { max-height: 70vh; overflow-y: auto; }
table { margin-bottom: 0; }
th { user-select: none; position: relative; }
th:hover { background-color: var(--bs-table-hover-bg); }
td { vertical-align: middle; }
td:hover { background-color: rgba(79, 70, 229, 0.06); cursor: text; }
.sort-btn { font-size: 0.7rem; line-height: 1; opacity: 0.4; }
.sort-btn:hover, .sort-btn.active { opacity: 1; }
.sort-badge {
  font-size: 0.55rem;
  vertical-align: super;
  margin-left: 1px;
}

/* Column filter button */
.filter-btn { font-size: 0.7rem; line-height: 1; opacity: 0.4; }
.filter-btn:hover, .filter-btn.active { opacity: 1; }

/* Column resize handle */
.resize-handle {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: col-resize;
  background-color: transparent;
  transition: background-color 0.15s ease;
  z-index: 10;
}

.resize-handle:hover,
.resize-handle:active {
  background-color: rgba(79, 70, 229, 0.4);
}

th:hover .resize-handle {
  background-color: rgba(79, 70, 229, 0.2);
}

/* Prevent text selection during resize */
.data-table-wrapper:active {
  user-select: none;
}

/* Smart Footer */
.smart-footer {
  background-color: #f8f9fa;
  border-top: 2px solid #dee2e6;
}

.smart-footer .footer-cell {
  font-size: 0.75rem;
  padding: 4px 8px;
  white-space: nowrap;
}

.smart-footer .footer-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  flex-grow: 1;
}

.smart-footer .footer-stat {
  color: #495057;
  padding: 1px 4px;
  background: #e9ecef;
  border-radius: 3px;
}

.smart-footer .stat-label {
  color: #6c757d;
  font-size: 0.7rem;
}

/* Ensure proper table structure */
tbody {
  display: table-row-group;
}

thead {
  display: table-header-group;
}

tfoot {
  display: table-footer-group;
}

/* Column Visibility Dropdown */


.column-visibility-dropdown .badge {
  font-size: 0.65rem;
  padding: 2px 5px;
}

.column-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 200px;
  max-height: 300px;
  display: flex;
  flex-direction: column;
  margin-top: 4px;
}

.column-menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 6px 6px 0 0;
}

.column-menu-list {
  overflow-y: auto;
  flex: 1;
  max-height: 200px;
}

.column-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.column-menu-item:hover {
  background: #f0f0f0;
}

.column-menu-item .column-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.85rem;
}

.column-menu-footer {
  padding: 8px 12px;
  border-top: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 0 0 6px 6px;
}

.btn-close-sm {
  font-size: 0.5rem;
  padding: 0.25rem;
}
</style>
