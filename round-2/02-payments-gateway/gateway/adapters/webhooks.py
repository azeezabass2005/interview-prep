import hashlib
import hmac
import json

from ..errors import Unauthorized

TOLERANCE_SECONDS = 300


def sign(secret: str, timestamp: int, payload: bytes) -> str:
    """What Paystream does: HMAC-SHA256 over '<timestamp>.<raw body>' with the endpoint's signing secret."""
    return hmac.new(secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256).hexdigest()


def verify(secret: str, header: str | None, body: bytes, now_ts: int) -> dict:
    """Checks the Paystream-Signature header ('t=<unix ts>,v1=<hex>') and returns the parsed event."""
    if not header:
        raise Unauthorized("missing Paystream-Signature")
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    try:
        timestamp = int(parts["t"])
        signature = parts["v1"]
    except (KeyError, ValueError) as e:
        raise Unauthorized("malformed Paystream-Signature") from e
    if abs(now_ts - timestamp) > TOLERANCE_SECONDS:
        raise Unauthorized("webhook timestamp outside tolerance")
    event = json.loads(body)
    canonical = json.dumps(event, separators=(",", ":")).encode()
    if not hmac.compare_digest(sign(secret, timestamp, canonical), signature):
        raise Unauthorized("bad webhook signature")
    return event
