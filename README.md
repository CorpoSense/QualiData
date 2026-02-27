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
- **Styling:** Modern, responsive UI components.
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
- [ ] Add OAuth providers (Google, GitHub)
- [x] Implement JWT token management
- [ ] Add password reset flow
- [x] Create user model and migrations

#### Database Setup
- [x] Configure PostgreSQL connection
- [x] Setup SQLAlchemy models (User, Project, Dataset, OperationHistory, Agent)
- [x] Run Alembic migrations to create tables
- [ ] Implement connection pooling
- [ ] Add MySQL support (optional)

#### Project Management
- [x] Create project model
- [x] Implement project CRUD endpoints
- [x] Add project listing with pagination
- [x] Implement project search/filter
- [x] Add row count and storage tracking

#### Dataset Import/Export
- [x] CSV import
- [x] Excel (.xlsx, .xls) import
- [x] JSON import
- [x] CSV export
- [ ] Excel export
- [x] JSON export
- [ ] Clipboard import (paste CSV)
- [ ] Clipboard export (copy to clipboard)

---

### Phase 2: Core Operations

#### Standard Operations (pandas-based)
- [x] Add column (empty/default/calculated)
- [x] Remove column(s)
- [x] Rename column
- [x] Merge columns (concatenate with delimiter)
- [x] Split column (delimiter/regex/count)
- [x] Duplicate column
- [x] Reorder columns (drag-and-drop)
- [x] Filter rows
- [x] Sort data
- [x] Remove duplicates
- [x] Find & replace
- [x] Change data type

#### Simple Cleaning Operations
- [x] Strip whitespace
- [x] Convert to uppercase
- [x] Convert to lowercase
- [x] Convert to title case
- [x] Remove duplicates
- [x] Handle missing values (fillna, impute)
- [x] Standardize date/time formats
- [x] Fix structural errors (typos, capitalization)
- [ ] Custom function chaining (predefined library) - optional

#### Preview System
- [x] Implement preview endpoint
- [ ] Add row count options (25, 50, 100)
- [ ] Create scrollable data table
- [ ] Display summary statistics

#### Operation History
- [x] Create operation history model
- [x] Implement undo (single step)
- [x] Implement redo (single step)
- [x] Add history list view

---

### Phase 3: AI Integration

#### Agent Management
- [x] Create agent model
- [x] Implement agent CRUD endpoints
- [x] Add provider/model selection
- [x] Create system prompt editor
- [x] Add prompt template support
- [x] Implement temperature configuration

#### Pre-built Agent Templates
- [x] Email Normalizer agent
- [x] Address Formatter agent
- [x] Phone Number Formatter agent
- [x] Text Cleaner agent
- [x] Date Parser agent

#### AI Cleaning Operations
- [x] Create AI operation endpoint
- [ ] Implement batch processing
- [x] Add column selection for context
- [x] Support summary statistics for agent
- [ ] Implement cross-row context option
- [ ] Handle structured JSON output
- [ ] Add progress tracking

#### Rate Limiting & Observability
- [ ] Implement global sleep between requests
- [ ] Add per-provider rate limits
- [ ] Display quota warnings
- [ ] Integrate LangSmith observability
- [ ] Track API usage per user

---

### Phase 4: UX Polish

#### Column Profiling
- [ ] Auto-detect data types
- [ ] Calculate column statistics
- [ ] Display categorical stats (count, distinct, mode)
- [ ] Display numerical stats (sum, avg, median, min, max)
- [ ] Highlight data quality issues

#### Notifications
- [ ] Create notification system
- [ ] Add real-time updates (WebSocket/SSE)
- [ ] Show operation progress
- [ ] Display success/error messages
- [ ] Add rate limit warnings

#### Before/After Comparison
- [ ] Side-by-side view
- [ ] Toggle view (before/after switch)
- [ ] Diff highlighting for changed cells
- [ ] Summary comparison stats

#### Assistant Feature
- [ ] Create step-by-step wizard
- [ ] Implement data analysis step
- [ ] Add suggestion review step
- [ ] Create operation selection step
- [ ] Add confirmation step

---

### Phase 5: Billing & Launch

#### Lago Integration
- [ ] Setup Lago connection
- [ ] Create billing plans
- [ ] Implement subscription management
- [ ] Add usage tracking
- [ ] Generate invoices
- [ ] Handle payment webhooks

#### Tier Enforcement
- [ ] Implement row limits per tier
- [ ] Add storage limits per tier
- [ ] Restrict project count per tier
- [ ] Block operations on limit exceeded
- [ ] Add upgrade prompts

#### Landing Page
- [ ] Design hero section
- [ ] Add features showcase
- [ ] Create pricing table
- [ ] Add FAQ section
- [ ] Implement call-to-action buttons

#### Pricing Page
- [ ] Create tier comparison table
- [ ] Add feature matrix
- [ ] Implement plan selector
- [ ] Add monthly/yearly toggle
- [ ] Create checkout flow

#### Final Polish
- [ ] Add loading states
- [ ] Implement error boundaries
- [ ] Optimize performance
- [ ] Add SEO meta tags
- [ ] Create sitemap

---

### DevOps & Infrastructure

#### Testing
- [ ] Unit tests for all services
- [ ] Integration tests for API endpoints
- [ ] E2E tests for critical flows
- [ ] Add test coverage reporting

#### CI/CD
- [x] GitHub Actions workflow for backend tests
- [ ] GitHub Actions workflow for frontend tests
- [ ] Automated deployment pipeline (Koyeb)
- [ ] Staging environment setup
- [ ] Dockerfile for Koyeb deployment

#### Monitoring
- [ ] Add application logging
- [ ] Setup error tracking (Sentry)
- [ ] Add performance monitoring
- [x] Create health check endpoints

---

### Documentation

- [x] README.md with setup instructions
- [x] SPEC.md with full specification
- [x] MIGRATION.md with migration guide
- [x] .env.sample file
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide
- [ ] Contributing guide

---

### Collaboration (Enterprise Only)

- [ ] Team member management
- [ ] Role-based access control
- [ ] Project sharing
- [ ] Activity logging
- [ ] Comments/annotations

---

*Last updated: 2026-02-24*
