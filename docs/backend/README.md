# Backend Documentation

FastAPI backend service documentation.

## Overview

The MasterDataCleaner backend is a Python FastAPI application that provides REST APIs for data cleaning operations, AI integration, and user management.

## Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115+ | REST API framework |
| **Python** | 3.11+ | Runtime language |
| **SQLAlchemy** | 2.0+ | ORM |
| **pandas** | 2.2+ | Data manipulation |
| **polars** | 1.0+ | High-performance data processing |
| **LangChain** | 0.3+ | AI/LLM integration |
| **Pydantic** | 2.10+ | Data validation |
| **Alembic** | 1.13+ | Database migrations |
| **pytest** | 8.3+ | Testing framework |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry
│   ├── config.py                # Configuration management
│   ├── rate_limit.py            # Rate limiting middleware
│   ├── seed_templates.py        # Built-in agent templates
│   │
│   ├── db/                      # Database layer
│   │   ├── __init__.py
│   │   ├── database.py          # Connection management
│   │   ├── models.py            # Model exports
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py          # User model
│   │       ├── project.py       # Project, Dataset, OperationHistory
│   │       └── agent.py         # Agent model
│   │
│   ├── routers/                 # API routes (23 routers)
│   │   ├── __init__.py
│   │   ├── health.py            # Health check endpoint
│   │   ├── auth.py              # Authentication
│   │   ├── users.py             # User management
│   │   ├── projects.py          # Project CRUD
│   │   ├── datasets.py          # Dataset operations
│   │   ├── operations.py        # Core data operations
│   │   ├── operations_extra.py  # Additional operations
│   │   ├── structural_ops.py    # Structural transformations
│   │   ├── cell_ops.py          # Cell-level operations
│   │   ├── datetime_ops.py      # Date/time operations
│   │   ├── missing_values.py    # Null handling
│   │   ├── batch_ops.py         # Batch operations
│   │   ├── ai_operations.py     # AI-powered operations
│   │   ├── ai.py                # AI endpoints
│   │   ├── assistant.py         # Assistant wizard
│   │   ├── agents.py            # Agent management
│   │   ├── profiling.py         # Data profiling
│   │   ├── comparison.py        # Before/after comparison
│   │   ├── undo_redo.py         # Undo/redo functionality
│   │   ├── notifications.py     # Notification system
│   │   └── rate_limit.py        # Rate limit endpoints
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── ai_provider.py       # AI provider factory
│   │   ├── cleaner.py           # Data cleaning assistant
│   │   └── smart_importer.py    # Smart data import
│   │
│   └── models/                  # Pydantic schemas
│       ├── __init__.py
│       └── schemas.py           # Request/Response models
│
├── tests/                       # Test suite
│   ├── test_health.py
│   ├── test_ai.py
│   └── ...
│
├── alembic/                     # Database migrations
│   ├── versions/
│   └── ...
│
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── ruff.toml                    # Linter configuration
└── .env.sample                  # Environment template
```

## Configuration

### Environment Variables

Configuration is managed in `config.py` using Pydantic Settings:

```python
class Settings(BaseSettings):
    # App Settings
    app_name: str = "MasterDataCleaner API"
    debug: bool = False
    secret_key: str = "your-secret-key-here"
    frontend_url: str = "http://localhost:5173"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./master_data_cleaner.db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # AI Provider Keys
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    deepseek_api_key: str | None = None
    openrouter_api_key: str | None = None
    
    # OAuth
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    
    # Admin
    admin_email: str = ""
    admin_password: str = ""
```

### Environment File

Create `backend/.env`:

```env
# App
SECRET_KEY=your-secret-key-here
DEBUG=true
FRONTEND_URL=http://localhost:5173

# Database
DATABASE_URL=sqlite+aiosqlite:///./master_data_cleaner.db

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Admin (optional)
ADMIN_USER=admin@example.com
ADMIN_PASSWORD=securepassword
```

## Main Application

### FastAPI App Creation

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="AI-guided data cleaning API",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(users.router, prefix="/api")
    app.include_router(health.router, prefix="/api")
    # ... other routers
    
    return app

app = create_app()
```

### Lifespan Events

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await run_migrations()
    await create_admin_user()
    yield
    # Shutdown cleanup
```

## Database Layer

### Connection Management

```python
# db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

_async_engine = None

def get_async_engine():
    global _async_engine
    if _async_engine is None:
        database_url = settings.database_url
        # Convert to async URL
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        
        _async_engine = create_async_engine(
            database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
        )
    return _async_engine

def get_async_session_maker():
    return async_sessionmaker(
        get_async_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )
```

### Models

#### User Model

```python
# db/models/user.py
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str | None]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    google_id: Mapped[str | None]
    github_id: Mapped[str | None]
    storage_used_bytes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    @property
    def tier_limits(self) -> dict:
        """Get tier limits based on role."""
        # Returns limits based on user role
```

#### Project Model

```python
# db/models/project.py
class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    row_count: Mapped[int] = mapped_column(default=0)
    storage_bytes: Mapped[int] = mapped_column(default=0)
    
    user = relationship("User", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project")
```

## API Routers

### Router Organization

Routers are organized by feature:

| Router | Endpoints | Description |
|--------|-----------|-------------|
| `health` | `GET /health` | Health check |
| `auth` | `POST /auth/*` | Authentication |
| `users` | `GET,PUT /users/*` | User management |
| `projects` | `CRUD /projects` | Project operations |
| `datasets` | `CRUD /datasets` | Dataset operations |
| `operations` | `POST /operations/*` | Data operations |
| `agents` | `CRUD /agents` | Agent management |
| `ai` | `POST /ai/*` | AI operations |

### Example Router

```python
# routers/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### Authentication Router

```python
# routers/auth.py
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"])

@router.post("/auth/register")
async def register(user_data: UserCreate):
    """Register new user."""
    # Check if user exists
    # Create user with hashed password
    # Return JWT token

@router.post("/auth/login")
async def login(credentials: Credentials):
    """Login and get JWT token."""
    # Validate credentials
    # Generate JWT token
    # Return token

@router.post("/auth/debug-login")
async def debug_login():
    """Debug login for development."""
    # Create test user if needed
    # Return token
```

## Services

### AI Provider Service

```python
# services/ai_provider.py
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from enum import Enum

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    GROQ = "groq"
    DEEPSEEK = "deepseek"

def get_chat_model(
    provider: AIProvider,
    model: str | None = None,
    temperature: float = 0.7,
    **kwargs,
) -> BaseChatModel:
    """Get chat model for specified provider."""
    match provider:
        case AIProvider.OPENAI:
            return ChatOpenAI(model=model, temperature=temperature, **kwargs)
        case AIProvider.ANTHROPIC:
            return ChatAnthropic(model=model, temperature=temperature, **kwargs)
        # ... other providers
```

### Cleaner Service

```python
# services/cleaner.py
class DataCleaningAssistant:
    """AI assistant for data cleaning."""
    
    def __init__(self, provider: AIProvider, model: str | None = None):
        self.llm = get_chat_model(provider, model)
    
    async def analyze_data(self, data_summary: str) -> str:
        """Analyze data and provide recommendations."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Analyze this data:\n\n{data}"),
        ])
        chain = prompt | self.llm
        response = await chain.ainvoke({"data": data_summary})
        return response.content
    
    async def suggest_fix(self, issue: str) -> str:
        """Suggest fix for data quality issue."""
        # Implementation
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/debug-login` | Debug login (dev only) |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/{id}` | Get project |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/import` | Import data |
| GET | `/api/datasets/{id}/export` | Export data |
| GET | `/api/datasets/{id}/preview` | Preview data |
| GET | `/api/datasets/{id}/profile` | Column profiling |

### Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/operations/standard` | Standard operation |
| POST | `/api/operations/cleaning` | Cleaning operation |
| POST | `/api/operations/ai` | AI operation |
| POST | `/api/operations/commit` | Commit changes |
| POST | `/api/operations/rollback` | Rollback changes |
| GET | `/api/operations/history` | Get history |
| POST | `/api/operations/undo` | Undo operation |
| POST | `/api/operations/redo` | Redo operation |

### AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/providers` | List providers |
| POST | `/api/ai/analyze` | Analyze data |
| POST | `/api/ai/suggest` | Get suggestions |
| POST | `/api/ai/chat` | Chat with assistant |

## Request/Response Models

### Pydantic Schemas

```python
# models/schemas.py
class AIProviderRequest(BaseModel):
    provider: str = "openai"
    model: str | None = None
    temperature: float = 0.3

class AnalyzeDataRequest(BaseModel):
    provider: str | None = "openai"
    model: str | None = None
    data_summary: str

class AnalyzeDataResponse(BaseModel):
    analysis: str
    provider: str
    model: str

class ChatRequest(BaseModel):
    provider: str | None = "openai"
    model: str | None = None
    message: str

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str
```

## Data Operations

### Operation Types

Operations are implemented as separate endpoints:

**Missing Values:**
```python
@router.post("/operations/fillna")
async def fillna(
    dataset_id: str,
    column: str,
    value: str | float,
    method: str = "constant"  # constant, mean, median, mode, forward, backward
):
    # Apply fillna operation
    # Create before/after snapshots
    # Save to history
    # Return preview
```

**String Operations:**
```python
@router.post("/operations/string/strip")
async def string_strip(dataset_id: str, columns: list[str]):
    # Apply str.strip() to columns
    # Return preview
```

**AI Operations:**
```python
@router.post("/operations/ai/clean")
async def ai_clean(
    dataset_id: str,
    columns: list[str],
    agent_id: str,
    prompt: str,
    batch_size: int = 10,
):
    # Load agent configuration
    # Process data in batches
    # Call AI provider for each batch
    # Aggregate results
    # Return with confidence scores
```

## Error Handling

### Global Exception Handler

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## Testing

### Test Structure

```python
# tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_health.py -v
```

## Development

### Running Locally

```bash
# Activate virtual environment
source .venv/bin/activate

# Start server
uvicorn app.main:app --reload --port 8000
```

### Code Quality

**Linting:**
```bash
ruff check .
black .
```

**Type Checking:**
```bash
mypy app/
```

## Deployment

### Production Server

```bash
# Using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Environment Variables (Production)

```env
SECRET_KEY=<secure-random-key>
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_API_KEY=sk-...
FRONTEND_URL=https://your-domain.com
```

## Next Steps

- **[Frontend](../frontend/README.md)** - Vue.js application
- **[Database](../database/README.md)** - Database schema details
- **[API Reference](../api-reference/README.md)** - Complete API documentation

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
