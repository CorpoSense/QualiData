<template>
  <BModal v-model="visible" :title="title" @hide="onCancel">
    <p v-if="message" class="mb-2">{{ message }}</p>
    <BFormInput
      ref="inputRef"
      v-model="inputValue"
      :type="inputType"
      :placeholder="placeholder"
      @keyup.enter="onConfirm"
    ></BFormInput>
    <template #footer>
      <BButton @click="onCancel">Cancel</BButton>
      <BButton variant="primary" @click="onConfirm">{{ confirmText }}</BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Input' },
  message: { type: String, default: '' },
  defaultValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  inputType: { type: String, default: 'text' },
  confirmText: { type: String, default: 'OK' },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const visible = ref(false)
const inputValue = ref('')
const inputRef = ref(null)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    inputValue.value = props.defaultValue
    nextTick(() => inputRef.value?.$el?.focus?.())
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

function onConfirm() {
  emit('confirm', inputValue.value)
  visible.value = false
}

function onCancel() {
  emit('cancel')
  visible.value = false
}
</script>
