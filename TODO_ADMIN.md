# Admin User Implementation

## Task
Implement smart admin/user creation for MasterDataCleaner

## Sub-tasks

### Phase 1: Admin Creation on Startup
- [x] 1. Add admin env vars to config.py (ADMIN_USER, ADMIN_PASSWORD)
- [x] 2. Create admin creation function in main.py startup
- [x] 3. Add warning if admin env vars not set

### Phase 2: Signup Logic Update
- [x] 4. Check if admin exists in database
- [x] 5. First user = admin (if no admin env)
- [x] 6. Add "Please try again" error handling

### Phase 3: Testing
- [x] 7. Tests pass
- [x] 8. Build passes
