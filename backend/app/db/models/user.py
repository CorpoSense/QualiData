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
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


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

    # Role: admin, manager, user
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False, values_callable=lambda x: [e.value for e in UserRole]),
        default=UserRole.USER,
        nullable=False
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
        role_value = self.role.value if hasattr(self.role, 'value') else str(self.role)
        
        # Simple role-based limits
        if role_value == 'admin':
            return {
                "max_projects": -1,
                "max_rows": 1_000_000,
                "max_storage_mb": 5000,
                "history_size": 500,
                "collaboration": True,
            }
        elif role_value == 'manager':
            return {
                "max_projects": 50,
                "max_rows": 200_000,
                "max_storage_mb": 500,
                "history_size": 200,
                "collaboration": True,
            }
        else:  # user
            return {
                "max_projects": 1,
                "max_rows": 1_000,
                "max_storage_mb": 5,
                "history_size": 10,
                "collaboration": False,
            }
