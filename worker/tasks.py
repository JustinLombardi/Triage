import logging

import heuristics
import llm
from db import SessionLocal
from github_client import fetch_job_log
from models import Diagnosis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_diagnosis(diagnosis_id: str) -> None:
    """The one job the queue ever hands us: given a diagnosis id, get it to
    'done' or 'error'. Runs in the RQ worker process, not the API process."""
    db = SessionLocal()
    try:
        row = db.get(Diagnosis, diagnosis_id)
        if row is None:
            logger.warning("Diagnosis %s vanished before we could process it", diagnosis_id)
            return

        try:
            log_text = row.log_text
            if not log_text:
                # github_webhook path: the API only stored where to find the
                # log, not the log itself, so fetch it now.
                owner, repo = row.repo.split("/", 1)
                log_text = fetch_job_log(owner, repo, row.job_id)
                row.log_text = log_text
                db.commit()

            heuristic = heuristics.scan(log_text)

            try:
                result = llm.classify(log_text, row.job_name, row.seen_before, heuristic)
                row.category = result["category"]
                row.confidence = result["confidence"]
                row.summary = result["summary"]
                row.evidence = result["evidence"]
                row.root_cause = result["root_cause"]
                row.next_step = result["next_step"]
            except Exception:  # noqa: BLE001
                # LLM call failed or came back unparseable -- fall back to
                # the heuristic scan alone rather than leaving the row stuck.
                logger.exception("LLM classification failed for %s, falling back", diagnosis_id)
                top = heuristic["top_category"]
                row.category = top
                row.confidence = 40 if heuristic["signals"] else 20
                row.summary = "AI diagnosis failed for this run; showing the pattern-scan result only."
                row.evidence = [s["text"] for s in heuristic["signals"][:2]]
                row.root_cause = "Based on keyword matches in the log, not a full analysis."
                row.next_step = "Re-run the diagnosis, or read the log manually around the flagged signals."

            row.signals = heuristic["signals"]
            row.status = "done"
            db.commit()

        except Exception as exc:  # noqa: BLE001
            logger.exception("Diagnosis %s failed", diagnosis_id)
            row.status = "error"
            row.error_message = str(exc)
            db.commit()
    finally:
        db.close()
