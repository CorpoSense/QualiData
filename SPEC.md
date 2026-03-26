# MasterDataCleaner - Full Specification

## Overview

MasterDataCleaner is a SaaS platform for AI-guided data cleaning. Users can upload datasets, apply transformations (standard, simple cleaning, or AI-powered), and export cleaned data through an intuitive web interface.

---

## Architecture

### Data Flow

```
Upload → Memory (pandas) → Transform → Preview → Commit → Database (persistent)
                                     ↓
                                   Rollback (discard)
```

### Storage Strategy

| Phase | Storage | Technology |
|-------|---------|------------|
| Working (active session) | In-memory | pandas DataFrame |
| Saved/Persisted | Database | PostgreSQL (Supabase, NeonDB) or MySQL (Aiven, Filess) |
| Import/Export | Files + DB | CSV, Excel, JSON, SQLAlchemy connections |

---

## User Roles & Authentication

- **Authentication:** Email/password + OAuth (Google, GitHub)
- **Session Management:** JWT tokens, persistent sessions for registered users
- **Roles:** Owner, Collaborator (Enterprise tier only)

---

## Core Features

### 1. Dashboard

**Projects Management:**
- Create, Read, Update, Delete projects
- Rename projects
- List all user projects with metadata (row count, last modified, status)
- Search/filter projects

**Agents Management:**
- Create, Read, Update, Delete agents
- Rename agents
- Agents are reusable across projects
- Pre-built agent templates (see below)

### 2. Project (Dataset)

**Import Sources:**
| Source | Format | Features |
|--------|--------|----------|
| File Upload | CSV, TSV, Excel (.xlsx, .xls), JSON, XML | Auto-detection, preview, schema mapping |
| Database | PostgreSQL, MySQL (via SQLAlchemy with dynamic schema discovery) | Connection pooling, query builder |
| Clipboard | Paste CSV/TSV data | Auto-detect delimiter |
| Remote | FTP, SFTP | Fetch files from remote servers |

**Import Features:**
- **Auto-detection** - Automatically detect delimiters, encoding, and data types
- **Preview** - Review data before importing (first 100 rows)
- **Schema mapping** - Configure column names and types
- **Validation** - Check for data quality issues on import
- **Encoding detection** - Auto-detect UTF-8, Latin-1, etc.
- **Header detection** - Auto-detect header rows
- **Skip rows** - Skip N rows at start (for metadata headers)
- **Comment handling** - Ignore comment lines (starting with #)

**Export Formats:**
| Format | Use Case | Features |
|--------|----------|----------|
| **CSV** | Universal compatibility, small file size | Configurable delimiter, quoting, encoding |
| **TSV** | Tab-separated values | For spreadsheet compatibility |
| **Excel** | Rich formatting, multiple sheets | Sheet naming, column widths, formatting |
| **JSON** | API integration, nested data | Pretty print, nested structure support |
| **XML** | Legacy systems, data exchange | Configurable root/row elements |
| **Database** | Direct export to production databases | Same connection types as import |
| **Clipboard** | Quick copy-paste to other applications | Copy selected rows/columns |

**Export Features:**
- **Column selection** - Choose which columns to export
- **Row filtering** - Export only filtered/selected rows
- **Format configuration** - Delimiter, encoding, quoting options
- **Template export** - Custom export formats using templates
- **Batch export** - Export multiple datasets at once
- **Scheduled export** - Export on schedule (Enterprise tier)

**Dataset Limits (by tier):**

| Tier | Max Rows | Max Storage | Max Projects |
|------|----------|-------------|--------------|
| Free | 1,000 | 5 MB | 1 |
| Pro | 50,000 | 100 MB | 10 |
| Enterprise | 500,000 | 1 GB | Unlimited |

### 3. Agent Configuration

**Agent Properties:**
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| name | string | required | Agent identifier |
| provider | enum | openai | AI provider (openai, anthropic, google, ollama, groq, deepseek, openrouter) |
| model | string | provider default | Specific model name |
| system_prompt | string | built-in | Agent personality/instructions |
| prompt_template | string | optional | Template for user prompts |
| temperature | float | 0.3 | Sampling temperature (0-1) |

**Pre-built Agent Templates (MVP):**
1. **Email Normalizer** - Standardize email formats
2. **Address Formatter** - Normalize addresses
3. **Phone Number Formatter** - Standardize phone formats
4. **Text Cleaner** - Remove special chars, fix encoding
5. **Date Parser** - Parse various date formats to standard

### 4. Column Operations

#### 4.1 Standard Operations (pandas-based)

| Operation | Description | Parameters |
|-----------|-------------|------------|
| Add Column | Create new column | empty / default value / calculated (pandas expressions) |
| Remove Column | Delete column(s) | column selection |
| Rename Column | Change column name | new name |
| Merge Columns | Concatenate columns | delimiter, columns to merge |
| Split Column | Split into multiple columns | delimiter / regex / number of columns |
| Duplicate Column | Copy column | new name |
| Reorder Columns | Change column order | drag-and-drop |
| Transpose | Swap rows and columns | - |
| Fill Down | Fill empty cells with value from above | column selection |
| Fill Up | Fill empty cells with value from below | column selection |
| Blank Down | Clear duplicate values in sorted column | column selection |

#### 4.2 Simple Cleaning Operations

| Operation | Description | Parameters |
|-----------|-------------|------------|
| Strip Spaces | Remove leading/trailing whitespace | - |
| To Uppercase | Convert to uppercase | - |
| To Lowercase | Convert to lowercase | - |
| To Title Case | Capitalize first letter of each word | - |
| Remove Duplicates | Remove duplicate rows | subset columns, keep first/last/none |
| Handle Missing Values | Fill or impute missing data | fillna value, forward fill, backward fill, mean/median/mode imputation |
| Standardize Format | Convert date/time formats | target format (date, time, datetime), input format hint |
| Fix Structural Errors | Correct typos, capitalization | auto-detect or manual rules |
| Custom Function | Chain predefined functions | function library (see below) |

**Predefined Function Library:**
```python
# Examples shown to users
strip()                    # Remove whitespace
lower()                    # Convert to lowercase
upper()                    # Convert to uppercase
capitalize()               # Capitalize first letter
replace(old, new)          # Replace text
extract(pattern)           # Extract with regex
slice(start, end)          # Substring
trim(length)               # Truncate to length
pad(length, char)          # Pad with character
```

#### 4.3 Advanced String Operations

| Operation | Description | Use Case |
|-----------|-------------|----------|
| **Fingerprint** | Normalize text for comparison | Find duplicates with different formatting |
| **N-gram** | Generate character n-grams | Fuzzy matching, clustering |
| **Metaphone** | Phonetic encoding | Match names with similar pronunciation |
| **Soundex** | Phonetic algorithm | Match names by sound |
| **Levenshtein** | Edit distance calculation | Find similar strings |
| **Jaro-Winkler** | String similarity score | Match short strings (names) |

#### 4.4 AI Cleaning Operations

**Workflow:**
1. User selects column(s)
2. User selects or configures agent
3. User provides prompt (or uses template)
4. Optional: Enable summary statistics for agent context
5. Optional: Enable cross-row context (checkbox)
6. Configure batch size (default: 10 rows)
7. Preview before/after
8. Commit or Rollback

**Agent Input (per batch):**
```json
{
  "column_name": "email",
  "column_type": "string",
  "sample_data": [...],
  "summary_stats": {  // optional
    "count": 100,
    "null_count": 5,
    "distinct_count": 95
  },
  "previous_rows": [...],  // if cross-row context enabled
  "user_prompt": "Normalize these emails to lowercase"
}
```

**Agent Output (structured JSON):**
```json
{
  "transformed_values": ["user@example.com", ...],
  "confidence": 0.95,
  "notes": "5 invalid emails marked as null"
}
```

**Batch Processing:**
- Default batch size: 10 rows
- Configurable per operation
- Progress indicator with current row
- Sleep between batches to avoid rate limits

**Rate Limiting:**
| Provider | Requests/min | Tokens/min | Notes |
|----------|--------------|------------|-------|
| OpenAI | 500 | 90,000 | Varies by tier |
| Anthropic | 60 | 40,000 | - |
| Google | 300 | 60,000 | - |
| Groq | 30 | 18,000 | - |
| DeepSeek | 60 | 30,000 | - |
| OpenRouter | Varies | Varies | Depends on underlying provider |

*Implementation:* Global sleep between requests, display quota warnings via notifications.

### 5. Data Exploration & Filtering

#### 5.1 Faceted Browsing

**Core feature for data exploration (inspired by OpenRefine):**

| Facet Type | Description | Use Case |
|------------|-------------|----------|
| **Text Facet** | List all unique values with counts | See distribution of categorical data |
| **Numeric Facet** | Histogram, min/max slider | Filter numeric ranges |
| **Timeline Facet** | Date range picker | Filter by date ranges |
| **Scatterplot Facet** | Two numeric columns plotted | Find correlations, outliers |
| **Custom Facet** | GREL expression-based | Advanced filtering logic |

**Facet Features:**
- **Multi-select** - Choose multiple values
- **Range selection** - Numeric/date ranges
- **Include/Exclude** - Include or exclude selected values
- **Sort by count** - See most common values first
- **Cluster within facet** - Group similar values
- **Save facet** - Save facet configuration for reuse

**Facet Workflow:**
1. Click column header → "Facet"
2. Choose facet type (text, numeric, timeline, etc.)
3. Configure facet options
4. Select values/ranges to filter
5. View filtered results
6. Combine multiple facets for complex filtering

#### 5.2 Clustering

**Fuzzy matching for deduplication (inspired by OpenRefine):**

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| **Key Collision** | Group by normalized key | Fast, exact-ish matching |
| **Nearest Neighbor** | Compare all pairs | Small datasets, high accuracy |
| **Fingerprint** | Normalize whitespace, punctuation | General text |
| **N-gram Fingerprint** | Use n-grams as keys | Partial matches |
| **Metaphone** | Phonetic encoding | Names, words |
| **Double Metaphone** | Improved phonetic | Names with variations |

**Clustering Features:**
- **Similarity threshold** - Adjust how strict matching is
- **Merge suggestions** - AI suggests which values to merge
- **Preview merge** - See result before applying
- **Bulk merge** - Merge all selected clusters at once
- **Undo merge** - Revert cluster merges

**Clustering Workflow:**
1. Select column to cluster
2. Choose clustering algorithm
3. Adjust similarity threshold
4. Review cluster suggestions
5. Select clusters to merge
6. Choose canonical value (or create new)
7. Apply merge

#### 5.3 Reconciliation

**Match data against external knowledge bases (inspired by OpenRefine):**

| Service | Description | Use Case |
|---------|-------------|----------|
| **Wikidata** | Match entities to Wikidata | People, organizations, places |
| **VIAF** | Virtual International Authority File | Authors, creators |
| **Custom API** | Any reconciliation service | Domain-specific matching |

**Reconciliation Features:**
- **Scored matches** - Confidence score for each match
- **Multiple candidates** - See top N matches
- **Manual review** - Accept/reject matches
- **Auto-match** - Accept matches above threshold
- **Create new** - Add new entity if no match found

**Reconciliation Workflow:**
1. Select column to reconcile
2. Choose reconciliation service
3. Configure matching options
4. Run reconciliation
5. Review matches (scored by confidence)
6. Accept/reject matches
7. Add matched IDs to dataset

### 6. Preview & History

**Preview Panel:**
- Display options: 25, 50, 100 rows
- Scrollable table
- Before/After comparison (side-by-side or toggle)
- Summary statistics (count, distinct, sum, avg, median)

**Operation History:**
- Stack of last N operations (default: 10, configurable by tier)
- Undo/Redo buttons
- Click to restore any previous state
- Auto-drop oldest when stack full
- **Export history** - Save operation history as JSON
- **Import history** - Apply saved operations to new data
- **Replay operations** - Run same operations on different dataset

**Column Profiling:**
- Auto-detect data types (string, number, date, boolean)
- Show column statistics:
  - Categorical: count, distinct count, most frequent
  - Numerical: count, sum, avg, median, min, max, std
  - Date: min, max, range
- Highlight potential issues (nulls, mixed types, outliers)

### 7. Assistant Feature

Step-by-step wizard for guided cleaning:
1. **Analyze** - Agent analyzes data and suggests operations
2. **Review** - User reviews suggestions with preview
3. **Apply** - User selects which operations to apply
4. **Confirm** - Final review before commit

### 8. Notifications

Real-time notification system for:
- Operation progress (with percentage)
- Operation completed
- Errors with retry option
- Rate limit warnings
- Quota approaching limits

**Implementation:** WebSocket or Server-Sent Events (SSE) for real-time updates.

---

## Technical Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| Vue 3 | Framework |
| Pinia | State management |
| Vue Router | Routing |
| Buefy | UI component library |
| Axios | HTTP client |
| Vite | Build tool |

### Backend

| Technology | Purpose |
|------------|---------|
| FastAPI | API framework |
| SQLAlchemy | ORM with dynamic schema discovery |
| pandas | Data manipulation |
| polars | Alternative (faster for large datasets) |
| LangChain | AI abstraction layer |
| Pydantic | Data validation |
| Celery | Background task queue (for long operations) |
| Redis | Task queue backend + caching |

### AI Providers

| Provider | Package | Default Model |
|----------|---------|---------------|
| OpenAI | langchain-openai | gpt-4o-mini |
| Anthropic | langchain-anthropic | claude-sonnet-4-20250514 |
| Google | langchain-google-genai | gemini-2.0-flash |
| Ollama | langchain-ollama | llama3.2 |
| Groq | langchain-groq | llama-3.3-70b-versatile |
| DeepSeek | langchain-deepseek | deepseek-chat |
| OpenRouter | langchain-openrouter | openai/gpt-4o-mini |

### Database

| Database | Use Case |
|----------|----------|
| PostgreSQL (Supabase/NeonDB) | Primary storage |
| MySQL (Aiven/Filess) | Alternative storage |
| Redis | Caching + task queue |

### Billing & Payments

| Service | Purpose |
|---------|---------|
| Lago | Billing engine, usage tracking, invoicing |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Authentication | JWT + OAuth (Google, GitHub) |
| Real-time updates | WebSocket / SSE |
| File storage | S3-compatible (Supabase Storage, Cloudflare R2) |
| Monitoring | LangSmith (LangChain observability) |

---

## Pricing Tiers

### Free Tier (Exploration)
- 1 project
- 1,000 rows max
- 5 MB storage
- All features included
- No collaboration
- Community support

### Pro Tier ($19/month)
- 10 projects
- 50,000 rows max
- 100 MB storage
- All features included
- No collaboration
- Priority email support

### Enterprise Tier ($99/month)
- Unlimited projects
- 500,000 rows max
- 1 GB storage
- All features included
- **Collaboration:** Up to 5 team members per project
- Role-based access (Owner, Editor, Viewer)
- Dedicated support
- Custom integrations

---

## Database Schema (Core)

### Users
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE,
  password_hash VARCHAR,
  name VARCHAR,
  tier VARCHAR DEFAULT 'free',
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Projects
```sql
projects (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR,
  description TEXT,
  row_count INTEGER,
  storage_bytes BIGINT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Datasets (stored data)
```sql
datasets (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  data JSONB,  -- Serialized DataFrame
  schema JSONB,  -- Column names and types
  version INTEGER,
  created_at TIMESTAMP
)
```

### Agents
```sql
agents (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR,
  provider VARCHAR,
  model VARCHAR,
  system_prompt TEXT,
  prompt_template TEXT,
  temperature FLOAT DEFAULT 0.3,
  is_template BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Operation History
```sql
operation_history (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  operation_type VARCHAR,
  operation_config JSONB,
  snapshot JSONB,  -- DataFrame state
  created_at TIMESTAMP
)
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get current user |

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
| POST | `/api/projects/{id}/import` | Import data |
| GET | `/api/projects/{id}/export` | Export data |
| GET | `/api/projects/{id}/preview` | Preview data |
| GET | `/api/projects/{id}/profile` | Column profiling |

### Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/operations/standard` | Apply standard operation |
| POST | `/api/projects/{id}/operations/cleaning` | Apply cleaning operation |
| POST | `/api/projects/{id}/operations/ai` | Apply AI operation |
| POST | `/api/projects/{id}/operations/commit` | Commit changes |
| POST | `/api/projects/{id}/operations/rollback` | Rollback changes |
| GET | `/api/projects/{id}/history` | Get operation history |
| POST | `/api/projects/{id}/undo` | Undo last operation |
| POST | `/api/projects/{id}/redo` | Redo operation |
| POST | `/api/projects/{id}/history/export` | Export operation history |
| POST | `/api/projects/{id}/history/import` | Import operation history |
| POST | `/api/projects/{id}/history/replay` | Replay operations on new data |

### Agents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents` | List agents |
| POST | `/api/agents` | Create agent |
| GET | `/api/agents/{id}` | Get agent |
| PUT | `/api/agents/{id}` | Update agent |
| DELETE | `/api/agents/{id}` | Delete agent |
| GET | `/api/agents/templates` | List pre-built templates |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/providers` | List providers |
| POST | `/api/ai/analyze` | Analyze data |
| POST | `/api/ai/suggest` | Get suggestions |
| POST | `/api/ai/chat` | Chat with assistant |

### Facets & Clustering
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/facets` | Create facet |
| GET | `/api/projects/{id}/facets` | List facets |
| DELETE | `/api/projects/{id}/facets/{facet_id}` | Delete facet |
| POST | `/api/projects/{id}/cluster` | Run clustering |
| GET | `/api/projects/{id}/clusters` | List clusters |
| POST | `/api/projects/{id}/clusters/merge` | Merge clusters |

### Reconciliation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/reconcile` | Run reconciliation |
| GET | `/api/projects/{id}/reconcile/matches` | List matches |
| POST | `/api/projects/{id}/reconcile/accept` | Accept match |
| POST | `/api/projects/{id}/reconcile/reject` | Reject match |

---

## UI/UX Guidelines

### General
- AJAX-like updates with instant partial refreshes
- Optimistic UI updates where appropriate
- Loading states for async operations
- Error boundaries with user-friendly messages

### Data Table
- Sortable columns
- Filterable columns
- Resizable columns
- Column selection (checkbox in header)
- Row selection for operations

### Operation Flow
```
Select Columns → Choose Operation → Configure → Preview → Commit/Rollback
```

### Notifications
- Toast notifications (success, error, warning, info)
- Persistent notifications for long operations
- Progress bars with percentage

### Before/After Comparison
- Side-by-side view (default)
- Toggle view (switch between before/after)
- Diff highlighting (changed cells)

### Faceted Browsing UI
- Facet panel on left side
- Collapsible facet groups
- Visual indicators for selected values
- Count badges for each value
- Range sliders for numeric facets
- Timeline picker for date facets

### Clustering UI
- Cluster preview modal
- Side-by-side value comparison
- Similarity score display
- Bulk select/deselect
- Merge confirmation dialog

---

## Security Considerations

1. **No arbitrary Python execution** - Use predefined function library only
2. **Input validation** - All user inputs sanitized
3. **Rate limiting** - Per-user and per-endpoint limits
4. **API key encryption** - User's AI provider keys encrypted at rest
5. **Row-level security** - Users can only access their own data
6. **Audit logging** - Track all operations for debugging

---

## MVP Scope

### Included
- User registration/login
- Project CRUD
- Agent CRUD + pre-built templates
- Import/Export (CSV, Excel, JSON)
- Standard operations
- Simple cleaning operations
- AI cleaning operations
- Preview + Before/After
- Operation history (undo/redo)
- Column profiling
- Notification system
- Free + Pro tiers

### Deferred (Post-MVP)
- Database import/export (SQLAlchemy connections)
- Collaboration features
- Enterprise tier
- Templates for cleaning workflows
- Advanced scheduling/batch processing
- Faceted browsing
- Clustering algorithms
- Reconciliation services
- Operation replay/export

### Deferred (Post-MVP)
- Database import/export (SQLAlchemy connections)
- Collaboration features
- Enterprise tier
- Templates for cleaning workflows
- Advanced scheduling/batch processing

---

## Development Phases

### Phase 1: Foundation
- [ ] User authentication
- [ ] Database setup (PostgreSQL)
- [ ] Project CRUD
- [ ] Basic dataset import/export

### Phase 2: Core Operations
- [ ] Standard operations
- [ ] Simple cleaning operations
- [ ] Preview system
- [ ] Operation history

### Phase 3: AI Integration
- [ ] Agent management
- [ ] AI cleaning operations
- [ ] Batch processing
- [ ] Rate limiting

### Phase 4: UX Polish
- [ ] Column profiling
- [ ] Notifications
- [ ] Before/After comparison
- [ ] Assistant wizard

### Phase 5: Advanced Features
- [ ] Faceted browsing
- [ ] Clustering algorithms
- [ ] Reconciliation services
- [ ] Operation replay/export

### Phase 6: Billing & Launch

### Phase 5: Billing & Launch
- [ ] Lago integration
- [ ] Tier enforcement
- [ ] Landing page
- [ ] Pricing page

---

*Document Version: 2.0*
*Last Updated: 2026-03-26*

---

*Document Version: 1.0*
*Last Updated: 2026-02-24*
