<template>
  <div class="login-container">
    <div class="box login-box">
      <h1 class="title has-text-centered">Reset Password</h1>
      <h2 class="subtitle has-text-centered">Enter your email to receive a reset link</h2>

      <!-- Request Reset Form -->
      <b-form v-if="!emailSent" @submit.prevent="requestReset">
        <b-field label="Email" :label-position="labelPosition">
          <b-input 
            v-model="form.email" 
            type="email" 
            placeholder="your@email.com"
            required
          ></b-input>
        </b-field>

        <b-button 
          type="is-primary" 
          native-type="submit" 
          :loading="loading"
          expanded
        >
          Send Reset Link
        </b-button>

        <p class="has-text-centered mt-4">
          <router-link to="/login">Back to Login</router-link>
        </p>
      </b-form>

      <!-- Success Message -->
      <div v-else class="has-text-centered">
        <b-icon icon="email-check" size="is-large" type="is-success"></b-icon>
        <p class="mt-4">If an account with that email exists, we've sent a password reset link.</p>
        <p class="is-size-7 has-text-grey mt-2">Check your email and click the reset link.</p>
        
        <b-button class="mt-4" @click="emailSent = false">Resend Email</b-button>
        
        <p class="mt-4">
          <router-link to="/login">Back to Login</router-link>
        </p>
      </div>

      <!-- Error Message -->
      <b-notification 
        v-if="error" 
        type="is-danger" 
        :closable="false"
        class="mt-4"
      >
        {{ error }}
      </b-notification>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(false)
const error = ref('')
const emailSent = ref(false)
const labelPosition = 'on-border'

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
