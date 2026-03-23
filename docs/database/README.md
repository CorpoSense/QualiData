# Database Documentation

Database schema, models, and data management for MasterDataCleaner.

## Overview

MasterDataCleaner uses a relational database to store user data, projects, datasets, and operation history. The application supports multiple database backends through SQLAlchemy ORM.

## Supported Databases

| Database | Use Case | Driver |
|----------|----------|--------|
| **PostgreSQL** | Production (primary) | asyncpg |
| **MySQL** | Production (alternative) | aiomysql |
| **SQLite** | Development, testing | aiosqlite |

## Database URL Configuration

```env
# SQLite (Development)
DATABASE_URL=sqlite+aiosqlite:///./master_data_cleaner.db

# PostgreSQL (Production)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# MySQL (Production)
DATABASE_URL=mysql+aiomysql://user:password@host:3306/database
```

## Schema Diagram

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ email           │
│ password_hash   │
│ role            │
│ google_id       │
│ github_id       │
│ storage_used    │
│ created_at      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐  ┌──▼──────┐
│projects│  │ agents  │
├────────┤  ├─────────┤
│id (PK) │  │ id (PK) │
│user_id │  │ user_id │
│name    │  │ name    │
│...     │  │ provider│
└───┬────┘  │ ...     │
    │       └─────────┘
    │
┌───▼────┐
│datasets│
├────────┤
│id (PK) │
│proj_id │
│data    │
│schema  │
└───┬────┘
    │
┌───▼──────────┐
│operation_hist│
├──────────────┤
│id (PK)       │
│project_id    │
│dataset_id    │
│operation_type│
│snapshots     │
└──────────────┘
```

## Tables

### users

User accounts and authentication.

```sql
CREATE TABLE users (
    id                  VARCHAR(36) PRIMARY KEY,
    email               VARCHAR(255) UNIQUE NOT NULL,
    password_hash       VARCHAR(255),
    name                VARCHAR(255),
    avatar_url          VARCHAR(500),
    role                VARCHAR(20) DEFAULT 'user',
    google_id           VARCHAR(255) UNIQUE,
    github_id           VARCHAR(255) UNIQUE,
    storage_used_bytes  BIGINT DEFAULT 0,
    api_calls_this_month INT DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at       TIMESTAMP,
    is_active           BOOLEAN DEFAULT TRUE,
    is_verified         BOOLEAN DEFAULT FALSE,
    timezone            VARCHAR(50)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | VARCHAR(255) | Unique email address |
| `password_hash` | VARCHAR(255) | Bcrypt hashed password |
| `name` | VARCHAR(255) | Display name |
| `avatar_url` | VARCHAR(500) | Profile picture URL |
| `role` | ENUM | admin, manager, user |
| `google_id` | VARCHAR(255) | Google OAuth ID |
| `github_id` | VARCHAR(255) | GitHub OAuth ID |
| `storage_used_bytes` | BIGINT | Storage tracking |
| `api_calls_this_month` | INT | Rate limit tracking |
| `created_at` | TIMESTAMP | Account creation |
| `updated_at` | TIMESTAMP | Last update |
| `last_login_at` | TIMESTAMP | Last login time |
| `is_active` | BOOLEAN | Account status |
| `is_verified` | BOOLEAN | Email verified |
| `timezone` | VARCHAR(50) | User timezone |

### projects

User projects (workspaces).

```sql
CREATE TABLE projects (
    id              VARCHAR(36) PRIMARY KEY,
    user_id         VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    row_count       INTEGER DEFAULT 0,
    column_count    INTEGER DEFAULT 0,
    storage_bytes   BIGINT DEFAULT 0,
    schema_json     JSON,
    is_saved        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_user_id ON projects(user_id);
```

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key to users |
| `name` | VARCHAR(255) | Project name |
| `description` | TEXT | Project description |
| `row_count` | INTEGER | Total rows in datasets |
| `column_count` | INTEGER | Total columns |
| `storage_bytes` | BIGINT | Storage used |
| `schema_json` | JSON | Dataset schema |
| `is_saved` | BOOLEAN | Persisted flag |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update |

### datasets

Dataset data and metadata.

```sql
CREATE TABLE datasets (
    id              VARCHAR(36) PRIMARY KEY,
    project_id      VARCHAR(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name            VARCHAR(255),
    description     TEXT,
    file_name       VARCHAR(255),
    file_size       INTEGER DEFAULT 0,
    file_type       VARCHAR(50),
    row_count       INTEGER DEFAULT 0,
    columns         JSON,
    preview_data    JSON,
    data_json       JSON,
    schema_json     JSON,
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_datasets_project_id ON datasets(project_id);
```

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `project_id` | UUID | Foreign key to projects |
| `name` | VARCHAR(255) | Dataset name |
| `description` | TEXT | Dataset description |
| `file_name` | VARCHAR(255) | Original file name |
| `file_size` | INTEGER | File size in bytes |
| `file_type` | VARCHAR(50) | File type (csv, xlsx, json) |
| `row_count` | INTEGER | Number of rows |
| `columns` | JSON | Column metadata |
| `preview_data` | JSON | Preview rows |
| `data_json` | JSON | Serialized DataFrame |
| `schema_json` | JSON | Column schema |
| `version` | INTEGER | Version number |
| `created_at` | TIMESTAMP | Creation time |

### agents

AI agent configurations.

```sql
CREATE TABLE agents (
    id              VARCHAR(36) PRIMARY KEY,
    user_id         VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    provider        VARCHAR(50) DEFAULT 'openai',
    model           VARCHAR(100) DEFAULT 'gpt-4o-mini',
    system_prompt   TEXT,
    prompt_template TEXT,
    api_key         TEXT,
    base_url        VARCHAR(500),
    temperature     FLOAT DEFAULT 0.3,
    is_template     BOOLEAN DEFAULT FALSE,
    is_builtin      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agents_user_id ON agents(user_id);
CREATE INDEX idx_agents_provider ON agents(provider);
```

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key to users |
| `name` | VARCHAR(255) | Agent name |
| `description` | TEXT | Agent description |
| `provider` | VARCHAR(50) | AI provider |
| `model` | VARCHAR(100) | Model name |
| `system_prompt` | TEXT | System instructions |
| `prompt_template` | TEXT | Prompt template |
| `api_key` | TEXT | API credentials |
| `base_url` | VARCHAR(500) | Custom endpoint |
| `temperature` | FLOAT | Sampling temperature |
| `is_template` | BOOLEAN | Template flag |
| `is_builtin` | BOOLEAN | Built-in flag |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update |

### operation_history

Operation history for undo/redo.

```sql
CREATE TABLE operation_history (
    id              VARCHAR(36) PRIMARY KEY,
    project_id      VARCHAR(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    dataset_id      VARCHAR(36) REFERENCES datasets(id) ON DELETE CASCADE,
    operation_type  VARCHAR(50) NOT NULL,
    operation_name  VARCHAR(100) NOT NULL,
    operation_config JSON,
    operation_params JSON,
    is_undone       BOOLEAN DEFAULT FALSE,
    is_applied      BOOLEAN DEFAULT TRUE,
    before_snapshot JSON,
    after_snapshot  JSON,
    columns_affected JSON,
    snapshot_json   JSON,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operation_history_project_id ON operation_history(project_id);
CREATE INDEX idx_operation_history_dataset_id ON operation_history(dataset_id);
CREATE INDEX idx_operation_history_created_at ON operation_history(created_at);
```

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `project_id` | UUID | Foreign key to projects |
| `dataset_id` | UUID | Foreign key to datasets |
| `operation_type` | VARCHAR(50) | Operation category |
| `operation_name` | VARCHAR(100) | Specific operation |
| `operation_config` | JSON | Operation configuration |
| `operation_params` | JSON | Operation parameters |
| `is_undone` | BOOLEAN | Undo status |
| `is_applied` | BOOLEAN | Apply status |
| `before_snapshot` | JSON | Before state |
| `after_snapshot` | JSON | After state |
| `columns_affected` | JSON | Affected columns |
| `snapshot_json` | JSON | Full snapshot |
| `created_at` | TIMESTAMP | Operation time |

## SQLAlchemy Models

### User Model

```python
# db/models/user.py
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False),
        default=UserRole.USER,
        nullable=False
    )
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    github_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    storage_used_bytes: Mapped[int] = mapped_column(default=0)
    api_calls_this_month: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")

    @property
    def tier_limits(self) -> dict:
        """Get tier limits based on role."""
        role_value = self.role.value if hasattr(self.role, 'value') else str(self.role)
        
        if role_value == 'admin':
            return {
                "max_projects": -1,
                "max_rows": 1_000_000,
                "max_storage_mb": 5000,
                "history_size": 500,
                "collaboration": True,
            }
        elif role_value == 'manager':
            return {
                "max_projects": 50,
                "max_rows": 200_000,
                "max_storage_mb": 500,
                "history_size": 200,
                "collaboration": True,
            }
        else:  # user
            return {
                "max_projects": 1,
                "max_rows": 1_000,
                "max_storage_mb": 5,
                "history_size": 10,
                "collaboration": False,
            }
```

### Project Model

```python
# db/models/project.py
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    column_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    schema_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_saved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    operations = relationship("OperationHistory", back_populates="project", cascade="all, delete-orphan")
```

### Dataset Model

```python
# db/models/project.py
class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    columns: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    preview_data: Mapped[list | None] = mapped_column(JSON, nullable=True)
    data_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    schema_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="datasets")
```

### Agent Model

```python
# db/models/agent.py
class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(50), default="openai")
    model: Mapped[str] = mapped_column(String(100), default="gpt-4o-mini")
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.3)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="agents")
```

### OperationHistory Model

```python
# db/models/project.py
class OperationHistory(Base):
    __tablename__ = "operation_history"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=True, index=True
    )
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    operation_name: Mapped[str] = mapped_column(String(100), nullable=False)
    operation_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    operation_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_undone: Mapped[bool] = mapped_column(Boolean, default=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, default=True)
    before_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    columns_affected: Mapped[list | None] = mapped_column(JSON, nullable=True)
    snapshot_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    project = relationship("Project", back_populates="operations")
```

## Database Migrations

### Alembic Configuration

Migrations are managed with Alembic:

```bash
# Initialize Alembic (already done)
alembic init alembic

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Migration Scripts

Located in `alembic/versions/`:

```python
"""create users table

Revision ID: abc123
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        # ... other columns
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
```

## Data Storage Strategy

### Working Data (In-Memory)

During active sessions:
- Data stored in pandas DataFrame
- Fast operations and previews
- Lost on session end (not committed)

### Persisted Data (Database)

After commit:
- Serialized to JSON
- Stored in `datasets.data_json`
- Schema stored in `datasets.schema_json`
- Preserved across sessions

### Serialization Format

```python
# DataFrame to JSON
data_dict = {
    "columns": list(df.columns),
    "data": df.values.tolist(),
    "types": {col: str(dtype) for col, dtype in df.dtypes.items()}
}

# JSON to DataFrame
df = pd.DataFrame(
    data=data["data"],
    columns=data["columns"]
).astype(data["types"])
```

## Query Examples

### Get User's Projects

```python
from sqlalchemy import select

stmt = select(Project).where(Project.user_id == user_id)
result = await session.execute(stmt)
projects = result.scalars().all()
```

### Get Dataset with Project

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

stmt = (
    select(Dataset)
    .options(selectinload(Dataset.project))
    .where(Dataset.id == dataset_id)
)
result = await session.execute(stmt)
dataset = result.scalar_one_or_none()
```

### Get Operation History

```python
from sqlalchemy import select, desc

stmt = (
    select(OperationHistory)
    .where(OperationHistory.project_id == project_id)
    .order_by(desc(OperationHistory.created_at))
    .limit(10)
)
result = await session.execute(stmt)
operations = result.scalars().all()
```

## Performance Considerations

### Indexing

Key indexes for performance:
- `users.email` - Login lookups
- `projects.user_id` - User's projects
- `datasets.project_id` - Project's datasets
- `operation_history.project_id` - History queries
- `operation_history.created_at` - Recent operations

### Connection Pooling

```python
# Configuration in config.py
db_pool_size: int = 10
db_max_overflow: int = 20
db_pool_timeout: int = 30
db_pool_recycle: int = 3600
```

### Query Optimization

1. **Use eager loading** - `selectinload()` for relationships
2. **Limit results** - Always paginate large queries
3. **Avoid N+1** - Load related data in single query
4. **Use indexes** - Query on indexed columns

## Backup & Recovery

### Backup

```bash
# PostgreSQL
pg_dump -U user database_name > backup.sql

# MySQL
mysqldump -u user -p database_name > backup.sql

# SQLite
cp master_data_cleaner.db backup.db
```

### Restore

```bash
# PostgreSQL
psql -U user database_name < backup.sql

# MySQL
mysql -u user -p database_name < backup.sql

# SQLite
cp backup.db master_data_cleaner.db
```

## Next Steps

- **[Backend](../backend/README.md)** - Backend service details
- **[API Reference](../api-reference/README.md)** - API documentation
- **[Architecture](../architecture/README.md)** - System architecture

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
