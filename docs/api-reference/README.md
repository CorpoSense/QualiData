# API Reference

Complete API documentation for MasterDataCleaner.

## Base URL

**Development:** `http://localhost:8000`

**Production:** `https://your-domain.com`

## Authentication

Most endpoints require authentication using JWT tokens.

### Getting a Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the `Authorization` header:

```http
GET /api/projects
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Endpoints

### Health

#### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Authentication

#### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "role": "user"
  }
}
```

#### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "role": "user",
  "tier_limits": {
    "max_projects": 1,
    "max_rows": 1000,
    "max_storage_mb": 5
  }
}
```

---

### Users

#### Get User by ID

```http
GET /api/users/{user_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "role": "user"
}
```

#### Update User

```http
PUT /api/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Name",
  "timezone": "America/New_York"
}
```

#### List All Users (Admin)

```http
GET /api/users
Authorization: Bearer <admin_token>
```

---

### Projects

#### List Projects

```http
GET /api/projects
Authorization: Bearer <token>
```

**Response:**
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "My Project",
      "description": "Project description",
      "row_count": 1000,
      "column_count": 10,
      "storage_bytes": 524288,
      "datasets_count": 2,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-02T00:00:00"
    }
  ]
}
```

#### Create Project

```http
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Project",
  "description": "Project description"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "New Project",
  "description": "Project description",
  "created_at": "2024-01-01T00:00:00"
}
```

#### Get Project

```http
GET /api/projects/{project_id}
Authorization: Bearer <token>
```

#### Update Project

```http
PUT /api/projects/{project_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Delete Project

```http
DELETE /api/projects/{project_id}
Authorization: Bearer <token>
```

---

### Datasets

#### Import Dataset

```http
POST /api/datasets/import
Authorization: Bearer <token>
Content-Type: multipart/form-data

project_id: uuid
file: <file>
# OR
data: <pasted CSV data>
```

**Response:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "name": "data.csv",
  "row_count": 100,
  "columns": ["col1", "col2", "col3"],
  "preview_data": [...],
  "schema": {
    "col1": "string",
    "col2": "int64",
    "col3": "datetime64"
  }
}
```

#### Get Dataset Preview

```http
GET /api/datasets/{dataset_id}/preview?limit=50&offset=0
Authorization: Bearer <token>
```

**Response:**
```json
{
  "data": [...],
  "columns": ["col1", "col2"],
  "total_rows": 1000,
  "limit": 50,
  "offset": 0
}
```

#### Get Dataset Profile

```http
GET /api/datasets/{dataset_id}/profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "columns": [
    {
      "name": "email",
      "type": "string",
      "count": 100,
      "null_count": 5,
      "distinct_count": 95,
      "most_frequent": ["user@example.com"]
    },
    {
      "name": "age",
      "type": "int64",
      "count": 100,
      "null_count": 3,
      "mean": 35.5,
      "min": 18,
      "max": 80,
      "std": 12.3
    }
  ]
}
```

#### Export Dataset

```http
GET /api/datasets/{dataset_id}/export?format=csv
Authorization: Bearer <token>
```

**Response:** File download

---

### Operations

#### Apply Standard Operation

```http
POST /api/operations/standard
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "operation": "add_column",
  "params": {
    "column_name": "new_col",
    "value": "default"
  }
}
```

**Response:**
```json
{
  "success": true,
  "preview": {...},
  "operation_id": "uuid"
}
```

#### Apply Cleaning Operation

```http
POST /api/operations/cleaning
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "operation": "string_strip",
  "columns": ["name", "email"]
}
```

#### Apply AI Operation

```http
POST /api/operations/ai
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "columns": ["address"],
  "agent_id": "uuid",
  "prompt": "Standardize these addresses to: Street, City, State ZIP",
  "batch_size": 10
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "row": 0,
      "original": "123 main st, ny 10001",
      "transformed": "123 Main Street, New York, NY 10001",
      "confidence": 0.95
    }
  ],
  "batch_progress": {
    "current_batch": 1,
    "total_batches": 10
  }
}
```

#### Commit Changes

```http
POST /api/operations/commit
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid"
}
```

#### Rollback Changes

```http
POST /api/operations/rollback
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid"
}
```

#### Get Operation History

```http
GET /api/operations/history?project_id=uuid&limit=10
Authorization: Bearer <token>
```

**Response:**
```json
{
  "operations": [
    {
      "id": "uuid",
      "operation_type": "cleaning",
      "operation_name": "string_strip",
      "columns_affected": ["name", "email"],
      "created_at": "2024-01-01T00:00:00",
      "is_undone": false
    }
  ]
}
```

#### Undo Operation

```http
POST /api/operations/undo
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": "uuid",
  "operation_id": "uuid"
}
```

#### Redo Operation

```http
POST /api/operations/redo
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": "uuid",
  "operation_id": "uuid"
}
```

#### Get Operation Stats

```http
GET /api/operations/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total": 150,
  "active": 140,
  "undone": 10,
  "ai_operations": 25,
  "top_types": [
    {"type": "string_strip", "count": 50},
    {"type": "fillna", "count": 30}
  ]
}
```

#### Get Recent Operations

```http
GET /api/operations/recent?limit=10
Authorization: Bearer <token>
```

---

### Missing Values

#### Fill Missing Values

```http
POST /api/operations/fillna
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "column": "age",
  "method": "mean"
}
```

**Methods:**
- `constant` - Fill with specific value
- `mean` - Fill with column mean
- `median` - Fill with column median
- `mode` - Fill with most frequent value
- `forward` - Forward fill
- `backward` - Backward fill

---

### String Operations

#### Strip Whitespace

```http
POST /api/operations/string/strip
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "columns": ["name", "email"]
}
```

#### Convert Case

```http
POST /api/operations/string/case
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "columns": ["email"],
  "case": "lower"
}
```

**Case options:** `lower`, `upper`, `title`, `capitalize`

---

### Datetime Operations

#### Datetime Operations (Parse, Extract)

```http
POST /api/datasets/{dataset_id}/operations/datetime-operations
Authorization: Bearer <token>
Content-Type: application/json

{
  "columns": ["created_at"],
  "operation": "parse-datetime",
  "error_handling": "coerce",
  "input_format": "%d/%m/%Y",
  "output_format": "%Y-%m-%d",
  "new_column": "parsed_date",
  "fallback_value": "1970-01-01",
  "row_indices": [0, 1, 2]
}
```

**Operations:** `parse-datetime`, `extract-year`, `extract-month`, `extract-day`, `extract-weekday`

**Parameters:**
- `columns` (required): Array of column names
- `operation` (required): Operation to perform
- `error_handling` (optional): `coerce` (default), `fallback`, or `raise`
- `fallback_value` (optional): Value for unparseable rows when `error_handling=fallback`
- `input_format` (optional): Python strptime format (e.g. `%d/%m/%Y`)
- `output_format` (optional): Python strftime format for output
- `new_column` (optional): Write result to a new column (single column only)
- `row_indices` (optional): Apply only to specific rows

---

### Structural Operations

#### Add Column

```http
POST /api/operations/structural/add_column
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "column_name": "new_col",
  "value": "default"
}
```

#### Remove Column

```http
POST /api/operations/structural/remove_column
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "columns": ["unwanted_col"]
}
```

#### Rename Column

```http
POST /api/operations/structural/rename_column
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "old_name": "old_col",
  "new_name": "new_col"
}
```

#### Merge Columns

```http
POST /api/operations/structural/merge_columns
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "columns": ["first_name", "last_name"],
  "new_column": "full_name",
  "delimiter": " "
}
```

#### Split Column

```http
POST /api/operations/structural/split_column
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "column": "full_name",
  "delimiter": " ",
  "num_columns": 2
}
```

---

### Agents

#### List Agents

```http
GET /api/agents
Authorization: Bearer <token>
```

**Response:**
```json
{
  "agents": [
    {
      "id": "uuid",
      "name": "Email Normalizer",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "temperature": 0.3,
      "is_template": false,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### Create Agent

```http
POST /api/agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Custom Agent",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "system_prompt": "You are a data cleaning assistant...",
  "temperature": 0.3
}
```

#### Get Agent

```http
GET /api/agents/{agent_id}
Authorization: Bearer <token>
```

#### Update Agent

```http
PUT /api/agents/{agent_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "temperature": 0.5
}
```

#### Delete Agent

```http
DELETE /api/agents/{agent_id}
Authorization: Bearer <token>
```

#### Get Agent Templates

```http
GET /api/agents/templates
Authorization: Bearer <token>
```

**Response:**
```json
{
  "templates": [
    {
      "name": "Email Normalizer",
      "description": "Standardize email formats",
      "provider": "openai",
      "system_prompt": "...",
      "is_builtin": true
    }
  ]
}
```

---

### AI

#### List Providers

```http
GET /api/ai/providers
Authorization: Bearer <token>
```

**Response:**
```json
{
  "providers": [
    {
      "provider": "openai",
      "default_model": "gpt-4o-mini",
      "supports_base_url": true
    },
    {
      "provider": "anthropic",
      "default_model": "claude-sonnet-4-20250514",
      "supports_base_url": false
    }
  ]
}
```

#### Analyze Data

```http
POST /api/ai/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "openai",
  "data_summary": "Column: email, 100 rows, 5 nulls, mixed case"
}
```

**Response:**
```json
{
  "analysis": "The email column has inconsistent casing and 5% null values. Recommendations: 1) Normalize to lowercase, 2) Fill nulls with 'unknown'...",
  "provider": "openai",
  "model": "gpt-4o-mini"
}
```

#### Suggest Fix

```http
POST /api/ai/suggest
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "openai",
  "issue_description": "Phone numbers in various formats: (123) 456-7890, 123-456-7890, 1234567890"
}
```

**Response:**
```json
{
  "suggestion": "Standardize all phone numbers to format (XXX) XXX-XXXX using regex replacement...",
  "provider": "openai",
  "model": "gpt-4o-mini"
}
```

#### Chat with Assistant

```http
POST /api/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "openai",
  "message": "How should I handle missing values in a numeric column with outliers?"
}
```

**Response:**
```json
{
  "response": "For numeric columns with outliers, use median imputation instead of mean. The median is robust to outliers...",
  "provider": "openai",
  "model": "gpt-4o-mini"
}
```

---

### Assistant

#### Analyze Dataset

```http
POST /api/assistant/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "agent_id": "uuid"
}
```

**Response:**
```json
{
  "analysis": {
    "issues": [
      {
        "column": "email",
        "issue": "Inconsistent casing",
        "suggestion": "Convert to lowercase",
        "severity": "medium"
      }
    ],
    "recommended_operations": [
      {
        "operation": "string_lower",
        "columns": ["email"],
        "description": "Convert emails to lowercase"
      }
    ]
  }
}
```

#### Apply Suggestions

```http
POST /api/assistant/apply
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "uuid",
  "operations": [
    {
      "operation": "string_lower",
      "columns": ["email"]
    }
  ]
}
```

---

### Comparison

#### Get Before/After Comparison

```http
GET /api/comparison/{operation_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "before": {...},
  "after": {...},
  "diff": [
    {
      "row": 0,
      "column": "email",
      "before": "USER@Example.COM",
      "after": "user@example.com"
    }
  ]
}
```

---

### Notifications

#### Get User Notifications

```http
GET /api/notifications
Authorization: Bearer <token>
```

#### Mark as Read

```http
POST /api/notifications/{notification_id}/read
Authorization: Bearer <token>
```

---

### Rate Limit

#### Get Rate Limit Status

```http
GET /api/rate-limit/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "provider": "openai",
  "requests_remaining": 450,
  "tokens_remaining": 85000,
  "reset_at": "2024-01-01T00:01:00"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Error Examples

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Project not found"
}
```

**429 Rate Limit:**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

**Swagger UI:** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

These interfaces allow you to:
- Browse all endpoints
- View request/response schemas
- Test endpoints directly
- Download OpenAPI specification

---

*Part of the [MasterDataCleaner Documentation](../README.md)*
