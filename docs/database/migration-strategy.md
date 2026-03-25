# Database Migration Strategy

## Overview

This document describes the database migration strategy for MasterDataCleaner, which has been simplified to avoid recurring schema mismatch errors during development.

## Problem Statement

Previously, the project accumulated 14+ migration files with complex branching and merging, leading to:
- Recurring schema mismatch errors (e.g., `column datasets.version does not exist`)
- Type conversion errors (e.g., `column "id" is of type integer but expression is of type character varying`)
- Complex migration chain with multiple heads and merge points
- Difficulty debugging and maintaining database schema

## Solution: Simplified Migration Approach

### Development Phase (Current)

For local development, we use SQLAlchemy's `create_all()` approach:

1. **Single Initial Migration**: One clean migration file generated from current models
2. **Auto-Create Tables**: Application uses `Base.metadata.create_all()` on startup
3. **No Manual Migrations**: Schema changes are automatically applied when models change

### Production Phase (Future)

For production deployments, we will use Alembic migrations:

1. **Version Control**: Track schema changes via Alembic migrations
2. **Upgrade Path**: Apply migrations sequentially to existing databases
3. **Rollback Support**: Maintain downgrade capability for production safety

## Implementation Details

### Current Setup

1. **Migration Files**: Only one file in `backend/alembic/versions/`
   - `155b9933f705_initial_migration_create_.py` - Clean initial migration from current models

2. **Startup Code**: `backend/app/main.py`
   - `run_migrations()` function uses `Base.metadata.create_all()`
   - Tables are created/verified on application startup

3. **Development Workflow**:
   ```bash
   # Start development server
   pnpm dev
   
   # Tables are automatically created from models
   # No manual migration commands needed
   ```

### Schema Changes During Development

When you need to change the database schema:

1. **Modify Models**: Update SQLAlchemy models in `backend/app/db/models/`
2. **Restart Application**: Tables are automatically updated on startup
3. **No Migration Commands**: No need to run `alembic revision` or `alembic upgrade`

### Production Deployment

When deploying to production:

1. **Generate Migration**: Create Alembic migration from model changes
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Review Migration**: Check generated migration file for correctness

3. **Apply Migration**: Run migration on production database
   ```bash
   alembic upgrade head
   ```

## Benefits

1. **Simplified Development**: No manual migration commands during active development
2. **Reduced Errors**: Eliminates schema mismatch issues from complex migration chains
3. **Faster Iteration**: Quick schema changes without migration overhead
4. **Clean Foundation**: Single source of truth (models) for database schema

## Migration History Cleanup

All previous migration files have been removed:
- `add_is_saved_to_projects.py`
- `add_operation_history_fields.py`
- `add_role_timezone.py`
- `add_schema_json_to_projects.py`
- `add_version_to_datasets.py`
- `convert_role_to_varchar.py`
- `fix_agents_owner_id_to_user_id.py`
- `fix_all_schema_discrepancies.py`
- `fix_user_columns.py`
- `fix_user_id_to_uuid.py`
- `merge_heads.py`
- `merge_heads_version.py`
- `rename_password_column.py`
- `21b545f994e8_initial_migration.py`

## Future Considerations

1. **Production Migrations**: When ready for production, establish proper Alembic workflow
2. **Data Migrations**: Plan for data migration scripts if needed
3. **Testing**: Ensure migration tests cover upgrade and downgrade paths
4. **Documentation**: Keep migration strategy updated as project evolves

## Related Files

- `backend/app/main.py` - Application startup with `run_migrations()`
- `backend/app/db/models/` - SQLAlchemy model definitions
- `backend/alembic/versions/` - Migration files (currently single initial migration)
- `backend/alembic/env.py` - Alembic configuration