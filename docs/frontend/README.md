# Frontend Documentation

Vue.js 3 frontend application documentation.

## Overview

The MasterDataCleaner frontend is built with Vue 3, TypeScript, and BootstrapVueNext, providing a modern, responsive user interface for data cleaning operations.

## Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Vue** | 3.5+ | Reactive UI framework |
| **TypeScript** | 5.9+ | Type safety |
| **Pinia** | 3.0+ | State management |
| **Vue Router** | 4.6+ | Client-side routing |
| **BootstrapVueNext** | 0.43+ | UI components |
| **Bootstrap** | 5.3+ | CSS framework |
| **Vite** | 5.4+ | Build tool |
| **Vitest** | 0.34+ | Unit testing |
| **Cypress** | 13.0+ | E2E testing |

## Project Structure

```
src/
├── main.ts                    # Application entry point
├── App.vue                    # Root component
├── router.ts                  # Route configuration
├── env.d.ts                   # Environment type declarations
├── shims-vue.d.ts             # Vue component type declarations
├── vite-env.d.ts              # Vite type declarations
│
├── views/                     # Page-level components
│   ├── Home.vue               # Landing page
│   ├── Login.vue              # Login page
│   ├── Dashboard.vue          # User dashboard
│   ├── Projects.vue           # Projects list
│   ├── ProjectDetail.vue      # Single project view
│   ├── DataViewer.vue         # Data table and operations
│   ├── Assistant.vue          # AI assistant wizard
│   ├── AgentManager.vue       # AI agent management
│   ├── Pricing.vue            # Pricing page
│   ├── Profile.vue            # User profile
│   ├── ForgotPassword.vue     # Password reset request
│   ├── ResetPassword.vue      # Password reset form
│   ├── OAuthCallback.vue      # OAuth callback handler
│   └── admin/
│       └── Users.vue          # Admin user management
│
├── components/                # Reusable components
│   ├── ProjectCard.vue        # Project display card
│   ├── DatasetCard.vue        # Dataset display card
│   ├── DataTable.vue          # Data table with operations
│   ├── OperationConfirmModal.vue  # Operation confirmation
│   ├── PromptModal.vue        # AI prompt input modal
│   ├── ClipboardImport.vue    # Clipboard paste import
│   ├── PricingSection.vue     # Pricing display
│   └── RateLimitStatus.vue    # API rate limit indicator
│
├── composables/               # Composable functions
│   ├── useUser.js             # User role utilities
│   └── useToast.js            # Toast notification system
│
├── stores/                    # Pinia state stores
│   └── debug.ts               # Debug mode state
│
├── utils/                     # Utility functions
│   └── api.js                 # API client utilities
│
└── assets/                    # Static assets
    └── style.css              # Global styles
```

## Routing

### Route Configuration

Routes are defined in `router.ts` with meta information for authentication:

```typescript
const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/pricing', component: Pricing },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/projects', component: Projects, meta: { requiresAuth: true } },
  { path: '/projects/:id', component: ProjectDetail, meta: { requiresAuth: true } },
  { path: '/projects/:id/dataset/:datasetId', component: DataViewer, meta: { requiresAuth: true } },
  { path: '/assistant', component: Assistant, meta: { requiresAuth: true } },
  { path: '/agents', component: AgentManager, meta: { requiresAuth: true } },
  { path: '/admin/users', component: Users, meta: { requiresAuth: true, requiresAdmin: true } },
  // ... auth and OAuth routes
]
```

### Route Guards

Navigation guards handle authentication:

```typescript
router.beforeEach(async (to, _from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const token = localStorage.getItem('token')

  if (requiresAuth && !token) {
    next('/login')
  } else if (requiresAdmin && !isAdminUser) {
    next('/dashboard')
  } else {
    next()
  }
})
```

### Route Types

| Route | Path | Auth Required | Description |
|-------|------|---------------|-------------|
| Home | `/` | No | Landing page |
| Login | `/login` | No | User login |
| Dashboard | `/dashboard` | Yes | User dashboard |
| Projects | `/projects` | Yes | Projects list |
| Project Detail | `/projects/:id` | Yes | Single project view |
| Data Viewer | `/projects/:id/dataset/:datasetId` | Yes | Data table and operations |
| Assistant | `/assistant` | Yes | AI cleaning wizard |
| Agents | `/agents` | Yes | AI agent management |
| Profile | `/profile` | Yes | User profile settings |
| Pricing | `/pricing` | No | Pricing information |
| Admin Users | `/admin/users` | Admin only | User management |

## State Management

### Pinia Stores

#### Debug Store

```typescript
// stores/debug.ts
import { defineStore } from 'pinia'

export const useDebugStore = defineStore('debug', {
  state: () => ({
    isDebug: false,
    debugToken: null,
  }),
  actions: {
    init() {
      this.isDebug = import.meta.env.DEV
    },
  },
})
```

### Global State

User authentication state is managed via localStorage:
- `token` - JWT authentication token
- Auto-login in debug mode

## Components

### View Components

#### DataViewer.vue

The main data cleaning interface (3100+ lines):

**Features:**
- Data table with sorting and filtering
- Operation toolbar with dropdowns
- Real-time preview
- Before/after comparison
- Operation history panel
- Column profiling

**Operations Available:**
- Missing values (fill, drop)
- String operations (trim, case conversion)
- Date operations (parse, extract)
- AI cleaning
- Deduplication
- Structural operations

**Key Sections:**
```vue
<template>
  <div class="data-viewer">
    <!-- Operations Toolbar -->
    <div class="card mb-3">
      <!-- Operation dropdowns -->
    </div>

    <!-- Data Table -->
    <DataTable :data="displayedData" />

    <!-- History Panel -->
    <div v-if="showHistory">
      <!-- Operation history list -->
    </div>

    <!-- Profile Panel -->
    <div v-if="showProfile">
      <!-- Column statistics -->
    </div>
  </div>
</template>
```

#### Dashboard.vue

User overview and quick access:

**Features:**
- Statistics cards (projects, datasets, rows, storage)
- Quick actions
- Recent projects list
- Recent operations
- Operation stats

#### ProjectDetail.vue

Project management and dataset list:

**Features:**
- Project information
- Dataset list
- Import data button
- Export options
- Project settings

### Reusable Components

#### DataTable.vue

Generic data table component:

**Props:**
- `data` - Array of row objects
- `columns` - Column definitions
- `sortable` - Enable column sorting
- `selectable` - Enable row selection

**Events:**
- `sort` - Column sort requested
- `select` - Row selection changed
- `cell-click` - Cell clicked

#### OperationConfirmModal.vue

Modal for confirming operations:

**Props:**
- `operation` - Operation type
- `columns` - Selected columns
- `preview` - Operation preview

**Events:**
- `confirm` - User confirmed operation
- `cancel` - User cancelled

#### ProjectCard.vue

Project display card:

**Props:**
- `project` - Project object
- `showStats` - Display statistics

**Events:**
- `click` - Card clicked
- `delete` - Delete requested

## Composables

### useUser

User role utilities:

```javascript
// composables/useUser.js
import { ref } from 'vue'

export const currentUser = ref(null)

export function isAdmin(user) {
  return user?.role?.toLowerCase() === 'admin'
}

export function isManager(user) {
  return user?.role?.toLowerCase() === 'manager'
}

export function hasRole(user, role) {
  return user?.role?.toLowerCase() === role.toLowerCase()
}
```

**Usage:**
```vue
<script setup>
import { isAdmin } from '@/composables/useUser'
import { currentUser } from '@/composables/useUser'

const isUserAdmin = computed(() => isAdmin(currentUser.value))
</script>
```

### useToast

Toast notification system:

```javascript
// composables/useToast.js
import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  function show(message, variant = 'info', duration = 3000) {
    const id = Date.now()
    toasts.value.push({ id, message, variant })
    setTimeout(() => remove(id), duration)
  }

  return {
    toasts,
    show,
    success: (msg) => show(msg, 'success'),
    error: (msg) => show(msg, 'danger', 5000),
    warning: (msg) => show(msg, 'warning', 4000),
    info: (msg) => show(msg, 'info'),
  }
}
```

**Usage:**
```vue
<script setup>
import { useToast } from '@/composables/useToast'

const { success, error } = useToast()

async function saveData() {
  try {
    await api.save(data)
    success('Data saved successfully')
  } catch (e) {
    error('Failed to save data')
  }
}
</script>
```

## Utilities

### API Client

```javascript
// utils/api.js
export function getApiUrl() {
  // In production, use relative URL
  if (import.meta.env.PROD || window.location.hostname !== 'localhost') {
    return ''
  }
  // In development, use configured URL
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}
```

**Usage:**
```javascript
import { getApiUrl } from '@/utils/api'

const apiUrl = getApiUrl()
const response = await fetch(`${apiUrl}/api/projects`)
```

## Styling

### Bootstrap Integration

BootstrapVueNext provides Bootstrap 5 components:

```vue
<template>
  <BButton variant="primary">Click Me</BButton>
  <BFormInput v-model="value" />
  <BTable :items="data" />
</template>
```

### Custom Styles

Global styles in `assets/style.css`:

```css
/* Custom component styles */
.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
}

.operation-item {
  cursor: pointer;
  transition: all 0.2s ease;
}
```

### Responsive Design

Bootstrap grid system for responsive layouts:

```vue
<template>
  <div class="row">
    <div class="col-12 col-lg-6">Left Column</div>
    <div class="col-12 col-lg-6">Right Column</div>
  </div>
</template>
```

## API Integration

### Authentication

```javascript
// Login
const response = await fetch(`${apiUrl}/api/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})
const { access_token } = await response.json()
localStorage.setItem('token', access_token)

// Authenticated request
const response = await fetch(`${apiUrl}/api/projects`, {
  headers: { Authorization: `Bearer ${token}` }
})
```

### Error Handling

```javascript
async function fetchData() {
  try {
    const response = await fetch(url, options)
    if (!response.ok) {
      if (response.status === 401) {
        // Redirect to login
        router.push('/login')
      }
      throw new Error(response.statusText)
    }
    return await response.json()
  } catch (error) {
    toast.error(error.message)
  }
}
```

## Build & Development

### Development Server

```bash
pnpm dev
```

Features:
- Hot module replacement (HMR)
- Fast refresh
- Source maps

### Build

```bash
pnpm build
```

Output:
- Minified JavaScript
- Optimized CSS
- Asset optimization
- Code splitting

### Type Checking

```bash
vue-tsc --noEmit
```

### Testing

**Unit Tests:**
```bash
pnpm test:frontend
```

**E2E Tests:**
```bash
pnpm test:e2e
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

## Best Practices

### Component Design

1. **Single Responsibility** - Each component does one thing well
2. **Props Down, Events Up** - Data flows down, events bubble up
3. **Composables** - Extract reusable logic
4. **Type Safety** - Use TypeScript for props and data

### Code Organization

1. **Logical Grouping** - Related components together
2. **Clear Naming** - Descriptive component names
3. **Consistent Structure** - Similar components follow same pattern

### Performance

1. **Lazy Loading** - Load routes on demand
2. **Computed Properties** - Cache expensive calculations
3. **Virtual Scrolling** - Efficient large list rendering
4. **Debouncing** - Limit frequent operations

## Next Steps

- **[Backend](../backend/README.md)** - FastAPI service documentation
- **[API Reference](../api-reference/README.md)** - Complete API documentation
- **[Guides](../guides/README.md)** - Development tutorials

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
