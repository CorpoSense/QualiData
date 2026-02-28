<template>
  <div class="assistant-page">
    <div class="columns">
      <!-- Sidebar: Project/Dataset Selection -->
      <div class="column is-3">
        <div class="box">
          <h3 class="title is-5 mb-4">Select Data</h3>
          
          <b-field label="Project">
            <b-select v-model="selectedProject" expanded placeholder="Select project" @change="onProjectChange">
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </b-select>
          </b-field>

          <b-field v-if="selectedProject" label="Dataset">
            <b-select v-model="selectedDataset" expanded placeholder="Select dataset" @change="onDatasetChange">
              <option v-for="d in datasets" :key="d.id" :value="d.id">{{ d.name }}</option>
            </b-select>
          </b-field>
        </div>

        <!-- Column Info -->
        <div v-if="columns.length" class="box mt-4">
          <h4 class="title is-6 mb-3">Columns</h4>
          <div class="tags">
            <b-tag v-for="col in columns" :key="col.name" :type="getColumnType(col.dtype)">
              {{ col.name }}
            </b-tag>
          </div>
        </div>
      </div>

      <!-- Main: Wizard -->
      <div class="column is-9">
        <div class="box">
          <h2 class="title is-4 mb-4">AI Cleaning Assistant</h2>
          
          <!-- Step Indicator -->
          <b-steps 
            v-model="currentStep" 
            :animated="true" 
            :has-navigation="false"
          >
            <b-step-item label="Analyze" value="0">
              <div class="step-content">
                <h3 class="title is-5">Analyze Your Data</h3>
                <p class="mb-4">Let AI analyze your dataset and suggest cleaning operations.</p>
                
                <b-button 
                  type="is-primary" 
                  :loading="analyzing"
                  :disabled="!selectedDataset"
                  @click="analyzeData"
                >
                  Analyze Dataset
                </b-button>

                <!-- Analysis Results -->
                <div v-if="analysisResults" class="mt-4">
                  <b-notification type="is-info" :closable="false">
                    <strong>Analysis Complete!</strong>
                    <p>{{ analysisResults.message }}</p>
                  </b-notification>

                  <div v-if="analysisResults.data?.insights?.length" class="mt-3">
                    <div v-for="(insight, i) in analysisResults.data.insights" :key="i" class="mb-2">
                      <b-tag :type="insight.type === 'warning' ? 'is-warning' : 'is-info'">
                        {{ insight.type }}
                      </b-tag>
                      {{ insight.message }}
                    </div>
                  </div>
                </div>
              </div>
            </b-step-item>

            <b-step-item label="Operations" value="1">
              <div class="step-content">
                <h3 class="title is-5">Select Operation</h3>
                
                <b-field>
                  <b-select v-model="selectedOperation" expanded placeholder="Select operation">
                    <option value="remove_nulls">Remove Missing Values</option>
                    <option value="remove_duplicates">Remove Duplicates</option>
                    <option value="standardize">Standardize Text</option>
                    <option value="ai_clean">AI-Powered Cleaning</option>
                  </b-select>
                </b-field>

                <!-- Operation Options -->
                <div v-if="selectedOperation === 'remove_nulls'" class="mt-4">
                  <b-field label="Method">
                    <b-radio v-model="operationParams.method" native-value="drop">Drop rows with nulls</b-radio>
                    <b-radio v-model="operationParams.method" native-value="fill_mean">Fill with mean (numeric)</b-radio>
                    <b-radio v-model="operationParams.method" native-value="fill_mode">Fill with mode</b-radio>
                    <b-radio v-model="operationParams.method" native-value="constant">Fill with value</b-radio>
                  </b-field>
                </div>

                <div v-if="selectedOperation === 'standardize'" class="mt-4">
                  <b-field label="Operation">
                    <b-radio v-model="operationParams.operation" native-value="trim">Trim whitespace</b-radio>
                    <b-radio v-model="operationParams.operation" native-value="lower">Lowercase</b-radio>
                    <b-radio v-model="operationParams.operation" native-value="upper">Uppercase</b-radio>
                    <b-radio v-model="operationParams.operation" native-value="title">Title case</b-radio>
                  </b-field>
                </div>

                <b-button 
                  type="is-primary" 
                  :loading="executing"
                  :disabled="!selectedOperation"
                  class="mt-4"
                  @click="executeOperation"
                >
                  Apply Operation
                </b-button>
              </div>
            </b-step-item>

            <b-step-item label="Results" value="2">
              <div class="step-content">
                <h3 class="title is-5">Results</h3>
                
                <b-notification v-if="operationResult" :type="operationResult.status === 'success' ? 'is-success' : 'is-danger'">
                  {{ operationResult.message }}
                </b-notification>

                <div v-if="operationResult?.columns" class="mt-4">
                  <h4 class="title is-6">Updated Columns:</h4>
                  <div class="tags">
                    <b-tag v-for="col in operationResult.columns" :key="col.name" type="is-success">
                      {{ col.name }}
                    </b-tag>
                  </div>
                </div>

                <div class="buttons mt-4">
                  <b-button type="is-primary" @click="currentStep = 0">
                    Start Over
                  </b-button>
                  <b-button @click="$router.push(`/projects/${selectedProject}`)">
                    View Project
                  </b-button>
                </div>
              </div>
            </b-step-item>
          </b-steps>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

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
  if (dtype.includes('int') || dtype.includes('float')) return 'is-info'
  if (dtype === 'object') return 'is-warning'
  return 'is-light'
}
</script>

<style scoped>
.step-content {
  padding: 1rem 0;
}
</style>
