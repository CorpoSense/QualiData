"""AI-powered data cleaning operations."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Agent, Dataset, Project, User
from app.routers.auth import get_current_active_user
from app.services.ai_provider import AIProvider, get_chat_model

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai-operations"])


class AICleaningRequest(BaseModel):
    type: str = Field(default='structural')
    column: str | None = None
    columns: list[str] | None = None
    instruction: str
    batch_size: int = Field(default=10, ge=1, le=100)
    agent_id: str | None = None

    @property
    def column_list(self) -> list[str]:
        """Get columns as a list."""
        if self.columns:
            return self.columns
        elif self.column:
            return [self.column]
        return []


class AICleaningResponse(BaseModel):
    status: str
    message: str
    results: list[dict] | None = None
    columns: list[dict] | None = None
    json_output: dict | None = None


STRUCTURAL_SYSTEM_PROMPT = """You are a data cleaning assistant. The user will provide column names from a dataset and an instruction for structural changes.

Respond ONLY with a valid JSON object. No markdown, no explanation outside the JSON.

Supported operations (use "operation" as the key):

Rename columns:
{"operation": "rename", "renames": {"old_name": "new_name"}}

Drop columns:
{"operation": "drop", "columns": ["col1", "col2"]}

Change column types:
{"operation": "astype", "columns": ["col1"], "dtype": "int"}

Add a new column copied from an existing one:
{"operation": "add_column", "column": "new_name", "source": "existing_col"}

Add a new column with a default value:
{"operation": "add_column", "column": "new_name", "default": "value"}

Multiple operations:
{"operations": [{"operation": "add_column", "column": "country", "source": "city"}, {"operation": "rename", "renames": {"old": "new"}}]}

Rules:
- "add_column" creates a NEW column — do NOT use "rename" when the user says "add"
- "rename" changes an existing column's name — do NOT use it to create new columns
- Only reference existing columns in "source" or "drop"
- Use snake_case for column names unless instructed otherwise"""

DATA_SYSTEM_PROMPT = """You are a data cleaning assistant. The user will provide rows of data and an instruction for data transformation.

Respond ONLY with a valid JSON object. No markdown, no explanation outside the JSON.

Format:
{"rows": [{"col1": "value", "col2": "value"}, ...]}

Return the SAME rows in the SAME order with corrected values. You may change any column's value based on the instruction and context from other columns.

Examples:
- Fix dates: {"rows": [{"date": "2024-01-15"}, {"date": "1970-01-01"}]}
- Derive country from city: {"rows": [{"city": "London", "country": "UK"}, {"city": "Paris", "country": "France"}]}
- Categorize: {"rows": [{"amount": 500, "category": "medium"}, {"amount": 50, "category": "low"}]}

Rules:
- Return ALL rows, even unchanged ones
- You may change any column, not just the "selected" ones
- Use null for values that should remain empty
- Be precise — only change what the instruction asks for"""


async def _get_agent_config(agent_id: str | None, user_id: str, session: AsyncSession) -> dict:
    """Load agent configuration. Validates ownership when agent_id is provided."""
    if agent_id:
        result = await session.execute(
            select(Agent).where(Agent.id == agent_id, Agent.user_id == user_id)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(
                status_code=404,
                detail="Agent not found or does not belong to you",
            )
        return {
            "provider": agent.provider,
            "model": agent.model,
            "temperature": agent.temperature,
            "system_prompt": agent.system_prompt,
            "api_key": agent.api_key,
        }
    # No agent selected — use defaults
    return {
        "provider": "openai",
        "model": None,
        "temperature": 0.3,
        "system_prompt": None,
        "api_key": None,
    }


@router.post("/datasets/{dataset_id}/ai-clean", response_model=AICleaningResponse)
async def ai_clean_column(
    dataset_id: str,
    request: AICleaningRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Apply AI cleaning to data based on natural language instruction."""
    from app.routers.datasets import detect_columns, get_preview_data
    from app.routers.operations import save_operation

    # Validate that at least one column is provided
    columns_to_clean = request.column_list
    if not columns_to_clean:
        raise HTTPException(
            status_code=422, detail="Either 'column' or 'columns' must be provided"
        )

    # Get dataset
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to operate on")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    # Validate all columns exist
    for col in columns_to_clean:
        if col not in df.columns:
            raise HTTPException(
                status_code=400, detail=f"Column '{col}' not found"
            )

    # Load agent config
    agent_config = await _get_agent_config(request.agent_id, current_user.id, session)
    provider = AIProvider(agent_config["provider"])

    if request.type == "structural":
        return await _ai_structural_clean(
            df, dataset, columns_to_clean, request.instruction,
            provider, agent_config, session,
        )
    else:
        return await _ai_data_clean(
            df, dataset, columns_to_clean, request.instruction,
            provider, agent_config, request.batch_size, session,
        )


async def _ai_structural_clean(
    df, dataset, columns: list[str], instruction: str,
    provider: AIProvider, agent_config: dict, session: AsyncSession,
) -> AICleaningResponse:
    """Use AI to perform structural operations (rename, drop, change types)."""
    from app.routers.datasets import detect_columns, get_preview_data
    from app.routers.operations import save_operation

    # Build the prompt
    column_info = []
    for col in columns:
        dtype = str(df[col].dtype)
        sample = df[col].head(3).tolist()
        column_info.append(f"  - {col} (type: {dtype}, samples: {sample})")

    # Also include non-selected columns for context
    other_cols = [c for c in df.columns if c not in columns]
    all_cols_info = f"All columns: {list(df.columns)}\n"
    selected_info = "Selected columns:\n" + "\n".join(column_info)

    FORMAT_INSTRUCTIONS = """
Respond with JSON only. Use one of these formats:
- Rename: {"operation": "rename", "renames": {"old_col": "new_col"}}
- Drop: {"operation": "drop", "columns": ["col1", "col2"]}
- Change type: {"operation": "astype", "columns": ["col1"], "dtype": "int"}
- Multiple: {"operations": [{"operation": "rename", "renames": {...}}, ...]}"""

    user_prompt = (
        f"{all_cols_info}\n{selected_info}\n\n"
        f"Instruction: {instruction}\n"
        f"{FORMAT_INSTRUCTIONS}"
    )

    # Get system prompt
    system_prompt = agent_config.get("system_prompt") or STRUCTURAL_SYSTEM_PROMPT

    # Call AI
    try:
        llm_kwargs = {}
        if agent_config.get("api_key"):
            llm_kwargs["api_key"] = agent_config["api_key"]
        llm = get_chat_model(
            provider,
            model=agent_config.get("model"),
            temperature=agent_config.get("temperature", 0.3),
            **llm_kwargs,
        )
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

        raw_text = response.content.strip()
        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        ai_response = json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error(f"AI returned invalid JSON: {raw_text}")
        raise HTTPException(
            status_code=500,
            detail=f"AI returned invalid response. Please try rephrasing your instruction.",
        )
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # Parse and apply operations
    # Normalize: AI might wrap in {"operations": [...]} or return a single op object
    if isinstance(ai_response, list):
        operations = ai_response
    elif "operations" in ai_response:
        operations = ai_response["operations"]
    else:
        operations = [ai_response]

    results = []
    applied_any = False

    for op in operations:
        if not isinstance(op, dict):
            continue
        # AI might use "operation", "action", or "type" as the key
        op_type = op.get("operation") or op.get("action") or op.get("type") or ""
        op_type = op_type.lower().strip()

        if op_type in ("rename", "renaming", "rename_column", "rename_columns"):
            renames = op.get("renames") or op.get("rename") or op.get("mapping") or {}
            valid_renames = {k: v for k, v in renames.items() if k in df.columns}
            if valid_renames:
                df = df.rename(columns=valid_renames)
                for old, new in valid_renames.items():
                    results.append({"operation": "rename", "from": old, "to": new, "status": "success"})
                applied_any = True
            else:
                results.append({"operation": "rename", "status": "skipped", "reason": "No matching columns"})

        elif op_type in ("drop", "remove", "delete", "drop_columns", "remove_columns"):
            cols_to_drop = op.get("columns") or op.get("drop") or op.get("remove") or []
            if isinstance(cols_to_drop, str):
                cols_to_drop = [cols_to_drop]
            cols_to_drop = [c for c in cols_to_drop if c in df.columns]
            if cols_to_drop:
                df = df.drop(columns=cols_to_drop)
                results.append({"operation": "drop", "columns": cols_to_drop, "status": "success"})
                applied_any = True

        elif op_type in ("astype", "change_type", "convert_type", "cast", "type"):
            dtype = op.get("dtype") or op.get("type_to") or op.get("target_type") or "str"
            cols_to_cast = op.get("columns") or op.get("column") or []
            if isinstance(cols_to_cast, str):
                cols_to_cast = [cols_to_cast]
            cols_to_cast = [c for c in cols_to_cast if c in df.columns]
            for col in cols_to_cast:
                try:
                    df[col] = df[col].astype(dtype)
                    results.append({"operation": "astype", "column": col, "dtype": dtype, "status": "success"})
                    applied_any = True
                except Exception as e:
                    results.append({"operation": "astype", "column": col, "status": "error", "reason": str(e)})

        elif op_type in ("add_column", "add", "new_column", "copy_column", "duplicate_column", "create_column"):
            new_col = op.get("column") or op.get("name") or op.get("target")
            source_col = op.get("source") or op.get("from")
            default_val = op.get("default") or op.get("value")
            if not new_col:
                results.append({"operation": "add_column", "status": "skipped", "reason": "No column name provided"})
            elif source_col and source_col in df.columns:
                df[new_col] = df[source_col].copy()
                results.append({"operation": "add_column", "column": new_col, "source": source_col, "status": "success"})
                applied_any = True
            elif default_val is not None:
                df[new_col] = default_val
                results.append({"operation": "add_column", "column": new_col, "default": default_val, "status": "success"})
                applied_any = True
            else:
                results.append({"operation": "add_column", "column": new_col, "status": "skipped", "reason": f"Source column '{source_col}' not found"})

        else:
            logger.warning(f"AI returned unknown operation type: {op_type!r}, full op: {op}")
            results.append({"operation": op_type or "unknown", "status": "skipped", "reason": f"Unknown operation: {op_type!r}"})

    if not applied_any:
        return AICleaningResponse(
            status="no_changes",
            message="AI did not produce any applicable changes. Try a different instruction.",
            results=results,
        )

    # Save before committing
    before_snapshot = {
        "columns": dataset.columns,
        "row_count": dataset.row_count,
        "preview_data": dataset.preview_data,
    }

    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)
    dataset.row_count = len(df)

    after_snapshot = {
        "columns": dataset.columns,
        "row_count": dataset.row_count,
        "preview_data": dataset.preview_data,
    }

    await save_operation(
        dataset.id,
        "ai_structural",
        {"instruction": instruction, "operations": operations},
        before_snapshot,
        after_snapshot,
        session,
    )
    await session.commit()

    return AICleaningResponse(
        status="success",
        message=f"AI applied {len(results)} structural change(s)",
        results=results,
        columns=dataset.columns,
    )


async def _ai_data_clean(
    df, dataset, columns: list[str], instruction: str,
    provider: AIProvider, agent_config: dict, batch_size: int,
    session: AsyncSession,
) -> AICleaningResponse:
    """Use AI to clean data values. Shows full rows for context-aware derivation."""
    from app.routers.datasets import detect_columns, get_preview_data
    from app.routers.operations import save_operation

    # Build prompt: show full rows so AI can derive values from context
    sample_rows = df.head(batch_size)
    rows_data = sample_rows.to_dict("records")

    FORMAT_INSTRUCTIONS = """
Respond with JSON only. Use this format:
{"rows": [{"col1": "value", "col2": "value"}, ...]}

Return the SAME number of rows in the SAME order with corrected values.
You may change any column based on the instruction and other columns' context."""

    user_prompt = (
        f"Data (first {batch_size} rows):\n"
        f"{json.dumps(rows_data, indent=2, default=str)}\n\n"
        f"Instruction: {instruction}\n"
        f"{FORMAT_INSTRUCTIONS}"
    )

    system_prompt = agent_config.get("system_prompt") or DATA_SYSTEM_PROMPT

    try:
        llm_kwargs = {}
        if agent_config.get("api_key"):
            llm_kwargs["api_key"] = agent_config["api_key"]
        llm = get_chat_model(
            provider,
            model=agent_config.get("model"),
            temperature=agent_config.get("temperature", 0.3),
            **llm_kwargs,
        )
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

        raw_text = response.content.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        ai_response = json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error(f"AI returned invalid JSON: {raw_text}")
        raise HTTPException(
            status_code=500,
            detail="AI returned invalid response. Please try rephrasing your instruction.",
        )
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    # Parse response — expect {"rows": [...]} format
    ai_rows = ai_response.get("rows", [])

    if not ai_rows:
        # Fallback: maybe AI used old {"operations": [...]} format
        return AICleaningResponse(
            status="no_changes",
            message="AI returned no rows. Try rephrasing your instruction.",
            results=[],
        )

    # Apply changes: compare each AI row with original, update changed cells
    results = []
    changed_cells = 0

    # Normalize null-like values for comparison
    def _is_null(val):
        if val is None:
            return True
        s = str(val).lower()
        return s in ("nan", "none", "nat", "")

    for i, ai_row in enumerate(ai_rows):
        if i >= len(df):
            break
        for col, new_val in ai_row.items():
            if col not in df.columns:
                continue
            old_val = df.at[df.index[i], col]
            # Compare: both null = same, otherwise compare strings
            if _is_null(old_val) and _is_null(new_val):
                continue
            if str(old_val) == str(new_val):
                continue
            df.at[df.index[i], col] = new_val
            changed_cells += 1

    if changed_cells == 0:
        return AICleaningResponse(
            status="no_changes",
            message="AI returned rows but no values were different from the original data.",
            results=[{"rows_processed": len(ai_rows), "cells_changed": 0}],
        )

    before_snapshot = {
        "columns": dataset.columns,
        "row_count": dataset.row_count,
        "preview_data": dataset.preview_data,
    }

    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)

    after_snapshot = {
        "columns": dataset.columns,
        "row_count": dataset.row_count,
        "preview_data": dataset.preview_data,
    }

    await save_operation(
        dataset.id,
        "ai_data_clean",
        {"instruction": instruction, "columns": columns},
        before_snapshot,
        after_snapshot,
        session,
    )
    await session.commit()

    return AICleaningResponse(
        status="success",
        message=f"AI updated {changed_cells} cell(s) across {len(ai_rows)} row(s)",
        results=[{"rows_processed": len(ai_rows), "cells_changed": changed_cells}],
        columns=dataset.columns,
    )


@router.post("/datasets/{dataset_id}/ai-analyze", response_model=AICleaningResponse)
async def ai_analyze_column(
    dataset_id: str,
    column: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get AI analysis and suggestions for a column."""
    from sqlalchemy import select

    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Verify ownership
    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to analyze")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    # Basic statistics
    col_data = df[column]
    analysis = {
        "column": column,
        "dtype": str(col_data.dtype),
        "total_rows": len(col_data),
        "null_count": int(col_data.isna().sum()),
        "unique_count": int(col_data.nunique()),
        "sample_values": col_data.head(5).tolist(),
    }

    # Add numeric stats if applicable
    if pd.api.types.is_numeric_dtype(col_data):
        analysis.update(
            {
                "min": float(col_data.min()) if not pd.isna(col_data.min()) else None,
                "max": float(col_data.max()) if not pd.isna(col_data.max()) else None,
                "mean": (
                    float(col_data.mean()) if not pd.isna(col_data.mean()) else None
                ),
                "median": (
                    float(col_data.median()) if not pd.isna(col_data.median()) else None
                ),
            }
        )

    return AICleaningResponse(
        status="success", message=f"Analysis for column '{column}'", results=[analysis]
    )


@router.post(
    "/datasets/{dataset_id}/ai-json-clean", response_model=AICleaningResponse
)
async def ai_clean_json(
    dataset_id: str,
    column: str,
    instruction: str,
    output_column: str | None = None,
    batch_size: int = 10,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Apply AI cleaning with structured JSON output."""
    from sqlalchemy import select

    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    project_result = await session.execute(
        select(Project).where(
            Project.id == dataset.project_id, Project.user_id == current_user.id
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data")

    import pandas as pd

    df = pd.DataFrame(dataset.preview_data)

    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")

    # Get column data
    column_data = df[column].head(batch_size).tolist()

    # Simulate structured JSON response
    # In production, this would call the AI with JSON schema
    results = []
    for val in column_data:
        results.append(
            {
                "original": str(val),
                "cleaned": str(val).strip().lower() if val else "",
                "valid": True,
            }
        )

    # Create output column
    out_col = output_column or f"{column}_cleaned"
    df[out_col] = df[column].apply(lambda x: str(x).strip().lower() if x else "")

    # Update dataset
    from app.routers.datasets import detect_columns, get_preview_data

    dataset.columns = detect_columns(df)
    dataset.preview_data = get_preview_data(df)

    await session.commit()

    return AICleaningResponse(
        status="success",
        message=f"Applied JSON-structured cleaning to column '{column}'",
        results=results[:5],
        json_output={
            "instruction": instruction,
            "processed": len(results),
            "output_column": out_col,
        },
    )
