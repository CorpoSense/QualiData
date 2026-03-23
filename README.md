# MasterDataCleaner

**MasterDataCleaner** is an intelligent, step-by-step data cleaning solution designed for professional environments. It empowers users to transform messy, inconsistent data into structured, high-quality information through an AI-guided assistant.

## 🚀 Overview

In modern business environments, data often arrives in various formats and states of "cleanliness." MasterDataCleaner streamlines the data preparation process by providing a guided workflow that handles everything from ingestion to final export.

### Key Pillars:
- **Intelligent Guidance:** An AI assistant that understands your data structure and suggests cleaning steps.
- **Versatile Connectivity:** Support for local files, databases, and clipboard import.
- **Customizable Logic:** Powerful operations for complex data transformation rules.
- **Structured Output:** Export cleaned data to files or databases.

## 📚 Documentation

**Comprehensive documentation is available in the [`docs/`](docs/) directory:**

| Topic | Description |
|-------|-------------|
| **[Getting Started](docs/getting-started/README.md)** | Installation, setup, and quick start guide |
| **[Features](docs/features/README.md)** | Complete feature overview and capabilities |
| **[Architecture](docs/architecture/README.md)** | System architecture and design decisions |
| **[Frontend](docs/frontend/README.md)** | Vue.js frontend documentation |
| **[Backend](docs/backend/README.md)** | FastAPI backend documentation |
| **[Database](docs/database/README.md)** | Database schema and models |
| **[API Reference](docs/api-reference/README.md)** | Complete API endpoint documentation |
| **[Deployment](docs/deployment/README.md)** | Deployment guides for various platforms |
| **[Guides](docs/guides/README.md)** | Step-by-step user tutorials |

For AI agents and contributors, see **[AGENTS.md](AGENTS.md)** for project guidelines and coding standards.

## ✨ Features

### Data Import & Export
- **Import:** CSV, Excel (.xlsx, .xls), JSON, Database (PostgreSQL, MySQL), Clipboard
- **Export:** CSV, Excel, JSON, Database, Clipboard, Parquet (coming soon)
- **Auto-detection:** Delimiter, encoding, data types

### Data Operations
- **String Operations:** Trim, lowercase, uppercase, title case, find & replace, JSON extraction
- **Missing Values:** Fill (constant, mean, median, mode), forward/backward fill, drop rows
- **Date & Time:** Parse datetime, extract year/month/day/hour, format dates
- **Deduplication:** Exact match, fuzzy matching with similarity threshold
- **Structural:** Add/remove/rename columns, merge, split, clone, reorder
- **ML Operations:** One-Hot encoding, label encoding, value mapping, binning, scaling

### AI-Powered Features
- **AI Analysis:** Automatically detect data quality issues
- **AI Cleaning:** Transform data using natural language prompts
- **Batch Processing:** Process data in configurable batches with progress tracking
- **Multi-Provider Support:** OpenAI, Anthropic, Google, Ollama, Groq, DeepSeek, OpenRouter, HuggingFace
- **Custom Agents:** Create and configure reusable AI agents
- **Assistant Wizard:** Step-by-step guided cleaning workflow

### User Experience
- **Real-time Preview:** See changes before committing
- **Undo/Redo:** Full operation history with rollback capability
- **Before/After Comparison:** Side-by-side diff view
- **Column Profiling:** Automatic statistics and issue detection
- **In-place Editing:** Double-click cells to edit values
- **Search & Filter:** Find specific values across the dataset
- **Multi-select:** Select multiple rows/columns for batch operations

### User Management
- **Authentication:** Email/password, OAuth (Google, GitHub)
- **Roles:** Admin, Manager, User with tier-based permissions
- **Tier System:** Free, Pro, Enterprise with different limits

## 🛠 Tech Stack

### Frontend
- **Vue 3** with Composition API (`<script setup>`)
- **TypeScript** for type safety
- **Pinia** for state management
- **Vue Router** for navigation
- **BootstrapVueNext** for UI components
- **Vite** for build tooling
- **Vitest** for unit testing
- **Cypress** for E2E testing

### Backend
- **FastAPI** (Python 3.11+)
- **SQLAlchemy** (async) for ORM
- **pandas** & **polars** for data processing
- **LangChain** for AI integration
- **Pydantic** for data validation
- **Alembic** for database migrations
- **pytest** for testing

### Database
- **PostgreSQL** (production)
- **MySQL** (production)
- **SQLite** (development)

## 🤖 AI Providers

MasterDataCleaner supports multiple AI providers through LangChain:

| Provider | Default Model | Environment Variable |
|----------|---------------|---------------------|
| OpenAI | gpt-4o-mini | `OPENAI_API_KEY` |
| Anthropic | claude-sonnet-4-20250514 | `ANTHROPIC_API_KEY` |
| Google | gemini-2.0-flash | `GOOGLE_API_KEY` |
| Ollama | llama3.2 | (local, no key needed) |
| Groq | llama-3.3-70b-versatile | `GROQ_API_KEY` |
| DeepSeek | deepseek-chat | `DEEPSEEK_API_KEY` |
| OpenRouter | openai/gpt-4o-mini | `OPENROUTER_API_KEY` |
| HuggingFace | meta-llama/Llama-3.1-8B-Instruct | `HUGGINGFACE_API_KEY` |

See **[AI Providers](docs/features/ai-providers.md)** for detailed configuration and comparison.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm (`npm install -g pnpm`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bitsnaps/MasterDataCleaner.git
   cd MasterDataCleaner
   ```

2. **Set up the Python backend:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd ..
   pnpm install
   ```

4. **Configure environment (optional):**
   ```bash
   cd backend
   cp .env.sample .env
   # Edit .env with your settings
   ```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
pnpm dev
```

**Access:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Running Tests

```bash
# Backend tests
pnpm test:backend

# Frontend tests
pnpm test:frontend

# E2E tests
pnpm test:e2e

# All tests
pnpm test
```

## 📁 Project Structure

```
MasterDataCleaner/
├── backend/                    # Python FastAPI backend
│   ├── .venv/                  # Virtual environment
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── main.py             # Application entry
│   │   ├── config.py           # Configuration
│   │   ├── routers/            # API endpoints (23 routers)
│   │   ├── services/           # Business logic
│   │   ├── db/                 # Database layer
│   │   └── models/             # Pydantic schemas
│   ├── tests/                  # pytest tests
│   └── requirements.txt        # Python dependencies
│
├── src/                        # Vue.js frontend
│   ├── components/             # Reusable components
│   ├── views/                  # Page components
│   ├── composables/            # Composable functions
│   ├── stores/                 # Pinia stores
│   ├── utils/                  # Utilities
│   └── router.ts               # Routes
│
├── docs/                       # 📚 Documentation
├── cypress/                    # E2E tests
├── package.json                # Frontend dependencies
└── TODO.md                     # Task tracking
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Projects & Datasets
- `GET /api/projects` - List projects
- `POST /api/datasets/import` - Import data
- `GET /api/datasets/{id}/export` - Export data
- `GET /api/datasets/{id}/preview` - Preview data
- `GET /api/datasets/{id}/profile` - Column profiling

### Operations
- `POST /api/operations/standard` - Standard operations
- `POST /api/operations/cleaning` - Cleaning operations
- `POST /api/operations/ai` - AI-powered operations
- `POST /api/operations/undo` - Undo operation
- `POST /api/operations/redo` - Redo operation

### AI & Agents
- `GET /api/ai/providers` - List AI providers
- `POST /api/ai/analyze` - Analyze data
- `POST /api/ai/chat` - Chat with assistant
- `GET /api/agents` - List agents
- `POST /api/agents` - Create agent

**Full API documentation:** [docs/api-reference/](docs/api-reference/README.md) or http://localhost:8000/docs

## 📊 Tier Limits

| Tier | Projects | Max Rows | Storage | History | Collaboration |
|------|----------|----------|---------|---------|---------------|
| **Free** | 1 | 1,000 | 5 MB | 10 ops | No |
| **Pro** | 10 | 50,000 | 100 MB | 100 ops | No |
| **Enterprise** | Unlimited | 500,000 | 1 GB | 500 ops | Yes (5 users) |

## 🧪 Testing

```bash
# Backend with coverage
pnpm test:backend:coverage

# Frontend type check
pnpm exec vue-tsc --noEmit

# Build verification
pnpm build
```

## 📝 License

MIT License

## 🔗 Links

- **GitHub Repository:** https://github.com/bitsnaps/MasterDataCleaner
- **Documentation:** [docs/](docs/)
- **API Reference:** [docs/api-reference/](docs/api-reference/README.md)
- **Contributor Guidelines:** [AGENTS.md](AGENTS.md)
- **Task Tracking:** [TODO.md](TODO.md)

---

*Last updated: March 2026*
