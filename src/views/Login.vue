<template>
  <div class="login-container">
    <div class="card login-box">
      <div class="card-body">
        <h1 class="h3 text-center mb-4">MasterDataCleaner</h1>
        <h2 class="h5 text-center text-muted mb-4">Sign in to your account</h2>

        <!-- Tabs for Login/Register -->
        <BTabs v-model="activeTab" nav-wrapper-class="mb-3">
          <BTab title="Sign In" value="login">
            <BForm @submit.prevent="handleLogin">
              <BFormGroup label="Email" label-class="fw-bold">
                <BFormInput 
                  v-model="loginForm.email" 
                  type="email" 
                  placeholder="your@email.com"
                  required
                ></BFormInput>
              </BFormGroup>

              <BFormGroup label="Password" label-class="fw-bold">
                <BFormInput 
                  v-model="loginForm.password" 
                  type="password" 
                  placeholder="Password"
                  required
                ></BFormInput>
              </BFormGroup>

              <BButton 
                variant="primary" 
                type="submit" 
                :loading="loading"
                class="w-100"
              >
                Sign In
              </BButton>

              <p class="text-center mt-4">
                <router-link to="/forgot-password">Forgot your password?</router-link>
              </p>

              <p class="text">
                <a @click="activeTab = 'register'" class="cursor-pointer">Don't have an account? Sign up</a>
              </p>
            </BForm>

            <!-- OAuth Options -->
            <div class="mt-4">
              <p class="text-center text-muted small mb-2">Or continue with</p>
              <div class="d-flex justify-content-center gap-2">
                <BButton 
                  variant="outline-secondary" 
                  @click="oauthLogin('google')"
                  :disabled="!oauthEnabled"
                >
                  <i class="bi bi-google"></i>
                  <span class="ms-2">Google</span>
                </BButton>
                <BButton 
                  variant="outline-dark" 
                  @click="oauthLogin('github')"
                  :disabled="!oauthEnabled"
                >
                  <i class="bi bi-github"></i>
                  <span class="ms-2">GitHub</span>
                </BButton>
              </div>
            </div>
          </BTab>

          <BTab title="Sign Up" value="register">
            <BForm @submit.prevent="handleRegister">
              <BFormGroup label="Full Name" label-class="fw-bold">
                <BFormInput 
                  v-model="registerForm.fullName" 
                  placeholder="John Doe"
                ></BFormInput>
              </BFormGroup>

              <BFormGroup label="Email" label-class="fw-bold">
                <BFormInput 
                  v-model="registerForm.email" 
                  type="email" 
                  placeholder="your@email.com"
                  required
                ></BFormInput>
              </BFormGroup>

              <BFormGroup label="Password" label-class="fw-bold">
                <BFormInput 
                  v-model="registerForm.password" 
                  type="password" 
                  placeholder="Password"
                  required
                ></BFormInput>
              </BFormGroup>

              <BFormGroup label="Confirm Password" label-class="fw-bold">
                <BFormInput 
                  v-model="registerForm.confirmPassword" 
                  type="password" 
                  placeholder="Confirm password"
                  required
                ></BFormInput>
              </BFormGroup>

              <BButton 
                variant="primary" 
                type="submit" 
                :loading="loading"
                class="w-100"
              >
                Create Account
              </BButton>

              <p class="text-center mt-4">
                <a @click="activeTab = 'login'" class="cursor-pointer">Already have an account? Sign in</a>
              </p>
            </BForm>
          </BTab>
        </BTabs>

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
import { useRouter } from 'vue-router'
import { BForm, BFormGroup, BFormInput, BButton, BTab, BTabs, BAlert } from 'bootstrap-vue-next'
import { getApiUrl } from '@/utils/api'

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
      body: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
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
    router.push('/dashboard')
  } catch (e) {
    error.value = e.message || 'An error occurred. Please try again.'
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
    error.value = e.message || 'An error occurred. Please try again.'
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
