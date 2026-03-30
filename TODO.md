# TODO - MasterDataCleaner

Track tasks and improvements for the project.

---

## Pending Tasks

### AI Provider Updates

- [ ] Update default LLM models for each provider:
  - [ ] OpenRouter: `openrouter/auto`
  - [ ] OpenAI: `gpt-5.4-mini`
  - [ ] Anthropic: `claude-sonnet-4-6`
  - [ ] Google: `gemini-flash-latest`
  - [ ] Ollama: `qwen3.5`
  - [ ] Groq: `openai/gpt-oss-120b`

**Files to update:**
- `backend/app/services/ai_provider.py` - `DEFAULT_MODELS` constant
- `docs/features/ai-providers.md` - Provider comparison table
- `AGENTS.md` - Default models reference

---

### Export Features

- [x] **Export to Database**
  - Export cleaned data to same or different database connection
  - Options: create new table or append to existing table
  - Support same databases as import (PostgreSQL, MySQL, SQLite, SQL Server)
  - Add database tab to export modal (similar to import)
  - Reuse connection UI components from import feature
  - Add validation and warnings for schema mismatches

- [x] **Export to Parquet format**
  - Add Parquet export option (simple, uncompressed)
  - Support standard .parquet files

---

### Dataset Management

- [ ] **Clone Dataset**
  - Add "Clone" option to dataset card menu
  - Create exact copy with different name
  - Support multi-select for bulk clone

- [ ] **Bulk Delete Datasets**
  - Add multi-select checkboxes to dataset cards
  - Add bulk delete action with confirmation
  - Update existing multi-check UI from merge feature

---

### Free Plan Restrictions

- [ ] **Implement Free Plan Limits**
  - Scan codebase for features requiring restrictions
  - Implement plan-based profiling at backend
  - Show friendly limit warnings (not errors) when hitting limits
  - Display upgrade prompts at limit boundaries
  - Reference SPEC.md for tier limits:
    - Free: 1 project, 1,000 rows, 5 MB storage
    - Pro: 10 projects, 50,000 rows, 100 MB storage
    - Enterprise: Unlimited projects, 500,000 rows, 1 GB storage

---

### Documentation

- [x] **Comprehensive Documentation**
  - Create hierarchical markdown documentation in `docs/` directory
  - Include: overview, getting started, features, architecture, API reference, guides
  - Target audience: users, developers, AI agents
  - Exclude: bug reports, package versions, irrelevant technical details
  - **Completed:** 15 markdown files created in `docs/` directory

- [x] **Update README.md**
  - Sync with current project state
  - Add links to new documentation
  - Update feature list and tech stack
  - **Completed:** README.md updated with full documentation links and current features

---

### API Automation Feature

- [ ] **Public API for Integrations**
  - Create API endpoints for all UI operations
  - Generate API documentation (improve existing /docs)
  - Add API key management for users
  - Restrict to paid plans (Pro/Enterprise)
  - Add rate limiting per API key
  - Include usage tracking

**Considerations:**
- Authentication via API keys
- Webhook support for async operations
- SDK examples for common languages

---

### Data Analysis Page (New Feature)

- [ ] **Data Visualization & Analysis**
  - Create new "Analysis" page/route similar to DataViewer
  - Integrate `vue-chartjs` for graphs
  - Implement smart chart type detection based on data types:
    - Categorical → Bar chart
    - Numerical → Histogram, Box plot
    - Time series → Line chart
    - Relationships → Scatter plot
  - Add AI agent for chart suggestions

- [ ] **Data Science Algorithms**
  - Implement algorithms:
    - Regression (Logistic, Linear)
    - Clustering (K-Means, Hierarchical)
    - Classification
    - Time Series Analysis
  - Add target column selection for supervised learning
  - Display results with predictions

- [ ] **Outlier Detection**
  - Box plot visualization for outlier detection
  - Options: delete, filter, or sample outliers
  - Show impact preview before applying

- [ ] **Feature Engineering Operations**
  - One-Hot Encoding for categorical variables
  - Label Encoding
  - Value mapping
  - Binning/Discretization
  - Scaling numerical values (min/max, standard)
  - Follow existing operation UI pattern:
    - Modal with operation description
    - Step-by-step wizard with preview
    - Apply to all or subset
    - Log to operation history (undo/redo support)
    - AI Assistant integration

- [ ] **Workflow Integration**
  - Add navigation between Analysis and DataViewer
  - Save analysis results as new dataset
  - Export analysis visualizations

---

### Authentication & Security Improvements

- [ ] **Evaluate better-auth/vue**
  - Compare with current JWT-based auth
  - Assess benefits: OAuth providers, session management, CSRF protection
  - Estimate migration effort
  - Document pros/cons for decision

- [ ] **Billing Integration (Lago)**
  - Integrate Lago API for billing
  - Implement plan management (Free, Pro, Enterprise)
  - Add usage tracking
  - Generate invoices
  - Add upgrade/downgrade flows
  - Required before public launch

---

### AI Chat Feature (Future)

- [ ] **Free AI Chat with Context**
  - Full chat interface with conversation history
  - Context: N rows/columns as input
  - Features:
    - Sidebar with chat history
    - File upload support
    - Text-to-speech (optional)
    - Function calling to execute data operations
  - **Note:** Very high effort - major feature requiring careful planning

---

### Project Naming

- [ ] **Consider Renaming Project**
  - Current: "MasterDataCleaner"
  - Suggestion: "CleanOps" or similar
  - Evaluate branding, domain availability, trademark concerns

---

## Completed Tasks

### AI Operations
- [x] AI Clean operations with loop/cycle through rows
- [x] Optional sleep time between cycles to avoid throttling

### Data Table Features
- [x] Sorting capabilities with toggleable up/down buttons
- [x] Search feature in text input
- [x] Delete rows (from beginning, from row N to end)
- [x] Extract JSON sub-values (automated key extraction)
- [x] Dynamic model list from provider APIs (HuggingFace compatibility)
- [x] Multi-undo in history operations
- [x] Reorder columns with arrow buttons
- [x] Reorder rows with arrow buttons (multi-select mode)

### UI Improvements
- [x] Project card padding/margins
- [x] History sidebar padding/margins
- [x] Edit/rename dataset in card dropdown
- [x] Replace alert()/prompt() with modals
- [x] Enhanced operation history details modal
- [x] Improved fillna options (mean, median, custom value)
- [x] Step-by-Step AI Clean assistant
- [x] Operations listing with useful information
- [x] Delete All button in operations sidebar
- [x] Data table customization dialog (index, multi-select, sorting)
- [x] Add record to dataset (single/bulk import)
- [x] Operations import/export (JSON format)
- [x] HuggingFace models endpoint integration
- [x] Operation modals with descriptions and options
- [x] Fuzzy match deduplication improvements
- [x] Merge/Join columns operation
- [x] Split column operation
- [x] Preview modal UI fix (nested dialogs)
- [x] Merge/Union multiple datasets
- [x] In-place cell editing (double-click modal)
- [x] ML operations: One-Hot Encoding, Label Encoding, Mapping, Binning
- [x] Scaling numerical values
- [x] Clone/Copy column operation

### Security
- [x] Encrypt AI provider API keys at rest
- [x] Tests for encryption/decryption

### Bug Fixes
- [x] Project page operations listing (Vue iteration error)
- [x] Dashboard import button routing

### Documentation
- [x] Create comprehensive documentation in `docs/` directory
- [x] Create AGENTS.md for AI agents
- [x] Create TODO.md for task tracking

---

## Discussion Items

These items require discussion/decision before implementation:

- **AI Chat Feature** - Major undertaking, needs detailed planning
- **Project Renaming** - Branding decision
- **Better-auth Integration** - Evaluate if current auth is sufficient
- **Data Analysis Scope** - Prioritize which algorithms/charts first

---

*Last updated: March 2026*
