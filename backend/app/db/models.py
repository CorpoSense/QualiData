"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """User model for authentication and ownership."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # OAuth fields
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    """Project model for organizing datasets."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Foreign keys
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Stats
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    datasets: Mapped[list["Dataset"]] = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")


class Dataset(Base):
    """Dataset model for storing data files."""

    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # File info
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # csv, xlsx, json, etc.

    # Data preview (stored as JSON)
    preview_data: Mapped[Optional[JSON]] = mapped_column(JSON, nullable=True)
    columns: Mapped[Optional[JSON]] = mapped_column(JSON, nullable=True)  # Column names and types

    # Row count
    row_count: Mapped[int] = mapped_column(Integer, default=0)

    # Foreign keys
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="datasets")
    operations: Mapped[list["OperationHistory"]] = relationship(
        "OperationHistory", back_populates="dataset", cascade="all, delete-orphan"
    )


class OperationHistory(Base):
    """Operation history for undo/redo functionality."""

    __tablename__ = "operation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Operation details
    operation_type: Mapped[str] = mapped_column(String(100), nullable=False)  # add_column, rename, etc.
    operation_params: Mapped[Optional[JSON]] = mapped_column(JSON, nullable=True)
    operation_result: Mapped[Optional[JSON]] = mapped_column(JSON, nullable=True)

    # Before/After snapshots (stored as JSON for simplicity)
    before_snapshot: Mapped[Optional[JSON]] = mapped_column(JSON, nullable=True)
    after_snapshot: Mapped[Optional[JSON]] = mapped_column(JSON, nullable=True)

    # Status
    is_applied: Mapped[bool] = mapped_column(Boolean, default=True)
    is_undone: Mapped[bool] = mapped_column(Boolean, default=False)

    # Foreign keys
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="operations")


class Agent(Base):
    """AI Agent configuration."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI Configuration
    provider: Mapped[str] = mapped_column(String(50), default="openai")
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    temperature: Mapped[float] = mapped_column(default=0.3)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Template flag
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)

    # Usage stats
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    # Foreign keys
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="agents")
