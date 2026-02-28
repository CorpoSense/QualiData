<template>
  <div class="data-viewer">
    <!-- Toolbar -->
    <div class="box mb-3">
      <div class="is-flex is-justify-content-space-between is-align-items-center">
        <div class="is-flex is-align-items-center">
          <b-field class="mb-0 mr-3">
            <b-select v-model="limit" size="is-small">
              <option :value="25">25 rows</option>
              <option :value="50">50 rows</option>
              <option :value="100">100 rows</option>
            </b-select>
          </b-field>
          <b-button size="is-small" @click="refreshData" icon-left="refresh"></b-button>
        </div>
        
        <div class="is-flex is-align-items-center">
          <b-field class="mb-0 mr-2">
            <b-input v-model="searchQuery" size="is-small" placeholder="Search..." icon="magnify"></b-input>
          </b-field>
          <b-button size="is-small" type="is-info" @click="showProfile = true" icon-left="chart-bar">
            Profile
          </b-button>
          <b-button size="is-small" type="is-success" @click="showCompare = true" icon-left="compare">
            Compare
          </b-button>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="box table-container">
      <div v-if="loading" class="has-text-centered py-6">
        <b-icon icon="loading" size="is-large" spin></b-icon>
      </div>
      
      <b-table
        v-else
        :data="filteredData"
        :columns="columns"
        :per-page="limit"
        paginated
        sticky-header
        :height="'500px'"
        :narrowed="true"
        :loading="loading"
        @click="handleCellClick"
      >
        <template #empty>
          <div class="has-text-centered py-4">
            <p class="has-text-grey">No data available</p>
          </div>
        </template>
      </b-table>
    </div>

    <!-- Summary Stats -->
    <div class="columns mt-3">
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Total Rows</p>
          <p class="title is-5">{{ dataset?.row_count || 0 }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Columns</p>
          <p class="title is-5">{{ columns.length }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Null Values</p>
          <p class="title is-5">{{ nullCount }}</p>
        </div>
      </div>
      <div class="column is-3">
        <div class="box has-text-centered py-3">
          <p class="heading">Duplicates</p>
          <p class="title is-5">{{ duplicateCount }}</p>
        </div>
      </div>
    </div>

    <!-- Profile Modal -->
    <b-modal v-model="showProfile" :has-modal-card="true" :width="'80%'">
      <div class="modal-card" style="width: 80%">
        <header class="modal-card-head">
          <p class="modal-card-title">Column Profile</p>
          <button class="delete" @click="showProfile = false"></button>
        </header>
        <section class="modal-card-body">
          <div v-if="profileData" class="columns is-multiline">
            <div v-for="col in profileData.columns" :key="col.name" class="column is-4">
              <div class="box">
                <h4 class="title is-6">{{ col.name }}</h4>
                <p><strong>Type:</strong> {{ col.dtype }}</p>
                <p><strong>Nulls:</strong> {{ col.null_count }} ({{ col.null_pct }}%)</p>
                <p><strong>Unique:</strong> {{ col.unique_count }}</p>
                <div v-if="col.type === 'numeric'">
                  <p><strong>Min:</strong> {{ col.min }}</p>
                  <p><strong>Max:</strong> {{ col.max }}</p>
                  <p><strong>Mean:</strong> {{ col.mean?.toFixed(2) }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </b-modal>

    <!-- Compare Modal -->
    <b-modal v-model="showCompare" :has-modal-card="true">
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Compare Operations</p>
          <button class="delete" @click="showCompare = false"></button>
        </header>
        <section class="modal-card-body">
          <b-field label="Select Operation">
            <b-select v-model="compareOpId" expanded>
              <option v-for="op in operations" :key="op.id" :value="op.id">
                {{ op.operation_type }} - {{ formatDate(op.created_at) }}
              </option>
            </b-select>
          </b-field>
          <b-button type="is-primary" :loading="comparing" @click="loadComparison">Compare</b-button>
        </section>
      </div>
    </b-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  datasetId: { type: Number, required: true }
})

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(true)
const dataset = ref(null)
const data = ref([])
const columns = ref([])
const operations = ref([])
const limit = ref(25)
const searchQuery = ref('')
const showProfile = ref(false)
const showCompare = ref(false)
const profileData = ref(null)
const comparing = ref(false)
const compareOpId = ref(null)
const nullCount = ref(0)
const duplicateCount = ref(0)

const filteredData = computed(() => {
  if (!searchQuery.value) return data.value
  const q = searchQuery.value.toLowerCase()
  return data.value.filter(row => 
    Object.values(row).some(val => String(val).toLowerCase().includes(q))
  )
})

onMounted(async () => {
  await refreshData()
})

watch(limit, refreshData)

async function refreshData() {
  loading.value = true
  try {
    const [previewRes, opsRes] = await Promise.all([
      fetch(`${apiUrl}/api/datasets/${props.datasetId}/preview?limit=${limit.value}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      }),
      fetch(`${apiUrl}/api/datasets/${props.datasetId}/operations`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
    ])
    
    if (previewRes.ok) {
      const preview = await previewRes.json()
      data.value = preview.preview_data || []
      columns.value = (preview.columns || []).map(col => ({
        field: col.name,
        label: col.name
      }))
      dataset.value = preview
    }
    
    if (opsRes.ok) {
      operations.value = await opsRes.json()
    }
    
    // Fetch profile
    const profileRes = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (profileRes.ok) {
      profileData.value = await profileRes.json()
      nullCount.value = profileData.value.columns?.reduce((sum, c) => sum + c.null_count, 0) || 0
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadComparison() {
  if (!compareOpId.value) return
  comparing.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${props.datasetId}/compare/${compareOpId.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const comparison = await res.json()
      // Show comparison in a new view or modal
      console.log('Comparison:', comparison)
    }
  } catch (e) {
    console.error(e)
  } finally {
    comparing.value = false
  }
}

function handleCellClick(row) {
  // Could open cell editor
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}
</script>

<style scoped>
.table-container {
  overflow: auto;
}
</style>
