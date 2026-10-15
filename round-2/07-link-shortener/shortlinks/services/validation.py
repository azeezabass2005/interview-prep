import re
from urllib.parse import urlparse

from ..abuse import is_blocked
from ..config import MAX_ALIAS_LENGTH, RESERVED_ALIASES
from ..errors import LinkError

_ALIAS = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_target(url: str) -> str:
    parsed = urlparse(url or "")
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise LinkError("target must be an http(s) URL")
    if is_blocked(url):
        raise LinkError("destination is blocked")
    return url


def validate_alias(alias: str) -> str:
    if not alias or len(alias) > MAX_ALIAS_LENGTH or not _ALIAS.match(alias):
        raise LinkError("alias must be 1-40 letters, digits, '-' or '_'")
    if alias.lower() in RESERVED_ALIASES:
        raise LinkError("alias is reserved")
    return alias
