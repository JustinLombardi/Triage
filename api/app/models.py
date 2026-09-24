import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Diagnosis(Base):
    """One classified (or in-flight) CI failure."""

    __tablename__ = "diagnoses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Where the failure came from.
    source: Mapped[str] = mapped_column(String(20), default="manual")  # manual | github_webhook
    repo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    job_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    job_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seen_before: Mapped[bool] = mapped_column(Boolean, default=False)

    # Raw input.
    log_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pipeline state: pending -> done | error
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Result, filled in by the worker.
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[list | None] = mapped_column(JSON, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_step: Mapped[str | None] = mapped_column(Text, nullable=True)
    signals: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
