from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..config import TRACKING_PARAMS


def _is_tracking(key: str) -> bool:
    return any(key == p or key.startswith(p) for p in TRACKING_PARAMS)


def canonical_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.netloc
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if not _is_tracking(k)))
    return urlunsplit((parts.scheme, host, parts.path, query, ""))
