import uuid
from datetime import datetime

from sqlalchemy import (
    Integer,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MonitorResult(Base):
    __tablename__ = "monitor_results"

    __table_args__ = (
        CheckConstraint(
            "response_time_ms >= 0",
            name="check_response_time"
        ),
        Index(
            "idx_monitor_results_monitor_checked",
            "monitor_id",
            text("checked_at DESC")
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    monitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monitors.id", ondelete="CASCADE"),
        nullable=False
    )

    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    response_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    is_success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )