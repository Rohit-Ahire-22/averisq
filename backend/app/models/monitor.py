import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Monitor(Base):
    __tablename__ = "monitors"

    __table_args__ = (
        CheckConstraint(
            "interval_seconds >= 10 AND interval_seconds <= 3600",
            name="check_interval"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    interval: Mapped[int] = mapped_column(
        "interval_seconds",
        Integer,
        nullable=False,
        server_default=text("60")
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'active'")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )