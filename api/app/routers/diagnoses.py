from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Diagnosis
from ..queue import enqueue_diagnosis
from ..schemas import DiagnosisCreate, DiagnosisOut

router = APIRouter(prefix="/api/diagnoses", tags=["diagnoses"])


@router.post("", response_model=DiagnosisOut, status_code=201)
def create_diagnosis(body: DiagnosisCreate, db: Session = Depends(get_db)):
    """Paste-based path: the caller already has the log text in hand."""
    row = Diagnosis(
        source="manual",
        job_name=body.job_name,
        log_text=body.log_text,
        seen_before=body.seen_before,
        status="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    enqueue_diagnosis(row.id)
    return row


@router.get("", response_model=list[DiagnosisOut])
def list_diagnoses(limit: int = 25, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Diagnosis).order_by(Diagnosis.created_at.desc()).limit(limit)
    ).scalars().all()
    return rows


@router.get("/{diagnosis_id}", response_model=DiagnosisOut)
def get_diagnosis(diagnosis_id: str, db: Session = Depends(get_db)):
    row = db.get(Diagnosis, diagnosis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return row
