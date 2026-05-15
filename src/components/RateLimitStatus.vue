<template>
  <div class="card">
    <div class="card-body">
      <h3 class="h5 mb-4">API Usage & Rate Limits</h3>
      
      <div class="row g-3">
        <div v-for="provider in providers" :key="provider.name" class="col-md-4">
          <div class="card border">
            <div class="card-body p-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <strong>{{ provider.name }}</strong>
                <BBadge :variant="getStatusType(provider)">{{ provider.remaining }}/{{ provider.limit }}</BBadge>
              </div>
              <BProgress :model-value="getUsagePercent(provider)" :variant="getProgressType(provider)" style="height: 8px;"></BProgress>
              <p class="small text-muted mt-1 mb-0">
                Resets in {{ formatTime(provider.resetsAt) }}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="text-center mt-4">
        <BButton size="sm" variant="outline-secondary" @click="refreshUsage" :loading="loading">
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh
        </BButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, onMounted } from 'vue'
import { BButton, BBadge, BProgress } from 'bootstrap-vue-next'

const apiUrl = getApiUrl()
const loading = ref(false)
const providers = ref([
  { name: 'OpenAI', limit: 60, remaining: 60, resetsAt: null },
  { name: 'Anthropic', limit: 50, remaining: 50, resetsAt: null },
  { name: 'Google', limit: 60, remaining: 60, resetsAt: null },
  { name: 'Groq', limit: 30, remaining: 30, resetsAt: null },
  { name: 'NVIDIA', limit: 30, remaining: 30, resetsAt: null },
  { name: 'DeepSeek', limit: 60, remaining: 60, resetsAt: null },
])

onMounted(() => {
  refreshUsage()
})

async function refreshUsage() {
  loading.value = true
  try {
    const res = await fetch(`${apiUrl}/api/rate-limit/status`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      if (data.providers) {
        providers.value = providers.value.map(p => {
          const providerData = data.providers[p.name.toLowerCase()]
          if (providerData) {
            return { ...p, ...providerData }
          }
          return p
        })
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getUsagePercent(provider) {
  if (!provider.limit) return 0
  return ((provider.limit - provider.remaining) / provider.limit) * 100
}

function getProgressType(provider) {
  const percent = getUsagePercent(provider)
  if (percent >= 90) return 'danger'
  if (percent >= 70) return 'warning'
  return 'success'
}

function getStatusType(provider) {
  const percent = getUsagePercent(provider)
  if (percent >= 90) return 'danger'
  if (percent >= 70) return 'warning'
  return 'success'
}

function formatTime(dateStr) {
  if (!dateStr) return '1 min'
  const diff = new Date(dateStr) - new Date()
  if (diff <= 0) return 'now'
  return Math.ceil(diff / 60000) + ' min'
}
</script>
