import json
import os
import re

import anthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

VALID_CATEGORIES = {"flaky", "infra", "bug", "config", "unknown"}

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    return _client


def _build_prompt(log_text: str, job_name: str | None, seen_before: bool, heuristic: dict) -> str:
    signals = heuristic.get("signals", [])
    signal_str = (
        "; ".join(f"{s['category']}:{s['text']}" for s in signals) if signals else "none"
    )
    return f"""You are a CI/CD failure triage assistant. A developer's GitHub Actions
job failed. You're given its log output. Classify why it failed and explain
it in plain English.

Job or check name: {job_name or "not given"}
Has failed before on this branch/PR: {"yes" if seen_before else "not indicated"}
A local regex scan found these possible signals (may be noisy, use your own
judgment, you may disagree): {signal_str}

LOG:
```
{log_text[:12000]}
```

Respond with ONLY a JSON object, no markdown fences, no commentary, matching
exactly this shape:
{{"category": "flaky|infra|bug|config|unknown", "confidence": <0-100 integer>,
"summary": "1-2 sentence plain-English explanation of what actually broke",
"evidence": ["at most 2 short exact lines copied verbatim from the log that
best support this"], "root_cause": "explanation of the underlying cause",
"next_step": "one concrete, specific action the developer should take next"}}
"""


def _extract_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def classify(log_text: str, job_name: str | None, seen_before: bool, heuristic: dict) -> dict:
    """Call Claude once, parse its JSON, and normalize the fields we trust
    downstream (category must be one we know about, confidence is a clamped
    int). Raises on transport errors -- the caller decides the fallback."""
    client = _get_client()
    prompt = _build_prompt(log_text, job_name, seen_before, heuristic)

    message = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    text_out = "".join(block.text for block in message.content if block.type == "text")
    parsed = _extract_json(text_out)

    if not parsed or "category" not in parsed:
        raise ValueError(f"Could not parse a diagnosis out of the model's response: {text_out!r}")

    if parsed["category"] not in VALID_CATEGORIES:
        parsed["category"] = "unknown"

    try:
        parsed["confidence"] = max(0, min(100, int(parsed.get("confidence", 50))))
    except (TypeError, ValueError):
        parsed["confidence"] = 50

    parsed.setdefault("evidence", [])
    parsed.setdefault("summary", "")
    parsed.setdefault("root_cause", "")
    parsed.setdefault("next_step", "")

    return parsed
