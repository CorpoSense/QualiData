<template>
  <div class="login-container">
    <div class="box login-box">
      <h1 class="title has-text-centered">MasterDataCleaner</h1>
      <h2 class="subtitle has-text-centered">Sign in to your account</h2>

      <!-- Tabs for Login/Register -->
      <b-tabs v-model="activeTab" type="is-toggle" expanded>
        <b-tab-item label="Sign In" value="login">
          <b-form @submit.prevent="handleLogin">
            <b-field label="Email" :label-position="labelPosition">
              <b-input 
                v-model="loginForm.email" 
                type="email" 
                placeholder="your@email.com"
                required
              ></b-input>
            </b-field>

            <b-field label="Password" :label-position="labelPosition">
              <b-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="Password"
                required
                password-reveal
              ></b-input>
            </b-field>

            <b-button 
              type="is-primary" 
              native-type="submit" 
              :loading="loading"
              expanded
            >
              Sign In
            </b-button>

            <p class="has-text-centered mt-4">
              <a @click="activeTab = 'register'">Don't have an account? Sign up</a>
            </p>
          </b-form>
        </b-tab-item>

        <b-tab-item label="Sign Up" value="register">
          <b-form @submit.prevent="handleRegister">
            <b-field label="Full Name" :label-position="labelPosition">
              <b-input 
                v-model="registerForm.fullName" 
                placeholder="John Doe"
              ></b-input>
            </b-field>

            <b-field label="Email" :label-position="labelPosition">
              <b-input 
                v-model="registerForm.email" 
                type="email" 
                placeholder="your@email.com"
                required
              ></b-input>
            </b-field>

            <b-field label="Password" :label-position="labelPosition">
              <b-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="Password"
                required
                password-reveal
              ></b-input>
            </b-field>

            <b-field label="Confirm Password" :label-position="labelPosition">
              <b-input 
                v-model="registerForm.confirmPassword" 
                type="password" 
                placeholder="Confirm password"
                required
                password-reveal
              ></b-input>
            </b-field>

            <b-button 
              type="is-primary" 
              native-type="submit" 
              :loading="loading"
              expanded
            >
              Create Account
            </b-button>

            <p class="has-text-centered mt-4">
              <a @click="activeTab = 'login'">Already have an account? Sign in</a>
            </p>
          </b-form>
        </b-tab-item>
      </b-tabs>

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
import { useRouter } from 'vue-router'

const router = useRouter()
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const activeTab = ref('login')
const loading = ref(false)
const error = ref('')
const labelPosition = 'on-border'

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: ''
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('username', loginForm.value.email)
    formData.append('password', loginForm.value.password)
    
    const res = await fetch(`${apiUrl}/api/auth/login`, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Login failed')
    }
    
    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  error.value = ''
  
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    error.value = 'Passwords do not match'
    loading.value = false
    return
  }
  
  try {
    const res = await fetch(`${apiUrl}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: registerForm.value.email,
        password: registerForm.value.password,
        full_name: registerForm.value.fullName
      })
    })
    
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Registration failed')
    }
    
    // Auto-login after registration
    activeTab.value = 'login'
    loginForm.value.email = registerForm.value.email
    loginForm.value.password = registerForm.value.password
    handleLogin()
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
