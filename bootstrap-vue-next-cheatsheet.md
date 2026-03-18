# BootstrapVueNext Mega Cheat Sheet

Quick reference for BootstrapVueNext components (Vue 3 + Bootstrap 5).

## Installation
```bash
npm install bootstrap bootstrap-vue-next sass
```
```js
// main.js
import 'bootstrap/dist/css/bootstrap.min.css'
import { BApp } from 'bootstrap-vue-next'

createApp(App).use(BApp).mount('#app')
```

---

## 1. Modal (`<BModal>`)

### Basic Usage
```vue
<BButton @click="show = true">Open Modal</BButton>
<BModal v-model="show" title="Hello World">
  Modal content here
</BModal>
```

### Button Customization
| Prop | Description |
|------|-------------|
| `ok-title` | OK button text |
| `cancel-title` | Cancel button text (set to `''` to hide) |
| `ok-variant` | Button variant (primary, danger, etc.) |
| `no-footer` | Hide footer entirely |

```vue
<!-- OK-only modal (no cancel button) -->
<BModal v-model="show" ok-title="Import" @ok="handleImport" :cancel-title="''">
  Content here
</BModal>
```

### Slots
- `header` - Custom header (removes default X close button)
- `title` - Custom title
- `footer` - Custom footer (removes default OK/Cancel buttons)

```vue
<BModal v-model="show">
  <template #header>
    <h5 class="m-0">My Title</h5>
  </template>
  Body content
</BModal>
```

### Events
- `@ok` - OK button clicked
- `@cancel` - Cancel button clicked
- `@close` - X button clicked
- `@hide` - Modal closing (can call `e.preventDefault()`)

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `v-model` | boolean | false | Visibility |
| `title` | string | - | Modal title |
| `size` | string | - | sm, lg, xl |
| `scrollable` | boolean | false | Scrollable body |
| `no-close-on-esc` | boolean | false | Disable ESC close |
| `no-close-on-backdrop` | boolean | false | Disable backdrop close |
| `no-header-close` | boolean | false | Hide X button |
| `teleportDisabled` | boolean | false | Render in-place |

---

## 2. Button (`<BButton>`)

### Variants
```vue
<BButton>Default</BButton>
<BButton variant="primary">Primary</BButton>
<BButton variant="success">Success</BButton>
<BButton variant="danger">Danger</BButton>
<BButton variant="warning">Warning</BButton>
<BButton variant="info">Info</BButton>
<BButton variant="outline-primary">Outline</BButton>
<BButton variant="link">Link</BButton>
```

### Sizing
```vue
<BButton size="sm">Small</BButton>
<BButton>Default</BButton>
<BButton size="lg">Large</BButton>
```

### States
```vue
<BButton disabled>Disabled</BButton>
<BButton :loading="true">Loading</BButton>
<BButton pressed>Pressed</BButton>
<BButton v-model:pressed="toggle">Toggle</BButton>
```

### Other Props
```vue
<BButton pill>Pill</BButton>
<BButton squared>Squared</BButton>
<BButton block>Block</BButton>
<BButton type="submit">Submit</BButton>
<BButton href="/link">Link</BButton>
<BButton to="/route">Router</BButton>
```

---

## 3. Form Inputs

### Text Input (`<BFormInput>`)
```vue
<BFormInput v-model="text" placeholder="Enter text" />
<BFormInput v-model="email" type="email" />
<BFormInput v-model="password" type="password" />
<BFormInput v-model="number" type="number" min="0" max="100" />

<!-- Sizes -->
<BFormInput size="sm" />
<BFormInput size="lg" />

<!-- States -->
<BFormInput :state="true" />   <!-- Valid -->
<BFormInput :state="false" />  <!-- Invalid -->
<BFormInput disabled />
<BFormInput readonly />
```

### Select (`<BFormSelect>`)
```vue
<BFormSelect v-model="selected" :options="options" />

<script setup>
const selected = ref('a')
const options = [
  { value: 'a', text: 'Option A' },
  { value: 'b', text: 'Option B' },
  { value: null, text: 'Choose...', disabled: true }
]
</script>
```

### Checkbox (`<BFormCheckbox>`)
```vue
<BFormCheckbox v-model="checked">Label text</BFormCheckbox>
<BFormCheckboxGroup v-model="selected" :options="options" />
```

### Radio (`<BFormRadio>`)
```vue
<BFormRadio v-model="picked" value="a">Option A</BFormRadio>
<BFormRadioGroup v-model="picked" :options="options" />
```

### File Input (`<BFormFile>`)
```vue
<BFormFile v-model="file" accept=".csv,.xlsx" />
<BFormFile v-model="files" multiple />
<BFormFile v-model="file" disabled />
```

---

## 4. Dropdown (`<BDropdown>`)

### Basic
```vue
<BDropdown text="Actions">
  <BDropdownItem @click="doSomething">Do It</BDropdownItem>
  <BDropdownItem>Another Action</BDropdownItem>
  <BDropdownDivider />
  <BDropdownItem disabled>Disabled</BDropdownItem>
</BDropdown>
```

### With Variant
```vue
<BDropdown text="Menu" variant="primary">
  <BDropdownItem>Action</BDropdownItem>
</BDropdown>
```

### Custom Button Content
```vue
<BDropdown>
  <template #button-content>
    <i class="bi bi-gear"></i> Settings
  </template>
  <BDropdownItem>Option 1</BDropdownItem>
</BDropdown>
```

### Positioning
```vue
<BDropdown placement="bottom-end">
  <BDropdownItem>Bottom End</BDropdownItem>
</BDropdown>
```
Options: `top`, `top-start`, `top-end`, `bottom`, `bottom-start`, `bottom-end`, `left`, `left-start`, `left-end`, `right`, `right-start`, `right-end`

### Split Button
```vue
<BDropdown split text="Split Menu">
  <BDropdownItem>Action 1</BDropdownItem>
  <BDropdownItem>Action 2</BDropdownItem>
</BDropdown>
```

---

## 5. Toast Notifications

### Using `useToast` Composable
```js
import { useToast } from 'bootstrap-vue-next'

const { show, create, success, danger, warning, info } = useToast()

// Quick methods
success('Saved!', 'Success')
danger('Error!', 'Error')
warning('Warning', 'Watch out')
info('Info', 'FYI')

// Custom
create({
  title: 'My Toast',
  variant: 'success',
  modelValue: 3000,  // auto-dismiss ms
  solid: true,
  body: 'Message here'
})
```

### Component Usage
```vue
<BToast v-model="show" variant="success" solid>
  <template #title>Success</template>
  Operation completed!
</BToast>
```

### Position (via BOrchestrator)
```vue
<!-- Place BOrchestrator in App.vue -->
<BOrchestrator />

<!-- Then use positions -->
create({
  title: 'Toast',
  position: 'top-end'  // top-start, top-end, bottom-start, bottom-end
})
```

---

## 6. Table (`<BTable>`)

### Basic
```vue
<BTable :items="items" :fields="fields" striped bordered hover />
```

### Fields Definition
```js
const fields = [
  'name',                    // Simple column
  { key: 'age', sortable: true },  // Sortable
  { key: 'actions', label: 'Ops' } // Custom label
]
```

### With Data
```vue
<script setup>
const items = [
  { name: 'John', age: 30 },
  { name: 'Jane', age: 25 }
]
</script>

<BTable :items="items" :fields="['name', 'age']" />
```

### Features
```vue
<BTable
  :items="items"
  :fields="fields"
  striped           <!-- Striped rows -->
  bordered          <!-- Borders -->
  hover             <!-- Hover effect -->
  dark              <!-- Dark theme -->
  small             <!-- Condensed -->
  responsive        <!-- Responsive wrapper -->
  :per-page="10"    <!-- Pagination -->
  :current-page="1"
/>
```

---

## 7. Nav & Tabs

### Basic Nav
```vue
<BNav>
  <BNavItem active>Active</BNavItem>
  <BNavItem>Link</BNavItem>
  <BNavItem disabled>Disabled</BNavItem>
</BNav>
```

### Nav with Router
```vue
<BNav>
  <BNavItem to="/home">Home</BNavItem>
  <BNavItem to="/about">About</BNavItem>
</BNav>
```

### Pills Style
```vue
<BNav pills>
  <BNavItem to="/a" active>A</BNavItem>
  <BNavItem to="/b">B</BNavItem>
</BNav>
```

---

## 8. Grid System

```vue
<BContainer>
  <BRow>
    <BCol>12 columns</BCol>
  </BRow>
  <BRow>
    <BCol sm="6">6 on small</BCol>
    <BCol sm="6">6 on small</BCol>
  </BRow>
  <BRow>
    <BCol md="4">4</BCol>
    <BCol md="4">4</BCol>
    <BCol md="4">4</BCol>
  </BRow>
</BContainer>
```

### Container Variants
- `<BContainer>` - Fixed width
- `<BContainer fluid>` - Full width

---

## 9. Card (`<BCard>`)

```vue
<BCard title="Card Title" img-src="/image.jpg">
  Card content here
  <template #footer>
    Footer content
  </template>
</BCard>

<!-- With body-only (no header/footer) -->
<BCard body>
  Just the body
</BCard>
```

---

## 10. Alert (`<BAlert>`)

```vue
<BAlert variant="success" dismissible>
  Success message!
</BAlert>

<BAlert variant="danger" :modelValue="true">
  Error occurred
</BAlert>
```

---

## 11. Collapse (`<BCollapse>`)

```vue
<BButton v-b-toggle.collapse-1>Toggle</BButton>
<BCollapse id="collapse-1">
  <BCard>Collapsed content</BCard>
</BCollapse>
```

---

## 12. Spinner (`<BSpinner>`)

```vue
<BSpinner />
<BSpinner label="Loading..." />
<BSpinner small />
<BSpinner variant="primary" />
<BSpinner type="grow" />  <!-- Growing spinner -->
```

---

## 13. Badge (`<BBadge>`)

```vue
<BBadge>Default</BBadge>
<BBadge variant="primary">Primary</BBadge>
<BBadge pill>Pill</BBadge>
```

---

## 14. Progress (`<BProgress>`)

```vue
<BProgress :value="50" :max="100" />
<BProgress :value="25" variant="success" striped animated />
```

---

## Common Props Reference

| Prop | Values | Description |
|------|--------|-------------|
| `variant` | primary, secondary, success, danger, warning, info, light, dark | Color theme |
| `size` | sm, lg | Component size |
| `disabled` | boolean | Disabled state |
| `readonly` | boolean | Read-only state |
| `multiple` | boolean | Multiple selection |

---

## Import Cheatsheet

```js
// Import from main package
import { BApp, BModal, BButton, BFormInput, BTable, BDropdown, BDropdownItem, BToast, useToast } from 'bootstrap-vue-next'

// Import individual components
import { BModal } from 'bootstrap-vue-next/components/BModal'
import { useToast } from 'bootstrap-vue-next/composables/useToast'

// Directives (if needed)
import { vBModal } from 'bootstrap-vue-next/directives/BModal'
import { vBTooltip } from 'bootstrap-vue-next/directives/BTooltip'
```

---

## Component List (~35 Components)

| Component | Description |
|-----------|-------------|
| BAccordion | Accordion container |
| BAccordionItem | Single accordion item |
| BAlert | Alert messages |
| BApp | Root app component |
| BAvatar | User avatar |
| BBadge | Badge/label |
| BBreadcrumb | Breadcrumb navigation |
| BButton | Button |
| BButtonGroup | Button group |
| BButtonToolbar | Button toolbar |
| BCard | Card container |
| BCarousel | Image carousel |
| BCollapse | Collapsible content |
| BDropdown | Dropdown menu |
| BDropdownItem | Dropdown item |
| BDropdownDivider | Dropdown divider |
| BForm | Form wrapper |
| BFormCheckbox | Checkbox |
| BFormFile | File input |
| BFormGroup | Form group |
| BFormInput | Text input |
| BFormRadio | Radio button |
| BFormSelect | Select dropdown |
| BFormTextarea | Textarea |
| BImg | Responsive image |
| BInputGroup | Input group |
| BLink | Link/router link |
| BListGroup | List group |
| BModal | Modal dialog |
| BNav | Navigation |
| BNavbar | Navbar |
| BOffcanvas | Slide-out panel |
| BOverlay | Loading overlay |
| BPagination | Pagination |
| BPlaceholder | Loading placeholder |
| BPopover | Popover |
| BProgress | Progress bar |
| BSpinner | Loading spinner |
| BTable | Data table |
| BTab | Tab pane |
| BTabs | Tab container |
| BToast | Toast notification |
| BTooltip | Tooltip |

---

*Last Updated: 2026-03-07*
*Source: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/*
