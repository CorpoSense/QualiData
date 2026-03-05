import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  function show(message, variant = 'info', duration = 3000) {
    const id = Date.now()
    toasts.value.push({ id, message, variant })
    
    setTimeout(() => {
      remove(id)
    }, duration)
  }
  
  function remove(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      toasts.value.splice(idx, 1)
    }
  }
  
  function success(message) {
    show(message, 'success')
  }
  
  function error(message) {
    show(message, 'danger', 5000)
  }
  
  function warning(message) {
    show(message, 'warning', 4000)
  }
  
  function info(message) {
    show(message, 'info')
  }
  
  return {
    toasts,
    show,
    success,
    error,
    warning,
    info,
    remove
  }
}
