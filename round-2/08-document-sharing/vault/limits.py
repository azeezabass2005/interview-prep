from .config import MAX_BODY_BYTES
from .errors import PayloadTooLarge


def body_limit(max_bytes: int = MAX_BODY_BYTES):
    """Rejects oversized request bodies before any handler parses them."""
    def middleware(request, call_next):
        declared = int(request.headers.get("Content-Length") or 0)
        if declared > max_bytes:
            raise PayloadTooLarge(f"request body is larger than {max_bytes} bytes")
        return call_next(request)
    return middleware
