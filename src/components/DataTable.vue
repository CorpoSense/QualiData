<template>
  <div class="data-table-wrapper">
    <!-- Table -->
    <div class="table-responsive">
      <table class="table table-hover table-striped table-sm">
        <thead>
          <tr>
            <th 
              v-for="field in fields" 
              :key="field.key"
              @click="$emit('head-clicked', field)"
              style="cursor: pointer"
            >
              {{ field.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(row, index) in items" 
            :key="index"
            :class="{ 'table-active': isSelected(row) }"
            @click="handleRowClick(row, index)"
          >
            <td v-for="field in fields" :key="field.key">
              {{ row[field.key] }}
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td :colspan="fields.length" class="text-center text-muted py-4">
              No data to display
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="d-flex justify-content-between align-items-center mt-3">
      <small class="text-muted">
        Showing {{ startRow }} - {{ endRow }} of {{ totalRows }}
      </small>
      <div class="d-flex align-items-center gap-2">
        <button 
          class="btn btn-sm btn-outline-secondary" 
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          ← Prev
        </button>
        <span class="text-muted">Page {{ currentPage }} of {{ totalPages }}</span>
        <button 
          class="btn btn-sm btn-outline-secondary" 
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Use defineModel for two-way binding
const currentPage = defineModel('currentPage', { default: 1 })
const perPage = defineModel('perPage', { default: 10 })
const totalRows = defineModel('totalRows', { default: 0 })

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  fields: {
    type: Array,
    default: () => []
  },
  selectedItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['page-change', 'row-clicked', 'head-clicked'])

// Computed values using the model
const totalPages = computed(() => {
  return Math.ceil(totalRows.value / perPage.value) || 1
})

const startRow = computed(() => {
  if (totalRows.value === 0) return 0
  return (currentPage.value - 1) * perPage.value + 1
})

const endRow = computed(() => {
  return Math.min(currentPage.value * perPage.value, totalRows.value)
})

function goToPage(newPage) {
  if (newPage >= 1 && newPage <= totalPages.value) {
    currentPage.value = newPage
    emit('page-change', newPage)
  }
}

function isSelected(row) {
  return props.selectedItems.some(item => JSON.stringify(item) === JSON.stringify(row))
}

function handleRowClick(row, index) {
  emit('row-clicked', { item: row, index })
}
</script>

<style scoped>
.data-table-wrapper {
  width: 100%;
}

.table-responsive {
  max-height: 70vh;
  overflow-y: auto;
}

table {
  margin-bottom: 0;
}

th {
  user-select: none;
}

th:hover {
  background-color: var(--bs-table-hover-bg);
}

td {
  vertical-align: middle;
}
</style>
