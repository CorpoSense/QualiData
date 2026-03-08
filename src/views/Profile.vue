<template>
  <div class="container py-4">
    <div class="row">
      <div class="col-md-8 mx-auto">
        <h1 class="mb-4">Profile Settings</h1>
        
        <!-- Profile Info -->
        <b-card header="Personal Information" class="mb-4">
          <b-form-group label="Email" class="mb-3">
            <b-form-input type="email" v-model="profile.email" disabled></b-form-input>
            <small class="text-muted">Email cannot be changed</small>
          </b-form-group>
          
          <b-form-group label="Name" class="mb-3">
            <b-form-input type="text" v-model="profile.name" placeholder="Your name"></b-form-input>
          </b-form-group>
          
          <b-form-group label="Timezone" class="mb-3">
            <b-form-input type="text" v-model="profile.timezone" placeholder="e.g., UTC, America/New_York, Europe/London"></b-form-input>
            <small class="text-muted">Used for datetime display</small>
          </b-form-group>
          
          <b-form-group label="Role" class="mb-3">
            <b-form-input type="text" :modelValue="profile.role" disabled></b-form-input>
          </b-form-group>
          
          <b-button variant="primary" @click="saveProfile" :loading="saving">
            Save Changes
          </b-button>
        </b-card>

        <!-- Change Password -->
        <b-card header="Change Password" class="mb-4">
          <b-form-group label="Current Password" class="mb-3">
            <b-form-input type="password" v-model="passwordForm.current"></b-form-input>
          </b-form-group>
          
          <b-form-group label="New Password" class="mb-3">
            <b-form-input type="password" v-model="passwordForm.new"></b-form-input>
          </b-form-group>
          
          <b-form-group label="Confirm New Password" class="mb-3">
            <b-form-input type="password" v-model="passwordForm.confirm"></b-form-input>
          </b-form-group>
          
          <b-alert v-if="passwordForm.new !== passwordForm.confirm && passwordForm.confirm" variant="warning">
            Passwords do not match
          </b-alert>
          
          <b-button variant="warning" @click="changePassword" :loading="changingPassword" :disabled="!canChangePassword">
            Change Password
          </b-button>
        </b-card>

        <!-- Account Info -->
        <b-card header="Account Information">
          <b-row>
            <b-col sm="6">
              <small class="text-muted">Member Since</small>
              <div>{{ formatDate(profile.created_at) }}</div>
            </b-col>
            <b-col sm="6">
              <small class="text-muted">Last Login</small>
              <div>{{ formatDate(profile.last_login) }}</div>
            </b-col>
          </b-row>
        </b-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getApiUrl } from '@/utils/api'

const apiUrl = getApiUrl()

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

function getToken() {
  return localStorage.getItem('token')
}

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
        Authorization: `Bearer ${getToken()}`,
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
        Authorization: `Bearer ${getToken()}`,
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
