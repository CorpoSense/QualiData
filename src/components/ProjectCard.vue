<template>
  <div class="project-card" @click="$emit('click')">
    <div class="card-body d-flex flex-column p-3">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <div class="project-icon">
          <i class="bi bi-folder-fill"></i>
        </div>
        <BDropdown v-if="showActions" no-caret variant="link" size="sm" class="p-0 text-muted" @click.stop>
          <template #button-content>
            <i class="bi bi-three-dots-vertical"></i>
          </template>
          <slot name="actions"></slot>
        </BDropdown>
      </div>

      <h3 class="h6 mb-1 project-title">{{ project.name }}</h3>

      <p class="text-muted small mb-3 project-description">
        {{ project.description || 'No description' }}
      </p>

      <div class="mt-auto d-flex justify-content-between align-items-center project-meta">
        <span class="badge bg-light text-dark">
          <i class="bi bi-database me-1"></i>
          {{ project.datasets_count || project.row_count || 0 }} {{ project.datasets_count ? 'datasets' : 'rows' }}
        </span>
        <span class="small text-muted">
          <i class="bi bi-clock me-1"></i>{{ formatMeta(project) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatFileSize } from '@/utils/file'

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

function formatMeta(project) {
  if (project.storage_bytes) {
    return formatFileSize(project.storage_bytes)
  }
  return formatDate(project.created_at)
}
</script>

<style scoped>
.project-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 100%;
  overflow: hidden;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  border-color: #c7d2fe;
}

.project-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #6366f1;
}

.project-title {
  font-weight: 600;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.project-description {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.4em;
  line-height: 1.4;
  color: #94a3b8;
}

.project-meta {
  padding-top: 0.75rem;
  border-top: 1px solid #f1f5f9;
}

.project-meta .badge {
  font-weight: 500;
  font-size: 0.75rem;
}
</style>
