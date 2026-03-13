import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getApiUrl } from '@/utils/api'

export const useDebugStore = defineStore('debug', () => {
  const isDebug = ref(false)
  const initialized = ref(false)

  async function init() {
    if (initialized.value) return
    
    try {
      const res = await fetch(`${getApiUrl()}/api/health`)
      if (res.ok) {
        const data = await res.json()
        isDebug.value = data.debug === true
      }
    } catch (e) {
      console.error('Failed to fetch debug mode:', e)
    }
    initialized.value = true
  }

  return { isDebug, initialized, init }
})
