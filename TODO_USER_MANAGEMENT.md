# User Management Implementation Plan

## Phase 1: Backend - Database & Models

### Task 1.1: Update User Model ✅ DONE
- [x] Add `role` column (String, default='user', values: admin/manager/user)
- [x] Add `timezone` column (String, nullable)
- [x] Create migration file

### Task 1.2: Create Users Router ✅ DONE
- [ ] Create `backend/app/routers/users.py`
- [ ] Implement list users (admin only)
- [ ] Implement create user (admin only)
- [ ] Implement get user by ID (admin only)
- [ ] Implement update user (admin only)
- [ ] Implement delete user (admin only)
- [ ] Implement get current user profile
- [ ] Implement update own profile
- [ ] Include users router in main.py

### Task 1.3: Update Auth Router ✅ DONE
- [ ] Update registration to set default role='user'
- [ ] Add admin user creation from env vars on startup (ADMIN_USER/ADMIN_PASSWORD)

## Phase 2: Backend - Tests

### Task 2.1: Write Unit Tests for Users Router (Deferred)
- [ ] Test list users (admin only - returns 403 for non-admin)
- [ ] Test create user (admin only)
- [ ] Test get user by ID (admin only)
- [ ] Test update user (admin only)
- [ ] Test delete user (admin only)
- [ ] Test get own profile (authenticated)
- [ ] Test update own profile (authenticated)
- [ ] Test update own password

## Phase 3: Frontend - User Management UI

### Task 3.1: Create Users Admin Page ✅ DONE
- [ ] Create `src/views/admin/Users.vue`
- [ ] Add table listing all users
- [ ] Add search/filter functionality
- [ ] Add "Add User" button
- [ ] Add edit user modal
- [ ] Add delete user confirmation

### Task 3.2: Add Router & Navigation ✅ DONE
- [ ] Add `/admin/users` route (requires admin)
- [ ] Add admin link in navbar (only for admin role)

### Task 3.3: Create Profile Page ✅ DONE
- [ ] Create `src/views/Profile.vue`
- [ ] Show user info (name, email, role, timezone)
- [ ] Allow editing name, email, timezone
- [ ] Allow changing password
- [ ] Add route `/profile`

## Phase 4: Integration & Polish

### Task 4.1: Update Frontend API Client
- [ ] Add users API functions
- [ ] Add auth header handling

### Task 4.2: Test End-to-End
- [ ] Test admin can access /admin/users
- [ ] Test regular user cannot access /admin/users
- [ ] Test user can edit own profile
- [ ] Test all CRUD operations work

## Phase 5: Cleanup & Documentation

### Task 5.1: Cleanup
- [ ] Remove unused code
- [ ] Update README if needed

---

## Implementation Order
1. Task 1.1 → Task 1.2 → Task 1.3 (Backend)
2. Task 2.1 (Backend Tests)
3. Task 3.1 → Task 3.2 → Task 3.3 (Frontend)
4. Task 4.1 → Task 4.2 (Integration)
5. Task 5.1 (Cleanup)

---

## Progress
- **Task 1.1**: ✅ Complete
- **Task 1.2**: ✅ Complete
- **Task 1.3**: ✅ Complete
- **Task 1.3**: Pending
- **Task 2.1**: Pending
- **Task 3.1-3.3**: Pending
- **Task 4.1-4.2**: Pending
- **Task 5.1**: Pending
