<template>
  <div class="login-container">
    <div class="card login-box text-center">
      <div class="card-body">
        <i class="bi bi-arrow-repeat spinner-border spinner-border-lg"></i>
        <p class="mt-4">Connecting your account...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getApiUrl } from '@/utils/api'
import { currentUser } from '@/composables/useUser'

const route = useRoute()
const router = useRouter()
const apiUrl = getApiUrl()

onMounted(async () => {
  const code = route.query.code
  const provider = route.params.provider
  
  if (!code) {
    router.push('/login')
    return
  }
  
  try {
    const res = await fetch(`${apiUrl}/api/auth/oauth/callback/${provider}?code=${code}`)
    if (res.ok) {
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
    } else {
      throw new Error('OAuth failed')
    }
  } catch (e) {
    console.error(e)
    router.push('/login?error=oauth_failed')
  }
})
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
