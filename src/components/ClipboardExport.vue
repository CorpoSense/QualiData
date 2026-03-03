<template>
  <BButton variant="info" outline @click="copyToClipboard" :loading="copying">
    <i class="bi bi-clipboard"></i>
    <span class="ms-2">Copy to Clipboard</span>
  </BButton>
</template>

<script setup>
import { ref } from 'vue'
import { BButton } from 'bootstrap-vue-next'

const props = defineProps({
  data: { type: Array, required: true }
})

const copying = ref(false)

async function copyToClipboard() {
  if (!props.data || props.data.length === 0) return
  
  copying.value = true
  try {
    // Convert data to CSV format
    const headers = Object.keys(props.data[0])
    const csvRows = [
      headers.join(','),
      ...props.data.map(row => 
        headers.map(header => {
          const val = row[header]
          // Escape quotes and wrap in quotes if contains comma
          if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
            return `"${val.replace(/"/g, '""')}"`
          }
          return val ?? ''
        }).join(',')
      )
    ]
    
    await navigator.clipboard.writeText(csvRows.join('\n'))
  } catch (e) {
    console.error('Failed to copy:', e)
  } finally {
    copying.value = false
  }
}
</script>
