<template>
  <div
    v-if="modelValue"
    class="pivot-modal"
    :style="modalStyle"
    @mousedown="bringToFront"
  >
    <!-- Header (Drag Handle) -->
    <div class="pivot-modal-header" @mousedown="startDrag">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-table"></i>
        <h6 class="mb-0">Pivot Table</h6>
        <span v-if="datasetName" class="text-muted small">— {{ datasetName }}</span>
      </div>
      <div class="d-flex gap-1">
        <BButton
          size="sm"
          variant="link"
          class="p-0"
          @click="togglePin"
          :title="isPinned ? 'Unpin' : 'Pin on top'"
        >
          <i :class="isPinned ? 'bi bi-pin-fill text-primary' : 'bi bi-pin'"></i>
        </BButton>
        <BButton
          size="sm"
          variant="link"
          class="p-0"
          @click="toggleMinimize"
          :title="isMinimized ? 'Maximize' : 'Minimize'"
        >
          <i :class="isMinimized ? 'bi bi-arrows-angle-expand' : 'bi bi-arrows-angle-contract'"></i>
        </BButton>
        <BButton
          size="sm"
          variant="link"
          class="p-0"
          @click="closeModal"
          title="Close"
        >
          <i class="bi bi-x-lg"></i>
        </BButton>
      </div>
    </div>

    <!-- Content -->
    <div v-show="!isMinimized" class="pivot-modal-content">
      <PivotTable
        :dataset-id="datasetId"
        :columns="columns"
        :selected-columns="selectedColumns"
        @close="closeModal"
      />
    </div>

    <!-- Resize Handle -->
    <div
      v-if="!isMinimized"
      class="resize-handle"
      @mousedown="startResize"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { BButton } from 'bootstrap-vue-next'
import PivotTable from './PivotTable.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  datasetId: {
    type: String,
    required: true
  },
  datasetName: {
    type: String,
    default: ''
  },
  columns: {
    type: Array,
    default: () => []
  },
  selectedColumns: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

// State
const isMinimized = ref(false)
const isPinned = ref(false)
const isDragging = ref(false)
const isResizing = ref(false)
const position = ref({ x: 100, y: 100 })
const size = ref({ width: 900, height: 600 })
const zIndex = ref(10000)
const dragOffset = ref({ x: 0, y: 0 })
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0 })

// Computed
const modalStyle = computed(() => ({
  left: `${position.value.x}px`,
  top: `${position.value.y}px`,
  width: isMinimized.value ? 'auto' : `${size.value.width}px`,
  height: isMinimized.value ? 'auto' : `${size.value.height}px`,
  zIndex: zIndex.value
}))

// Methods
function startDrag(event) {
  if (event.target.closest('button')) return
  
  isDragging.value = true
  dragOffset.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event) {
  if (!isDragging.value) return
  
  position.value = {
    x: event.clientX - dragOffset.value.x,
    y: event.clientY - dragOffset.value.y
  }
}

function stopDrag() {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  
  // Save position to localStorage
  savePosition()
}

function startResize(event) {
  isResizing.value = true
  resizeStart.value = {
    x: event.clientX,
    y: event.clientY,
    width: size.value.width,
    height: size.value.height
  }
  
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  event.preventDefault()
}

function onResize(event) {
  if (!isResizing.value) return
  
  const deltaX = event.clientX - resizeStart.value.x
  const deltaY = event.clientY - resizeStart.value.y
  
  size.value = {
    width: Math.max(400, resizeStart.value.width + deltaX),
    height: Math.max(300, resizeStart.value.height + deltaY)
  }
}

function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  
  // Save size to localStorage
  saveSize()
}

function toggleMinimize() {
  isMinimized.value = !isMinimized.value
}

function togglePin() {
  isPinned.value = !isPinned.value
}

function bringToFront() {
  if (!isPinned.value) {
    zIndex.value = Math.max(zIndex.value, 10000) + 1
  }
}

function closeModal() {
  emit('update:modelValue', false)
  emit('close')
}

function savePosition() {
  try {
    localStorage.setItem('pivot-modal-position', JSON.stringify(position.value))
  } catch (e) {
    // Ignore
  }
}

function saveSize() {
  try {
    localStorage.setItem('pivot-modal-size', JSON.stringify(size.value))
  } catch (e) {
    // Ignore
  }
}

function loadPosition() {
  try {
    const saved = localStorage.getItem('pivot-modal-position')
    if (saved) {
      position.value = JSON.parse(saved)
    }
  } catch (e) {
    // Ignore
  }
}

function loadSize() {
  try {
    const saved = localStorage.getItem('pivot-modal-size')
    if (saved) {
      size.value = JSON.parse(saved)
    }
  } catch (e) {
    // Ignore
  }
}

// Keyboard shortcuts
function handleKeydown(event) {
  if (event.key === 'Escape' && props.modelValue) {
    closeModal()
  }
}

// Lifecycle
onMounted(() => {
  loadPosition()
  loadSize()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
})

// Watch for modal open
watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      isMinimized.value = false
      bringToFront()
    }
  }
)
</script>

<style scoped>
.pivot-modal {
  position: fixed;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  resize: both;
}

.pivot-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  cursor: move;
  user-select: none;
}

.pivot-modal-header h6 {
  font-weight: 600;
  color: #334155;
}

.pivot-modal-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  background: linear-gradient(
    135deg,
    transparent 50%,
    #cbd5e1 50%,
    #cbd5e1 60%,
    transparent 60%,
    transparent 70%,
    #cbd5e1 70%,
    #cbd5e1 80%,
    transparent 80%
  );
}

.resize-handle:hover {
  background: linear-gradient(
    135deg,
    transparent 50%,
    #3b82f6 50%,
    #3b82f6 60%,
    transparent 60%,
    transparent 70%,
    #3b82f6 70%,
    #3b82f6 80%,
    transparent 80%
  );
}
</style>
