<template>
  <nav aria-label="breadcrumb" class="mb-3">
    <ol class="breadcrumb mb-0">
      <li 
        v-for="(item, index) in items" 
        :key="index" 
        class="breadcrumb-item"
        :class="{ active: index === items.length - 1 }"
      >
        <router-link 
          v-if="item.path && index < items.length - 1" 
          :to="item.path"
        >
          <i v-if="item.icon" :class="`${item.icon} me-1`"></i>{{ item.label }}
        </router-link>
        <span v-else>
          <i v-if="item.icon" :class="`${item.icon} me-1`"></i>{{ item.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
// import { computed } from 'vue'
// import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  label: string
  path?: string
  icon?: string
}

/*const props = */defineProps<{
  items: BreadcrumbItem[]
}>()

/*const route = useRoute()

// Allow dynamic items override from props or compute from route
const breadcrumbItems = computed(() => {
  if (props.items.length > 0) {
    return props.items
  }
  return []
})*/
</script>

<style scoped>
.breadcrumb {
  background-color: transparent;
  padding: 0;
  margin: 0;
}

.breadcrumb-item {
  font-size: 0.875rem;
}

.breadcrumb-item a {
  color: var(--bs-primary);
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}

.breadcrumb-item.active {
  color: var(--bs-body-color);
  font-weight: 500;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: var(--bs-secondary-color);
}
</style>
