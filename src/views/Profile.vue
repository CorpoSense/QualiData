<template>
  <div class="container py-4">
    <Breadcrumb :items="breadcrumbItems" />
    <div class="row">
      <div class="col-md-8 mx-auto">
        <h1 class="mb-4">Profile Settings</h1>
        
        <!-- Profile Info -->
        <BCard header="Personal Information" class="mb-4">
          <BFormGroup label="Email" class="mb-3">
            <BFormInput type="email" v-model="profile.email" disabled></BFormInput>
            <small class="text-muted">Email cannot be changed</small>
          </BFormGroup>
          
          <BFormGroup label="Name" class="mb-3">
            <BFormInput type="text" v-model="profile.name" placeholder="Your name"></BFormInput>
          </BFormGroup>
          
          <BFormGroup label="Timezone" class="mb-3">
            <BFormInput type="text" v-model="profile.timezone" placeholder="e.g., UTC, America/New_York, Europe/London"></BFormInput>
            <small class="text-muted">Used for datetime display</small>
          </BFormGroup>
          
          <BFormGroup label="Role" class="mb-3">
            <BFormInput type="text" :modelValue="profile.role" disabled></BFormInput>
          </BFormGroup>
          
          <BButton variant="primary" @click="saveProfile" :loading="saving">
            Save Changes
          </BButton>
        </BCard>

        <!-- Change Password -->
        <BCard header="Change Password" class="mb-4">
          <BFormGroup label="Current Password" class="mb-3">
            <BFormInput type="password" v-model="passwordForm.current"></BFormInput>
          </BFormGroup>
          
          <BFormGroup label="New Password" class="mb-3">
            <BFormInput type="password" v-model="passwordForm.new"></BFormInput>
          </BFormGroup>
          
          <BFormGroup label="Confirm New Password" class="mb-3">
            <BFormInput type="password" v-model="passwordForm.confirm"></BFormInput>
          </BFormGroup>
          
          <BAlert v-if="passwordForm.new !== passwordForm.confirm && passwordForm.confirm" variant="warning">
            Passwords do not match
          </BAlert>
          
          <BButton variant="warning" @click="changePassword" :loading="changingPassword" :disabled="!canChangePassword">
            Change Password
          </BButton>
        </BCard>

        <!-- Account Info -->
        <BCard header="Account Information">
          <BRow>
            <BCol sm="6">
              <small class="text-muted">Member Since</small>
              <div>{{ formatDate(profile.created_at) }}</div>
            </BCol>
            <BCol sm="6">
              <small class="text-muted">Last Login</small>
              <div>{{ formatDate(profile.last_login) }}</div>
            </BCol>
          </BRow>
        </BCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getApiUrl } from '@/utils/api'
import { useToast } from '@/composables/useToast'
import Breadcrumb from '@/components/Breadcrumb.vue'

const apiUrl = getApiUrl()
const toast = useToast()

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
      toast.success('Profile saved!')
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Error saving profile')
    }
  } catch (e) {
    console.error(e)
    toast.error('Error saving profile')
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
      toast.success('Password changed successfully!')
      passwordForm.current = ''
      passwordForm.new = ''
      passwordForm.confirm = ''
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Error changing password')
    }
  } catch (e) {
    console.error(e)
    toast.error('Error changing password')
  } finally {
    changingPassword.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return 'Never'
  return new Date(dateStr).toLocaleString()
}

const breadcrumbItems = [
  { label: 'Dashboard', path: '/dashboard', icon: 'bi bi-house' },
  { label: 'Profile', icon: 'bi bi-person' }
]

onMounted(() => {
  fetchProfile()
})
</script>
