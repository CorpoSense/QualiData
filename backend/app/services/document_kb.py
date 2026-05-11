"""Document Knowledge Base service using ChromaDB for RAG.

Creates LangChain retriever tools from uploaded documents.
Supports: PDF, TXT, CSV, Markdown (configurable via embedding_providers.json).
"""

import logging
import os
import time
from pathlib import Path

from app.services.embedding_factory import (
    get_default_chunk_overlap,
    get_default_chunk_size,
    get_embeddings,
    get_supported_file_types,
)

logger = logging.getLogger(__name__)


def load_and_split_document(
    file_path: str,
    file_type: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list:
    """Load a document and split into chunks.

    Args:
        file_path: Absolute path to the document file.
        file_type: File type identifier (pdf, txt, csv, md).
        chunk_size: Size of each chunk in characters (default from JSON catalog).
        chunk_overlap: Overlap between chunks in characters (default from JSON catalog).

    Returns:
        List of LangChain Document objects (split into chunks).

    Raises:
        ValueError: If the file type is not supported.
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document file not found: {file_path}")

    chunk_size = chunk_size or get_default_chunk_size()
    chunk_overlap = chunk_overlap or get_default_chunk_overlap()

    # Load based on file type
    match file_type:
        case "pdf":
            from langchain_community.document_loaders import PyPDFLoader

            loader = PyPDFLoader(file_path)
        case "csv":
            from langchain_community.document_loaders import CSVLoader

            loader = CSVLoader(file_path)
        case "txt" | "md" | "markdown":
            from langchain_community.document_loaders import TextLoader

            loader = TextLoader(file_path)
        case _:
            supported = get_supported_file_types()
            raise ValueError(
                f"Unsupported file type: {file_type}. "
                f"Supported: {list(v['loader'] for v in supported.values())}"
            )

    docs = loader.load()

    # Split into chunks
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return text_splitter.split_documents(docs)


def create_retriever_tool_from_document(
    file_path: str,
    file_type: str,
    doc_kb_config: dict,
    fallback_api_key: str | None = None,
    collection_name: str = "doc_kb",
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
):
    """Create a retriever tool from an uploaded document.

    Orchestrates: load → split → embed → store in ChromaDB → create retriever tool.

    Args:
        file_path: Absolute path to the document file.
        file_type: File type identifier (pdf, txt, csv, md).
        doc_kb_config: Agent's doc_kb_config dict with embedding settings.
        fallback_api_key: Agent's own API key as fallback for embeddings.
        collection_name: Unique ChromaDB collection name (per document).
        chunk_size: Override chunk size (default from doc_kb_config or JSON catalog).
        chunk_overlap: Override chunk overlap (default from doc_kb_config or JSON catalog).

    Returns:
        A LangChain tool that the agent can use to search the document.
    """
    from langchain_chroma import Chroma
    from langchain_core.tools.retriever import create_retriever_tool

    # Resolve chunk settings: param > doc_kb_config > JSON catalog defaults
    cs = chunk_size or doc_kb_config.get("chunk_size") or get_default_chunk_size()
    co = chunk_overlap or doc_kb_config.get("chunk_overlap") or get_default_chunk_overlap()

    # Create embeddings
    embedding_provider = doc_kb_config.get("embedding_provider", "openai")
    embedding_model = doc_kb_config.get("embedding_model")
    embedding_api_key = doc_kb_config.get("embedding_api_key")
    embedding_base_url = doc_kb_config.get("embedding_base_url")

    embeddings = get_embeddings(
        provider=embedding_provider,
        model=embedding_model,
        api_key=embedding_api_key,
        base_url=embedding_base_url,
        fallback_api_key=fallback_api_key,
    )

    # Load and split document
    splits = load_and_split_document(file_path, file_type, chunk_size=cs, chunk_overlap=co)

    logger.info(
        f"Document split into {len(splits)} chunks "
        f"(chunk_size={cs}, chunk_overlap={co}, file_type={file_type})"
    )

    # Create ChromaDB vector store (ephemeral — no persist_directory for v1)
    vector_db = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name=collection_name,
    )

    retriever = vector_db.as_retriever()

    return create_retriever_tool(
        retriever,
        "document_search",
        "Search for information within the uploaded document. "
        "Use this tool for any questions about the content of the uploaded file.",
    )


def cleanup_expired_documents(storage_path: str, ttl_seconds: int) -> int:
    """Remove expired document files from storage.

    Scans the storage directory for files older than TTL and deletes them.

    Args:
        storage_path: Path to the document storage directory.
        ttl_seconds: Time-to-live in seconds. Files older than this are deleted.

    Returns:
        Number of files cleaned up.
    """
    if not os.path.exists(storage_path):
        return 0

    now = time.time()
    cleaned = 0

    for entry in Path(storage_path).iterdir():
        if entry.is_file():
            file_age = now - entry.stat().st_mtime
            if file_age > ttl_seconds:
                try:
                    entry.unlink()
                    cleaned += 1
                    logger.debug(f"Cleaned up expired file: {entry.name}")
                except OSError as e:
                    logger.warning(f"Failed to delete {entry}: {e}")

    if cleaned > 0:
        logger.info(f"Cleaned up {cleaned} expired document(s) from {storage_path}")

    return cleaned


def ensure_storage_dir(storage_path: str) -> str:
    """Ensure the document storage directory exists.

    Args:
        storage_path: Path to the document storage directory.

    Returns:
        The absolute path to the storage directory.
    """
    abs_path = os.path.abspath(storage_path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path
