<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>User Management</h1>
      <b-button variant="primary" @click="showAddModal = true">
        <i class="bi bi-plus-lg me-2"></i>Add User
      </b-button>
    </div>

    <!-- Search -->
    <div class="mb-3">
      <b-form-input 
        type="text" 
        placeholder="Search users..." 
        v-model="search"
        @update:modelValue="debouncedSearch"
      ></b-form-input>
    </div>

    <!-- Users Table -->
    <b-card>
      <div v-if="loading" class="text-center py-4">
        <b-spinner label="Loading..."></b-spinner>
      </div>
      <table v-if="!loading" class="table table-striped table-hover">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.name || '-' }}</td>
            <td>{{ user.email }}</td>
            <td><b-badge :variant="getRoleVariant(user.role)">{{ user.role }}</b-badge></td>
            <td><b-badge :variant="user.is_active ? 'success' : 'secondary'">{{ user.is_active ? 'Active' : 'Inactive' }}</b-badge></td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <div class="d-flex gap-2">
                <b-button size="sm" variant="outline-primary" @click="editUser(user)">
                  <i class="bi bi-pencil"></i>
                </b-button>
                <b-button size="sm" variant="outline-danger" @click="confirmDelete(user)" :disabled="user.id === currentUserId">
                  <i class="bi bi-trash"></i>
                </b-button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && users.length === 0" class="text-center py-4 text-muted">
        No users found
      </div>
    </b-card>

    <!-- Add/Edit Modal -->
    <b-modal v-model="showAddModal" :has-modal-card="true" :title="editingUser ? 'Edit User' : 'Add User'" @ok.prevent="saveUser" :ok-title="editingUser ? 'Update' : 'Create'" no-header-close>
      <b-form-group label="Email" class="mb-3">
        <b-form-input type="email" v-model="userForm.email" :disabled="editingUser" placeholder="user@example.com"></b-form-input>
      </b-form-group>
      
      <b-form-group v-if="!editingUser" label="Password" class="mb-3">
        <b-form-input type="password" v-model="userForm.password" placeholder="Password"></b-form-input>
      </b-form-group>
      
      <b-form-group label="Name" class="mb-3">
        <b-form-input type="text" v-model="userForm.name" placeholder="Full Name"></b-form-input>
      </b-form-group>
      
      <b-form-group label="Role" class="mb-3">
        <b-form-select v-model="userForm.role" :options="roleOptions"></b-form-select>
      </b-form-group>
      
      <b-form-group label="Timezone" class="mb-3">
        <b-form-input type="text" v-model="userForm.timezone" placeholder="e.g., UTC, America/New_York"></b-form-input>
      </b-form-group>
      
      <b-form-group v-if="editingUser">
        <b-form-checkbox v-model="userForm.is_active">Active</b-form-checkbox>
      </b-form-group>
    </b-modal>

    <!-- Delete Confirmation -->
    <b-modal v-model="showDeleteModal" title="Confirm Delete" ok-title="Delete" ok-variant="danger" @ok.prevent="deleteUser">
      <p>Are you sure you want to delete user <strong>{{ deletingUser?.email }}</strong>?</p>
    </b-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getApiUrl } from '@/utils/api'

const apiUrl = getApiUrl()

const users = ref([])
const loading = ref(true)
const search = ref('')
const showAddModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)
const currentUserId = ref(null)

const fields = [
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'role', label: 'Role' },
  { key: 'is_active', label: 'Status' },
  { key: 'created_at', label: 'Created' },
  { key: 'actions', label: 'Actions' }
]

const roleOptions = [
  { value: 'user', text: 'User' },
  { value: 'manager', text: 'Manager' },
  { value: 'admin', text: 'Admin' }
]

const userForm = reactive({
  email: '',
  password: '',
  name: '',
  role: 'user',
  timezone: '',
  is_active: true
})

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchUsers()
  }, 300)
}

function getToken() {
  return localStorage.getItem('token')
}

async function fetchUsers() {
  loading.value = true
  try {
    const url = search.value 
      ? `${apiUrl}/api/users?search=${encodeURIComponent(search.value)}`
      : `${apiUrl}/api/users`
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    if (res.ok) {
      const data = await res.json()
      users.value = data.users
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchCurrentUser() {
  try {
    const res = await fetch(`${apiUrl}/api/users/me`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    if (res.ok) {
      const data = await res.json()
      currentUserId.value = data.id
    }
  } catch (e) {
    console.error(e)
  }
}

function openAddModal() {
  editingUser.value = null
  userForm.email = ''
  userForm.password = ''
  userForm.name = ''
  userForm.role = 'user'
  userForm.timezone = ''
  userForm.is_active = true
  showAddModal.value = true
}

function editUser(user) {
  editingUser.value = user
  userForm.email = user.email
  userForm.name = user.name || ''
  userForm.role = user.role
  userForm.timezone = user.timezone || ''
  userForm.is_active = user.is_active
  showAddModal.value = true
}

async function saveUser() {
  const method = editingUser.value ? 'PATCH' : 'POST'
  const url = editingUser.value 
    ? `${apiUrl}/api/users/${editingUser.value.id}`
    : `${apiUrl}/api/users`
  
  const body = editingUser.value
    ? { name: userForm.name, role: userForm.role, timezone: userForm.timezone, is_active: userForm.is_active }
    : { email: userForm.email, password: userForm.password, name: userForm.name, role: userForm.role, timezone: userForm.timezone }
  
  try {
    const res = await fetch(url, {
      method,
      headers: { 
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
    
    if (res.ok) {
      showAddModal.value = false
      resetForm()
      fetchUsers()
    } else {
      const err = await res.json()
      alert(err.detail || 'Error saving user')
    }
  } catch (e) {
    console.error(e)
    alert('Error saving user')
  }
}

function confirmDelete(user) {
  deletingUser.value = user
  showDeleteModal.value = true
}

async function deleteUser() {
  try {
    const res = await fetch(`${apiUrl}/api/users/${deletingUser.value.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    
    if (res.ok) {
      showDeleteModal.value = false
      deletingUser.value = null
      fetchUsers()
    } else {
      alert('Error deleting user')
    }
  } catch (e) {
    console.error(e)
    alert('Error deleting user')
  }
}

function resetForm() {
  editingUser.value = null
  userForm.email = ''
  userForm.password = ''
  userForm.name = ''
  userForm.role = 'user'
  userForm.timezone = ''
  userForm.is_active = true
}

function getRoleVariant(role) {
  const variants = {
    'admin': 'primary',
    'manager': 'info',
    'user': 'secondary'
  }
  return variants[role?.toLowerCase()] || 'secondary'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchUsers()
  fetchCurrentUser()
})
</script>
