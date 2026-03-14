<template>
  <div class="dataset-card" @click="$emit('click')">
    <div class="card-body d-flex flex-column">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <h3 class="h6 mb-0 dataset-title">{{ dataset.name }}</h3>
        <BDropdown v-if="showActions" :text="dropdownText" variant="outline-secondary" size="sm" @click.stop>
          <slot name="actions"></slot>
        </BDropdown>
      </div>
      
      <p class="small text-muted mb-3 dataset-description">
        {{ dataset.description || 'No description' }}
      </p>
      
      <div class="mt-auto d-flex justify-content-between align-items-center dataset-meta">
        <span class="small text-muted">
          <i class="bi bi-table me-1"></i> {{ formatNumber(dataset.row_count) }} rows
        </span>
        <span class="badge bg-light text-dark">{{ dataset.file_type?.toUpperCase() || 'FILE' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  dataset: {
    type: Object,
    required: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  dropdownText: {
    type: String,
    default: 'Actions'
  }
})

defineEmits(['click'])

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped>
.dataset-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.dataset-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(79, 70, 229, 0.2);
}

.card-body {
  padding: 1.25rem;
}

.dataset-title {
  font-weight: 600;
  color: var(--dark-color, #0f172a);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dataset-description {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.5em;
}

.dataset-meta {
  padding-top: 0.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}
</style>
