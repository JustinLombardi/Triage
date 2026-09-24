import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..github_client import list_failed_jobs, verify_signature
from ..models import Diagnosis
from ..queue import enqueue_diagnosis

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/github", status_code=202)
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    body = await request.body()

    #verify webhook signature 
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    if x_github_event != "workflow_run":
        # We only care about this one event type; ack anything else so
        # GitHub doesn't retry it as a failed delivery.
        return {"ignored": x_github_event}


    payload = await request.json()
    run = payload.get("workflow_run", {})

    if payload.get("action") != "completed" or run.get("conclusion") != "failure":
        return {"ignored": "not a failed, completed run"}

    owner = payload["repository"]["owner"]["login"]
    repo_name = payload["repository"]["name"]
    run_id = run["id"]

    try:
        failed_jobs = list_failed_jobs(owner, repo_name, run_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Could not list jobs for run %s", run_id)
        raise HTTPException(status_code=502, detail="Could not reach GitHub API") from exc

    created_ids = []
    for job in failed_jobs:
        row = Diagnosis(
            source="github_webhook",
            repo=f"{owner}/{repo_name}",
            run_id=str(run_id),
            job_id=str(job["id"]),
            job_name=job.get("name"),
            status="pending",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        enqueue_diagnosis(row.id)
        created_ids.append(row.id)

    return {"queued": created_ids}
