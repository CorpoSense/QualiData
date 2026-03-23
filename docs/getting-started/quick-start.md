# Quick Start Guide

Get MasterDataCleaner up and running in 5 minutes.

## Quick Installation

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/bitsnaps/MasterDataCleaner.git
cd MasterDataCleaner

# Install backend dependencies
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd ..
pnpm install
```

### 2. Configure (Optional)

Create `backend/.env` for AI features:

```env
OPENAI_API_KEY=sk-your-key-here
ADMIN_USER=admin@example.com
ADMIN_PASSWORD=admin123
```

### 3. Run

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

### 4. Access

Open http://localhost:3000 in your browser.

## Your First Data Cleaning Project

### Step 1: Create Account
- First user becomes admin (or use configured admin credentials)

### Step 2: Create Project
1. Click **"New Project"**
2. Name it "My First Project"
3. Click **Create**

### Step 3: Import Data
1. Click **"Import Data"**
2. Choose **File Upload** or **Paste from Clipboard**
3. Select/upload your CSV or Excel file
4. Click **Import**

### Step 4: Clean Data
1. **Select columns** you want to clean
2. **Choose operation** from toolbar:
   - Trim whitespace
   - Convert case
   - Fill missing values
   - Remove duplicates
3. **Preview** changes
4. **Apply** to commit

### Step 5: Export
1. Click **"Export"**
2. Choose format (CSV, Excel, JSON)
3. Download cleaned data

## Common Operations

| Task | How To |
|------|--------|
| Remove duplicates | Select columns → String Ops → Remove Duplicates |
| Fix capitalization | Select columns → String Ops → Title Case |
| Fill missing values | Select columns → Missing Values → Fill with value |
| Standardize dates | Select columns → Date Ops → Parse datetime |
| AI cleaning | Select columns → AI Clean → Choose agent → Enter prompt |

## Need Help?

- **[Full Installation Guide](README.md)** - Detailed setup instructions
- **[Features](../features/README.md)** - Complete feature overview
- **[Guides](../guides/README.md)** - Step-by-step tutorials

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
