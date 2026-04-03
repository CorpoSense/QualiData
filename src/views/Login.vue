<template>
  <div class="login-container">
    <div class="card login-box">
      <div class="card-body">
        <h1 class="h3 text-center mb-4">MasterDataCleaner</h1>
        <h2 class="h5 text-center text-muted mb-4">Sign in to your account</h2>

        <!-- Tabs -->
        <ul class="nav nav-pills mb-3" role="tablist">
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ active: activeTab === 'login' }"
              @click="activeTab = 'login'"
            >
              Sign In
            </button>
          </li>
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ active: activeTab === 'register' }"
              @click="activeTab = 'register'"
            >
              Sign Up
            </button>
          </li>
        </ul>

        <!-- Login Form -->
        <form v-show="activeTab === 'login'" @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label fw-bold">Email</label>
            <input 
              v-model="loginForm.email" 
              type="email" 
              class="form-control"
              placeholder="your@email.com"
              required
              autofocus
            >
          </div>

          <div class="mb-3">
            <label class="form-label fw-bold">Password</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              class="form-control"
              placeholder="Password"
              required
            >
          </div>

          <button 
            type="submit" 
            class="btn btn-primary w-100"
            :disabled="loading"
          >
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>

          <p class="text-center mt-4">
            <router-link to="/forgot-password">Forgot your password?</router-link>
          </p>

          <p class="text-center mt-2">
            <a @click="activeTab = 'register'" class="cursor-pointer">Don't have an account? Sign up</a>
          </p>
        </form>

        <!-- OAuth Options -->
        <!-- div v-show="activeTab === 'login'" class="mt-4">
          <p class="text-center text-muted small mb-2">Or continue with</p>
          <div class="d-flex justify-content-center gap-2">
            <button 
              class="btn btn-outline-secondary" 
              @click="oauthLogin('google')"
              :disabled="!oauthEnabled"
            >
              <i class="bi bi-google"></i>
              <span class="ms-2">Google</span>
            </button>
            <button 
              class="btn btn-outline-dark" 
              @click="oauthLogin('github')"
              :disabled="!oauthEnabled"
            >
              <i class="bi bi-github"></i>
              <span class="ms-2">GitHub</span>
            </button>
          </div>
        </div -->

        <!-- Register Form -->
        <form v-show="activeTab === 'register'" @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label fw-bold">Full Name</label>
            <input 
              v-model="registerForm.fullName" 
              type="text" 
              class="form-control"
              placeholder="John Doe"
            >
          </div>

          <div class="mb-3">
            <label class="form-label fw-bold">Email</label>
            <input 
              v-model="registerForm.email" 
              type="email" 
              class="form-control"
              placeholder="your@email.com"
              required
            >
          </div>

          <div class="mb-3">
            <label class="form-label fw-bold">Password</label>
            <input 
              v-model="registerForm.password" 
              type="password" 
              class="form-control"
              placeholder="Password"
              required
            >
          </div>

          <div class="mb-3">
            <label class="form-label fw-bold">Confirm Password</label>
            <input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              class="form-control"
              placeholder="Confirm password"
              required
            >
          </div>

          <button 
            type="submit" 
            class="btn btn-primary w-100"
            :disabled="loading"
          >
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>

          <p class="text-center mt-4">
            <a @click="activeTab = 'login'" class="cursor-pointer">Already have an account? Sign in</a>
          </p>
        </form>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger mt-4">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { getApiUrl } from '@/utils/api'
import { currentUser } from '@/composables/useUser'

const router = useRouter()
const apiUrl = getApiUrl()

const oauthEnabled = ref(true)
const activeTab = ref('login')
const loading = ref(false)
const error = ref('')

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
      body: formData
      // Note: Don't set Content-Type for FormData - browser does it automatically
    })
    
    if (!res.ok) {
      const contentType = res.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const data = await res.json()
        throw new Error(data.detail || 'Login failed')
      } else {
        const text = await res.text()
        throw new Error(text || `Server error: ${res.status}`)
      }
    }
    
    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    
    // Fetch user data and update currentUser
    const userRes = await fetch(`${apiUrl}/api/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` }
    })
    if (userRes.ok) {
      currentUser.value = await userRes.json()
    }
    
    router.push('/dashboard')
  } catch (e) {
    const errorMsg = e?.message || (typeof e === 'string' ? e : JSON.stringify(e) || 'An error occurred. Please try again.')
    error.value = errorMsg
    console.error('Login error:', e)
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
    const formData = new FormData()
    formData.append('email', registerForm.value.email)
    formData.append('password', registerForm.value.password)
    formData.append('full_name', registerForm.value.fullName)
    
    const res = await fetch(`${apiUrl}/api/auth/register`, {
      method: 'POST',
      body: formData
    })
    
    if (!res.ok) {
      const contentType = res.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const data = await res.json()
        throw new Error(data.detail || 'Registration failed')
      } else {
        const text = await res.text()
        throw new Error(text || `Server error: ${res.status}`)
      }
    }
    
    // Auto-login after registration
    activeTab.value = 'login'
    loginForm.value.email = registerForm.value.email
    loginForm.value.password = registerForm.value.password
    handleLogin()
  } catch (e) {
    const errorMsg = e?.message || (typeof e === 'string' ? e : JSON.stringify(e) || 'An error occurred. Please try again.')
    error.value = errorMsg
    console.error('Registration error:', e)
  } finally {
    loading.value = false
  }
}

function oauthLogin(provider) {
  window.location.href = `${apiUrl}/api/auth/oauth/${provider}`
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

.cursor-pointer {
  cursor: pointer;
}
</style>
