# Data Operations

Complete guide to all data transformation operations available in MasterDataCleaner.

## Operation Categories

MasterDataCleaner organizes operations into logical categories:

1. **[Standard Operations](#standard-operations)** - Structural transformations
2. **[String Operations](#string-operations)** - Text cleaning
3. **[Missing Values](#missing-values)** - Handle nulls and empty data
4. **[Date & Time](#date--time-operations)** - Datetime parsing and extraction
5. **[Deduplication](#deduplication)** - Remove duplicates
6. **[AI Operations](#ai-operations)** - Intelligent cleaning

## Standard Operations

### Add Column

Create a new column in your dataset.

**Options:**
- **Empty** - Create blank column to fill manually
- **Default Value** - Fill with constant value
- **Calculated** - Use pandas expression based on other columns

**Example:**
```
# Calculated column example
Total = Price * Quantity
```

### Remove Column

Delete one or more columns from your dataset.

**Usage:**
1. Select column(s) to remove
2. Click **Standard Ops** → **Remove Column**
3. Confirm deletion

### Rename Column

Change a column's name.

**Usage:**
1. Select column to rename
2. Click **Standard Ops** → **Rename Column**
3. Enter new name
4. Apply

### Merge Columns

Combine multiple columns into one.

**Parameters:**
- **Columns to merge** - Select source columns
- **Delimiter** - Separator between values (space, comma, custom)

**Example:**
```
# Merge First and Last name
Full Name = First Name + " " + Last Name
```

### Split Column

Divide one column into multiple columns.

**Parameters:**
- **Delimiter** - Character to split on (comma, space, custom)
- **Regex** - Advanced pattern matching
- **Number of columns** - How many columns to create

**Example:**
```
# Split "Last, First" into two columns
Split on comma → Column1: Last, Column2: First
```

### Duplicate Column

Create an exact copy of a column.

**Usage:**
1. Select column to duplicate
2. Click **Standard Ops** → **Duplicate Column**
3. Enter new column name

### Reorder Columns

Change the order of columns.

**Usage:**
- Drag and drop column headers
- Use arrow buttons to move selected column

## String Operations

### Trim Whitespace

Remove leading and trailing whitespace from text.

**Before → After:**
```
"  John Doe  " → "John Doe"
```

### Lowercase

Convert all text to lowercase.

**Use cases:**
- Email normalization
- Consistent text comparison

**Before → After:**
```
"John@Example.COM" → "john@example.com"
```

### Uppercase

Convert all text to uppercase.

**Use cases:**
- Country codes
- Status indicators

**Before → After:**
```
"us" → "US"
```

### Title Case

Capitalize the first letter of each word.

**Use cases:**
- Names
- Titles
- Addresses

**Before → After:**
```
"john doe" → "John Doe"
```

### Capitalize

Capitalize only the first letter of the string.

**Before → After:**
```
"hello world" → "Hello world"
```

### Find & Replace

Search for text patterns and replace them.

**Parameters:**
- **Find** - Text or regex pattern to search for
- **Replace** - Replacement text
- **Case sensitive** - Toggle case sensitivity
- **Regex** - Enable regular expressions

**Examples:**
```
# Simple replacement
Find: "St." → Replace: "Street"

# Regex replacement
Find: "\d{3}-\d{4}" → Replace: "XXX-XXXX" (mask phone numbers)
```

### Extract JSON Value

Extract a specific value from a JSON string.

**Parameters:**
- **JSON column** - Column containing JSON
- **Key path** - JSON key to extract (supports nested: `address.city`)

**Before → After:**
```
{"name": "John", "age": 30} → "John" (extracting "name" key)
```

## Missing Values

### Drop Rows with Nulls

Remove any row that contains null values.

**Options:**
- **All columns** - Drop if any column is null
- **Selected columns** - Drop only if specific columns are null

**Use case:** Remove incomplete records

### Fill with Value

Replace null values with a constant.

**Parameters:**
- **Fill value** - Text, number, or date to use
- **Columns** - Which columns to fill

**Examples:**
```
# Fill text
Null → "Unknown"

# Fill numbers
Null → 0

# Fill dates
Null → "2024-01-01"
```

### Fill with Mean

Replace nulls with the column's average value.

**Use case:** Numeric columns with normal distribution

**Example:**
```
Column: [10, 20, null, 30, 40]
Mean: 25
Result: [10, 20, 25, 30, 40]
```

### Fill with Median

Replace nulls with the column's median value.

**Use case:** Numeric columns with outliers

**Example:**
```
Column: [10, 20, null, 30, 1000]
Median: 25 (better than mean of 265)
Result: [10, 20, 25, 30, 1000]
```

### Fill with Mode

Replace nulls with the most frequent value.

**Use case:** Categorical columns

**Example:**
```
Column: ["US", "US", null, "UK", "US"]
Mode: "US"
Result: ["US", "US", "US", "UK", "US"]
```

### Forward Fill

Use the previous row's value to fill nulls.

**Use case:** Time series data

**Example:**
```
Column: [10, null, null, 30, null]
Result: [10, 10, 10, 30, 30]
```

### Backward Fill

Use the next row's value to fill nulls.

**Use case:** Time series data (reverse)

**Example:**
```
Column: [10, null, null, 30, null]
Result: [10, 30, 30, 30, null]
```

## Date & Time Operations

### Parse Datetime

Convert text to standardized datetime format.

**Parameters:**
- **Input format** - Current format (auto-detected or specified)
- **Output format** - Target format

**Supported formats:**
- `MM/DD/YYYY`
- `DD-MM-YYYY`
- `YYYY-MM-DD`
- `MM/DD/YYYY HH:MM:SS`
- And many more...

**Before → After:**
```
"03/15/2024" → "2024-03-15"
"15-Mar-24" → "2024-03-15"
```

### Extract Year

Extract the year from a date column.

**Before → After:**
```
"2024-03-15" → 2024
```

### Extract Month

Extract the month from a date column.

**Options:**
- **Number** - 1-12
- **Name** - January, February, etc.
- **Abbreviated** - Jan, Feb, etc.

**Before → After:**
```
"2024-03-15" → 3 (or "March" or "Mar")
```

### Extract Day

Extract the day of the month.

**Before → After:**
```
"2024-03-15" → 15
```

### Extract Hour

Extract the hour from a timestamp.

**Before → After:**
```
"2024-03-15 14:30:00" → 14
```

### Format Date

Convert date to a specific string format.

**Common formats:**
- `YYYY-MM-DD` - ISO format
- `MM/DD/YYYY` - US format
- `DD/MM/YYYY` - European format
- `MMMM D, YYYY` - Long format

## Deduplication

### Exact Deduplication

Remove rows that are exact duplicates.

**Options:**
- **All columns** - Compare entire row
- **Selected columns** - Compare specific columns only
- **Keep** - First, Last, or None

**Example:**
```
# Before
John, john@example.com
John, john@example.com  (duplicate)
Jane, jane@example.com

# After (Keep First)
John, john@example.com
Jane, jane@example.com
```

### Fuzzy Deduplication

Remove similar (not exact) matches using intelligent comparison.

**Parameters:**
- **Similarity threshold** - How similar to consider duplicate (0-1)
- **Columns to compare** - Which columns to check
- **Keep** - Which duplicate to retain

**Use cases:**
- Typos in names ("Jon" vs "John")
- Format variations ("St." vs "Street")
- Case differences

**Example:**
```
# Before (threshold: 0.9)
John Doe, john@example.com
Jon Doe, john@example.com  (90% similar)
Jane Smith, jane@example.com

# After
John Doe, john@example.com
Jane Smith, jane@example.com
```

## AI Operations

### AI Clean

Use AI to transform data based on natural language instructions.

**Workflow:**
1. Select column(s) to clean
2. Click **AI Clean**
3. Choose an agent
4. Enter your prompt
5. Configure batch size
6. Preview results
7. Commit or rollback

**Prompt Examples:**
```
# Email normalization
"Convert all emails to lowercase and validate format"

# Address formatting
"Parse addresses into: Street, City, State, ZIP"

# Phone formatting
"Format phone numbers as (XXX) XXX-XXXX"

# Text cleanup
"Remove special characters and extra spaces"

# Category mapping
"Map country variations to ISO codes:
 - USA, U.S., United States → US
 - UK, U.K., United Kingdom → GB"
```

### Batch Processing

AI operations process data in batches to:
- Manage API costs
- Enable progress tracking
- Allow preview before full completion

**Configuration:**
- **Batch size** - Rows per API call (default: 10)
- **Delay between batches** - Avoid rate limits

### Cross-Row Context

Enable AI to see previous/next rows for better context.

**Use cases:**
- Sequential data
- Related records
- Pattern recognition

**Example:**
```
# Without context
Input: "Same as above" → AI doesn't know what "above" is

# With context
Input: "Same as above" + previous row → AI understands reference
```

### Confidence Scoring

AI returns confidence level for each transformation.

**Indicators:**
- 🟢 High confidence (0.8-1.0) - Reliable transformation
- 🟡 Medium confidence (0.5-0.8) - Review recommended
- 🔴 Low confidence (<0.5) - Manual review suggested

## Operation Best Practices

### General Guidelines

1. **Preview first** - Always review changes before committing
2. **Backup important data** - Export before major operations
3. **Test on sample** - Try operations on small subset first
4. **Use undo** - Leverage operation history for mistakes

### Performance Tips

1. **Batch large operations** - Process in chunks for better control
2. **Select specific columns** - Don't process entire dataset unnecessarily
3. **Use appropriate operations** - Simple ops are faster than AI

### Quality Assurance

1. **Check profiles** - Review column statistics after operations
2. **Compare before/after** - Use comparison view to verify changes
3. **Validate results** - Spot-check transformed data

## Chaining Operations

Combine multiple operations for complex transformations:

**Example: Clean Customer Data**
```
1. Trim whitespace (all text columns)
2. Lowercase (email column)
3. Fill missing values (country → "Unknown")
4. Remove duplicates (by email)
5. AI Clean (address formatting)
6. Parse dates (signup date column)
```

## Next Steps

- **[AI Providers](ai-providers.md)** - Configure AI for intelligent cleaning
- **[Guides](../guides/README.md)** - Step-by-step tutorials
- **[API Reference](../api-reference/README.md)** - Programmatic access

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
