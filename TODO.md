# AI Clean Feature Plan

## Overview
Implement AI Clean as a dropdown menu with two main operation types:
1. Structural/column-level operations (e.g., rename columns, change types, drop columns)
2. Data-level operations (apply AI to selected columns with their rows)

## Tasks

- [x] Analyze current AI Clean button implementation
- [x] Design dropdown menu UI (BootstrapVueNext or plain Bootstrap 5)
- [x] Define structural operations list (rename, type conversion, drop, reorder, etc.)
- [x] Define data operations list (AI cleaning, categorization, extraction, etc.)
- [x] Implement dropdown toggle functionality
- [x] Create modal/dialog for column selection (for structural ops)
- [x] Create modal/dialog for column+row selection (for data ops)
- [x] Connect selected columns to backend AI cleaning endpoint
- [x] Handle loading states and user feedback
- [x] Add validation for operation prerequisites
- [x] Test with sample dataset (manual verification via browser)
- [x] Update documentation/comments
- [x] Ensure accessibility and keyboard navigation
- [x] Implement backend AI agent using OpenAI-compatible API for structural cleaning
- [x] Implement Agent CRUD endpoints for managing reusable AI configurations
- [x] Test AI Structural Clean with real LLM (via manual verification)

## Technical Details
- Backend endpoint: `/api/projects/{projectId}/datasets/{datasetId}/clean` (handled by `/datasets/{dataset_id}/ai-clean`)
- Frontend state: selected columns, operation type, parameters
- Use existing AI service integration patterns (see app/services/ai_provider.py)
- Follow existing code style in Vue 3 + TypeScript

## Dependencies
- BootstrapVueNext components (Dropdown, Button, Modal)
- Existing API service functions
- Type definitions for cleaning operations
- LangChain OpenAI integration (langchain-openai)
