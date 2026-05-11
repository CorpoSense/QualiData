"""Document model for uploaded files used in RAG-based chat."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Document(Base):
    """Document model — tracks uploaded files for document knowledge base."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
    )

    # File metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, txt, csv, md
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)  # relative to DOC_STORAGE_PATH

    # Processing status
    status: Mapped[str] = mapped_column(
        String(20), default="uploaded"
    )  # uploaded, processing, ready, error
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )  # for TTL-based cleanup

    # Relationships
    user = relationship("User", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"
