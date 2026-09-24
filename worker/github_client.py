import os

import requests

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def fetch_job_log(owner: str, repo: str, job_id: str) -> str:
    """Download the raw log for one job. GitHub answers this endpoint with a
    redirect to a short-lived blob URL; `requests` follows it by default."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/jobs/{job_id}/logs"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text
