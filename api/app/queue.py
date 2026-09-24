import redis
from rq import Queue

from .config import settings

redis_conn = redis.from_url(settings.redis_url)
diagnosis_queue = Queue("diagnoses", connection=redis_conn)


def enqueue_diagnosis(diagnosis_id: str) -> None:
    """Hand a diagnosis id to the worker. The worker looks up the row itself,
    so we only ever pass the id across the queue -- never the payload."""
    diagnosis_queue.enqueue("tasks.run_diagnosis", diagnosis_id, job_timeout=180)
