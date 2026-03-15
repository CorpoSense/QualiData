# Revert to BTable with Built-in Pagination

## Plan

### Phase 1: Backup & Setup
- [x] 1.1 Create backup of current DataViewer.vue
- [x] 1.2 Verify current state compiles

### Phase 2: Update DataViewer.vue
- [ ] 2.1 Replace SmartTable import with BTable import
- [ ] 2.2 Replace SmartTable component with BTable component
- [ ] 2.3 Add BTable pagination props (per-page, current-page, total-rows)
- [ ] 2.4 Remove custom pagination code (top toolbar pagination)
- [ ] 2.5 Keep column selection badges (external to table)
- [ ] 2.6 Fix row selection handler

### Phase 3: Test & Verify
- [ ] 3.1 Run build to check for errors
- [ ] 3.2 Fix any TypeScript/template errors
- [ ] 3.3 Run backend tests

### Phase 4: Commit & Deploy
- [ ] 4.1 Commit changes
- [ ] 4.2 Push to GitHub
- [ ] 4.3 Verify deployment
