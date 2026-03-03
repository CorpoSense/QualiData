<template>
  <div class="projects-page">
    <div class="d-flex justify-content-between align-items-center mb-5">
      <h1 class="h3 mb-0">Projects</h1>
      <BButton variant="primary" @click="showCreateModal = true">
        <i class="bi bi-plus-lg me-2"></i>New Project
      </BButton>
    </div>

    <!-- Search -->
    <div class="card mb-4">
      <div class="card-body">
        <BFormGroup>
          <BFormInput 
            v-model="search" 
            placeholder="Search projects..." 
            @update:model-value="debouncedSearch"
          >
            <template #prepend>
              <span class="input-group-text"><i class="bi bi-search"></i></span>
            </template>
          </BFormInput>
        </BFormGroup>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-6">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="projects.length === 0" class="card text-center py-6">
      <div class="card-body">
        <i class="bi bi-folder2-open text-muted mb-4" style="font-size: 3rem;"></i>
        <p class="text-muted mb-4">No projects yet</p>
        <BButton variant="primary" @click="showCreateModal = true">
          Create Your First Project
        </BButton>
      </div>
    </div>

    <!-- Projects Grid -->
    <div v-else class="row">
      <div v-for="project in projects" :key="project.id" class="col-md-4 mb-4">
        <div class="card project-card" @click="$router.push(`/projects/${project.id}`)">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h3 class="h5 mb-0">{{ project.name }}</h3>
              <BDropdown>
                <template #button-content>
                  <i class="bi bi-three-dots-vertical"></i>
                </template>
                <BDropdownItem @click.stop="editProject(project)">Edit</BDropdownItem>
                <BDropdownItem @click.stop="deleteProject(project)" variant="danger">Delete</BDropdownItem>
              </BDropdown>
            </div>
            
            <p class="text-muted small mb-3">
              {{ project.description || 'No description' }}
            </p>
            
            <div class="d-flex justify-content-between small text-muted">
              <span>
                <i class="bi bi-database me-1"></i>
                {{ project.row_count || 0 }} rows
              </span>
              <span>
                {{ formatBytes(project.storage_bytes || 0) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="mt-4">
      <BPagination
        :total="total"
        v-model:model-value="currentPage"
        :per-page="pageSize"
        @update:model-value="fetchProjects"
      ></BPagination>
    </div>

    <!-- Create/Edit Modal -->
    <BModal v-model="showCreateModal" :has-modal-card="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingProject ? 'Edit Project' : 'New Project' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <BFormGroup label="Name" label-class="fw-bold">
              <BFormInput v-model="projectForm.name" placeholder="My Project" required></BFormInput>
            </BFormGroup>
            <BFormGroup label="Description" label-class="fw-bold">
              <BFormTextarea v-model="projectForm.description" placeholder="Project description..."></BFormTextarea>
            </BFormGroup>
          </div>
          <div class="modal-footer">
            <BButton variant="primary" :loading="saving" @click="saveProject">
              {{ editingProject ? 'Update' : 'Create' }}
            </BButton>
            <BButton @click="closeModal">Cancel</BButton>
          </div>
        </div>
      </div>
    </BModal>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, reactive, onMounted } from 'vue'
import { BButton, BFormGroup, BFormInput, BFormTextarea, BDropdown, BDropdownItem, BPagination, BModal } from 'bootstrap-vue-next'

const apiUrl = getApiUrl()

const loading = ref(true)
const projects = ref([])
const search = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const showCreateModal = ref(false)
const editingProject = ref(null)
const saving = ref(false)

const projectForm = reactive({
  name: '',
  description: ''
})

let searchTimeout = null

onMounted(() => {
  fetchProjects()
})

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchProjects()
  }, 300)
}

async function fetchProjects() {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize.value
    })
    if (search.value) {
      params.append('search', search.value)
    }
    
    const res = await fetch(`${apiUrl}/api/projects?${params}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      projects.value = data.projects
      total.value = data.total
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function editProject(project) {
  editingProject.value = project
  projectForm.name = project.name
  projectForm.description = project.description || ''
  showCreateModal.value = true
}

async function saveProject() {
  saving.value = true
  try {
    const url = editingProject.value 
      ? `${apiUrl}/api/projects/${editingProject.value.id}`
      : `${apiUrl}/api/projects`
    
    const method = editingProject.value ? 'PUT' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(projectForm)
    })
    
    if (res.ok) {
      closeModal()
      fetchProjects()
    }
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}

async function deleteProject(project) {
  try {
    await fetch(`${apiUrl}/api/projects/${project.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    fetchProjects()
  } catch (e) {
    console.error(e)
  }
}

function closeModal() {
  showCreateModal.value = false
  editingProject.value = null
  projectForm.name = ''
  projectForm.description = ''
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>

<style scoped>
.project-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
