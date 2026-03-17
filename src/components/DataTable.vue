<template>
  <div class="data-table-wrapper">
    <!-- Table -->
    <div class="table-responsive">
      <table class="table table-hover table-striped table-sm">
        <thead>
          <tr>
            <th 
              v-for="field in fields" 
              :key="field.key"
              :class="{ 'table-primary': isSelected(field) }"
              @click="$emit('head-clicked', field)"
              style="cursor: pointer"
            >
              {{ field.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(row, index) in items" 
            :key="index"
            @click="$emit('row-clicked', { item: row, index })"
          >
            <td v-for="field in fields" :key="field.key">
              {{ row[field.key] }}
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td :colspan="fields.length" class="text-center text-muted py-4">
              No data to display
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  items: { type: Array, default: () => [] },
  fields: { type: Array, default: () => [] },
  selectedColumns: { type: Array, default: () => [] }
})

defineEmits(['row-clicked', 'head-clicked'])

function isSelected(field) {
  const fieldKey = field.key || field.field
  return props.selectedColumns.includes(fieldKey)
}
</script>

<style scoped>
.data-table-wrapper { width: 100%; }
.table-responsive { max-height: 70vh; overflow-y: auto; }
table { margin-bottom: 0; }
th { user-select: none; }
th:hover { background-color: var(--bs-table-hover-bg); }
td { vertical-align: middle; }
</style>
