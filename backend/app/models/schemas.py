"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel


class AIProviderRequest(BaseModel):
    """Request model for AI provider configuration."""

    provider: str = "openai"
    model: str | None = None
    temperature: float = 0.3


class AnalyzeDataRequest(BaseModel):
    """Request model for data analysis."""

    provider: str | None = "openai"
    model: str | None = None
    data_summary: str


class AnalyzeDataResponse(BaseModel):
    """Response model for data analysis."""

    analysis: str
    provider: str
    model: str


class SuggestFixRequest(BaseModel):
    """Request model for fix suggestions."""

    provider: str | None = "openai"
    model: str | None = None
    issue_description: str


class SuggestFixResponse(BaseModel):
    """Response model for fix suggestions."""

    suggestion: str
    provider: str
    model: str


class GenerateCodeRequest(BaseModel):
    """Request model for code generation."""

    provider: str | None = "openai"
    model: str | None = None
    task_description: str
    language: str = "python"


class GenerateCodeResponse(BaseModel):
    """Response model for code generation."""

    code: str
    provider: str
    model: str


class ChatMessage(BaseModel):
    """A single message in the conversation history."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request model for general chat."""

    provider: str | None = "openai"
    model: str | None = None
    message: str
    agent_id: str | None = None
    conversation_history: list[ChatMessage] | None = None
    dataset_id: str | None = None
    dataset_context_rows: int = 10


class ChatResponse(BaseModel):
    """Response model for chat."""

    response: str
    provider: str
    model: str
    conversation_id: str | None = None


class ProviderInfo(BaseModel):
    """Information about an AI provider."""

    provider: str
    default_model: str


class ProvidersListResponse(BaseModel):
    """Response model for listing providers."""

    providers: list[ProviderInfo]
