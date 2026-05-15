# MasterDataCleaner Features

A comprehensive overview of all features and capabilities.

## Data Import & Export

### Import Sources

| Source | Formats | Description |
|--------|---------|-------------|
| **File Upload** | CSV, Excel (.xlsx, .xls), JSON | Upload files from your computer |
| **Clipboard** | CSV, TSV, tabular data | Paste data directly from spreadsheets |
| **Database** | PostgreSQL, MySQL, SQL Server | Connect to external databases |
| **Remote** | FTP, SFTP | Fetch files from remote servers |

### Import Features
- **Auto-detection** - Automatically detect delimiters, encoding, and data types
- **Preview** - Review data before importing
- **Schema mapping** - Configure column names and types
- **Validation** - Check for data quality issues on import

### Export Formats

| Format | Use Case |
|--------|----------|
| **CSV** | Universal compatibility, small file size |
| **Excel** | Rich formatting, multiple sheets |
| **JSON** | API integration, nested data |
| **Database** | Direct export to production databases |
| **Clipboard** | Quick copy-paste to other applications |

## Data Operations

### Standard Operations

Structural transformations for your dataset:

| Operation | Description | Parameters |
|-----------|-------------|------------|
| **Add Column** | Create new column | Empty, default value, or calculated expression |
| **Remove Column** | Delete column(s) | Column selection |
| **Rename Column** | Change column name | New name |
| **Merge Columns** | Concatenate multiple columns | Delimiter, columns to merge |
| **Split Column** | Split into multiple columns | Delimiter or regex, number of splits |
| **Duplicate Column** | Copy column | New column name |
| **Reorder Columns** | Change column order | Drag-and-drop interface |

### String Operations

Text cleaning and transformation:

| Operation | Description | Example |
|-----------|-------------|---------|
| **Trim** | Remove leading/trailing whitespace | `"  hello "` → `"hello"` |
| **Lowercase** | Convert to lowercase | `"HELLO"` → `"hello"` |
| **Uppercase** | Convert to uppercase | `"hello"` → `"HELLO"` |
| **Title Case** | Capitalize first letter of each word | `"hello world"` → `"Hello World"` |
| **Capitalize** | Capitalize first letter | `"hello"` → `"Hello"` |
| **Find & Replace** | Replace text patterns | `"cat"` → `"dog"` |
| **Extract JSON** | Extract value from JSON string | `{"name":"John"}` → `"John"` |

### Missing Values Operations

Handle null and empty values:

| Operation | Description | Use Case |
|-----------|-------------|----------|
| **Drop Rows** | Remove rows with nulls | Clean dataset, remove incomplete records |
| **Fill with Value** | Replace nulls with constant | Fill with "Unknown", 0, etc. |
| **Fill with Mean** | Replace nulls with column mean | Numeric columns |
| **Fill with Median** | Replace nulls with column median | Numeric columns with outliers |
| **Fill with Mode** | Replace nulls with most frequent value | Categorical columns |
| **Forward Fill** | Use previous row's value | Time series data |
| **Backward Fill** | Use next row's value | Time series data |

### Date & Time Operations

Parse and transform datetime data:

| Operation | Description | Output |
|-----------|-------------|--------|
| **Parse Datetime** | Convert text to datetime | Standardized datetime format |
| **Extract Year** | Extract year from date | `2024` |
| **Extract Month** | Extract month from date | `3` or `March` |
| **Extract Day** | Extract day from date | `15` |
| **Extract Hour** | Extract hour from timestamp | `14` |
| **Format Date** | Convert to specific format | `"YYYY-MM-DD"` |

### Deduplication

Remove duplicate records:

| Operation | Description | Options |
|-----------|-------------|---------|
| **Exact Deduplication** | Remove identical rows | Select subset of columns |
| **Fuzzy Deduplication** | Remove similar (not exact) matches | Similarity threshold |
| **Keep First/Last** | Which duplicate to retain | First, last, or none |

### AI-Powered Operations

Intelligent cleaning using AI:

| Feature | Description |
|---------|-------------|
| **AI Analysis** | Automatically detect data quality issues |
| **AI Cleaning** | Transform data using natural language prompts |
| **Batch Processing** | Process data in configurable batch sizes |
| **Cross-Row Context** | Use previous/next rows for context |
| **Confidence Scoring** | See AI confidence for each transformation |
| **Preview & Review** | Review changes before committing |

#### AI Use Cases
- **Email normalization** - Standardize email formats
- **Address formatting** - Parse and standardize addresses
- **Phone number formatting** - Convert to international format
- **Text cleanup** - Remove special characters, fix encoding
- **Category mapping** - Map variations to standard categories
- **Entity extraction** - Extract names, dates, amounts from text

## Data Preview & Profiling

### Preview Panel

Real-time data visualization:

| Feature | Description |
|---------|-------------|
| **Row Display** | Show 25, 50, or 100 rows at a time |
| **Scrollable Table** | Navigate large datasets |
| **Before/After Comparison** | Side-by-side view of changes |
| **Diff Highlighting** | Highlight modified cells |
| **Search & Filter** | Find specific values |
| **Column Sorting** | Sort by any column |
| **Column Selection** | Select columns for operations |

### Column Profiling

Automatic data quality analysis:

| Data Type | Statistics |
|-----------|------------|
| **Categorical** | Count, distinct count, most frequent values, null count |
| **Numerical** | Count, sum, average, median, min, max, standard deviation |
| **Date/Time** | Min, max, range, null count |

### Issue Detection

Automatic highlighting of potential problems:
- **Null values** - Missing data indicators
- **Mixed types** - Columns with inconsistent data types
- **Outliers** - Values outside expected ranges
- **Duplicates** - Repeated records
- **Format inconsistencies** - Varying date/number formats

## Operation History

### Undo/Redo System

Full control over your changes:

| Feature | Description |
|---------|-------------|
| **Operation Stack** | Track last N operations (configurable by tier) |
| **Undo** | Revert last operation |
| **Redo** | Reapply undone operation |
| **History Browser** | View all past operations |
| **Restore Point** | Click to restore any previous state |
| **Snapshots** | Before/after state for each operation |

### Operation Details

Each operation records:
- Operation type and name
- Configuration parameters
- Affected columns
- Before/after snapshots
- Timestamp
- Dataset association

## Agent Management

### AI Agents

Configurable AI assistants for specific tasks:

| Property | Description |
|----------|-------------|
| **Name** | Unique identifier for the agent |
| **Provider** | AI provider (OpenAI, Anthropic, Google, etc.) |
| **Model** | Specific model to use |
| **System Prompt** | Agent personality and instructions |
| **Prompt Template** | Reusable template for prompts |
| **Temperature** | Creativity level (0-1) |
| **API Key** | Provider API credentials |
| **Base URL** | Custom endpoint (for self-hosted models) |

### Pre-built Agent Templates

Ready-to-use agents for common tasks:

| Template | Purpose |
|----------|---------|
| **Email Normalizer** | Standardize email formats to lowercase |
| **Address Formatter** | Parse and format addresses |
| **Phone Number Formatter** | Convert to international format |
| **Text Cleaner** | Remove special characters, fix encoding |
| **Date Parser** | Parse various date formats to standard |

### Custom Agents

Create agents for your specific needs:
1. Define the agent's purpose
2. Choose AI provider and model
3. Write system prompt with instructions
4. Create prompt template for reuse
5. Test with sample data
6. Save for future use

## Assistant Feature

### Step-by-Step Wizard

Guided data cleaning workflow:

1. **Analyze** - AI analyzes your data and identifies issues
2. **Review** - Review suggested operations with previews
3. **Select** - Choose which operations to apply
4. **Confirm** - Final review before committing changes

### AI Suggestions

The assistant can suggest:
- Missing value handling strategies
- Format standardization approaches
- Duplicate removal options
- Column type corrections
- Data validation rules

## Notifications

Real-time feedback system:

| Notification Type | Description |
|-------------------|-------------|
| **Success** | Operation completed successfully |
| **Error** | Operation failed with details |
| **Warning** | Potential issues or concerns |
| **Info** | General information |
| **Progress** | Long-running operation status |

### Progress Tracking
- Percentage complete for batch operations
- Current row being processed
- Estimated time remaining
- Rate limit warnings

## User Management

### Authentication

| Method | Description |
|--------|-------------|
| **Email/Password** | Traditional registration and login |
| **OAuth** | Google and GitHub single sign-on |
| **Password Reset** | Email-based password recovery |
| **Session Management** | JWT tokens for secure sessions |

### User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access, user management, all features |
| **Manager** | Create projects, manage agents, collaboration |
| **User** | Basic data cleaning, limited projects |

### Tier Limits

| Tier | Projects | Max Rows | Storage | History | Collaboration |
|------|----------|----------|---------|---------|---------------|
| **Free** | 1 | 1,000 | 5 MB | 10 ops | No |
| **Pro** | 10 | 50,000 | 100 MB | 100 ops | No |
| **Enterprise** | Unlimited | 500,000 | 1 GB | 500 ops | Yes (5 users) |

## Rate Limiting

API protection and fair usage:

| Provider | Requests/min | Tokens/min |
|----------|--------------|------------|
| OpenAI | 500 | 90,000 |
| Anthropic | 60 | 40,000 |
| Google | 300 | 60,000 |
| Groq | 30 | 18,000 |
| NVIDIA | 30 | 18,000 |
| DeepSeek | 60 | 30,000 |
| OpenRouter | Varies | Varies |

Features:
- Automatic rate limit handling with retries
- Progress indicators during delays
- Quota warnings before limits reached

## Search & Filter

### Data Search
- **Global search** - Search across all columns
- **Column-specific search** - Search within selected column
- **Regex support** - Advanced pattern matching
- **Case sensitivity** - Toggle case-sensitive search

### Row Filtering
- **Filter by value** - Show rows matching criteria
- **Filter by type** - Show rows with specific data types
- **Filter nulls** - Show/hide rows with null values
- **Active filter indicator** - See current filter status

## Collaboration (Enterprise)

### Team Features
- **Shared projects** - Multiple users on same dataset
- **Role-based access** - Owner, Editor, Viewer permissions
- **Activity tracking** - See who made what changes
- **Comments** - Add notes to operations

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
