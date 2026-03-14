<template>
  <div class="project-card" @click="$emit('click')">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div class="project-icon">
          <i class="bi bi-folder-fill text-warning"></i>
        </div>
        <BDropdown v-if="showActions" :text="dropdownText" variant="outline-secondary" size="sm" @click.stop>
          <slot name="actions"></slot>
        </BDropdown>
      </div>
      
      <h3 class="h6 mb-2 project-title">{{ project.name }}</h3>
      
      <p class="text-muted small mb-3 project-description">
        {{ project.description || 'No description' }}
      </p>

      <div class="d-flex justify-content-between small text-muted">
        <span>
          <i class="bi bi-database me-1"></i>
          {{ project.datasets_count || project.row_count || 0 }} {{ project.datasets_count ? 'datasets' : 'rows' }}
        </span>
        <span>{{ formatMeta(project) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  project: {
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

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return date.toLocaleDateString()
}

function formatBytes(bytes) {
  if (!bytes) return ''
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatMeta(project) {
  if (project.storage_bytes) {
    return formatBytes(project.storage_bytes)
  }
  return formatDate(project.created_at)
}
</script>

<style scoped>
.project-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(79, 70, 229, 0.2);
}

.project-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(249, 192, 11, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.project-title {
  font-weight: 600;
  color: var(--dark-color, #0f172a);
}

.project-description {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
