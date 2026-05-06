
# TODO - MasterDataCleaner

Track tasks and improvements for the project.

---

## Pending Tasks

#### AI Agent Capabilities
- [ ] Support different type of memories
- [ ] Support uploading a file.

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

### AI Chat Feature (Future)

- [-] AI Chat with Context
  - [x] Full chat interface with conversation history
  - [x] Context: N rows/columns as input
  - [x] Basic Features:
    - Sidebar with chat history
    - Text-to-speech (optional)
  - [ ] Advanced Features:
    - File upload support
    - Function calling to execute data operations

#### Video
- [ ] Create a video presenation and place it in the home page

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

### Project Naming

- [ ] **Consider Renaming Project**
  - Current: "MasterDataCleaner"
  - Suggestion: "CleanOps" or similar
  - Evaluate branding, domain availability, trademark concerns

---

### Fix bugs:
- [x] Update a cell's value is not working when dataset in filtered.
- [x] Persist column(s) selection after any operation where possible (moving column, refresh page...)
- [x] Persist columns order after any operation.
- [x] Display correct number of dataset in each project.
- [x] Profile is only showing 500 rows!
- [x] Pivot need some bug fixes:
  - [x] Ability to select columns (display list of columns with the ability to drag a column to either "rows" or "columns" section which both accept drop)
  - [x] Fix resize issue it get's reset to default width after resizing

## Improvments:

- [x] Mapping multiple values with the ability to use regex
- [x] Improve error handling in Pivot table by displaying more explicit error message (rather than `Failed to fetch` which may occurs in certains situations when trying to use numerical values in rows or columns titles) to help user understand the issue and solve it.
- [x] Add extract pattern in string column.
- [x] Default value for rename column.
- [x] Make the "Projects" menu item in the navbar a dropdown menu to list projects and theirs datasets.
- [x] Add an extended menu for multi-filtering that is almost similar to Excel's while showing unique values and theirs counts.
- [x] The user is able to hide some columns to save some screen space and work easily on the visible columns.
- [x] Add an option to allow the user choose whether to apply operation on the invisible columns.

#### Apply on selected rows/columns
- [x] The ability to apply any operation to any selected combination of: rows, columns or rows and columns.

#### Fuzzy matching
- [x] Add the footer option to the data table.

#### Fuzzy matching
- [x] Add the ability to merge similar values instead of deleting them with a visual selection and AI suggestion

#### Moving columns
- [x] Display a modal with all existing columns and the ability to move up/down any selected column(s)


#### Database schema
- [x] Consider reviewing the database structure (the `preview_data` looks redandunt, why there is an empty `data_json`...)

---

### Pivot Tables
- [x] Provide a multple and flexible ways to display a pivot tables
- [x] Provide a checkbox option to enable/disable including None values.
- [x] Add totals for both: rows and columns
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

- [x] **Clone Dataset**
  - Add "Clone" option to dataset card menu
  - Create exact copy with different name
  - Support multi-select for bulk clone

- [x] **Bulk Delete Datasets**
  - Add multi-select checkboxes to dataset cards
  - Add bulk delete action with confirmation
  - Update existing multi-check UI from merge feature

- [x] **Copy/Move Datasets to Another Project**
  - Add "Copy to Project" and "Move to Project" buttons in selection bar
  - Modal to select target project from dropdown
  - Backend endpoint `/api/datasets/copy-move` with copy/move actions
  - Updates project stats (row_count, storage_bytes) for both source and target
  - Copy: clones datasets to target project (originals remain)
  - Move: transfers datasets to target project (originals removed)

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

*Last updated: May 2026*
