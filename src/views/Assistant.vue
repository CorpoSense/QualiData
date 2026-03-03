<template>
  <div class="assistant-page">
    <div class="row">
      <!-- Sidebar: Project/Dataset Selection -->
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h3 class="h5 mb-4">Select Data</h3>
            
            <BFormGroup label="Project">
              <BFormSelect v-model="selectedProject" :options="projectOptions" @update:model-value="onProjectChange"></BFormSelect>
            </BFormGroup>

            <BFormGroup v-if="selectedProject" label="Dataset" class="mt-3">
              <BFormSelect v-model="selectedDataset" :options="datasetOptions" @update:model-value="onDatasetChange"></BFormSelect>
            </BFormGroup>
          </div>
        </div>

        <!-- Column Info -->
        <div v-if="columns.length" class="card mt-4">
          <div class="card-body">
            <h4 class="h6 mb-3">Columns</h4>
            <div class="d-flex flex-wrap gap-2">
              <BBadge v-for="col in columns" :key="col.name" :variant="getColumnType(col.dtype)">
                {{ col.name }}
              </BBadge>
            </div>
          </div>
        </div>
      </div>

      <!-- Main: Wizard -->
      <div class="col-md-9">
        <div class="card">
          <div class="card-body">
            <h2 class="h4 mb-4">AI Cleaning Assistant</h2>
            
            <!-- Steps Navigation -->
            <ul class="nav nav-pills mb-4" role="tablist">
              <li class="nav-item">
                <button 
                  class="nav-link" 
                  :class="{ active: currentStep === 0 }"
                  @click="currentStep = 0"
                >
                  1. Analyze
                </button>
              </li>
              <li class="nav-item">
                <button 
                  class="nav-link" 
                  :class="{ active: currentStep === 1 }"
                  :disabled="!analysisResults"
                  @click="currentStep = 1"
                >
                  2. Operations
                </button>
              </li>
              <li class="nav-item">
                <button 
                  class="nav-link" 
                  :class="{ active: currentStep === 2 }"
                  :disabled="!operationResult"
                  @click="currentStep = 2"
                >
                  3. Results
                </button>
              </li>
            </ul>

            <!-- Step 1: Analyze -->
            <div v-show="currentStep === 0">
              <h3 class="h5">Analyze Your Data</h3>
              <p class="mb-4">Let AI analyze your dataset and suggest cleaning operations.</p>
              
              <BButton 
                variant="primary" 
                :loading="analyzing"
                :disabled="!selectedDataset"
                @click="analyzeData"
              >
                Analyze Dataset
              </BButton>

              <!-- Analysis Results -->
              <div v-if="analysisResults" class="mt-4">
                <BAlert variant="info" :closable="false">
                  <strong>Analysis Complete!</strong>
                  <p>{{ analysisResults.message }}</p>
                </BAlert>

                <div v-if="analysisResults.data?.insights?.length" class="mt-3">
                  <div v-for="(insight, i) in analysisResults.data.insights" :key="i" class="mb-2">
                    <BBadge :variant="insight.type === 'warning' ? 'warning' : 'info'">
                      {{ insight.type }}
                    </BBadge>
                    <span class="ms-2">{{ insight.message }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 2: Operations -->
            <div v-show="currentStep === 1">
              <h3 class="h5">Select Operation</h3>
              
              <BFormGroup class="mt-3">
                <BFormSelect v-model="selectedOperation" :options="operationOptions"></BFormSelect>
              </BFormGroup>

              <!-- Operation Options -->
              <div v-if="selectedOperation === 'remove_nulls'" class="mt-4">
                <BFormGroup label="Method">
                  <BFormRadioGroup v-model="operationParams.method">
                    <BFormRadio value="drop">Drop rows with nulls</BFormRadio>
                    <BFormRadio value="fill_mean">Fill with mean (numeric)</BFormRadio>
                    <BFormRadio value="fill_mode">Fill with mode</BFormRadio>
                    <BFormRadio value="constant">Fill with value</BFormRadio>
                  </BFormRadioGroup>
                </BFormGroup>
              </div>

              <div v-if="selectedOperation === 'standardize'" class="mt-4">
                <BFormGroup label="Operation">
                  <BFormRadioGroup v-model="operationParams.operation">
                    <BFormRadio value="trim">Trim whitespace</BFormRadio>
                    <BFormRadio value="lower">Lowercase</BFormRadio>
                    <BFormRadio value="upper">Uppercase</BFormRadio>
                    <BFormRadio value="title">Title case</BFormRadio>
                  </BFormRadioGroup>
                </BFormGroup>
              </div>

              <BButton 
                variant="primary" 
                :loading="executing"
                :disabled="!selectedOperation"
                class="mt-4"
                @click="executeOperation"
              >
                Apply Operation
              </BButton>
            </div>

            <!-- Step 3: Results -->
            <div v-show="currentStep === 2">
              <h3 class="h5">Results</h3>
              
              <BAlert v-if="operationResult" :variant="operationResult.status === 'success' ? 'success' : 'danger'">
                {{ operationResult.message }}
              </BAlert>

              <div v-if="operationResult?.columns" class="mt-4">
                <h4 class="h6">Updated Columns:</h4>
                <div class="d-flex flex-wrap gap-2 mt-2">
                  <BBadge v-for="col in operationResult.columns" :key="col.name" variant="success">
                    {{ col.name }}
                  </BBadge>
                </div>
              </div>

              <div class="d-flex gap-2 mt-4">
                <BButton variant="primary" @click="currentStep = 0">
                  Start Over
                </BButton>
                <BButton @click="$router.push(`/projects/${selectedProject}`)">
                  View Project
                </BButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { BFormGroup, BFormSelect, BFormRadioGroup, BFormRadio, BButton, BBadge, BAlert } from 'bootstrap-vue-next'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const projects = ref([])
const datasets = ref([])
const selectedProject = ref(null)
const selectedDataset = ref(null)
const columns = ref([])
const currentStep = ref(0)
const analyzing = ref(false)
const executing = ref(false)
const analysisResults = ref(null)
const operationResult = ref(null)
const selectedOperation = ref('')

const operationParams = reactive({
  method: 'drop',
  operation: 'trim'
})

const projectOptions = computed(() => [
  { value: null, text: 'Select project', disabled: true },
  ...projects.value.map(p => ({ value: p.id, text: p.name }))
])

const datasetOptions = computed(() => [
  { value: null, text: 'Select dataset', disabled: true },
  ...datasets.value.map(d => ({ value: d.id, text: d.name }))
])

const operationOptions = [
  { value: '', text: 'Select operation', disabled: true },
  { value: 'remove_nulls', text: 'Remove Missing Values' },
  { value: 'remove_duplicates', text: 'Remove Duplicates' },
  { value: 'standardize', text: 'Standardize Text' },
  { value: 'ai_clean', text: 'AI-Powered Cleaning' }
]

onMounted(async () => {
  await fetchProjects()
})

async function fetchProjects() {
  try {
    const res = await fetch(`${apiUrl}/api/projects?page=1&page_size=100`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      projects.value = data.projects
    }
  } catch (e) {
    console.error(e)
  }
}

async function onProjectChange() {
  datasets.value = []
  selectedDataset.value = null
  columns.value = []
  
  if (!selectedProject.value) return
  
  try {
    const res = await fetch(`${apiUrl}/api/datasets?project_id=${selectedProject.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      datasets.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

async function onDatasetChange() {
  columns.value = []
  if (!selectedDataset.value) return
  
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${selectedDataset.value}/preview?limit=1`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      columns.value = data.columns || []
    }
  } catch (e) {
    console.error(e)
  }
}

async function analyzeData() {
  analyzing.value = true
  try {
    const res = await fetch(`${apiUrl}/api/assistant/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ dataset_id: selectedDataset.value })
    })
    if (res.ok) {
      analysisResults.value = await res.json()
      currentStep.value = 1
    }
  } catch (e) {
    console.error(e)
  } finally {
    analyzing.value = false
  }
}

async function executeOperation() {
  executing.value = true
  try {
    let endpoint = ''
    let body = {}
    
    if (selectedOperation.value === 'remove_nulls') {
      endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/fillna`
      body = { method: operationParams.method }
    } else if (selectedOperation.value === 'remove_duplicates') {
      endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/remove-duplicates`
      body = {}
    } else if (selectedOperation.value === 'standardize') {
      endpoint = `${apiUrl}/api/datasets/${selectedDataset.value}/operations/string-operations`
      body = { column: columns.value[0]?.name, operation: operationParams.operation }
    }
    
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(body)
    })
    
    if (res.ok) {
      operationResult.value = await res.json()
      currentStep.value = 2
    }
  } catch (e) {
    console.error(e)
  } finally {
    executing.value = false
  }
}

function getColumnType(dtype) {
  if (dtype.includes('int') || dtype.includes('float')) return 'info'
  if (dtype === 'object') return 'warning'
  return 'secondary'
}
</script>
