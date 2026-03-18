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

## Technical Details
- Backend endpoint: likely `/api/projects/{projectId}/datasets/{datasetId}/clean`
- Frontend state: selected columns, operation type, parameters
- Use existing AI service integration patterns
- Follow existing code style in Vue 3 + TypeScript

## Dependencies
- BootstrapVueNext components (Dropdown, Button, Modal)
- Existing API service functions
- Type definitions for cleaning operations
