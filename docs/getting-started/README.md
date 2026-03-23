# Getting Started with MasterDataCleaner

This guide walks you through installing and setting up MasterDataCleaner on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend runtime |
| **pnpm** | 9+ | Package manager |

### Installing Prerequisites

**Python 3.11+**
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update && sudo apt install python3.11 python3.11-venv

# Windows
# Download from https://www.python.org/downloads/
```

**Node.js 18+**
```bash
# macOS
brew install node@18

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# Download from https://nodejs.org/
```

**pnpm**
```bash
npm install -g pnpm
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/bitsnaps/MasterDataCleaner.git
cd MasterDataCleaner
```

### 2. Set Up the Python Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd ..
pnpm install
```

### 4. Configure Environment Variables (Optional)

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.sample .env
```

Edit `.env` with your settings:

```env
# App Settings
SECRET_KEY=your-secret-key-here
DEBUG=true

# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./master_data_cleaner.db

# AI Provider Keys (optional - add as needed)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...
DEEPSEEK_API_KEY=...
OPENROUTER_API_KEY=...

# Admin User (optional - creates admin on startup)
ADMIN_USER=admin@example.com
ADMIN_PASSWORD=securepassword

# OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

## Running the Application

You need to run both the backend and frontend servers.

### Terminal 1: Start the Backend

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

The backend API will be available at:
- **API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Terminal 2: Start the Frontend

```bash
# From the project root directory
pnpm dev
```

The frontend will be available at:
- **Application:** http://localhost:3000 (or http://localhost:5173 depending on Vite config)

### Alternative: Using npm scripts

From the project root, you can use the provided npm scripts:

```bash
# Start backend only
pnpm backend

# Run backend tests
pnpm test:backend

# Run frontend tests
pnpm test:frontend

# Run all tests
pnpm test
```

## First Steps

### 1. Create an Account

1. Open http://localhost:3000 in your browser
2. Click "Sign Up" or navigate to the registration page
3. Enter your email and password
4. Complete registration

**Note:** If you set `ADMIN_USER` and `ADMIN_PASSWORD` in `.env`, that admin account is created automatically. Otherwise, the first registered user becomes admin.

### 2. Create Your First Project

1. Navigate to **Dashboard** or **Projects**
2. Click **"New Project"**
3. Enter a project name and description
4. Click **Create**

### 3. Import Data

1. Open your project
2. Click **"Import Data"**
3. Choose your data source:
   - **File Upload** - CSV, Excel, JSON
   - **Clipboard** - Paste data directly
   - **Database** - Connect to a database (advanced)
4. Configure import settings
5. Click **Import**

### 4. Apply Cleaning Operations

1. Select columns to clean
2. Choose an operation from the toolbar:
   - **Missing Values** - Fill or drop nulls
   - **String Ops** - Trim, case conversion, find/replace
   - **Date Ops** - Parse dates, extract components
   - **AI Clean** - Use AI for intelligent cleaning
3. Preview the changes
4. Click **Apply** to commit or **Cancel** to discard

### 5. Export Cleaned Data

1. Click **"Export"** in the project toolbar
2. Choose format: CSV, Excel, or JSON
3. Download the cleaned dataset

## AI Provider Configuration

MasterDataCleaner supports multiple AI providers. Configure them in your `.env` file:

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o-mini |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Google | `GOOGLE_API_KEY` | gemini-2.0-flash |
| Ollama | (none - local) | llama3.2 |
| Groq | `GROQ_API_KEY` | llama-3.3-70b-versatile |
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |
| OpenRouter | `OPENROUTER_API_KEY` | openai/gpt-4o-mini |

### Using AI Features

1. Go to **Agents** in the navigation
2. Create a new agent or use a pre-built template
3. Select your provider and enter API key (if not in `.env`)
4. Configure the agent settings
5. Use the agent in AI cleaning operations

## Running Tests

### Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest -v

# With coverage
pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Frontend Tests

```bash
pnpm test:frontend
```

### End-to-End Tests

```bash
pnpm test:e2e
```

## Troubleshooting

### Backend won't start

**Issue:** Module not found errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue:** Database errors
```bash
# Delete the SQLite database and restart
rm backend/master_data_cleaner.db
# Restart the backend to recreate tables
```

### Frontend won't start

**Issue:** Module not found errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
pnpm install
```

**Issue:** Port already in use
```bash
# Change port in vite.config.ts or kill the process using port 3000
lsof -ti:3000 | xargs kill
```

### AI features not working

**Issue:** API key errors
- Verify your API key is correct in `.env`
- Check that the key has the necessary permissions
- Ensure you have API credits/quota remaining

**Issue:** Rate limiting
- Different providers have different rate limits
- Check the provider's documentation for limits
- Consider upgrading your API tier

## Docker Deployment (Optional)

For containerized deployment:

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **Database:** localhost:5432

## Next Steps

- **[Features](../features/README.md)** - Explore all available features
- **[Guides](../guides/README.md)** - Step-by-step tutorials
- **[Architecture](../architecture/README.md)** - Understand the system design

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
