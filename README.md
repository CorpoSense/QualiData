# MasterDataCleaner

**MasterDataCleaner** is an intelligent, step-by-step data cleaning solution designed for professional environments. It empowers employees to transform messy, inconsistent data into structured, high-quality information through an AI-guided assistant.

## 🚀 Overview

In modern business environments, data often arrives in various formats and states of "cleanliness." MasterDataCleaner streamlines the data preparation process by providing a guided workflow that handles everything from ingestion to final export.

### Key Pillars:
- **Intelligent Guidance:** An AI assistant that understands your data structure and suggests cleaning steps.
- **Versatile Connectivity:** Support for local files, remote servers, and direct database connections.
- **Customizable Logic:** Powerful scripting capabilities for complex data transformation rules.
- **Structured Output:** Export cleaned data directly into your production databases or files.

## ✨ Features

- **Step-by-Step Workflow:** A logical, linear process that ensures no data validation step is missed.
- **AI-Powered Analysis:** Automatically detect anomalies, duplicates, and formatting errors.
- **Connectors & Integration:** 
  - **Files:** Excel (.xlsx, .xls), CSV, JSON, XML.
  - **Databases:** PostgreSQL, MySQL, SQL Server (via specialized connectors).
  - **Remote Access:** FTP/SFTP support for automated remote data fetching.
- **Scripting Engine:** Inject custom logic using a powerful scripting interface for unique business rules.
- **Visual Preview:** Real-time feedback on how cleaning steps affect your data.

## 🛠 Tech Stack

- **Frontend:** [Vue 3](https://vuejs.org/) with [Pinia](https://pinia.vuejs.org/) for state management.
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python) for a lightweight and fast API layer.
- **AI:** [LangChain](https://langchain.com/) with multi-provider support.
- **Data Processing:** [pandas](https://pandas.pydata.org/), [polars](https://pola.rs/).
- **Communication:** [Axios](https://axios-http.com/) for seamless frontend-backend integration.
- **Styling:** [Bootstrap 5](https://getbootstrap.com/) with [BootstrapVueNext](https://bootstrap-vue-next.github.io/bootstrap-vue-next/) for modern, responsive UI components.
- **Language:** [TypeScript](https://www.typescriptlang.org/) (frontend), Python (backend).

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

4. **Set up environment variables (optional):**
   ```bash
   # Create a .env file in the backend directory
   cd backend
   echo "OPENAI_API_KEY=your-key-here" > .env
   ```

### Running the Application

**Start the backend (Terminal 1):**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Start the frontend (Terminal 2):**
```bash
pnpm dev
```

The application will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Running Tests

```bash
# Backend tests
cd backend
source .venv/bin/activate
pytest -v
```

## 📁 Project Structure

```
MasterDataCleaner/
├── backend/                # Python FastAPI
│   ├── .venv/              # Python virtual environment
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── config.py       # Settings
│   │   ├── routers/
│   │   │   ├── health.py   # Health check endpoint
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
│   ├── components/
│   ├── views/
│   ├── router.ts
│   └── main.ts
├── dist/                   # Vite build output
├── package.json
├── vite.config.ts
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/ai/providers` | List supported AI providers |
| POST | `/api/ai/analyze` | Analyze data and get cleaning recommendations |
| POST | `/api/ai/suggest-fix` | Get suggestions for fixing data issues |
| POST | `/api/ai/generate-code` | Generate code for cleaning tasks |
| POST | `/api/ai/chat` | Chat with the data cleaning assistant |

## 🚧 Roadmap & Technical Challenges

As we evolve MasterDataCleaner, we are focusing on:
1. **Dynamic Schema Mapping:** Handling heterogeneous data sources with varying structures.
2. **Large Dataset Performance:** Optimizing the AI assistant and UI for millions of rows.
3. **Connector Extensibility:** Creating a plugin system for third-party data connectors.
4. **AI Context Awareness:** Improving the assistant's ability to learn from historical cleaning patterns.

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

## ✅ TODO

Track progress for the MasterDataCleaner SaaS project.

### Phase 1: Foundation

#### Authentication
- [x] Setup user registration (email/password)
- [x] Setup user login
- [x] Add password reset flow
- [x] Add OAuth providers (Google, GitHub)
- [x] Implement JWT token management
- [x] Create user model and migrations
- [x] Smart admin creation (env vars or first user)

#### Database Setup
- [x] Configure PostgreSQL connection
- [x] Setup SQLAlchemy models (User, Project, Dataset, OperationHistory, Agent)
- [x] Run Alembic migrations to create tables
- [x] Implement connection pooling
- [x] Auto-create tables on startup

#### Dataset Import/Export
- [x] CSV import with auto-detection (delimiter, encoding)
- [x] Excel (.xlsx, .xls) import
- [x] JSON import
- [x] CSV export
- [x] Excel export
- [x] Clipboard import (paste CSV)
- [x] Clipboard export (copy to clipboard)
- [x] Handle NaN/None values in JSON

### Phase 2: Core Operations

#### Data Operations
- [x] String operations (uppercase, lowercase, trim, titlecase)
- [x] Numeric operations (round, normalize, outliers)
- [x] Datetime operations (parse, extract year/month/day)
- [x] Fill NA (drop, forward, backward, constant)
- [x] Remove duplicates
- [x] Fuzzy deduplication
- [x] Sort by column
- [x] Structural (rename, drop column, change type)

#### Preview System
- [x] Implement preview endpoint
- [x] Add row count options (25, 50, 100)
- [x] Create scrollable data table
- [x] Display summary statistics

### Phase 3: AI Integration

#### AI Cleaning Operations
- [x] Create AI operation endpoint
- [x] Implement batch processing
- [x] Add column selection for context
- [x] Support summary statistics for agent

### Phase 4: UX Polish

#### UI Improvements
- [x] Toast notifications (replacing alert())
- [x] Modal improvements (OK/Cancel buttons)
- [x] Dropdown fixes

### Testing
- [x] Unit tests (104 tests)
- [x] Integration tests for import/operations
- [x] Model field consistency tests

### CI/CD
- [x] GitHub Actions workflow
- [x] Backend tests (pytest)
- [x] Frontend type check (vue-tsc)
- [x] Lint checks (ruff + black)

---

*Last updated: 2026-03-06*
# Force rebuild
