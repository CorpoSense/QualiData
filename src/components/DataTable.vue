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
          :disabled="props.currentPage <= 1"
          @click="goToPage(props.currentPage - 1)"
        >
          ← Prev
        </button>
        <span class="text-muted">Page {{ props.currentPage }} of {{ totalPages }}</span>
        <button 
          class="btn btn-sm btn-outline-secondary" 
          :disabled="props.currentPage >= totalPages"
          @click="goToPage(props.currentPage + 1)"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  fields: {
    type: Array,
    default: () => []
  },
  totalRows: {
    type: Number,
    default: 0
  },
  perPage: {
    type: Number,
    default: 10
  },
  currentPage: {
    type: Number,
    default: 1
  },
  selectedItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['page-change', 'row-clicked', 'head-clicked'])

// Watch for prop changes to debug
watch(() => props.currentPage, (newVal) => {
  console.log('currentPage changed to:', newVal)
})

// Computed values
const totalPages = computed(() => {
  return Math.ceil(props.totalRows / props.perPage) || 1
})

const startRow = computed(() => {
  if (props.totalRows === 0) return 0
  return (props.currentPage - 1) * props.perPage + 1
})

const endRow = computed(() => {
  return Math.min(props.currentPage * props.perPage, props.totalRows)
})

function goToPage(newPage) {
  if (newPage >= 1 && newPage <= totalPages.value) {
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
