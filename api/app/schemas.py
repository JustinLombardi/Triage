from datetime import datetime

from pydantic import BaseModel, Field


class DiagnosisCreate(BaseModel):
    job_name: str | None = None
    log_text: str = Field(min_length=1)
    seen_before: bool = False


class DiagnosisOut(BaseModel):
    id: str
    source: str
    repo: str | None = None
    run_id: str | None = None
    job_id: str | None = None
    job_name: str | None = None
    seen_before: bool
    status: str
    error_message: str | None = None
    category: str | None = None
    confidence: int | None = None
    summary: str | None = None
    evidence: list | None = None
    root_cause: str | None = None
    next_step: str | None = None
    signals: list | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
