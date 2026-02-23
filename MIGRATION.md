# Migration Plan: Hono → FastAPI

## Overview
Migrate the backend from Hono (Node.js/TypeScript) to FastAPI (Python) while keeping the Vue 3 frontend.

## Current State
- Frontend: Vue 3 + Pinia + Vue Router
- Backend: Hono (minimal - health check only)
- Build: Vite + pnpm

## Target State
- Frontend: Vue 3 (unchanged)
- Backend: FastAPI + Python
- Data processing: pandas/polars
- AI: LangChain with multi-provider support
- Tests: pytest

---

## Phase 1: Python Setup ✅
- [x] Create Python virtual environment
- [x] Install FastAPI + dependencies
- [x] Create `backend/` structure
- [x] Set up pytest

## Phase 2: Basic FastAPI Server ✅
- [x] Create FastAPI app with CORS for Vue frontend
- [x] Implement `/health` endpoint (port existing)
- [x] Add API router structure
- [x] Test with pytest

## Phase 3: AI Integration ✅
- [x] Install LangChain + provider packages
- [x] Create AI provider factory (multi-provider support)
- [x] Create data cleaning assistant service
- [x] Add AI endpoints (analyze, suggest-fix, generate-code, chat)
- [x] Support providers: OpenAI, Anthropic, Google, Ollama, Groq, DeepSeek, OpenRouter

## Phase 4: Frontend Integration ✅
- [x] Update Vite proxy config for FastAPI backend
- [x] Remove Hono dev server plugin

## Phase 5: Data Processing Features (TODO)
- [ ] File upload endpoint (CSV, Excel, JSON)
- [ ] Data preview endpoint
- [ ] Data cleaning operations
- [ ] Export endpoint

## Phase 6: Cleanup (TODO)
- [ ] Remove Hono/Node backend code
- [ ] Update package.json scripts
- [ ] Update README

---

## Project Structure (Current)

```
MasterDataCleaner/
├── backend/                # Python FastAPI ✅
│   ├── .venv/              # Python virtual env
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── config.py       # Settings
│   │   ├── routers/
│   │   │   ├── health.py   # Health check
│   │   │   └── ai.py       # AI endpoints
│   │   ├── services/
│   │   │   ├── ai_provider.py  # Multi-provider factory
│   │   │   └── cleaner.py      # Data cleaning assistant
│   │   └── models/
│   │       └── schemas.py  # Pydantic models
│   ├── tests/
│   │   ├── test_health.py
│   │   └── test_ai.py
│   ├── requirements.txt
│   └── pytest.ini
├── src/                    # Vue frontend
├── dist/                   # Vite build output
├── package.json
├── vite.config.ts          # Updated with FastAPI proxy
└── README.md
```

---

## Commands

### Python Backend
```bash
cd backend
. .venv/bin/activate        # Activate venv
uvicorn app.main:app --reload --port 8000
pytest                      # Run tests
```

### Frontend
```bash
pnpm install
pnpm dev        # Development (proxies /api to FastAPI)
pnpm build      # Production build
```

### Run Both (Development)
```bash
# Terminal 1: Backend
cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
pnpm dev
```

---

## AI Providers

| Provider | Package | Env Variable | Default Model |
|----------|---------|--------------|---------------|
| OpenAI | `langchain-openai` | `OPENAI_API_KEY` | gpt-4o-mini |
| Anthropic | `langchain-anthropic` | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Google | `langchain-google-genai` | `GOOGLE_API_KEY` | gemini-2.0-flash |
| Ollama | `langchain-ollama` | (local) | llama3.2 |
| Groq | `langchain-groq` | `GROQ_API_KEY` | llama-3.3-70b-versatile |
| DeepSeek | `langchain-deepseek` | `DEEPSEEK_API_KEY` | deepseek-chat |
| OpenRouter | `langchain-openrouter` | `OPENROUTER_API_KEY` | openai/gpt-4o-mini |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/ai/providers` | List AI providers |
| POST | `/api/ai/analyze` | Analyze data, get recommendations |
| POST | `/api/ai/suggest-fix` | Get fix suggestions |
| POST | `/api/ai/generate-code` | Generate cleaning code |
| POST | `/api/ai/chat` | Chat with assistant |

