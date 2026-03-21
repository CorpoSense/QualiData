"""Assistant wizard for guided data cleaning."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.db.models import Dataset, Project, User
from app.routers.auth import get_current_active_user

router = APIRouter(tags=["assistant"])


class AnalysisRequest(BaseModel):
    dataset_id: str


class WizardStep(BaseModel):
    step: int
    title: str
    description: str
    options: list[dict[str, Any]] | None = None


class WizardResponse(BaseModel):
    status: str
    current_step: int
    total_steps: int
    steps: list[WizardStep]
    data: dict[str, Any]


@router.post("/assistant/analyze", response_model=WizardResponse)
async def analyze_dataset(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Step 1: Analyze the dataset and provide insights."""
    from sqlalchemy import select

    result = await session.execute(
        select(Dataset).where(Dataset.id == request.dataset_id)
    )
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

    # Generate insights
    insights = []

    # Check for nulls
    null_counts = df.isnull().sum()
    high_null_cols = null_counts[null_counts > len(df) * 0.2].index.tolist()
    if high_null_cols:
        insights.append(
            {
                "type": "warning",
                "message": f"Columns with high null rates: {', '.join(high_null_cols)}",
            }
        )

    # Check for duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        insights.append(
            {"type": "info", "message": f"Found {dup_count} duplicate rows"}
        )

    # Check for potential issues
    for col in df.columns:
        if df[col].dtype == "object":
            unique = df[col].nunique()
            if unique == len(df):
                insights.append(
                    {
                        "type": "info",
                        "message": f"Column '{col}' has all unique values - might be IDs",
                    }
                )

    steps = [
        WizardStep(
            step=1,
            title="Analysis Complete",
            description="We've analyzed your dataset. Here are the findings:",
            options=(
                [
                    {"label": insight["message"], "type": insight["type"]}
                    for insight in insights
                ]
                if insights
                else [{"label": "No major issues found", "type": "success"}]
            ),
        ),
        WizardStep(
            step=2,
            title="Select Cleaning Operations",
            description="Choose what you'd like to do:",
            options=[
                {"value": "remove_nulls", "label": "Remove rows with missing values"},
                {"value": "remove_duplicates", "label": "Remove duplicate rows"},
                {"value": "standardize", "label": "Standardize text values"},
                {"value": "custom", "label": "Custom operation"},
            ],
        ),
        WizardStep(
            step=3,
            title="Review & Confirm",
            description="Review your selections and confirm:",
            options=[],
        ),
    ]

    return WizardResponse(
        status="success",
        current_step=1,
        total_steps=3,
        steps=steps,
        data={
            "dataset_id": request.dataset_id,
            "dataset_name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": len(dataset.columns) if dataset.columns else 0,
            "insights": insights,
        },
    )


@router.post("/assistant/suggest", response_model=WizardResponse)
async def get_suggestions(
    dataset_id: str,
    operation_type: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Step 2: Get operation suggestions based on selected type."""
    from sqlalchemy import select

    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Generate suggestions based on operation type
    suggestions = []

    if operation_type == "remove_nulls":
        suggestions = [
            {"value": "drop_rows", "label": "Drop rows with any null values"},
            {"value": "drop_columns", "label": "Drop columns with high null rate"},
            {"value": "fill_mean", "label": "Fill numeric nulls with mean"},
            {"value": "fill_mode", "label": "Fill with most common value (mode)"},
            {"value": "fill_custom", "label": "Fill with custom value"},
        ]
    elif operation_type == "standardize":
        suggestions = [
            {"value": "trim", "label": "Trim whitespace"},
            {"value": "lowercase", "label": "Convert to lowercase"},
            {"value": "uppercase", "label": "Convert to uppercase"},
            {"value": "titlecase", "label": "Convert to title case"},
        ]
    else:
        suggestions = [
            {"value": "filter", "label": "Filter rows"},
            {"value": "transform", "label": "Transform values"},
            {"value": "add_column", "label": "Add calculated column"},
        ]

    steps = [
        WizardStep(
            step=2,
            title=f"Options for {operation_type}",
            description="Select an option:",
            options=suggestions,
        ),
        WizardStep(
            step=3,
            title="Review & Confirm",
            description="Review your selections and confirm:",
            options=[],
        ),
    ]

    return WizardResponse(
        status="success",
        current_step=2,
        total_steps=3,
        steps=steps,
        data={"operation_type": operation_type, "suggestions": suggestions},
    )


@router.post("/assistant/execute", response_model=WizardResponse)
async def execute_operation(
    dataset_id: str,
    operation: dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Step 3: Execute the selected operation."""
    # This would call the appropriate operation endpoint
    # For now, return a confirmation

    return WizardResponse(
        status="success",
        current_step=3,
        total_steps=3,
        steps=[],
        data={
            "message": f"Operation queued for dataset {dataset_id}",
            "operation": operation,
        },
    )


@router.post("/assistant/ai-suggest")
async def ai_suggest_operations(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Use AI to analyze data and suggest cleaning operations.

    Body: { dataset_id, agent_id, rows: 10, include_description: false }
    Returns: { suggestions: [{operation, column, params, reasoning}, ...] }
    """
    import json as json_mod
    import pandas as pd
    from sqlalchemy import select
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.services.ai_provider import AIProvider, get_chat_model
    from app.routers.ai_operations import _get_agent_config

    dataset_id = request.get("dataset_id")
    agent_id = request.get("agent_id")
    rows = min(int(request.get("rows", 10)), 100)
    include_description = request.get("include_description", False)

    if not dataset_id or not agent_id:
        raise HTTPException(status_code=400, detail="dataset_id and agent_id required")

    # Get dataset
    result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    project_result = await session.execute(
        select(Project).where(Project.id == dataset.project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    if not dataset.preview_data:
        raise HTTPException(status_code=400, detail="No data to analyze")

    df = pd.DataFrame(dataset.preview_data)

    # Build context
    column_info = []
    for col in df.columns:
        nulls = int(df[col].isna().sum())
        dtype = str(df[col].dtype)
        unique = int(df[col].nunique())
        sample = df[col].dropna().head(3).tolist()
        column_info.append({
            "name": col, "dtype": dtype, "null_count": nulls,
            "unique_count": unique, "sample_values": [str(s) for s in sample]
        })

    sample_rows = df.head(rows).to_dict("records")

    context = f"Columns ({len(df.columns)}):\n{json_mod.dumps(column_info, indent=2)}\n\n"
    context += f"Sample rows ({rows}):\n{json_mod.dumps(sample_rows, indent=2, default=str)}\n\n"
    if include_description and dataset.description:
        context += f"Dataset description: {dataset.description}\n\n"

    AVAILABLE_OPS = """
Available operations:
- fillna: {operation: "fillna", column: "col", params: {method: "constant|drop|forward|backward|mean|median|mode", fill_value: "val"}}
- remove-duplicates: {operation: "remove-duplicates", params: {}}
- find-replace: {operation: "find-replace", column: "col", params: {find: "old", replace: "new", regex: false, case_sensitive: true}}
- extract-json: {operation: "extract-json", column: "col", params: {key: "field"}}
- string-operations: {operation: "string-operations", column: "col", params: {operation: "upper|lower|trim|title|capitalize"}}

Respond with JSON only: {"suggestions": [{"operation": "...", "column": "...", "params": {...}, "reasoning": "..."}, ...]}
Suggest only operations that would meaningfully improve data quality. Be specific about which columns to target and why."""

    system_prompt = "You are a data cleaning expert. Analyze the data and suggest the best cleaning operations."

    try:
        agent_config = await _get_agent_config(agent_id, current_user.id, session)
        provider = AIProvider(agent_config["provider"])
        llm_kwargs = {}
        if agent_config.get("api_key"):
            llm_kwargs["api_key"] = agent_config["api_key"]
        llm = get_chat_model(
            provider, model=agent_config.get("model"),
            temperature=agent_config.get("temperature", 0.3), **llm_kwargs,
        )

        sys = agent_config.get("system_prompt") or system_prompt
        response = await llm.ainvoke([
            SystemMessage(content=sys),
            HumanMessage(content=context + AVAILABLE_OPS),
        ])

        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        ai_response = json_mod.loads(raw)
        suggestions = ai_response.get("suggestions", [])

        # Validate suggestions
        valid = []
        for s in suggestions:
            if isinstance(s, dict) and s.get("operation"):
                valid.append({
                    "operation": s.get("operation", ""),
                    "column": s.get("column"),
                    "params": s.get("params", {}),
                    "reasoning": s.get("reasoning", ""),
                })

        return {"status": "success", "suggestions": valid, "rows_analyzed": len(sample_rows)}

    except json_mod.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid response. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")
