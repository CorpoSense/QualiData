"""SearchEngine model for third-party search integrations."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SearchEngine(Base):
    """SearchEngine model — reusable search engine configuration."""

    __tablename__ = "search_engines"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Engine configuration
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # duckduckgo, serper, brave, serpapi, google, exa, searxng, custom

    # API credentials (stored encrypted at rest via DB encryption)
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Free-form provider-specific configuration (JSON)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)

    # System status
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="search_engines")

    def __repr__(self) -> str:
        return f"<SearchEngine(id={self.id}, name={self.name}, provider={self.provider})>"
