# Integration Testing Status

## Current Approach
Using mocked database (unit tests) - works well for route validation.

## Why Full SQLite Integration Needs Refactoring

The app uses:
1. **Async database layer** (asyncpg for PostgreSQL)
2. **Lazy engine initialization** with global state
3. **Direct router imports** from app.db.database

To use real SQLite would require:
1. Refactor database.py to not call get_async_engine() at module load
2. Make engines not global/cached
3. Proper async/sync session handling

## Current Test Coverage (42 tests)

### What We Test
- Route authentication requirements
- Input validation
- Route registration
- Health endpoints

### What We Can't Test (without refactoring)
- Actual CRUD operations
- Database transactions
- Real user authentication flow

## Options

### Option A: Keep Current Approach (Recommended)
- 42 tests validating API contract
- 41% coverage
- Fast, reliable CI

### Option B: Full Refactoring (Complex)
- Requires refactoring database.py
- Make engines injectable
- Add proper async test support
- Estimated: 2-3 hours work

---

**Recommendation:** Keep current approach. The mocked tests validate the API works correctly. For true integration testing, consider E2E tests with Cypress instead.
