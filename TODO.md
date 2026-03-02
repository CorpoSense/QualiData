# Migration: Buefy/Bulma → Bootstrap/BootstrapVueNext

## Phase 1: Setup
- [x] Create backup branch (`buefy-backup`)
- [x] Remove `buefy` dependency
- [x] Install `bootstrap`, `bootstrap-vue-next`, `bootstrap-icons`
- [x] Update `main.ts` to use BootstrapVueNext
- [ ] Update README.md with migration notes

## Phase 2: Replace Core Components
- [ ] Replace `<b-table>` → `<BTable>`
- [ ] Replace `<b-input>` → `<BFormInput>`
- [ ] Replace `<b-button>` → `<BButton>`
- [ ] Replace `<b-modal>` → `<BModal>`
- [ ] Replace `<b-dropdown>` → `<BDropdown>`
- [ ] Replace `<b-notification>` → `<BAlert>`
- [ ] Replace `<b-tag>` → `<BBadge>`
- [ ] Replace `<b-icon>` → Bootstrap Icons (`<i class="bi bi-...">`)
- [ ] Replace MDI icons with Bootstrap Icons

## Phase 3: View-by-View Migration
- [ ] Login.vue
- [ ] OAuthCallback.vue
- [ ] Navbar.vue
- [ ] ClipboardImport.vue
- [ ] ClipboardExport.vue
- [ ] Dashboard.vue
- [ ] Pricing.vue
- [ ] Projects.vue
- [ ] ProjectDetail.vue
- [ ] Assistant.vue
- [ ] Home.vue
- [ ] DataViewer.vue

## Phase 4: Testing & Polish
- [ ] Verify all forms work
- [ ] Verify all tables work
- [ ] Verify all modals work
- [ ] Check responsive behavior
- [ ] Test auth flow
- [ ] Remove leftover Bulma/Buefy CSS
- [ ] Test full E2E flow
