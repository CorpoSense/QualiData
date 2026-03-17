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
import { computed, reactive } from 'vue'

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

// Force reactivity by using a reactive object
const state = reactive({
  currentPage: props.currentPage,
  totalPages: props.totalPages,
  startRow: props.startRow,
  endRow: props.endRow,
  totalRows: props.totalRows
})

// Update state when props change
import { watch } from 'vue'
watch(() => props.currentPage, (v) => { state.currentPage = v })
watch(() => props.totalPages, (v) => { state.totalPages = v })
watch(() => props.startRow, (v) => { state.startRow = v })
watch(() => props.endRow, (v) => { state.endRow = v })
watch(() => props.totalRows, (v) => { state.totalRows = v })

const showingText = computed(() => {
  if (state.totalRows === 0) return 'No data'
  return `Showing ${state.startRow} - ${state.endRow} of ${state.totalRows}`
})

const pageText = computed(() => `Page ${state.currentPage} of ${state.totalPages}`)

const canGoPrev = computed(() => state.currentPage > 1)
const canGoNext = computed(() => state.currentPage < state.totalPages)
</script>

<style scoped>
.data-table-wrapper { width: 100%; }
.table-responsive { max-height: 70vh; overflow-y: auto; }
table { margin-bottom: 0; }
th { user-select: none; }
th:hover { background-color: var(--bs-table-hover-bg); }
td { vertical-align: middle; }
</style>
