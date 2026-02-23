"""Pydantic models for API request/response schemas."""

from typing import Optional
from pydantic import BaseModel


class AIProviderRequest(BaseModel):
    """Request model for AI provider configuration."""
    provider: str = "openai"
    model: Optional[str] = None
    temperature: float = 0.3


class AnalyzeDataRequest(BaseModel):
    """Request model for data analysis."""
    provider: Optional[str] = "openai"
    model: Optional[str] = None
    data_summary: str


class AnalyzeDataResponse(BaseModel):
    """Response model for data analysis."""
    analysis: str
    provider: str
    model: str


class SuggestFixRequest(BaseModel):
    """Request model for fix suggestions."""
    provider: Optional[str] = "openai"
    model: Optional[str] = None
    issue_description: str


class SuggestFixResponse(BaseModel):
    """Response model for fix suggestions."""
    suggestion: str
    provider: str
    model: str


class GenerateCodeRequest(BaseModel):
    """Request model for code generation."""
    provider: Optional[str] = "openai"
    model: Optional[str] = None
    task_description: str
    language: str = "python"


class GenerateCodeResponse(BaseModel):
    """Response model for code generation."""
    code: str
    provider: str
    model: str


class ChatRequest(BaseModel):
    """Request model for general chat."""
    provider: Optional[str] = "openai"
    model: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """Response model for chat."""
    response: str
    provider: str
    model: str


class ProviderInfo(BaseModel):
    """Information about an AI provider."""
    provider: str
    default_model: str


class ProvidersListResponse(BaseModel):
    """Response model for listing providers."""
    providers: list[ProviderInfo]
