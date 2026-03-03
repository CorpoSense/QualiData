# Migration: Buefy/Bulma → Bootstrap/BootstrapVueNext

## Phase 1: Setup
- [x] Create backup branch (`buefy-backup`)
- [x] Remove `buefy` dependency
- [x] Install `bootstrap`, `bootstrap-vue-next`, `bootstrap-icons`
- [x] Update `main.ts` to use BootstrapVueNext
- [x] Update README.md with migration notes

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
- [ ] Home.vue (using hybrid Buefy+Bootstrap)
- [ ] DataViewer.vue (using hybrid Buefy+Bootstrap)

## Phase 4: Testing & Polish
- [ ] Verify all forms work
- [ ] Verify all tables work
- [ ] Verify all modals work
- [ ] Check responsive behavior
- [ ] Test auth flow
- [ ] Remove Buefy dependency (keep if needed for Home/DataViewer)
- [ ] Test full E2E flow
