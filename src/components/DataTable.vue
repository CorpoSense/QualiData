<template>
  <div class="data-table-wrapper">
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
              v-for="field in fields"
              :key="field.key"
              :class="{ 'table-primary': isSelected(field) }"
              :style="{ width: columnWidths[field.key] ? columnWidths[field.key] + 'px' : 'auto', minWidth: '50px', position: 'relative' }"
              @click="$emit('head-clicked', field)"
              style="cursor: pointer"
            >
              <span class="d-flex align-items-center justify-content-between">
                {{ field.label }}
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
              </span>
              <div
                class="resize-handle"
                @mousedown.prevent="startResize($event, field.key)"
                @dblclick.stop="autoFitColumn(field.key)"
                title="Drag to resize, double-click to auto-fit"
              ></div>
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
            <td v-for="field in fields" :key="field.key" @click="selectable && $emit('row-clicked', { item: row, index })" @dblclick="$emit('cell-dblclick', { row: index, column: field.key, value: row[field.key] })">
              {{ row[field.key] }}
            </td>
          </tr>
          <tr v-if="sortedItems.length === 0">
            <td :colspan="fields.length + (selectable ? 1 : 0) + (showIndex ? 1 : 0)" class="text-center text-muted py-4">
              No data to display
            </td>
          </tr>
        </tbody>
        <!-- Smart Footer -->
        <tfoot v-if="showFooter" class="smart-footer">
          <tr>
            <td v-if="showIndex" class="text-muted small text-center"></td>
            <td v-if="selectable"></td>
            <td v-for="field in fields" :key="field.key" class="footer-cell">
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
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  fields: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] },
  selectable: { type: Boolean, default: false },
  selectedRows: { type: Array, default: () => [] },
  showIndex: { type: Boolean, default: false },
  multiSort: { type: Boolean, default: false },
  // Footer props
  showFooter: { type: Boolean, default: false },
  footerStats: { type: Object, default: () => ({}) },
  // footerConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['row-clicked', 'head-clicked', 'row-selected', 'toggle-all', 'sort-changed', 'cell-dblclick', 'footer-config-changed'])

// Sort state: array of { key, dir } for multi-sort
const sortKeys = ref([]) // [{ key: 'name', dir: 'asc' }, ...]

// Column resizing state
const columnWidths = ref({}) // { key: width }
const resizing = ref(null) // { key, startX, startWidth }

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

// Cleanup event listeners on unmount
onUnmounted(() => {
  if (resizing.value) {
    document.removeEventListener('mousemove', handleResize)
    document.removeEventListener('mouseup', stopResize)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }
})
</script>

<style scoped>
.data-table-wrapper { width: 100%; }
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
</style>
