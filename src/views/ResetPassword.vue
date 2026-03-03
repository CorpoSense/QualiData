<template>
  <div class="login-container">
    <div class="card login-box">
      <div class="card-body">
        <h1 class="h3 text-center mb-4">Set New Password</h1>
        <h2 class="h5 text-center text-muted mb-4">Enter your new password below</h2>

        <BForm v-if="!success" @submit.prevent="resetPassword">
          <BFormGroup label="New Password" label-class="fw-bold">
            <BFormInput 
              v-model="form.password" 
              type="password" 
              placeholder="New password"
              required
            ></BFormInput>
          </BFormGroup>

          <BFormGroup label="Confirm Password" label-class="fw-bold">
            <BFormInput 
              v-model="form.confirmPassword" 
              type="password" 
              placeholder="Confirm new password"
              required
            ></BFormInput>
          </BFormGroup>

          <BButton 
            variant="primary" 
            type="submit" 
            :loading="loading"
            :disabled="form.password !== form.confirmPassword"
            class="w-100"
          >
            Reset Password
          </BButton>

          <p class="text-center mt-4">
            <router-link to="/login">Back to Login</router-link>
          </p>
        </BForm>

        <!-- Success Message -->
        <div v-else class="text-center">
          <i class="bi bi-check-circle text-success" style="font-size: 3rem;"></i>
          <p class="mt-4">Your password has been reset successfully!</p>
          
          <BButton class="mt-4" variant="primary" tag="router-link" to="/login">
            Go to Login
          </BButton>
        </div>

        <!-- Error Message -->
        <BAlert 
          v-if="error" 
          variant="danger" 
          :closable="false"
          class="mt-4"
        >
          {{ error }}
        </BAlert>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BForm, BFormGroup, BFormInput, BButton, BAlert } from 'bootstrap-vue-next'

const route = useRoute()
const router = useRouter()
const apiUrl = getApiUrl()

const loading = ref(false)
const error = ref('')
const success = ref(false)
const token = ref('')

const form = ref({
  password: '',
  confirmPassword: ''
})

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    error.value = 'Invalid reset token'
  }
})

async function resetPassword() {
  if (form.value.password !== form.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const res = await fetch(`${apiUrl}/api/auth/password-reset-confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        token: token.value,
        new_password: form.value.password
      })
    })
    
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Password reset failed')
    }
    
    success.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
}
</style>
