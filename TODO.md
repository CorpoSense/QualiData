# Migration: Buefy/Bulma → Bootstrap/BootstrapVueNext

## Phase 1: Setup
- [x] Create backup branch (`buefy-backup`)
- [x] Remove `buefy` dependency
- [x] Install `bootstrap`, `bootstrap-vue-next`, `bootstrap-icons`
- [x] Update `main.ts` to use BootstrapVueNext
- [x] Update README.md with migration notes

## Phase 2: Replace Core Components
- [x] Replace `<b-table>` → `<BTable>`
- [x] Replace `<b-input>` → `<BFormInput>`
- [x] Replace `<b-button>` → `<BButton>`
- [x] Replace `<b-modal>` → `<BModal>`
- [x] Replace `<b-dropdown>` → `<BDropdown>`
- [x] Replace `<b-notification>` → `<BAlert>`
- [x] Replace `<b-tag>` → `<BBadge>`
- [x] Replace `<b-icon>` → Bootstrap Icons (`<i class="bi bi-...">`)
- [x] Replace MDI icons with Bootstrap Icons

## Phase 3: View-by-View Migration
- [x] Login.vue
- [x] OAuthCallback.vue
- [x] Navbar.vue
- [x] ClipboardImport.vue
- [x] ClipboardExport.vue
- [x] Dashboard.vue
- [x] Pricing.vue
- [x] Projects.vue
- [x] ProjectDetail.vue
- [x] Assistant.vue
- [x] Home.vue
- [x] DataViewer.vue

## Phase 4: Testing & Polish
- [ ] Verify all forms work
- [ ] Verify all tables work
- [ ] Verify all modals work
- [ ] Check responsive behavior
- [ ] Test auth flow
- [ ] Test full E2E flow
