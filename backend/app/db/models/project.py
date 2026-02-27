"""Project and dataset models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.db.database import Base


class Project(Base):
    """Project model - represents a user's workspace."""
    
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Dataset metadata
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    column_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    schema_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status
    is_saved: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    operations = relationship("OperationHistory", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, rows={self.row_count})>"


class Dataset(Base):
    """Dataset model - stores serialized DataFrame data."""
    
    __tablename__ = "datasets"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Serialized data (JSON format for pandas DataFrame)
    data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    schema_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Version tracking
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="datasets")
    
    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, project_id={self.project_id}, version={self.version})>"


class OperationHistory(Base):
    """Operation history model for undo/redo functionality."""
    
    __tablename__ = "operation_history"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Operation details
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # standard, cleaning, ai
    operation_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "strip", "ai_clean"
    operation_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Affected columns
    columns_affected: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Snapshot for undo (serialized DataFrame state)
    snapshot_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="operations")
    
    def __repr__(self) -> str:
        return f"<OperationHistory(id={self.id}, type={self.operation_name})>"
