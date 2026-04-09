<template>
  <BModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="Reorder Columns"
    size="lg"
    @hide="onCancel"
  >
    <div class="alert alert-info py-2 mb-3">
      <i class="bi bi-info-circle me-1"></i>
      Drag and drop columns to reorder them, or use the <strong>Move Up</strong> / <strong>Move Down</strong> buttons.
    </div>

    <!-- Column List with Drag & Drop -->
    <div class="mb-3">
      <label class="form-label fw-bold">Column Order</label>
      <div 
        class="column-list" 
        style="max-height: 300px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 4px;"
      >
        <div
          v-for="(col, index) in columnOrder"
          :key="col.field"
          class="column-item d-flex align-items-center gap-2 p-2 border-bottom"
          :class="{ 'bg-light': isSelected(col.field), 'cursor-move': true }"
          style="cursor: grab;"
          draggable="true"
          @dragstart="onDragStart($event, index)"
          @dragover.prevent
          @drop="onDrop($event, index)"
        >
          <i class="bi bi-grip-vertical text-muted"></i>
          <span class="text-muted" style="min-width: 20px;">{{ index + 1 }}.</span>
          <div class="form-check">
            <input
              class="form-check-input"
              type="checkbox"
              :value="col.field"
              v-model="selectedCols"
              :id="'reorder-col-' + col.field"
            >
            <label class="form-check-label" :for="'reorder-col-' + col.field">
              {{ col.label || col.field }}
            </label>
          </div>
          <div class="ms-auto d-flex gap-1">
            <BButton 
              size="sm" 
              variant="link" 
              class="p-0" 
              :disabled="index === 0"
              @click="moveItemUp(index)"
              title="Move up"
            >
              <i class="bi bi-arrow-up"></i>
            </BButton>
            <BButton 
              size="sm" 
              variant="link" 
              class="p-0" 
              :disabled="index === columnOrder.length - 1"
              @click="moveItemDown(index)"
              title="Move down"
            >
              <i class="bi bi-arrow-down"></i>
            </BButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="d-flex gap-2 mb-3">
      <BButton size="sm" variant="outline-secondary" @click="selectAll">
        Select All
      </BButton>
      <BButton size="sm" variant="outline-secondary" @click="clearSelection">
        Clear
      </BButton>
      <BButton 
        size="sm" 
        variant="outline-primary" 
        :disabled="selectedCols.length === 0"
        @click="moveSelectedUp"
      >
        <i class="bi bi-arrow-up me-1"></i> Move Selected Up
      </BButton>
      <BButton 
        size="sm" 
        variant="outline-primary" 
        :disabled="selectedCols.length === 0"
        @click="moveSelectedDown"
      >
        <i class="bi bi-arrow-down me-1"></i> Move Selected Down
      </BButton>
    </div>

    <!-- Preview -->
    <div class="p-2 bg-light rounded">
      <small class="text-muted">Click Apply to save changes</small>
    </div>

    <template #footer>
      <BButton variant="outline-secondary" @click="onCancel">Cancel</BButton>
      <BButton variant="primary" @click="onApply">
        <i class="bi bi-check-lg me-1"></i> Apply
      </BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { BModal, BButton } from 'bootstrap-vue-next'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  columns: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'apply', 'cancel'])

// Local state - track the ordered columns
const columnOrder = ref([])
const selectedCols = ref([])

// Initialize when modal opens or columns change
watch(() => props.columns, (newCols) => {
  columnOrder.value = [...newCols]
  selectedCols.value = [...props.selectedColumns]
}, { immediate: true })

watch(() => props.selectedColumns, (newSelected) => {
  selectedCols.value = [...newSelected]
}, { immediate: true })

// Check if column is selected
function isSelected(field) {
  return selectedCols.value.includes(field)
}

// Selection controls
function selectAll() {
  selectedCols.value = columnOrder.value.map(c => c.field)
}

function clearSelection() {
  selectedCols.value = []
}

// Move a single item up
function moveItemUp(index) {
  if (index <= 0) return
  const temp = columnOrder.value[index]
  columnOrder.value[index] = columnOrder.value[index - 1]
  columnOrder.value[index - 1] = temp
}

// Move a single item down
function moveItemDown(index) {
  if (index >= columnOrder.value.length - 1) return
  const temp = columnOrder.value[index]
  columnOrder.value[index] = columnOrder.value[index + 1]
  columnOrder.value[index + 1] = temp
}

// Move all selected columns up together
function moveSelectedUp() {
  if (selectedCols.value.length === 0) return
  
  // Find positions of all selected columns in order
  const selectedPositions = columnOrder.value
    .map((col, idx) => ({ field: col.field, idx }))
    .filter(item => selectedCols.value.includes(item.field))
    .sort((a, b) => a.idx - b.idx)
  
  // Move each selected column up if possible (from top to bottom)
  for (const item of selectedPositions) {
    if (item.idx > 0) {
      // Check if the column above is NOT selected
      const aboveField = columnOrder.value[item.idx - 1].field
      if (!selectedCols.value.includes(aboveField)) {
        // Swap
        const temp = columnOrder.value[item.idx]
        columnOrder.value[item.idx] = columnOrder.value[item.idx - 1]
        columnOrder.value[item.idx - 1] = temp
      }
    }
  }
}

// Move all selected columns down together
function moveSelectedDown() {
  if (selectedCols.value.length === 0) return
  
  // Find positions of all selected columns in order (bottom to top)
  const selectedPositions = columnOrder.value
    .map((col, idx) => ({ field: col.field, idx }))
    .filter(item => selectedCols.value.includes(item.field))
    .sort((a, b) => b.idx - a.idx)
  
  // Move each selected column down if possible (from bottom to top)
  for (const item of selectedPositions) {
    if (item.idx < columnOrder.value.length - 1) {
      // Check if the column below is NOT selected
      const belowField = columnOrder.value[item.idx + 1].field
      if (!selectedCols.value.includes(belowField)) {
        // Swap
        const temp = columnOrder.value[item.idx]
        columnOrder.value[item.idx] = columnOrder.value[item.idx + 1]
        columnOrder.value[item.idx + 1] = temp
      }
    }
  }
}

// Drag & Drop handlers
let draggedIndex = null

function onDragStart(event, index) {
  draggedIndex = index
  event.dataTransfer.effectAllowed = 'move'
}

function onDrop(event, dropIndex) {
  if (draggedIndex === null || draggedIndex === dropIndex) return
  
  // Remove dragged item and insert at new position
  const item = columnOrder.value.splice(draggedIndex, 1)[0]
  columnOrder.value.splice(dropIndex, 0, item)
  draggedIndex = null
}

// Apply changes
function onApply() {
  const newOrder = columnOrder.value.map(c => c.field)
  emit('apply', newOrder)
  emit('update:modelValue', false)
}

// Cancel
function onCancel() {
  emit('cancel')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.column-list {
  background: #fff;
}

.column-item:last-child {
  border-bottom: none !important;
}

.column-item:hover {
  background: #f8f9fa !important;
}

.cursor-move {
  user-select: none;
}
</style>