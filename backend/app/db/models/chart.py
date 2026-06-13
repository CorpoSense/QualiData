"""Chart persistence model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Chart(Base):
    """Chart model - stores chart configurations for datasets."""

    __tablename__ = "charts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    dataset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Chart configuration (chartType, xAxis, yAxis, aggregation, colorPalette, etc.)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Chart metadata (title, warnings, row counts, etc.)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Ordering
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Chart(id={self.id}, dataset_id={self.dataset_id}, type={self.config.get('chartType', 'unknown')})>"