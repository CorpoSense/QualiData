<template>
  <BModal :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" :title="title" size="md">
    <div v-if="description" class="alert alert-info py-2 small mb-3">
      <i class="bi bi-info-circle me-1"></i>{{ description }}
    </div>

    <div v-for="opt in options" :key="opt.key" class="mb-3">
      <label class="form-label small fw-bold">{{ opt.label }}</label>

      <BFormSelect v-if="opt.type === 'select'" :model-value="params[opt.key]" @update:model-value="v => params[opt.key] = v" :options="opt.choices" size="sm"></BFormSelect>

      <div v-else-if="opt.type === 'range'" class="d-flex align-items-center gap-2">
        <input type="range" class="form-range flex-grow-1" :min="opt.min || 0" :max="opt.max || 100" :step="opt.step || 1" v-model.number="params[opt.key]">
        <span class="badge bg-light text-dark" style="min-width: 40px; text-align: center;">{{ params[opt.key] }}</span>
      </div>

      <div v-else-if="opt.type === 'checkbox'" class="form-check">
        <input class="form-check-input" type="checkbox" v-model="params[opt.key]" :id="'opt-' + opt.key">
        <label class="form-check-label small" :for="'opt-' + opt.key">{{ opt.checkboxLabel || opt.label }}</label>
      </div>

      <BFormInput v-else :model-value="params[opt.key]" @update:model-value="v => params[opt.key] = v" size="sm" :type="opt.type || 'text'" :placeholder="opt.placeholder"></BFormInput>

      <small v-if="opt.hint" class="text-muted">{{ opt.hint }}</small>
    </div>

    <div v-if="selectedColumns.length" class="mb-2">
      <small class="text-muted">Column(s): <strong>{{ selectedColumns.join(', ') }}</strong></small>
    </div>

    <template #footer>
      <BButton variant="outline-secondary" @click="$emit('update:modelValue', false)">Cancel</BButton>
      <BButton variant="primary" :loading="loading" @click="$emit('apply', { ...params })">
        <i class="bi bi-play-fill me-1"></i>Apply
      </BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { BModal, BButton, BFormSelect, BFormInput } from 'bootstrap-vue-next'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Operation' },
  description: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  defaults: { type: Object, default: () => ({}) },
  selectedColumns: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

defineEmits(['update:modelValue', 'apply'])

const params = ref({ ...props.defaults })

watch(() => props.defaults, (d) => {
  params.value = { ...d }
}, { deep: true })

watch(() => props.modelValue, (val) => {
  if (val) params.value = { ...props.defaults }
})
</script>
