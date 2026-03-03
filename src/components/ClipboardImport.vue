<template>
  <div class="card">
    <div class="card-body">
      <h3 class="h5 mb-4">Clipboard Import</h3>
      
      <BFormGroup label="Paste CSV Data">
        <BFormTextarea 
          v-model="clipboardData" 
          placeholder="Paste your CSV data here..."
          :rows="10"
        ></BFormTextarea>
      </BFormGroup>

      <div class="d-flex gap-2">
        <BButton variant="primary" :loading="importing" @click="importFromClipboard">
          Import Data
        </BButton>
        <BButton @click="pasteFromClipboard">
          <i class="bi bi-clipboard"></i>
          <span class="ms-2">Paste</span>
        </BButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BButton, BFormGroup, BFormTextarea } from 'bootstrap-vue-next'

const emit = defineEmits(['import'])

const clipboardData = ref('')
const importing = ref(false)

async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText()
    clipboardData.value = text
  } catch (e) {
    console.error('Failed to read clipboard:', e)
  }
}

async function importFromClipboard() {
  if (!clipboardData.value.trim()) return
  
  importing.value = true
  try {
    emit('import', clipboardData.value)
    clipboardData.value = ''
  } finally {
    importing.value = false
  }
}
</script>
