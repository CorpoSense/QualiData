<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>User Management</h1>
      <BButton variant="primary" @click="showAddModal = true">
        <i class="bi bi-plus-lg me-2"></i>Add User
      </BButton>
    </div>

    <!-- Search -->
    <div class="mb-3">
      <input 
        type="text" 
        class="form-control" 
        placeholder="Search users..." 
        v-model="search"
        @input="debouncedSearch"
      >
    </div>

    <!-- Users Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <table v-else class="table table-hover">
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
              <td>
                <span :class="roleBadgeClass(user.role)">{{ user.role }}</span>
              </td>
              <td>
                <span :class="user.is_active ? 'badge bg-success' : 'badge bg-secondary'">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <div class="d-flex gap-2">
                  <BButton size="sm" variant="outline-primary" @click="editUser(user)">
                    <i class="bi bi-pencil"></i>
                  </BButton>
                  <BButton size="sm" variant="outline-danger" @click="confirmDelete(user)" :disabled="user.id === currentUserId">
                    <i class="bi bi-trash"></i>
                  </BButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!loading && users.length === 0" class="text-center py-4 text-muted">
          No users found
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <BModal v-model="showAddModal" :has-modal-card="true" :title="editingUser ? 'Edit User' : 'Add User'" @ok="saveUser" :ok-title="editingUser ? 'Update' : 'Create'">
      <div class="p-3">
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input type="email" class="form-control" v-model="userForm.email" :disabled="editingUser">
        </div>
        <div class="mb-3" v-if="!editingUser">
          <label class="form-label">Password</label>
          <input type="password" class="form-control" v-model="userForm.password">
        </div>
        <div class="mb-3">
          <label class="form-label">Name</label>
          <input type="text" class="form-control" v-model="userForm.name">
        </div>
        <div class="mb-3">
          <label class="form-label">Role</label>
          <select class="form-select" v-model="userForm.role">
            <option value="user">User</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Timezone</label>
          <input type="text" class="form-control" v-model="userForm.timezone" placeholder="e.g., UTC, America/New_York">
        </div>
        <div class="mb-3" v-if="editingUser">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" v-model="userForm.is_active" id="isActive">
            <label class="form-check-label" for="isActive">Active</label>
          </div>
        </div>
      </div>
    </BModal>

    <!-- Delete Confirmation -->
    <BModal v-model="showDeleteModal" title="Confirm Delete">
      <p>Are you sure you want to delete user <strong>{{ deletingUser?.email }}</strong>?</p>
      <template #footer>
        <BButton variant="secondary" @click="showDeleteModal = false">Cancel</BButton>
        <BButton variant="danger" @click="deleteUser">Delete</BButton>
      </template>
    </BModal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getApiUrl } from '@/utils/api'

const apiUrl = getApiUrl()
const token = localStorage.getItem('token')

const users = ref([])
const loading = ref(true)
const search = ref('')
const showAddModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)
const currentUserId = ref(null)

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

async function fetchUsers() {
  loading.value = true
  try {
    const url = search.value 
      ? `${apiUrl}/api/users?search=${encodeURIComponent(search.value)}`
      : `${apiUrl}/api/users`
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
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
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      currentUserId.value = data.id
    }
  } catch (e) {
    console.error(e)
  }
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
        Authorization: `Bearer ${token}`,
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
      headers: { Authorization: `Bearer ${token}` }
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

function roleBadgeClass(role) {
  return {
    'badge': true,
    'bg-primary': role === 'admin',
    'bg-info': role === 'manager',
    'bg-secondary': role === 'user'
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

// Close modal handler
function handleModalClose() {
  if (showAddModal.value === false) {
    resetForm()
  }
}

onMounted(() => {
  fetchUsers()
  fetchCurrentUser()
})
</script>
