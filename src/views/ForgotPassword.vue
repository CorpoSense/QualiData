<template>
  <div class="login-container">
    <div class="card login-box">
      <div class="card-body">
        <h1 class="h3 text-center mb-4">Reset Password</h1>
        <h2 class="h5 text-center text-muted mb-4">Enter your email to receive a reset link</h2>

        <!-- Request Reset Form -->
        <BForm v-if="!emailSent" @submit.prevent="requestReset">
          <BFormGroup label="Email" label-class="fw-bold">
            <BFormInput 
              v-model="form.email" 
              type="email" 
              placeholder="your@email.com"
              required
            ></BFormInput>
          </BFormGroup>

          <BButton 
            variant="primary" 
            type="submit" 
            :loading="loading"
            class="w-100"
          >
            Send Reset Link
          </BButton>

          <p class="text-center mt-4">
            <router-link to="/login">Back to Login</router-link>
          </p>
        </BForm>

        <!-- Success Message -->
        <div v-else class="text-center">
          <i class="bi bi-check-circle text-success" style="font-size: 3rem;"></i>
          <p class="mt-4">If an account with that email exists, we've sent a password reset link.</p>
          <p class="text-muted small mt-2">Check your email and click the reset link.</p>
          
          <BButton class="mt-4" @click="emailSent = false">Resend Email</BButton>
          
          <p class="mt-4">
            <router-link to="/login">Back to Login</router-link>
          </p>
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
import { ref } from 'vue'
import { BForm, BFormGroup, BFormInput, BButton, BAlert } from 'bootstrap-vue-next'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(false)
const error = ref('')
const emailSent = ref(false)

const form = ref({
  email: ''
})

async function requestReset() {
  loading.value = true
  error.value = ''
  
  try {
    const res = await fetch(`${apiUrl}/api/auth/password-reset-request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: form.value.email })
    })
    
    if (res.ok) {
      emailSent.value = true
    } else {
      const data = await res.json()
      throw new Error(data.detail || 'Request failed')
    }
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
