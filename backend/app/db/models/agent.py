"""Agent model for AI configuration."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Agent(Base):
    """Agent model - reusable AI configuration."""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Agent configuration
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI Provider settings
    provider: Mapped[str] = mapped_column(
        String(50), default="openai"
    )  # openai, anthropic, google, etc.
    model: Mapped[str] = mapped_column(String(100), default="gpt-4o-mini")

    # Prompts
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_template: Mapped[str | None] = mapped_column(Text, nullable=True)

    # API credentials (stored encrypted at rest via DB encryption)
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Custom endpoint
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Generation settings
    temperature: Mapped[float] = mapped_column(Float, default=0.3)

    # Template status
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="agents")

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name={self.name}, provider={self.provider})>"
