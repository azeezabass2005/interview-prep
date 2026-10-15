from urllib.parse import urlparse

BLOCKED_DOMAINS = {"malware.example", "phish.example"}


def is_blocked(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in BLOCKED_DOMAINS)
