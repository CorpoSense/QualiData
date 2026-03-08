<template>
  <div class="container py-4">
    <div class="row">
      <div class="col-md-8 mx-auto">
        <h1 class="mb-4">Profile Settings</h1>
        
        <!-- Profile Info -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Personal Information</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" v-model="profile.email" disabled>
              <small class="text-muted">Email cannot be changed</small>
            </div>
            <div class="mb-3">
              <label class="form-label">Name</label>
              <input type="text" class="form-control" v-model="profile.name" placeholder="Your name">
            </div>
            <div class="mb-3">
              <label class="form-label">Timezone</label>
              <input type="text" class="form-control" v-model="profile.timezone" placeholder="e.g., UTC, America/New_York, Europe/London">
              <small class="text-muted">Used for datetime display</small>
            </div>
            <div class="mb-3">
              <label class="form-label">Role</label>
              <input type="text" class="form-control" :value="profile.role" disabled>
            </div>
            <BButton variant="primary" @click="saveProfile" :loading="saving">
              Save Changes
            </BButton>
          </div>
        </div>

        <!-- Change Password -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Change Password</h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Current Password</label>
              <input type="password" class="form-control" v-model="passwordForm.current">
            </div>
            <div class="mb-3">
              <label class="form-label">New Password</label>
              <input type="password" class="form-control" v-model="passwordForm.new">
            </div>
            <div class="mb-3">
              <label class="form-label">Confirm New Password</label>
              <input type="password" class="form-control" v-model="passwordForm.confirm">
            </div>
            <div v-if="passwordForm.new !== passwordForm.confirm && passwordForm.confirm" class="alert alert-warning">
              Passwords do not match
            </div>
            <BButton variant="warning" @click="changePassword" :loading="changingPassword" :disabled="!canChangePassword">
              Change Password
            </BButton>
          </div>
        </div>

        <!-- Account Info -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Account Information</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-sm-6 mb-3">
                <label class="form-label text-muted">Member Since</label>
                <div>{{ formatDate(profile.created_at) }}</div>
              </div>
              <div class="col-sm-6 mb-3">
                <label class="form-label text-muted">Last Login</label>
                <div>{{ formatDate(profile.last_login) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getApiUrl } from '@/utils/api'

const apiUrl = getApiUrl()
const getToken = () => localStorage.getItem('token')

const profile = reactive({
  email: '',
  name: '',
  timezone: '',
  role: '',
  created_at: null,
  last_login: null
})

const passwordForm = reactive({
  current: '',
  new: '',
  confirm: ''
})

const saving = ref(false)
const changingPassword = ref(false)

const canChangePassword = computed(() => {
  return passwordForm.current && 
         passwordForm.new && 
         passwordForm.new === passwordForm.confirm &&
         passwordForm.new.length >= 6
})

async function fetchProfile() {
  try {
    const res = await fetch(`${apiUrl}/api/users/me`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    if (res.ok) {
      const data = await res.json()
      profile.email = data.email
      profile.name = data.name || ''
      profile.timezone = data.timezone || ''
      profile.role = data.role
      profile.created_at = data.created_at
      profile.last_login = data.last_login
    }
  } catch (e) {
    console.error(e)
  }
}

async function saveProfile() {
  saving.value = true
  try {
    const res = await fetch(`${apiUrl}/api/users/me`, {
      method: 'PATCH',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: profile.name,
        timezone: profile.timezone
      })
    })
    
    if (res.ok) {
      alert('Profile saved!')
    } else {
      const err = await res.json()
      alert(err.detail || 'Error saving profile')
    }
  } catch (e) {
    console.error(e)
    alert('Error saving profile')
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  if (!canChangePassword.value) return
  
  changingPassword.value = true
  try {
    const res = await fetch(`${apiUrl}/api/users/me/change-password`, {
      method: 'POST',
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        current_password: passwordForm.current,
        new_password: passwordForm.new
      })
    })
    
    if (res.ok) {
      alert('Password changed successfully!')
      passwordForm.current = ''
      passwordForm.new = ''
      passwordForm.confirm = ''
    } else {
      const err = await res.json()
      alert(err.detail || 'Error changing password')
    }
  } catch (e) {
    console.error(e)
    alert('Error changing password')
  } finally {
    changingPassword.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return 'Never'
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  fetchProfile()
})
</script>
