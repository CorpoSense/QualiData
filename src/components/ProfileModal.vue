<template>
  <BModal :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" title="Data Profile" size="lg">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted mt-2">Loading profile…</p>
    </div>

    <!-- Profile Data -->
    <div v-else-if="profileData">
      <!-- KPI Cards Row (from DataViewer style) -->
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="card">
            <div class="card-body text-center">
              <h3>{{ profileData.total_rows || 0 }}</h3>
              <p class="text-muted mb-0">Total Rows</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-body text-center">
              <h3>{{ profileData.total_columns || 0 }}</h3>
              <p class="text-muted mb-0">Columns</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-body text-center">
              <h3>{{ totalNulls }}</h3>
              <p class="text-muted mb-0">Null Values</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Column Profiles Section -->
      <h5 class="mb-3">Column Profiles</h5>
      <div class="row g-3">
        <div v-for="col in profileData.columns" :key="col.name" class="col-md-6">
          <div class="card h-100">
            <div class="card-body py-2 px-3">
              <!-- Column Header -->
              <div class="d-flex justify-content-between align-items-center mb-1">
                <strong class="small">{{ col.name }}</strong>
                <span class="badge bg-light text-dark">{{ col.dtype }}</span>
              </div>

              <!-- Stats Row (from ProjectDetail style) -->
              <div class="small text-muted">
                <span v-if="col.null_count > 0" class="text-danger me-2">
                  {{ col.null_count }} nulls ({{ col.null_percent }}%)
                </span>
                <span v-else class="me-2">No nulls</span>
                <span class="me-2">{{ col.unique_count }} unique</span>
                <span class="ms-2">Quality: {{ col.quality_score }}%</span>
              </div>

              <!-- Null Percentage Progress Bar -->
              <div class="progress mt-1" style="height: 4px;">
                <div
                  class="progress-bar"
                  :class="getNullPercentageClass(col.null_percent)"
                  role="progressbar"
                  :style="{ width: Math.min(col.null_percent, 100) + '%' }"
                ></div>
              </div>

              <!-- Top Values (from ProjectDetail style) -->
              <div v-if="col.stats?.top_values?.length" class="mt-1">
                <small class="text-muted">Top: </small>
                <small
                  v-for="(v, i) in col.stats.top_values.slice(0, 3)"
                  :key="i"
                  class="badge bg-light text-dark me-1"
                >{{ v.value.slice(0, 10) }}... ({{ v.count }})</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-4 text-muted">
      <i class="bi bi-bar-chart fs-1"></i>
      <p class="mt-2">No profile data available</p>
    </div>

    <template #footer>
      <BButton variant="primary" @click="$emit('update:modelValue', false)">Close</BButton>
    </template>
  </BModal>
</template>

<script setup>
import { computed } from 'vue'
import { BModal, BButton } from 'bootstrap-vue-next'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  profileData: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

defineEmits(['update:modelValue'])

// Calculate total nulls from all columns
const totalNulls = computed(() => {
  if (!props.profileData?.columns) return 0
  return props.profileData.columns.reduce((sum, col) => sum + (col.null_count || 0), 0)
})

// Get CSS class based on null percentage for progress bar color
function getNullPercentageClass(percent) {
  if (percent > 50) return 'bg-danger'
  if (percent > 20) return 'bg-warning'
  return 'bg-success'
}
</script>

<style scoped>
.card {
  border: 1px solid #e2e8f0;
}

.progress {
  background-color: #e2e8f0;
}

.h-100 {
  height: 100%;
}

.badge {
  font-size: 0.75rem;
}
</style>