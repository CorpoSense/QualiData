# Architecture

System architecture and design decisions for MasterDataCleaner.

## Overview

MasterDataCleaner follows a modern, three-tier architecture with clear separation of concerns:

```
┌─────────────────┐
│   Frontend      │  Vue 3 + TypeScript
│   (Client)      │  BootstrapVueNext
└────────┬────────┘
         │ HTTP/REST API
         ▼
┌─────────────────┐
│   Backend       │  FastAPI (Python)
│   (Server)      │  LangChain
└────────┬────────┘
         │ SQLAlchemy
         ▼
┌─────────────────┐
│   Database      │  PostgreSQL / MySQL
│   (Storage)     │  SQLite (dev)
└─────────────────┘
```

## Technology Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **Vue 3** | Reactive UI framework |
| **TypeScript** | Type safety |
| **Pinia** | State management |
| **Vue Router** | Client-side routing |
| **BootstrapVueNext** | UI components |
| **Vite** | Build tool and dev server |
| **Vitest** | Unit testing |
| **Cypress** | E2E testing |

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **Python 3.11+** | Runtime language |
| **SQLAlchemy** | ORM and database abstraction |
| **pandas** | Data manipulation |
| **polars** | High-performance data processing |
| **LangChain** | AI/LLM integration |
| **Pydantic** | Data validation |
| **Alembic** | Database migrations |
| **pytest** | Testing framework |

### Database

| Database | Use Case |
|----------|----------|
| **PostgreSQL** | Production (Supabase, NeonDB) |
| **MySQL** | Production (Aiven, Filess) |
| **SQLite** | Development and testing |

## System Components

### Frontend Architecture

```
src/
├── main.ts              # Application entry point
├── App.vue              # Root component
├── router.ts            # Route configuration
├── views/               # Page components
│   ├── Home.vue
│   ├── Dashboard.vue
│   ├── Projects.vue
│   ├── ProjectDetail.vue
│   ├── DataViewer.vue
│   ├── Assistant.vue
│   └── ...
├── components/          # Reusable components
│   ├── DataTable.vue
│   ├── ProjectCard.vue
│   ├── OperationConfirmModal.vue
│   └── ...
├── composables/         # Composable functions
│   ├── useUser.js       # User role utilities
│   └── useToast.js      # Notification system
├── stores/              # Pinia stores
│   └── debug.ts         # Debug state
├── utils/               # Utility functions
│   └── api.js           # API client
└── assets/              # Static assets
    └── style.css        # Global styles
```

#### State Management

Pinia stores manage global state:
- User authentication state
- Current project context
- Operation history
- UI state (modals, notifications)

#### Component Hierarchy

```
App.vue
├── Navigation
├── Router View
│   ├── Dashboard.vue
│   │   ├── StatCard (multiple)
│   │   ├── ProjectCard (multiple)
│   │   └── OperationItem (multiple)
│   ├── DataViewer.vue
│   │   ├── DataTable
│   │   ├── OperationConfirmModal
│   │   └── ProfilePanel
│   └── ...
└── ToastContainer
```

### Backend Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── rate_limit.py        # Rate limiting middleware
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── models/
│   │       ├── user.py      # User model
│   │       ├── project.py   # Project, Dataset, OperationHistory
│   │       └── agent.py     # Agent model
│   ├── routers/             # API route handlers
│   │   ├── auth.py          # Authentication
│   │   ├── users.py         # User management
│   │   ├── projects.py      # Project CRUD
│   │   ├── datasets.py      # Dataset operations
│   │   ├── operations.py    # Data operations
│   │   ├── agents.py        # Agent management
│   │   ├── ai.py            # AI endpoints
│   │   └── ...
│   ├── services/            # Business logic
│   │   ├── cleaner.py       # Data cleaning assistant
│   │   ├── ai_provider.py   # AI provider factory
│   │   └── smart_importer.py # Data import
│   └── models/              # Pydantic schemas
│       └── schemas.py       # Request/Response models
├── tests/                   # Test suite
└── requirements.txt         # Dependencies
```

#### API Structure

RESTful API design with clear resource separation:

| Router | Prefix | Purpose |
|--------|--------|---------|
| `auth` | `/api/auth` | Authentication and OAuth |
| `users` | `/api/users` | User management |
| `projects` | `/api/projects` | Project CRUD |
| `datasets` | `/api/datasets` | Dataset operations |
| `operations` | `/api/operations` | Data transformations |
| `agents` | `/api/agents` | AI agent management |
| `ai` | `/api/ai` | AI operations |
| `health` | `/api/health` | Health checks |

#### Service Layer

Business logic encapsulated in services:

**AI Provider Service** (`ai_provider.py`):
- Multi-provider factory pattern
- Model configuration
- Rate limit handling

**Cleaner Service** (`cleaner.py`):
- Data cleaning assistant
- Operation execution
- Preview generation

**Smart Importer** (`smart_importer.py`):
- File format detection
- Encoding detection
- Data validation

## Data Flow

### Import Flow

```
1. User uploads file / pastes data
2. Frontend sends to /api/datasets/import
3. Backend detects format and encoding
4. Data loaded into pandas DataFrame
5. Schema inferred and validated
6. Data stored in memory (working session)
7. Preview returned to frontend
8. User confirms → persisted to database
```

### Operation Flow

```
1. User selects columns and operation
2. Frontend sends operation request
3. Backend applies operation to DataFrame
4. Before/after snapshots created
5. Operation recorded in history
6. Preview returned to frontend
7. User commits → changes saved
   User cancels → rollback from snapshot
```

### AI Operation Flow

```
1. User selects AI agent and enters prompt
2. Frontend sends AI operation request
3. Backend prepares batch data
4. For each batch:
   a. Format prompt with data context
   b. Call AI provider API
   c. Parse structured response
   d. Apply transformations
5. Aggregate results
6. Return with confidence scores
7. User reviews and commits
```

## Database Schema

### Core Tables

#### Users
```sql
users (
  id              UUID PRIMARY KEY
  email           VARCHAR(255) UNIQUE
  password_hash   VARCHAR(255)
  name            VARCHAR(255)
  role            ENUM(admin, manager, user)
  google_id       VARCHAR(255)
  github_id       VARCHAR(255)
  storage_used_bytes  BIGINT
  api_calls_this_month INT
  created_at      TIMESTAMP
  updated_at      TIMESTAMP
  last_login_at   TIMESTAMP
  is_active       BOOLEAN
  is_verified     BOOLEAN
)
```

#### Projects
```sql
projects (
  id              UUID PRIMARY KEY
  user_id         UUID REFERENCES users(id)
  name            VARCHAR(255)
  description     TEXT
  row_count       INTEGER
  column_count    INTEGER
  storage_bytes   BIGINT
  schema_json     JSON
  is_saved        BOOLEAN
  created_at      TIMESTAMP
  updated_at      TIMESTAMP
)
```

#### Datasets
```sql
datasets (
  id              UUID PRIMARY KEY
  project_id      UUID REFERENCES projects(id)
  name            VARCHAR(255)
  description     TEXT
  file_name       VARCHAR(255)
  file_size       INTEGER
  file_type       VARCHAR(50)
  row_count       INTEGER
  columns         JSON
  preview_data    JSON
  data_json       JSON
  schema_json     JSON
  version         INTEGER
  created_at      TIMESTAMP
)
```

#### Agents
```sql
agents (
  id              UUID PRIMARY KEY
  user_id         UUID REFERENCES users(id)
  name            VARCHAR(255)
  description     TEXT
  provider        VARCHAR(50)
  model           VARCHAR(100)
  system_prompt   TEXT
  prompt_template TEXT
  api_key         TEXT
  base_url        VARCHAR(500)
  temperature     FLOAT
  is_template     BOOLEAN
  is_builtin      BOOLEAN
  created_at      TIMESTAMP
  updated_at      TIMESTAMP
)
```

#### Operation History
```sql
operation_history (
  id              UUID PRIMARY KEY
  project_id      UUID REFERENCES projects(id)
  dataset_id      UUID REFERENCES datasets(id)
  operation_type  VARCHAR(50)
  operation_name  VARCHAR(100)
  operation_config JSON
  operation_params JSON
  is_undone       BOOLEAN
  is_applied      BOOLEAN
  before_snapshot JSON
  after_snapshot  JSON
  columns_affected JSON
  snapshot_json   JSON
  created_at      TIMESTAMP
)
```

## Security Architecture

### Authentication

**JWT-based authentication:**
1. User logs in with credentials
2. Server validates and issues JWT token
3. Token included in Authorization header
4. Server validates token on each request
5. Token expires after configured duration

**OAuth integration:**
- Google OAuth 2.0
- GitHub OAuth
- Automatic account linking

### Authorization

**Role-based access control (RBAC):**
- **Admin** - Full system access
- **Manager** - Project and team management
- **User** - Basic data cleaning

**Row-level security:**
- Users can only access their own data
- Database queries filtered by user_id
- Project collaboration via explicit sharing

### Data Protection

**At rest:**
- Password hashing with bcrypt
- API keys encrypted in database
- Secure session storage

**In transit:**
- HTTPS/TLS for all communications
- CORS configuration for API access
- Input sanitization

## Performance Considerations

### Frontend

- **Lazy loading** - Routes loaded on demand
- **Component optimization** - Computed properties, memoization
- **Virtual scrolling** - Efficient large table rendering
- **Debounced search** - Reduce API calls

### Backend

- **Connection pooling** - Reuse database connections
- **Async operations** - Non-blocking I/O
- **Pagination** - Limit result set sizes
- **Caching** - Frequently accessed data

### Database

- **Indexing** - Foreign keys, frequent queries
- **Query optimization** - Avoid N+1 queries
- **Connection limits** - Pool size configuration

## Scalability

### Horizontal Scaling

- **Stateless API** - Any instance can handle any request
- **Session storage** - External Redis for sessions
- **Load balancing** - Distribute traffic across instances

### Vertical Scaling

- **Database** - Increase connection pool size
- **Memory** - Larger datasets in memory
- **CPU** - Parallel data processing

### Caching Strategy

- **Query results** - Cache frequent queries
- **AI responses** - Cache identical prompts
- **Static assets** - CDN for frontend files

## Monitoring & Observability

### Logging

- **Application logs** - Structured JSON logging
- **Access logs** - Request/response tracking
- **Error logs** - Exception tracking

### Metrics

- **API performance** - Response times
- **Database queries** - Query duration
- **AI operations** - Token usage, costs

### Error Handling

- **Global error handler** - Catch unhandled exceptions
- **User-friendly messages** - Clear error descriptions
- **Retry logic** - Automatic retries for transient failures

## Development Workflow

### Local Development

```
Developer Machine
├── Frontend (localhost:3000)
│   └── Hot reload on file changes
├── Backend (localhost:8000)
│   └── Auto-reload on code changes
└── Database (SQLite or Docker PostgreSQL)
```

### Testing

**Frontend:**
```bash
pnpm test:frontend    # Unit tests
pnpm test:e2e         # End-to-end tests
```

**Backend:**
```bash
pytest -v             # Run all tests
pytest --cov          # With coverage
```

### CI/CD

GitHub Actions workflow:
1. Lint check (ruff, black, vue-tsc)
2. Type checking
3. Unit tests
4. Integration tests
5. Build verification

## Deployment Architecture

### Single Instance

```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
┌────────▼────────┐
│   Application   │
│   (Frontend +   │
│    Backend)     │
└────────┬────────┘
         │
┌────────▼────────┐
│    Database     │
└─────────────────┘
```

### Multi-Instance

```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ App 1│  │ App 2 │
└───┬──┘  └──┬────┘
    │         │
    └────┬────┘
         │
┌────────▼────────┐
│    Database     │
└─────────────────┘
```

## Next Steps

- **[Frontend](../frontend/README.md)** - Vue.js application details
- **[Backend](../backend/README.md)** - FastAPI service details
- **[Database](../database/README.md)** - Database schema and models
- **[Deployment](../deployment/README.md)** - Deployment guides

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
