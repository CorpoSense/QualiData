<template>
  <div class="data-table-wrapper">
    <!-- Table -->
    <div class="table-responsive">
      <table class="table table-hover table-striped table-sm">
        <thead>
          <tr>
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
              @click="$emit('head-clicked', field)"
              style="cursor: pointer"
            >
              <span class="d-flex align-items-center justify-content-between">
                {{ field.label }}
                <button
                  class="btn btn-sm btn-outline-secondary border-0 py-0 px-1 sort-btn"
                  :class="{ active: sortKey === field.key }"
                  @click.stop="toggleSort(field.key)"
                  :title="sortTitle(field.key)"
                >
                  <i v-if="sortKey !== field.key" class="bi bi-arrow-down-up text-muted"></i>
                  <i v-else-if="sortDir === 'asc'" class="bi bi-arrow-up"></i>
                  <i v-else class="bi bi-arrow-down"></i>
                </button>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(row, index) in sortedItems" 
            :key="index"
            @click="!selectable && $emit('row-clicked', { item: row, index })"
          >
            <td v-if="selectable" class="text-center" @click.stop>
              <input
                class="form-check-input"
                type="checkbox"
                :checked="selectedRows.includes(index)"
                @change="$emit('row-selected', index)"
              >
            </td>
            <td v-for="field in fields" :key="field.key" @click="selectable && $emit('row-clicked', { item: row, index })">
              {{ row[field.key] }}
            </td>
          </tr>
          <tr v-if="sortedItems.length === 0">
            <td :colspan="fields.length + (selectable ? 1 : 0)" class="text-center text-muted py-4">
              No data to display
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  fields: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] },
  selectable: { type: Boolean, default: false },
  selectedRows: { type: Array, default: () => [] },
})

defineEmits(['row-clicked', 'head-clicked', 'row-selected', 'toggle-all'])

const sortKey = ref(null)
const sortDir = ref('asc')

const allSelected = computed(() =>
  props.items.length > 0 && props.selectedRows.length === props.items.length
)
const someSelected = computed(() => props.selectedRows.length > 0)

function toggleSort(key) {
  if (sortKey.value === key) {
    if (sortDir.value === 'asc') {
      sortDir.value = 'desc'
    } else {
      // Reset
      sortKey.value = null
      sortDir.value = 'asc'
    }
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function sortTitle(key) {
  if (sortKey.value !== key) return 'Sort'
  return sortDir.value === 'asc' ? 'Sorted ascending' : 'Sorted descending'
}

const sortedItems = computed(() => {
  if (!sortKey.value) return props.items
  const key = sortKey.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  return [...props.items].sort((a, b) => {
    const va = a[key]
    const vb = b[key]
    if (va == null && vb == null) return 0
    if (va == null) return dir
    if (vb == null) return -dir
    // Numeric comparison if both are numbers
    const na = Number(va)
    const nb = Number(vb)
    if (!isNaN(na) && !isNaN(nb)) return (na - nb) * dir
    return String(va).localeCompare(String(vb)) * dir
  })
})

function isSelected(field) {
  const fieldKey = field.key || field.field
  return props.selectedColumns.includes(fieldKey)
}
</script>

<style scoped>
.data-table-wrapper { width: 100%; }
.table-responsive { max-height: 70vh; overflow-y: auto; }
table { margin-bottom: 0; }
th { user-select: none; }
th:hover { background-color: var(--bs-table-hover-bg); }
td { vertical-align: middle; }
.sort-btn { font-size: 0.7rem; line-height: 1; opacity: 0.4; }
.sort-btn:hover, .sort-btn.active { opacity: 1; }
</style>
