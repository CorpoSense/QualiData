<template>
  <div class="column-filter-dropdown" @click.stop>
    <!-- Header -->
    <div class="filter-header">
      <span class="fw-bold small">{{ field.label || field.key }}</span>
      <button class="btn-close btn-close-sm" @click.stop="$emit('close')"></button>
    </div>

    <!-- Search -->
    <div class="filter-search">
      <input
        ref="searchInput"
        v-model="searchQuery"
        type="text"
        class="form-control form-control-sm"
        placeholder="Search values..."
      >
    </div>

    <!-- Select All / Unselect All -->
    <div class="filter-actions">
      <button
        class="btn btn-sm btn-link text-decoration-none p-0"
        :disabled="allSelected"
        @click="selectAll"
      >Select All</button>
      <button
        class="btn btn-sm btn-link text-decoration-none p-0"
        :disabled="noneSelected"
        @click="unselectAll"
      >Unselect All</button>
      <span class="ms-auto text-muted small">{{ selectedCount }}/{{ totalItems }}</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="filter-loading">
      <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
      <span class="ms-2 small text-muted">Loading values...</span>
    </div>

    <!-- Value List -->
    <div v-else class="filter-list">
      <div
        v-for="item in filteredValues"
        :key="item.value === null ? '__null__' : item.value"
        class="filter-item"
        :class="{ 'text-muted': !isSelected(item) }"
        @click.stop="toggleValue(item)"
      >
        <input
          class="form-check-input"
          type="checkbox"
          :checked="isSelected(item)"
          @click.stop
          @change.stop="toggleValue(item)"
        >
        <span class="filter-value" :title="displayValue(item.value)">
          {{ displayValue(item.value) }}
        </span>
        <span class="filter-count badge bg-light text-dark">{{ item.count }}</span>
      </div>
      <div v-if="filteredValues.length === 0" class="text-center text-muted small py-2">
        No values found
      </div>
    </div>

    <!-- Too many values warning -->
    <div v-if="!loading && hasMoreValues" class="filter-warning">
      <i class="bi bi-exclamation-triangle me-1"></i>
      Showing top {{ values.length }} of {{ totalUnique }} unique values
    </div>

    <!-- Footer -->
    <div class="filter-footer">
      <button class="btn btn-sm btn-outline-secondary" @click.stop="clearFilter">Clear</button>
      <button class="btn btn-sm btn-primary" @click.stop="applyFilter">Apply</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const props = defineProps({
  field: { type: Object, required: true },
  values: { type: Array, default: () => [] }, // [{value, count}, ...]
  selectedValues: { type: Array, default: () => [] }, // values that are selected (null for null)
  loading: { type: Boolean, default: false },
  totalUnique: { type: Number, default: 0 },
})

const emit = defineEmits(['apply', 'close'])

const searchQuery = ref('')
const searchInput = ref(null)

// Local working copy of selected values (edited before Apply)
const localSelected = ref(new Set(props.selectedValues))

// Computed: filtered values based on search
const filteredValues = computed(() => {
  if (!searchQuery.value) return props.values
  const q = searchQuery.value.toLowerCase()
  return props.values.filter(item => {
    if (item.value === null) return searchQuery.value.toLowerCase().includes('null') || 'null'.includes(q)
    return String(item.value).toLowerCase().includes(q)
  })
})

// Computed: selection state
const allSelected = computed(() => {
  if (props.values.length === 0) return true
  return props.values.every(item => localSelected.value.has(item.value))
})

const noneSelected = computed(() => {
  return localSelected.value.size === 0
})

const selectedCount = computed(() => localSelected.value.size)

const totalItems = computed(() => props.values.length)

const hasMoreValues = computed(() => props.totalUnique > props.values.length)

// Methods
function isSelected(item) {
  return localSelected.value.has(item.value)
}

function toggleValue(item) {
  const key = item.value
  if (localSelected.value.has(key)) {
    localSelected.value.delete(key)
  } else {
    localSelected.value.add(key)
  }
  // Trigger reactivity
  localSelected.value = new Set(localSelected.value)
}

function selectAll() {
  localSelected.value = new Set(props.values.map(item => item.value))
}

function unselectAll() {
  localSelected.value = new Set()
}

function displayValue(val) {
  if (val === null || val === undefined) return '(null)'
  return String(val)
}

function clearFilter() {
  localSelected.value = new Set()
  emit('apply', [])
}

function applyFilter() {
  emit('apply', Array.from(localSelected.value))
}

// Focus search input on mount
onMounted(async () => {
  await nextTick()
  searchInput.value?.focus()
})
</script>

<style scoped>
.column-filter-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 260px;
  max-height: 400px;
  display: flex;
  flex-direction: column;
  margin-top: 2px;
  z-index: 1000;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 6px 6px 0 0;
}

.filter-search {
  padding: 6px 12px;
  border-bottom: 1px solid #eee;
}

.filter-search input {
  font-size: 0.8rem;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-bottom: 1px solid #eee;
  font-size: 0.75rem;
}

.filter-actions .btn-link {
  font-size: 0.75rem;
  color: #0d6efd;
}

.filter-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 12px;
}

.filter-list {
  overflow-y: auto;
  flex: 1;
  max-height: 220px;
  min-height: 40px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  cursor: pointer;
  transition: background 0.1s;
  font-size: 0.8rem;
}

.filter-item:hover {
  background: #f0f0f0;
}

.filter-item .form-check-input {
  margin-top: 0;
  cursor: pointer;
  flex-shrink: 0;
}

.filter-value {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.filter-count {
  font-size: 0.65rem;
  flex-shrink: 0;
}

.filter-warning {
  padding: 4px 12px;
  font-size: 0.7rem;
  color: #856404;
  background: #fff3cd;
  border-top: 1px solid #eee;
}

.filter-footer {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
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
