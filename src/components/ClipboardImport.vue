<template>
  <div class="box">
    <h3 class="title is-5 mb-4">Clipboard Import</h3>
    
    <b-field label="Paste CSV Data">
      <b-input 
        v-model="clipboardData" 
        type="textarea" 
        placeholder="Paste your CSV data here..."
        :rows="10"
      ></b-input>
    </b-field>

    <div class="buttons">
      <b-button type="is-primary" :loading="importing" @click="importFromClipboard">
        Import Data
      </b-button>
      <b-button @click="pasteFromClipboard">
        <b-icon icon="content-paste"></b-icon>
        <span>Paste</span>
      </b-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

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
