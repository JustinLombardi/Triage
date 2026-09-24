import re

PATTERNS: dict[str, list[re.Pattern]] = {
    "infra": [
        re.compile(p, re.I)
        for p in [
            r"ECONNREFUSED",
            r"ETIMEDOUT",
            r"connection timed out",
            r"network is unreachable",
            r"getaddrinfo ENOTFOUND",
            r"rate limit",
            r"\b503\b",
            r"\b502\b",
            r"runner (has )?(gone|terminated)",
            r"OOMKilled",
            r"no space left on device",
            r"docker daemon",
            r"could not resolve host",
            r"npm ERR! network",
            r"connection reset by peer",
        ]
    ],
    "flaky": [
        re.compile(p, re.I)
        for p in [
            r"flaky",
            r"retry (succeeded|passed)",
            r"intermittent",
            r"timeout.*async callback was not invoked",
            r"passed on (retry|rerun)",
            r"previously passed",
            r"timed out waiting for",
        ]
    ],
    "bug": [
        re.compile(p, re.I)
        for p in [
            r"expected .* to (equal|be|match)",
            r"assertionerror",
            r"typeerror:",
            r"referenceerror:",
            r"at Object\.<anonymous>",
            r"stack trace",
            r"test failed",
        ]
    ],
    "config": [
        re.compile(p, re.I)
        for p in [
            r"cannot find module",
            r"module not found",
            r"peer dep",
            r"version mismatch",
            r"ENOENT",
            r"permission denied",
            r"\.env",
            r"secret .* not (found|set)",
            r"unmet dependency",
            r"lockfile",
        ]
    ],
}


def scan(log_text: str) -> dict:
    """Fast, deterministic pattern scan. Runs before the LLM call so we can
    (a) hand Claude a hint instead of a blind wall of text, and (b) still
    return something useful if the LLM call fails."""
    scores = {cat: 0 for cat in PATTERNS}
    signals = []

    for cat, patterns in PATTERNS.items():
        for pattern in patterns:
            match = pattern.search(log_text)
            if match:
                scores[cat] += 1
                signals.append({"category": cat, "text": match.group(0)})

    top_category = "unknown"
    top_score = 0
    for cat, score in scores.items():
        if score > top_score:
            top_score = score
            top_category = cat

    return {"top_category": top_category, "scores": scores, "signals": signals[:6]}
