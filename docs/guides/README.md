# User Guides

Step-by-step guides for common tasks and workflows.

## Table of Contents

- **[Import Data](#import-data)** - Upload or paste data
- **[Clean Data](#clean-data)** - Apply cleaning operations
- **[AI Cleaning](#ai-cleaning)** - Use AI for intelligent cleaning
- **[Export Data](#export-data)** - Download cleaned data
- **[Manage Agents](#manage-agents)** - Create and configure AI agents
- **[Undo/Redo](#undo-and-redo)** - Revert and reapply operations

---

## Import Data

### From File

**Step 1:** Navigate to Project
1. Go to **Projects** page
2. Click on your project or create new one
3. Click **"Import Data"** button

**Step 2:** Choose File
1. Select **"File Upload"** tab
2. Click **"Choose File"** or drag and drop
3. Supported formats: CSV, Excel (.xlsx, .xls), JSON

**Step 3:** Configure Import
1. Review detected delimiter and encoding
2. Preview the data
3. Adjust settings if needed:
   - Delimiter (comma, tab, semicolon, etc.)
   - Encoding (UTF-8, Latin-1, etc.)
   - Header row detection

**Step 4:** Import
1. Click **"Import"** button
2. Wait for processing to complete
3. Data appears in the viewer

### From Clipboard

**Step 1:** Copy Data
1. Open your spreadsheet (Excel, Google Sheets, etc.)
2. Select the data range
3. Copy (Ctrl+C or Cmd+C)

**Step 2:** Paste in MasterDataCleaner
1. Go to your project
2. Click **"Import Data"**
3. Select **"Clipboard"** tab
4. Paste into the text area (Ctrl+V or Cmd+V)

**Step 3:** Import
1. Review the preview
2. Click **"Import"** button

### From Database (Advanced)

**Step 1:** Configure Connection
1. Go to **Import Data**
2. Select **"Database"** tab
3. Choose database type: PostgreSQL, MySQL

**Step 2:** Enter Connection Details
```
Host: your-database-host.com
Port: 5432
Database: database_name
Username: your_username
Password: your_password
```

**Step 3:** Select Table
1. Choose schema
2. Select table
3. Preview data

**Step 4:** Import
1. Click **"Import"**
2. Data loads into project

---

## Clean Data

### Basic Cleaning Workflow

**Step 1:** Select Columns
1. Click column headers to select
2. Use Ctrl/Cmd+click for multiple columns
3. Use Shift+click for range selection

**Step 2:** Choose Operation
1. Click operation dropdown (e.g., **"String Ops"**)
2. Select desired operation
3. Configure parameters if needed

**Step 3:** Preview Changes
1. Review before/after comparison
2. Check affected rows
3. Verify the transformation

**Step 4:** Apply
1. Click **"Apply"** to commit changes
2. Or **"Cancel"** to discard

### Common Cleaning Tasks

#### Remove Extra Spaces

**Problem:** Names have leading/trailing spaces

**Solution:**
1. Select text columns (name, email, etc.)
2. Click **"String Ops"** → **"Trim Whitespace"**
3. Preview shows spaces removed
4. Click **"Apply"**

#### Standardize Email Case

**Problem:** Emails in mixed case (John@Example.COM)

**Solution:**
1. Select email column
2. Click **"String Ops"** → **"Lowercase"**
3. Preview shows all lowercase
4. Click **"Apply"**

#### Fill Missing Values

**Problem:** Column has empty cells

**Solution:**
1. Select column with missing values
2. Click **"Missing Values"** → **"Fill with Value"**
3. Enter fill value (e.g., "Unknown", 0)
4. Preview shows filled values
5. Click **"Apply"**

**Alternative Methods:**
- **Mean/Median** - For numeric columns
- **Mode** - For categorical columns
- **Forward/Backward Fill** - For time series

#### Remove Duplicates

**Problem:** Dataset has duplicate rows

**Solution:**
1. Select columns to check for duplicates
2. Click **"String Ops"** → **"Remove Duplicates"**
3. Choose: Keep First, Last, or None
4. Preview shows duplicates removed
5. Click **"Apply"**

#### Parse Dates

**Problem:** Dates in various formats

**Solution:**
1. Select date column
2. Click **"Date Ops"** → **"Parse Datetime"**
3. Choose target format (YYYY-MM-DD)
4. Preview shows standardized dates
5. Click **"Apply"**

---

## AI Cleaning

### Setup AI Agent

**Step 1:** Go to Agents
1. Click **"Agents"** in navigation
2. Click **"Create Agent"**

**Step 2:** Configure Agent
1. **Name:** Email Normalizer
2. **Provider:** Select your provider (OpenAI, etc.)
3. **Model:** Use default or select specific model
4. **System Prompt:** "You are an email normalization assistant..."
5. **Temperature:** 0.3 (consistent results)
6. Click **"Save"**

### Use AI for Cleaning

**Step 1:** Select Data
1. Go to your project
2. Select column(s) to clean

**Step 2:** Choose AI Clean
1. Click **"AI Clean"** button
2. Select your agent from dropdown

**Step 3:** Enter Prompt
```
Example prompts:

"Convert all emails to lowercase and validate format"

"Standardize phone numbers to (XXX) XXX-XXXX format"

"Parse addresses into: Street, City, State, ZIP"

"Remove special characters and extra spaces"

"Map country variations to ISO codes"
```

**Step 4:** Configure Batch
1. **Batch Size:** 10 rows (default)
2. **Cross-Row Context:** Enable if needed
3. Click **"Start"**

**Step 5:** Review Results
1. Watch progress indicator
2. Review transformations with confidence scores
3. Check low-confidence items manually

**Step 6:** Commit or Adjust
1. Click **"Apply"** to commit all
2. Or adjust individual values
3. Click **"Apply"** when satisfied

### AI Use Cases

#### Email Normalization

**Prompt:**
```
"Convert all emails to lowercase and validate format. 
Mark invalid emails as null."
```

**Result:**
```
John@Example.COM → john@example.com
JANE@TEST.COM → jane@test.com
invalid-email → null
```

#### Phone Number Formatting

**Prompt:**
```
"Format all phone numbers as (XXX) XXX-XXXX. 
Remove country codes and extensions."
```

**Result:**
```
1234567890 → (123) 456-7890
123-456-7890 → (123) 456-7890
(123)456-7890 → (123) 456-7890
```

#### Address Standardization

**Prompt:**
```
"Parse addresses into standardized format:
Street, City, State ZIP

Expand abbreviations: St→Street, Ave→Avenue, NY→New York"
```

**Result:**
```
123 main st, ny 10001 → 123 Main Street, New York, NY 10001
456 oak ave, la 90001 → 456 Oak Avenue, Los Angeles, CA 90001
```

#### Category Mapping

**Prompt:**
```
"Map country variations to ISO codes:
- USA, U.S., United States, America → US
- UK, U.K., United Kingdom, Britain → GB
- Canada, CAN → CA"
```

**Result:**
```
United States → US
UK → GB
CAN → CA
```

---

## Export Data

### Export to File

**Step 1:** Open Project
1. Navigate to your project
2. Ensure all desired operations are applied

**Step 2:** Click Export
1. Click **"Export"** button in toolbar
2. Choose export format

**Step 3:** Choose Format

**CSV:**
- Universal compatibility
- Small file size
- No formatting

**Excel:**
- Rich formatting
- Multiple sheets
- Larger file size

**JSON:**
- API integration
- Nested data support
- Developer friendly

**Step 4:** Download
1. Click **"Download"**
2. File saves to your computer

### Export to Clipboard

**Step 1:** Click Export
1. Click **"Export"** button
2. Select **"Copy to Clipboard"**

**Step 2:** Paste
1. Open destination application
2. Paste (Ctrl+V or Cmd+V)

### Export to Database

**Step 1:** Configure Connection
1. Click **"Export"**
2. Select **"Database"** tab
3. Choose database type

**Step 2:** Enter Details
```
Host: your-database-host.com
Port: 5432
Database: database_name
Table: target_table
Username: your_username
Password: your_password
```

**Step 3:** Map Columns
1. Match source columns to target table
2. Create new table or append to existing

**Step 4:** Export
1. Click **"Export"**
2. Wait for completion
3. Verify in database

---

## Manage Agents

### Create Agent

**Step 1:** Navigate to Agents
1. Click **"Agents"** in main navigation

**Step 2:** Create New Agent
1. Click **"Create Agent"** button
2. Fill in agent details

**Step 3:** Configure Settings

**Basic Info:**
- **Name:** Descriptive name (e.g., "Address Formatter")
- **Description:** What this agent does

**AI Configuration:**
- **Provider:** OpenAI, Anthropic, Google, etc.
- **Model:** Specific model or use default
- **API Key:** Enter if not in .env
- **Base URL:** For custom endpoints

**Prompts:**
- **System Prompt:** Agent's role and instructions
- **Prompt Template:** Reusable prompt structure

**Generation:**
- **Temperature:** 0.0 (deterministic) to 1.0 (creative)
- Lower for consistent transformations
- Higher for creative tasks

**Step 4:** Save
1. Click **"Save"**
2. Agent appears in your agents list

### Edit Agent

**Step 1:** Find Agent
1. Go to **Agents** page
2. Locate agent in list

**Step 2:** Edit
1. Click **"Edit"** button
2. Modify settings
3. Click **"Save"**

### Delete Agent

**Step 1:** Find Agent
1. Go to **Agents** page

**Step 2:** Delete
1. Click **"Delete"** button
2. Confirm deletion

### Use Pre-built Templates

**Step 1:** Browse Templates
1. Go to **Agents** page
2. Click **"Use Template"**

**Step 2:** Select Template
1. Choose from available templates:
   - Email Normalizer
   - Address Formatter
   - Phone Number Formatter
   - Text Cleaner
   - Date Parser

**Step 3:** Customize
1. Modify settings if needed
2. Add your API key
3. Click **"Save"**

---

## Undo and Redo

### Undo Last Operation

**Method 1:** Toolbar Button
1. Click **"Undo"** button in toolbar
2. Last operation is reverted

**Method 2:** History Panel
1. Click **"History"** button
2. Find operation to undo
3. Click **"Undo"** next to operation

### Redo Undone Operation

**Method 1:** Toolbar Button
1. Click **"Redo"** button
2. Last undone operation is reapplied

**Method 2:** History Panel
1. Click **"History"** button
2. Find undone operation (grayed out)
3. Click **"Redo"** next to operation

### Restore to Previous State

**Step 1:** Open History
1. Click **"History"** button in toolbar

**Step 2:** Find State
1. Scroll through operation history
2. Find the state you want to restore

**Step 3:** Restore
1. Click **"Restore"** next to that operation
2. All operations after that point are undone
3. Data returns to that state

### Operation History

**View History:**
1. Click **"History"** button
2. See list of all operations

**History Shows:**
- Operation type and name
- When it was performed
- Which columns were affected
- Whether it's been undone
- Before/after snapshots

**Navigate History:**
- **Up Arrow** - Redo
- **Down Arrow** - Undo
- **Restore Button** - Jump to specific point

---

## Tips & Best Practices

### General Tips

1. **Preview First** - Always review changes before applying
2. **Start Small** - Test operations on sample data first
3. **Save Often** - Commit changes regularly
4. **Use Undo** - Don't worry about mistakes
5. **Backup Important Data** - Export before major changes

### Performance Tips

1. **Select Specific Columns** - Don't process entire dataset unnecessarily
2. **Use Appropriate Batch Sizes** - Balance speed and cost for AI ops
3. **Filter Before Operations** - Work with smaller subsets when possible

### Quality Tips

1. **Check Profiles** - Review column statistics after operations
2. **Compare Before/After** - Use comparison view to verify changes
3. **Spot Check Results** - Manually verify some transformed values

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
