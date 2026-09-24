"""
This mirrors api/app/models.py field-for-field, because the api and worker
are separate Docker build contexts and don't share a Python package here.
They point at the same Postgres table, so if you change one, change both --
or better, pull both into a shared `triage_core` package once this grows
past a prototype.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    source: Mapped[str] = mapped_column(String(20), default="manual")
    repo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    job_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    job_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seen_before: Mapped[bool] = mapped_column(Boolean, default=False)

    log_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

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
