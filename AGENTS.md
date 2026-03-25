# AI Agent Guidelines - MasterDataCleaner

Follow these guidelines when working on this project.

---

## General Rules

- **No third-party libraries** - Use only provided dependencies unless absolutely required
- **Exact versions** - Use the exact versions specified in `package.json` and `requirements.txt`
- **Coding standards** - Follow established coding standards and best practices
- **Clean code** - Write clean, readable, and maintainable code
- **Reuse code** - Reuse existing code whenever possible
- **Keep this file updated** - If you make changes that affect this document (new routers, models, structure, etc.), update the relevant sections in `AGENTS.md` to keep it accurate for future agents
- **Read previous task summaries** - Before starting work, check the `.memory/` directory for task summaries from previous sessions to understand context and avoid duplicating work

---

## Project Rules

1. **Output only code** - No explanations unless explicitly asked
2. **Use existing code** - Maximize reuse of existing implementations
3. **No explanations** - Don't explain what you're doing unless asked
4. **Use pnpm** - Always use `pnpm` (not `npm`) for all frontend package operations
5. **Don't run servers** - User runs both frontend/backend via `pnpm`; you don't need to
6. **Be brief** - Focus on the task, avoid detailed explanations
7. **Migrations exist** - Alembic migrations are in `backend/alembic/`; auto-run on startup
8. **No assumptions** - Look up code or ask; never assume what's available
9. **Ask before installing** - Never install packages without permission
10. **Testing**:
    - **Frontend**: Vitest (`pnpm test:frontend`)
    - **Backend**: pytest (`pnpm test:backend`)
    - **E2E**: Cypress (`pnpm test:e2e`)
11. **Check dependencies** - Review `package.json` or `requirements.txt` before using any library
12. **Use existing venv** - Always use the existing virtual environment at `backend/.venv/` when running Python commands or modules (e.g., `backend/.venv/bin/python`, `backend/.venv/bin/pip`)

---

## Project Overview

**MasterDataCleaner** is an AI-guided data cleaning platform.

| Component | Technology |
|-----------|------------|
| **Frontend** | Vue 3 + TypeScript + BootstrapVueNext + Pinia + Vue Router |
| **Backend** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL / MySQL / SQLite (dev) via SQLAlchemy |
| **AI** | LangChain (multi-provider) |
| **Data Processing** | pandas, polars |

---

## Project Structure

```
MasterDataCleaner/
├── backend/                 # Python FastAPI backend
│   ├── .venv/               # Python virtual environment
│   ├── alembic/             # Database migrations
│   ├── app/
│   │   ├── main.py          # App entry point
│   │   ├── config.py        # Settings
│   │   ├── routers/         # API endpoints (multiple routers)
│   │   ├── services/        # Business logic (AI, cleaner, importer)
│   │   ├── db/              # Database layer (models, connection)
│   │   └── models/          # Pydantic schemas
│   ├── tests/               # pytest tests
│   └── requirements.txt     # Python dependencies
│
├── src/                     # Vue.js frontend
│   ├── components/          # Reusable components
│   ├── views/               # Page components
│   ├── composables/         # Composable functions
│   ├── stores/              # Pinia stores
│   ├── utils/               # Utilities
│   └── router.ts            # Routes
│
├── docs/                    # 📚 Project documentation
├── package.json             # Frontend dependencies
└── pnpm-lock.yaml
```

---

## Documentation References

**Read the [`./docs`](./docs/) directory for comprehensive documentation covering all aspects of the project.**

| Topic | Document | Description |
|-------|----------|-------------|
| **Overview** | [`docs/overview/`](docs/overview/README.md) | What is MasterDataCleaner, use cases |
| **Getting Started** | [`docs/getting-started/`](docs/getting-started/README.md) | Installation, setup, first steps |
| **Quick Start** | [`docs/getting-started/quick-start.md`](docs/getting-started/quick-start.md) | 5-minute setup guide |
| **Features** | [`docs/features/`](docs/features/README.md) | Complete feature overview |
| **AI Providers** | [`docs/features/ai-providers.md`](docs/features/ai-providers.md) | AI configuration & comparison |
| **Data Operations** | [`docs/features/data-operations.md`](docs/features/data-operations.md) | All data transformations |
| **Architecture** | [`docs/architecture/`](docs/architecture/README.md) | System design, data flow, tech stack |
| **Frontend** | [`docs/frontend/`](docs/frontend/README.md) | Vue components, routing, state management |
| **Backend** | [`docs/backend/`](docs/backend/README.md) | FastAPI routers, services, database layer |
| **Database** | [`docs/database/`](docs/database/README.md) | Schema, models, migrations |
| **API Reference** | [`docs/api-reference/`](docs/api-reference/README.md) | All API endpoints |
| **Deployment** | [`docs/deployment/`](docs/deployment/README.md) | Docker, cloud, server deployment |
| **Guides** | [`docs/guides/`](docs/guides/README.md) | Step-by-step user guides |

---

## Development Commands

```bash
# Install dependencies
pnpm install

# Development (frontend)
pnpm dev

# Backend (user runs this)
pnpm backend

# Run tests
pnpm test:backend         # Backend pytest
pnpm test:backend:coverage  # With coverage
pnpm test:frontend        # Frontend Vitest
pnpm test:e2e             # Cypress E2E
pnpm test                 # Type check + build + backend tests

# Build
pnpm build

# Type check
pnpm exec vue-tsc --noEmit

# Clean
pnpm clean                # Remove dist
pnpm clean:all            # Remove dist, node_modules, .venv
```

---

## Coding Conventions

### Frontend (Vue 3 + TypeScript)

- Use `<script setup>` syntax
- Prefer composables over mixins
- Use Pinia for state management
- BootstrapVueNext components for UI
- TypeScript for type safety
- JSDoc for complex functions

**Example:**
```vue
<script setup>
import { ref, computed } from 'vue'
import { useToast } from '@/composables/useToast'

const { success, error } = useToast()
const data = ref([])
</script>
```

### Backend (Python 3.11+)

- Use type hints
- Follow FastAPI patterns
- Async/await for database operations
- Pydantic models for validation
- SQLAlchemy for ORM
- Docstrings for functions

**Example:**
```python
from fastapi import APIRouter
from sqlalchemy import select

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### Testing

| Framework | Command | Location |
|-----------|---------|----------|
| **pytest** | `pnpm test:backend` | `backend/tests/` |
| **Vitest** | `pnpm test:frontend` | `src/**/*.test.ts` |
| **Cypress** | `pnpm test:e2e` | `cypress/` |

---

## Key Files

| File | Purpose |
|------|---------|
| [`package.json`](package.json) | Frontend dependencies & scripts |
| [`backend/requirements.txt`](backend/requirements.txt) | Python dependencies |
| [`src/router.ts`](src/router.ts) | Frontend routes |
| [`backend/app/main.py`](backend/app/main.py) | Backend app entry |
| [`vite.config.ts`](vite.config.ts) | Vite configuration |
| [`tsconfig.json`](tsconfig.json) | TypeScript config |
| [`vitest.config.js`](vitest.config.js) | Vitest configuration |
| [`cypress.config.js`](cypress.config.js) | Cypress configuration |

---

## AI Integration

**Supported Providers:** OpenAI, Anthropic, Google, Ollama, Groq, DeepSeek, OpenRouter, Hugging Face (via LangChain)

**Key Files:**
- [`backend/app/services/ai_provider.py`](backend/app/services/ai_provider.py) - Provider factory
- [`backend/app/services/cleaner.py`](backend/app/services/cleaner.py) - Data cleaning assistant
- [`backend/app/routers/ai.py`](backend/app/routers/ai.py) - AI endpoints
- [`backend/app/routers/ai_operations.py`](backend/app/routers/ai_operations.py) - AI-powered operations
- [`backend/app/routers/assistant.py`](backend/app/routers/assistant.py) - Assistant wizard

**Configuration:** API keys in `backend/.env` or per-agent

**Default Models:**
- OpenAI: `gpt-4o-mini`
- Anthropic: `claude-sonnet-4-20250514`
- Google: `gemini-2.0-flash`
- Ollama: `llama3.2`
- Groq: `llama-3.3-70b-versatile`

---

## Database

**Models Location:** [`backend/app/db/models/`](backend/app/db/models/)

| Model | File | Description |
|-------|------|-------------|
| **User** | `user.py` | Authentication, roles (admin/manager/user), OAuth |
| **Project** | `project.py` | User projects/workspace |
| **Dataset** | `project.py` | Dataset data and metadata |
| **OperationHistory** | `project.py` | Undo/redo functionality |
| **Agent** | `agent.py` | AI agent configurations |

**Migrations:** [`backend/alembic/`](backend/alembic/) - Auto-run on startup via lifespan events

**Connection:** Async SQLAlchemy with connection pooling

---

## API Routers

Multiple routers organized by feature in [`backend/app/routers/`](backend/app/routers/):

| Router | Prefix | Purpose |
|--------|--------|---------|
| `health` | `/api/health` | Health check |
| `auth` | `/api/auth` | Authentication (login, register, OAuth) |
| `users` | `/api/users` | User CRUD |
| `projects` | `/api/projects` | Project CRUD |
| `datasets` | `/api/datasets` | Dataset import/export/preview |
| `operations*` | `/api/operations` | Data operations (core, extra, structural, cell, datetime, missing values, batch, undo/redo) |
| `agents` | `/api/agents` | Agent CRUD |
| `ai*` | `/api/ai` and `/api/operations` | AI endpoints and operations |
| `assistant` | `/api/assistant` | Assistant wizard |
| `profiling` | `/api/profiling` | Column profiling |
| `comparison` | `/api/comparison` | Before/after comparison |
| `notifications` | `/api/notifications` | Notification system |
| `rate_limit` | `/api/rate-limit` | Rate limit status |

*Multiple routers share the same prefix for organized code structure.

---

## Important Notes

- **Auto-generated files**: `components.d.ts` is generated by `unplugin-vue-components` (do not edit manually)
- **Environment**: Check `backend/.env` and `.env.sample` for configuration
- **Debug mode**: Auto-login enabled in development via router guard
- **Admin creation**: First user becomes admin (or use `ADMIN_USER`/`ADMIN_PASSWORD` env vars on startup)
- **Virtual environment**: Backend uses `.venv/` in the backend directory
- **Database auto-init**: Tables created/migrated automatically on startup

---

## Quick Reference

**Need to:**

| Task | Look Here |
|------|-----------|
| Add API endpoint | `backend/app/routers/` |
| Add Vue component | `src/components/` |
| Add database model | `backend/app/db/models/` |
| Add data operation | `backend/app/routers/operations*.py` |
| Configure AI | `backend/app/services/ai_provider.py` |
| Add route | `src/router.ts` |
| Add backend test | `backend/tests/` |
| Add migration | `backend/alembic/versions/` |
| View API docs | `http://localhost:8000/docs` |
| View project docs | [`docs/`](docs/) directory |

---

## Previous Task Memory

**Location:** `.memory/` directory

Before starting new work, check `.memory/` for summaries of previous tasks to understand:
- What issues were previously addressed
- What solutions were applied
- Any remaining TODOs or follow-up items

**Structure:**
```
.memory/
├── <task-name>/
│   └── summary.md    # Summary of the task, problems, solutions, and results
```

**How to use:**
1. List `.memory/` to see previous task directories
2. Read `summary.md` files to understand what was done
3. Use this context to avoid duplicating work and build on previous solutions

---

## Testing Details

### Backend Tests (pytest)

```bash
# Run all tests
pnpm test:backend

# Run with coverage
pnpm test:backend:coverage

# Run specific test file
cd backend && . .venv/bin/activate && pytest tests/test_health.py -v
```

**Test files:** Multiple test files covering routes, models, operations, AI, auth, etc.

### Frontend Tests (Vitest)

```bash
pnpm test:frontend
```

**Config:** [`vitest.config.js`](vitest.config.js)

### E2E Tests (Cypress)

```bash
pnpm test:e2e
```

**Config:** [`cypress.config.js`](cypress.config.js)

---

*For detailed documentation, see the [`docs/`](docs/) directory.*
