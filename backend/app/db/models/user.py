"""User model for authentication and account management."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role for RBAC."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Role and tier
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.FREE, nullable=False
    )

    # OAuth providers
    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    github_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )

    # Usage tracking
    storage_used_bytes: Mapped[int] = mapped_column(default=0)
    api_calls_this_month: Mapped[int] = mapped_column(default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def tier_limits(self) -> dict:
        """Get tier limits based on role."""
        limits = {
            UserRole.FREE: {
                "max_projects": 1,
                "max_rows": 1_000,
                "max_storage_mb": 5,
                "history_size": 10,
                "collaboration": False,
            },
            UserRole.PRO: {
                "max_projects": 10,
                "max_rows": 50_000,
                "max_storage_mb": 100,
                "history_size": 50,
                "collaboration": False,
            },
            UserRole.ENTERPRISE: {
                "max_projects": -1,  # Unlimited
                "max_rows": 500_000,
                "max_storage_mb": 1000,
                "history_size": 100,
                "collaboration": True,
            },
        }
        return limits.get(self.role, limits[UserRole.FREE])
