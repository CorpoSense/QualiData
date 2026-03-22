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
            <td v-for="field in fields" :key="field.key" @click="selectable && $emit('row-clicked', { item: row, index })">
              {{ row[field.key] }}
            </td>
          </tr>
          <tr v-if="sortedItems.length === 0">
            <td :colspan="fields.length + (selectable ? 1 : 0) + (showIndex ? 1 : 0)" class="text-center text-muted py-4">
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
  showIndex: { type: Boolean, default: false },
  multiSort: { type: Boolean, default: false },
})

const emit = defineEmits(['row-clicked', 'head-clicked', 'row-selected', 'toggle-all', 'sort-changed'])

// Sort state: array of { key, dir } for multi-sort
const sortKeys = ref([]) // [{ key: 'name', dir: 'asc' }, ...]

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
.sort-badge {
  font-size: 0.55rem;
  vertical-align: super;
  margin-left: 1px;
}
</style>
