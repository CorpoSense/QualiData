# MasterDataCleaner - Development TODO

Track progress for the MasterDataCleaner SaaS project.

---

## Phase 1: Foundation

### Authentication
- [ ] Setup user registration (email/password)
- [ ] Setup user login
- [ ] Add OAuth providers (Google, GitHub)
- [ ] Implement JWT token management
- [ ] Add password reset flow
- [ ] Create user model and migrations

### Database Setup
- [ ] Configure PostgreSQL connection
- [ ] Setup SQLAlchemy models
- [ ] Create database migrations (Alembic)
- [ ] Implement connection pooling
- [ ] Add MySQL support (optional)

### Project Management
- [ ] Create project model
- [ ] Implement project CRUD endpoints
- [ ] Add project listing with pagination
- [ ] Implement project search/filter
- [ ] Add row count and storage tracking

### Dataset Import/Export
- [ ] CSV import
- [ ] Excel (.xlsx, .xls) import
- [ ] JSON import
- [ ] CSV export
- [ ] Excel export
- [ ] JSON export
- [ ] Clipboard import (paste CSV)
- [ ] Clipboard export (copy to clipboard)

---

## Phase 2: Core Operations

### Standard Operations (pandas-based)
- [ ] Add column (empty/default/calculated)
- [ ] Remove column(s)
- [ ] Rename column
- [ ] Merge columns (concatenate with delimiter)
- [ ] Split column (delimiter/regex/count)
- [ ] Duplicate column
- [ ] Reorder columns (drag-and-drop)

### Simple Cleaning Operations
- [ ] Strip whitespace
- [ ] Convert to uppercase
- [ ] Convert to lowercase
- [ ] Convert to title case
- [ ] Remove duplicates
- [ ] Handle missing values (fillna, impute)
- [ ] Standardize date/time formats
- [ ] Fix structural errors (typos, capitalization)
- [ ] Custom function chaining (predefined library)

### Preview System
- [ ] Implement preview endpoint
- [ ] Add row count options (25, 50, 100)
- [ ] Create scrollable data table
- [ ] Display summary statistics

### Operation History
- [ ] Create operation history model
- [ ] Implement undo (single step)
- [ ] Implement redo (single step)
- [ ] Add history stack with configurable limit
- [ ] Create history list view

---

## Phase 3: AI Integration

### Agent Management
- [ ] Create agent model
- [ ] Implement agent CRUD endpoints
- [ ] Add provider/model selection
- [ ] Create system prompt editor
- [ ] Add prompt template support
- [ ] Implement temperature configuration

### Pre-built Agent Templates
- [ ] Email Normalizer agent
- [ ] Address Formatter agent
- [ ] Phone Number Formatter agent
- [ ] Text Cleaner agent
- [ ] Date Parser agent

### AI Cleaning Operations
- [ ] Create AI operation endpoint
- [ ] Implement batch processing
- [ ] Add column selection for context
- [ ] Support summary statistics for agent
- [ ] Implement cross-row context option
- [ ] Handle structured JSON output
- [ ] Add progress tracking

### Rate Limiting & Observability
- [ ] Implement global sleep between requests
- [ ] Add per-provider rate limits
- [ ] Display quota warnings
- [ ] Integrate LangSmith observability
- [ ] Track API usage per user

---

## Phase 4: UX Polish

### Column Profiling
- [ ] Auto-detect data types
- [ ] Calculate column statistics
- [ ] Display categorical stats (count, distinct, mode)
- [ ] Display numerical stats (sum, avg, median, min, max)
- [ ] Highlight data quality issues

### Notifications
- [ ] Create notification system
- [ ] Add real-time updates (WebSocket/SSE)
- [ ] Show operation progress
- [ ] Display success/error messages
- [ ] Add rate limit warnings

### Before/After Comparison
- [ ] Side-by-side view
- [ ] Toggle view (before/after switch)
- [ ] Diff highlighting for changed cells
- [ ] Summary comparison stats

### Assistant Feature
- [ ] Create step-by-step wizard
- [ ] Implement data analysis step
- [ ] Add suggestion review step
- [ ] Create operation selection step
- [ ] Add confirmation step

---

## Phase 5: Billing & Launch

### Lago Integration
- [ ] Setup Lago connection
- [ ] Create billing plans
- [ ] Implement subscription management
- [ ] Add usage tracking
- [ ] Generate invoices
- [ ] Handle payment webhooks

### Tier Enforcement
- [ ] Implement row limits per tier
- [ ] Add storage limits per tier
- [ ] Restrict project count per tier
- [ ] Block operations on limit exceeded
- [ ] Add upgrade prompts

### Landing Page
- [ ] Design hero section
- [ ] Add features showcase
- [ ] Create pricing table
- [ ] Add FAQ section
- [ ] Implement call-to-action buttons

### Pricing Page
- [ ] Create tier comparison table
- [ ] Add feature matrix
- [ ] Implement plan selector
- [ ] Add monthly/yearly toggle
- [ ] Create checkout flow

### Final Polish
- [ ] Add loading states
- [ ] Implement error boundaries
- [ ] Optimize performance
- [ ] Add SEO meta tags
- [ ] Create sitemap

---

## DevOps & Infrastructure

### Testing
- [ ] Unit tests for all services
- [ ] Integration tests for API endpoints
- [ ] E2E tests for critical flows
- [ ] Add test coverage reporting

### CI/CD
- [x] GitHub Actions workflow for backend tests
- [ ] GitHub Actions workflow for frontend tests
- [ ] Automated deployment pipeline
- [ ] Staging environment setup

### Monitoring
- [ ] Add application logging
- [ ] Setup error tracking (Sentry)
- [ ] Add performance monitoring
- [ ] Create health check endpoints

---

## Documentation

- [x] README.md with setup instructions
- [x] SPEC.md with full specification
- [x] MIGRATION.md with migration guide
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide
- [ ] Contributing guide

---

## Collaboration (Enterprise Only)

- [ ] Team member management
- [ ] Role-based access control
- [ ] Project sharing
- [ ] Activity logging
- [ ] Comments/annotations

---

*Last updated: 2026-02-24*
