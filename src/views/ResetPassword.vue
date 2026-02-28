<template>
  <div class="login-container">
    <div class="box login-box">
      <h1 class="title has-text-centered">Set New Password</h1>
      <h2 class="subtitle has-text-centered">Enter your new password below</h2>

      <b-form v-if="!success" @submit.prevent="resetPassword">
        <b-field label="New Password" :label-position="labelPosition">
          <b-input 
            v-model="form.password" 
            type="password" 
            placeholder="New password"
            required
            password-reveal
          ></b-input>
        </b-field>

        <b-field label="Confirm Password" :label-position="labelPosition">
          <b-input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="Confirm new password"
            required
            password-reveal
          ></b-input>
        </b-field>

        <b-button 
          type="is-primary" 
          native-type="submit" 
          :loading="loading"
          :disabled="form.password !== form.confirmPassword"
          expanded
        >
          Reset Password
        </b-button>

        <p class="has-text-centered mt-4">
          <router-link to="/login">Back to Login</router-link>
        </p>
      </b-form>

      <!-- Success Message -->
      <div v-else class="has-text-centered">
        <b-icon icon="check-circle" size="is-large" type="is-success"></b-icon>
        <p class="mt-4">Your password has been reset successfully!</p>
        
        <b-button class="mt-4" type="is-primary" tag="router-link" to="/login">
          Go to Login
        </b-button>
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(false)
const error = ref('')
const success = ref(false)
const labelPosition = 'on-border'
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
