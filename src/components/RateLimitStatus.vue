<template>
  <div class="box">
    <h3 class="title is-5 mb-4">API Usage & Rate Limits</h3>
    
    <div class="columns is-multiline">
      <div v-for="provider in providers" :key="provider.name" class="column is-4">
        <div class="box provider-box">
          <div class="is-flex is-justify-content-space-between is-align-items-center mb-2">
            <strong>{{ provider.name }}</strong>
            <b-tag :type="getStatusType(provider)">{{ provider.remaining }}/{{ provider.limit }}</b-tag>
          </div>
          <b-progress 
            :value="getUsagePercent(provider)" 
            :type="getProgressType(provider)"
            size="is-small"
          ></b-progress>
          <p class="is-size-7 has-text-grey mt-1">
            Resets in {{ formatTime(provider.resetsAt) }}
          </p>
        </div>
      </div>
    </div>
    
    <div class="has-text-centered mt-4">
      <b-button size="is-small" @click="refreshUsage" :loading="loading">
        Refresh
      </b-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const loading = ref(false)
const providers = ref([
  { name: 'OpenAI', limit: 60, remaining: 60, resetsAt: null },
  { name: 'Anthropic', limit: 50, remaining: 50, resetsAt: null },
  { name: 'Google', limit: 60, remaining: 60, resetsAt: null },
  { name: 'Groq', limit: 30, remaining: 30, resetsAt: null },
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
      // Update provider stats from response
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
  if (percent >= 90) return 'is-danger'
  if (percent >= 70) return 'is-warning'
  return 'is-success'
}

function getStatusType(provider) {
  const percent = getUsagePercent(provider)
  if (percent >= 90) return 'is-danger'
  if (percent >= 70) return 'is-warning'
  return 'is-success'
}

function formatTime(dateStr) {
  if (!dateStr) return '1 min'
  const diff = new Date(dateStr) - new Date()
  if (diff <= 0) return 'now'
  return Math.ceil(diff / 60000) + ' min'
}
</script>

<style scoped>
.provider-box {
  padding: 1rem;
}
</style>
