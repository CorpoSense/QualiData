"""Tests for document_kb service — document loading, splitting, cleanup."""

import os
import tempfile
import time

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import pytest
from unittest.mock import patch, MagicMock

from app.services.document_kb import (
    load_and_split_document,
    cleanup_expired_documents,
    ensure_storage_dir,
)


# --- load_and_split_document tests ---


def test_load_and_split_txt_file():
    """load_and_split_document loads and splits a plain text file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test document. " * 100)
        f.flush()
        try:
            splits = load_and_split_document(f.name, "txt", chunk_size=100, chunk_overlap=20)
            assert len(splits) > 1
            for doc in splits:
                assert hasattr(doc, "page_content")
                assert hasattr(doc, "metadata")
        finally:
            os.unlink(f.name)


def test_load_and_split_csv_file():
    """load_and_split_document loads and splits a CSV file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("name,age,city\n")
        for i in range(50):
            f.write(f"User {i},{20 + i % 50},City {i % 10}\n")
        f.flush()
        try:
            splits = load_and_split_document(f.name, "csv", chunk_size=200, chunk_overlap=50)
            assert len(splits) > 0
        finally:
            os.unlink(f.name)


def test_load_and_split_markdown_file():
    """load_and_split_document loads and splits a Markdown file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test Document\n\n")
        f.write("This is a markdown document with some content.\n\n")
        f.write("## Section 1\n\n")
        f.write("Content for section 1. " * 50)
        f.flush()
        try:
            splits = load_and_split_document(f.name, "md", chunk_size=200, chunk_overlap=30)
            assert len(splits) > 0
        finally:
            os.unlink(f.name)


def test_load_and_split_file_not_found():
    """load_and_split_document raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError, match="Document file not found"):
        load_and_split_document("/nonexistent/path/file.pdf", "pdf")


def test_load_and_split_unsupported_type():
    """load_and_split_document raises ValueError for unsupported file type."""
    with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
        f.write(b"test")
        f.flush()
        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                load_and_split_document(f.name, "xyz")
        finally:
            os.unlink(f.name)


def test_load_and_split_respects_chunk_size():
    """load_and_split_document respects chunk_size parameter."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("A" * 2000)
        f.flush()
        try:
            # Small chunk size should produce more chunks
            small_chunks = load_and_split_document(f.name, "txt", chunk_size=100, chunk_overlap=10)
            # Large chunk size should produce fewer chunks
            large_chunks = load_and_split_document(f.name, "txt", chunk_size=1000, chunk_overlap=10)
            assert len(small_chunks) > len(large_chunks)
        finally:
            os.unlink(f.name)


def test_load_and_split_uses_defaults():
    """load_and_split_document uses default chunk_size/overlap from JSON catalog."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content. " * 200)
        f.flush()
        try:
            # Should not raise — uses defaults from embedding_providers.json
            splits = load_and_split_document(f.name, "txt")
            assert len(splits) > 0
        finally:
            os.unlink(f.name)


# --- cleanup_expired_documents tests ---


def test_cleanup_removes_old_files():
    """cleanup_expired_documents removes files older than TTL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an old file
        old_file = os.path.join(tmpdir, "old_doc.txt")
        with open(old_file, "w") as f:
            f.write("old content")

        # Set modification time to 2 hours ago
        old_time = time.time() - 7200
        os.utime(old_file, (old_time, old_time))

        # Create a recent file
        recent_file = os.path.join(tmpdir, "recent_doc.txt")
        with open(recent_file, "w") as f:
            f.write("recent content")

        # Cleanup with 1 hour TTL
        cleaned = cleanup_expired_documents(tmpdir, ttl_seconds=3600)

        assert cleaned == 1
        assert not os.path.exists(old_file)
        assert os.path.exists(recent_file)


def test_cleanup_no_expired_files():
    """cleanup_expired_documents returns 0 when no files are expired."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a recent file
        recent_file = os.path.join(tmpdir, "recent_doc.txt")
        with open(recent_file, "w") as f:
            f.write("recent content")

        cleaned = cleanup_expired_documents(tmpdir, ttl_seconds=3600)
        assert cleaned == 0
        assert os.path.exists(recent_file)


def test_cleanup_nonexistent_directory():
    """cleanup_expired_documents returns 0 for nonexistent directory."""
    cleaned = cleanup_expired_documents("/nonexistent/path", ttl_seconds=3600)
    assert cleaned == 0


def test_cleanup_empty_directory():
    """cleanup_expired_documents returns 0 for empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cleaned = cleanup_expired_documents(tmpdir, ttl_seconds=3600)
        assert cleaned == 0


# --- ensure_storage_dir tests ---


def test_ensure_storage_dir_creates_dir():
    """ensure_storage_dir creates the directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        new_dir = os.path.join(tmpdir, "new_storage")
        assert not os.path.exists(new_dir)
        result = ensure_storage_dir(new_dir)
        assert os.path.isdir(new_dir)
        assert os.path.isabs(result)


def test_ensure_storage_dir_existing():
    """ensure_storage_dir works with existing directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = ensure_storage_dir(tmpdir)
        assert os.path.isdir(result)


# --- create_retriever_tool_from_document tests (mocked) ---


def test_create_retriever_tool_from_document():
    """create_retriever_tool_from_document creates a retriever tool."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test document for RAG. " * 50)
        f.flush()

        try:
            with patch("app.services.document_kb.get_embeddings") as mock_embeddings, \
                 patch("langchain_chroma.Chroma") as mock_chroma, \
                 patch("langchain_core.tools.retriever.create_retriever_tool") as mock_create_tool:

                mock_embeddings.return_value = MagicMock()
                mock_retriever = MagicMock()
                mock_chroma.from_documents.return_value.as_retriever.return_value = mock_retriever
                mock_tool = MagicMock()
                mock_create_tool.return_value = mock_tool

                from app.services.document_kb import create_retriever_tool_from_document

                doc_kb_config = {
                    "embedding_provider": "openai",
                    "embedding_model": "text-embedding-3-small",
                    "embedding_api_key": "test-key",
                    "chunk_size": 200,
                    "chunk_overlap": 30,
                }

                tool = create_retriever_tool_from_document(
                    file_path=f.name,
                    file_type="txt",
                    doc_kb_config=doc_kb_config,
                    collection_name="test_collection",
                )

                assert tool == mock_tool
                mock_embeddings.assert_called_once()
                mock_chroma.from_documents.assert_called_once()
                mock_create_tool.assert_called_once()
        finally:
            os.unlink(f.name)
