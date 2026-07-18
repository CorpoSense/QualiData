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
- **Prevent bad changes** - If the user asks to perform a catastrophic changes to the project or a very bad idea, just warn the user before doing it and tell him why it's a bad idea to do so.

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
12. **Use existing venv** - Always use the existing virtual environment at `backend/.venv/` when running Python commands or modules (e.g., `backend/.venv/bin/python`, `backend/.venv/bin/pip`, `backend/.venv/bin/pytest`...etc.)
13. **No inline imports** - Newer write inline import (like: `await import()`, `import("pkg").Type`, dynamic type imports), write Top-level imports only when needed.
14. **Frontend tests files** - Always place frontend test files in `tests` directory, never place them in `src` directory. Component tests go in `tests/unit/components/`.

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

**The [`./docs`](./docs/) directory contains comprehensive documentation. Search with `grep` command to find relevant files efficiently instead of reading the entire directory.**

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

**Search Strategy:**
- Use `grep_search` with keywords (e.g., "router", "model", "endpoint") to locate relevant documentation
- Use `glob` with patterns like `**/api*.md` or `**/database*.md` to find specific files
- Only read the specific file(s) you need, not the entire `docs/` directory

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

**Supported Providers:** OpenAI, Anthropic, Google, Ollama, Groq, NVIDIA, DeepSeek, OpenRouter, Hugging Face (via LangChain)

**Key Files:**
- [`backend/app/services/ai_provider.py`](backend/app/services/ai_provider.py) - Provider factory
- [`backend/app/services/cleaner.py`](backend/app/services/cleaner.py) - Data cleaning assistant
- [`backend/app/services/agent_factory.py`](backend/app/services/agent_factory.py) - LangGraph agent factory with memory middleware
- [`backend/app/routers/ai.py`](backend/app/routers/ai.py) - AI endpoints (chat, analyze, suggest-fix, generate-code)
- [`backend/app/routers/ai_operations.py`](backend/app/routers/ai_operations.py) - AI-powered operations
- [`backend/app/routers/assistant.py`](backend/app/routers/assistant.py) - Assistant wizard
- [`src/components/AiChatModal.vue`](src/components/AiChatModal.vue) - AI Chat modal (DataViewer)

**AI Chat Feature:**
- Full chat interface in DataViewer via "AI Chat" button
- User selects an AI Agent to chat with
- Dataset context (columns + N sample rows) injected into system prompt
- Multi-turn conversations with history sent to backend
- Chat sessions stored in localStorage (`ai-chat-sessions`)
- Text-to-speech via Web Speech API (toggle button)
- Markdown rendering for AI responses (code blocks, tables, lists)
- Backend endpoint: `POST /api/ai/chat` with `conversation_history`, `dataset_id`, `dataset_context_rows`, `conversation_id`, `doc_id`
- Document upload for RAG-based Q&A (when agent has Doc KB enabled)
- Future: function calling for data operations

**Agent Memory Feature:**
- Optional memory management for long conversations (Advanced tab in Agent Manager)
- When `memory_config` is set on an agent, chat uses LangGraph agent with middleware + InMemorySaver
- When `memory_config` is null (default), chat uses legacy stateless path (llm.ainvoke)
- Memory strategies: `sliding_window` (removes oldest messages), `summarizer` (condenses old messages), `trim_tokens` (keeps only recent messages)
- `conversation_id` in ChatRequest maps to LangGraph `thread_id` for server-side checkpointing
- Agent instances are cached per agent_id; cache invalidated when memory_config changes
- **Limitation (v1):** InMemorySaver is volatile — conversation state is lost on backend restart
- **Future (Phase 4):** Replace InMemorySaver with PostgresSaver for persistent checkpointing

**Configuration:** API keys in `backend/.env` or per-agent

**Integrations — Search Engines:**
- Users can configure search engines in the Integrations page (`/integrations`)
- Search engines are optionally attached to AI Agents (Advanced tab in Agent Manager)
- When an agent has a search engine, the AI chat uses LangGraph agent with search tools
- Search-aware system prompt is used when agent has search engine (unless custom system prompt is set)
- API keys for search engines are encrypted at rest (same pattern as agent API keys)

**Integrations — Document Knowledge Base (RAG):**
- Users can enable Document KB per agent (Advanced tab in Agent Manager)
- When enabled, users can upload documents (PDF, TXT, CSV, MD) in AI Chat for RAG-based Q&A
- Documents are loaded → split into chunks → embedded → stored in ChromaDB → retriever tool attached to agent
- Embedding provider/model is configurable per agent (separate from the LLM provider)
- `embedding_api_key` is encrypted at rest; falls back to agent's main API key if not set
- When `doc_id` is present in chat request, a fresh (non-cached) agent is created with the document retriever tool
- Doc-aware system prompt is used when document is attached (unless custom system prompt is set)
- Document files are stored locally with TTL-based cleanup; Document records track status/chunks/expiry

**Environment Variables:**
- `DOC_STORAGE_PATH` — Directory for uploaded document files (default: `./doc_storage`)
- `DOC_MAX_FILE_SIZE_MB` — Max upload file size in MB (default: `50`)
- `DOC_CLEANUP_TTL_SECONDS` — Document file TTL in seconds (default: `86400`)

---

## Database

**Models Location:** [`backend/app/db/models/`](backend/app/db/models/)

| Model | File | Description |
|-------|------|-------------|
| **User** | `user.py` | Authentication, roles (admin/manager/user), OAuth |
| **Project** | `project.py` | User projects/workspace |
| **Dataset** | `project.py` | Dataset data and metadata |
| **OperationHistory** | `project.py` | Undo/redo functionality |
| **Agent** | `agent.py` | AI agent configurations (includes `doc_kb_config` JSON column) |
| **SearchEngine** | `search_engine.py` | Search engine integrations (web search for agents) |
| **Document** | `document.py` | Uploaded documents for RAG (status, chunks, expiry) |

**Migrations:** [`backend/alembic/`](backend/alembic/) - Auto-run on startup via lifespan events

**Connection:** Async SQLAlchemy with connection pooling

**Data Storage:**
- `datasets.preview_data`: JSON array with ~500 rows for display (limited preview)
- `datasets.data_json`: Full dataset as `{"data": [...], "charts": [...]}` for complete data access
- The `charts` key stores chart configurations (config + meta) — chart data is computed on load, not stored
- Charts are managed via `GET /api/datasets/{id}/charts` (read) and `PUT /api/datasets/{id}/charts` (replace entire array)
- **Always update BOTH fields** when modifying data - use `get_preview_data()` and `get_full_data_json()` from `app/routers/datasets.py`

---

## API Routers

Multiple routers organized by feature in [`backend/app/routers/`](backend/app/routers/):

| Router | Prefix | Purpose |
|--------|--------|---------|
| `health` | `/api/health` | Health check |
| `auth` | `/api/auth` | Authentication (login, register, OAuth) |
| `users` | `/api/users` | User CRUD |
| `projects` | `/api/projects` | Project CRUD |
| `datasets` | `/api/datasets` | Dataset import/export/preview, charts (embedded in data_json) |
| `operations*` | `/api/operations` | Data operations (core, extra, structural, cell, datetime, missing values, batch, undo/redo, extract-json, extract-pattern, map-values) |
| `agents` | `/api/agents` | Agent CRUD |
| `search_engines` | `/api/search-engines` | Search engine CRUD & providers |
| `documents` | `/api/documents` | Document upload/CRUD, embedding provider catalog |
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
├── archived/          # Archived old/completed tasks (ignore unless necessary)
│   └── <task-name>/
│       └── summary.md
```

**How to use:**
1. List `.memory/` sorted by modification time: `ls -lt .memory/` to see task directories with most recent first
2. Focus on **recent tasks** (top of the list) for relevant context; older tasks are less likely to be relevant
3. Read `summary.md` files to understand what was done
4. Use this context to avoid duplicating work and build on previous solutions
5. **Ignore `archived/` subdirectory** unless explicitly instructed by the user or when investigating historical context is absolutely necessary

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
