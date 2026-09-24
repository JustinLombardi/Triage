import hashlib
import hmac

import requests

from .config import settings

GITHUB_API = "https://api.github.com"


def verify_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """Check the X-Hub-Signature-256 header GitHub sends on every webhook
    delivery against our shared secret. Reject anything that doesn't match --
    this is the only thing standing between the internet and your queue."""
    if not settings.github_webhook_secret:
        # No secret configured: refuse rather than silently trust anyone who
        # can reach this endpoint.
        return False
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.github_webhook_secret.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    got = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, got)


def list_failed_jobs(owner: str, repo: str, run_id: int) -> list[dict]:
    """Ask GitHub which jobs in this run actually failed, so we only queue
    the ones worth diagnosing instead of every job in the matrix."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    jobs = resp.json().get("jobs", [])
    return [j for j in jobs if j.get("conclusion") == "failure"]
