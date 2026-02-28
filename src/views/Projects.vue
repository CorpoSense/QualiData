<template>
  <div class="projects-page">
    <div class="is-flex is-justify-content-space-between is-align-items-center mb-5">
      <h1 class="title mb-0">Projects</h1>
      <b-button type="is-primary" icon-left="plus" @click="showCreateModal = true">
        New Project
      </b-button>
    </div>

    <!-- Search -->
    <div class="box mb-4">
      <b-field>
        <b-input 
          v-model="search" 
          placeholder="Search projects..." 
          icon="magnify"
          @input="debouncedSearch"
        ></b-input>
      </b-field>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="has-text-centered py-6">
      <b-icon icon="loading" size="is-large" spin></b-icon>
    </div>

    <!-- Empty State -->
    <div v-else-if="projects.length === 0" class="box has-text-centered py-6">
      <b-icon icon="folder-open-outline" size="is-large" class="has-text-grey-light mb-4"></b-icon>
      <p class="has-text-grey mb-4">No projects yet</p>
      <b-button type="is-primary" @click="showCreateModal = true">
        Create Your First Project
      </b-button>
    </div>

    <!-- Projects Grid -->
    <div v-else class="columns is-multiline">
      <div v-for="project in projects" :key="project.id" class="column is-4">
        <div class="box project-card" @click="$router.push(`/projects/${project.id}`)">
          <div class="is-flex is-justify-content-space-between is-align-items-start mb-3">
            <h3 class="title is-5 mb-0">{{ project.name }}</h3>
            <b-dropdown position="is-bottom-right" @click.stop>
              <b-button icon-left="dots-vertical" size="is-small" slot="trigger"></b-button>
              <b-dropdown-item @click="editProject(project)">Edit</b-dropdown-item>
              <b-dropdown-item @click="deleteProject(project)" class="has-text-danger">Delete</b-dropdown-item>
            </b-dropdown>
          </div>
          
          <p class="has-text-grey is-size-7 mb-3">
            {{ project.description || 'No description' }}
          </p>
          
          <div class="is-flex is-justify-content-space-between is-size-7 has-text-grey">
            <span>
              <b-icon icon="database" size="is-small"></b-icon>
              {{ project.row_count || 0 }} rows
            </span>
            <span>
              {{ formatBytes(project.storage_bytes || 0) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="mt-4">
      <b-pagination
        :total="total"
        :current.sync="currentPage"
        :per-page="pageSize"
        @change="fetchProjects"
      ></b-pagination>
    </div>

    <!-- Create/Edit Modal -->
    <b-modal v-model="showCreateModal" :has-modal-card="true">
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">{{ editingProject ? 'Edit Project' : 'New Project' }}</p>
          <button class="delete" @click="closeModal"></button>
        </header>
        <section class="modal-card-body">
          <b-field label="Name" :label-position="labelPosition">
            <b-input v-model="projectForm.name" placeholder="My Project" required></b-input>
          </b-field>
          <b-field label="Description" :label-position="labelPosition">
            <b-input v-model="projectForm.description" type="textarea" placeholder="Project description..."></b-input>
          </b-field>
        </section>
        <footer class="modal-card-foot">
          <b-button type="is-primary" :loading="saving" @click="saveProject">
            {{ editingProject ? 'Update' : 'Create' }}
          </b-button>
          <b-button @click="closeModal">Cancel</b-button>
        </footer>
      </div>
    </b-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(true)
const projects = ref([])
const search = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const showCreateModal = ref(false)
const editingProject = ref(null)
const saving = ref(false)
const labelPosition = 'on-border'

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
