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
            @click="$emit('row-clicked', { item: row, index })"
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
        {{ showingText }}
      </small>
      <div class="d-flex align-items-center gap-2">
        <button 
          class="btn btn-sm btn-outline-secondary" 
          :disabled="!canGoPrev"
          @click="$emit('prev-page')"
        >
          ← Prev
        </button>
        <span class="text-muted">{{ pageText }}</span>
        <button 
          class="btn btn-sm btn-outline-secondary" 
          :disabled="!canGoNext"
          @click="$emit('next-page')"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  fields: { type: Array, default: () => [] },
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  startRow: { type: Number, default: 1 },
  endRow: { type: Number, default: 0 },
  totalRows: { type: Number, default: 0 }
})

defineEmits(['prev-page', 'next-page', 'row-clicked', 'head-clicked'])

const showingText = computed(() => {
  if (props.totalRows === 0) return 'No data'
  return `Showing ${props.startRow} - ${props.endRow} of ${props.totalRows}`
})

const pageText = computed(() => `Page ${props.currentPage} of ${props.totalPages}`)

const canGoPrev = computed(() => props.currentPage > 1)
const canGoNext = computed(() => props.currentPage < props.totalPages)
</script>

<style scoped>
.data-table-wrapper { width: 100%; }
.table-responsive { max-height: 70vh; overflow-y: auto; }
table { margin-bottom: 0; }
th { user-select: none; }
th:hover { background-color: var(--bs-table-hover-bg); }
td { vertical-align: middle; }
</style>
