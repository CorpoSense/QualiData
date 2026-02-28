<template>
  <b-button type="is-info" outlined @click="copyToClipboard" :loading="copying">
    <b-icon icon="content-copy"></b-icon>
    <span>Copy to Clipboard</span>
  </b-button>
</template>

<script setup>
import { ref } from 'vue'

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
