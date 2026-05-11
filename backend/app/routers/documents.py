"""Document management endpoints for the Document Knowledge Base feature.

Provides upload, list, get, delete, and processing endpoints.
Embedding provider catalog is also served from here.
"""

import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.database import get_async_session
from app.db.models import Agent, Document, User
from app.routers.auth import get_current_active_user
from app.services.document_kb import ensure_storage_dir, cleanup_expired_documents
from app.services.embedding_factory import (
    get_supported_file_types,
    list_embedding_providers,
)

router = APIRouter(prefix="/documents", tags=["documents"])


# --- Pydantic schemas ---


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    agent_id: str | None = None
    filename: str
    content_type: str
    file_type: str
    size_bytes: int
    file_path: str
    status: str
    chunk_count: int = 0
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


def _document_to_response(doc: Document) -> dict:
    """Convert Document model to response dict."""
    return {
        "id": doc.id,
        "user_id": doc.user_id,
        "agent_id": doc.agent_id,
        "filename": doc.filename,
        "content_type": doc.content_type,
        "file_type": doc.file_type,
        "size_bytes": doc.size_bytes,
        "file_path": doc.file_path,
        "status": doc.status,
        "chunk_count": doc.chunk_count,
        "error_message": doc.error_message,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "expires_at": doc.expires_at,
    }


# --- Endpoints ---


@router.get("/providers")
async def list_doc_providers():
    """List supported embedding providers with their models."""
    providers = list_embedding_providers()
    file_types = get_supported_file_types()
    return {
        "providers": providers,
        "supported_file_types": file_types,
    }


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    agent_id: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Upload a document for RAG-based chat.

    Validates the agent has doc_kb_config, the file type is supported,
    and the file size is within limits. Saves the file and creates a
    Document record in the database.
    """
    settings = get_settings()

    # Validate agent exists and belongs to user
    result = await session.execute(
        select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Validate agent has doc_kb_config
    if not agent.doc_kb_config:
        raise HTTPException(
            status_code=400,
            detail="Agent does not have Document Knowledge Base configured. "
            "Enable it in the agent's Advanced tab.",
        )

    # Validate file type
    supported_types = get_supported_file_types()
    content_type = file.content_type or ""

    # Also check by extension as fallback
    file_type = None
    if content_type in supported_types:
        file_type = supported_types[content_type].get("extension", "").lstrip(".")
    else:
        # Fallback: check by extension
        suffix = Path(file.filename or "").suffix.lower()
        for mime_type, info in supported_types.items():
            if info.get("extension") == suffix:
                file_type = info.get("extension", "").lstrip(".")
                content_type = mime_type
                break

    if not file_type:
        supported_exts = [v["extension"] for v in supported_types.values()]
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. "
            f"Supported extensions: {', '.join(supported_exts)}",
        )

    # Validate file size
    max_size_bytes = settings.doc_max_file_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(content)} bytes). "
            f"Maximum: {settings.doc_max_file_size_mb}MB.",
        )

    # Save file to storage
    doc_id = str(uuid.uuid4())
    storage_dir = ensure_storage_dir(settings.doc_storage_path)
    suffix = Path(file.filename or "").suffix or f".{file_type}"
    file_name_on_disk = f"{doc_id}{suffix}"
    full_path = os.path.join(storage_dir, file_name_on_disk)

    with open(full_path, "wb") as f:
        f.write(content)

    # Calculate expiry time
    expires_at = datetime.utcnow() + timedelta(seconds=settings.doc_cleanup_ttl_seconds)

    # Create Document record
    doc = Document(
        id=doc_id,
        user_id=current_user.id,
        agent_id=agent_id,
        filename=file.filename or "unknown",
        content_type=content_type,
        file_type=file_type,
        size_bytes=len(content),
        file_path=file_name_on_disk,  # relative to storage dir
        status="uploaded",
        chunk_count=0,
        expires_at=expires_at,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    # Auto-process the document (v1: synchronous)
    try:
        doc.status = "processing"
        await session.commit()

        from app.services.document_kb import load_and_split_document
        from app.services.embedding_factory import get_default_chunk_size, get_default_chunk_overlap

        doc_kb_config = agent.doc_kb_config
        cs = doc_kb_config.get("chunk_size") or get_default_chunk_size()
        co = doc_kb_config.get("chunk_overlap") or get_default_chunk_overlap()

        splits = load_and_split_document(full_path, file_type, chunk_size=cs, chunk_overlap=co)

        doc.chunk_count = len(splits)
        doc.status = "ready"
        doc.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(doc)

    except Exception as e:
        doc.status = "error"
        doc.error_message = str(e)[:500]
        doc.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(doc)
        # Don't fail the upload — the document is saved, just not processed
        # User can retry processing later

    return _document_to_response(doc)


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    agent_id: str | None = None,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all documents for the current user, optionally filtered by agent."""
    query = select(Document).where(Document.user_id == current_user.id)
    if agent_id:
        query = query.where(Document.agent_id == agent_id)
    query = query.order_by(Document.created_at.desc())

    result = await session.execute(query)
    docs = result.scalars().all()
    return [_document_to_response(d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get document metadata by ID."""
    result = await session.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _document_to_response(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete a document record and its file from storage."""
    settings = get_settings()

    result = await session.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from storage
    storage_dir = ensure_storage_dir(settings.doc_storage_path)
    file_path = os.path.join(storage_dir, doc.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass  # File may already be cleaned up

    await session.delete(doc)
    await session.commit()
    return None


@router.post("/{doc_id}/process", response_model=DocumentResponse)
async def process_document(
    doc_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Re-process a document (load, split, count chunks).

    Useful if processing failed during upload or if chunk settings changed.
    """
    settings = get_settings()

    result = await session.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get the agent's doc_kb_config for chunk settings
    if doc.agent_id:
        agent_result = await session.execute(select(Agent).where(Agent.id == doc.agent_id))
        agent = agent_result.scalar_one_or_none()
        doc_kb_config = agent.doc_kb_config if agent else {}
    else:
        doc_kb_config = {}

    # Process
    try:
        doc.status = "processing"
        await session.commit()

        from app.services.document_kb import load_and_split_document
        from app.services.embedding_factory import get_default_chunk_size, get_default_chunk_overlap

        storage_dir = ensure_storage_dir(settings.doc_storage_path)
        full_path = os.path.join(storage_dir, doc.file_path)

        cs = doc_kb_config.get("chunk_size") or get_default_chunk_size()
        co = doc_kb_config.get("chunk_overlap") or get_default_chunk_overlap()

        splits = load_and_split_document(full_path, doc.file_type, chunk_size=cs, chunk_overlap=co)

        doc.chunk_count = len(splits)
        doc.status = "ready"
        doc.error_message = None
        doc.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(doc)

    except Exception as e:
        doc.status = "error"
        doc.error_message = str(e)[:500]
        doc.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(doc)

    return _document_to_response(doc)


@router.post("/cleanup")
async def cleanup_documents(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Clean up expired document files from storage.

    Removes files older than DOC_CLEANUP_TTL_SECONDS and marks
    corresponding Document records as expired.
    """
    settings = get_settings()
    storage_dir = ensure_storage_dir(settings.doc_storage_path)

    # Clean up files
    cleaned_files = cleanup_expired_documents(storage_dir, settings.doc_cleanup_ttl_seconds)

    # Mark expired documents in DB
    cutoff = datetime.utcnow() - timedelta(seconds=settings.doc_cleanup_ttl_seconds)
    result = await session.execute(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.expires_at < datetime.utcnow(),
        )
    )
    expired_docs = result.scalars().all()
    cleaned_records = 0
    for doc in expired_docs:
        await session.delete(doc)
        cleaned_records += 1

    if cleaned_records > 0:
        await session.commit()

    return {
        "files_cleaned": cleaned_files,
        "records_cleaned": cleaned_records,
    }
