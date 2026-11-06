import json

from .transport import TransportError, TransportTimeout


class DeliveryError(Exception):
    def __init__(self, message: str, retryable: bool):
        super().__init__(message)
        self.retryable = retryable


def _send(transport, url: str, api_key: str, payload: dict, timeout: float) -> dict:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        result = transport.send("POST", url, headers, json.dumps(payload).encode(), timeout)
    except (TransportTimeout, TransportError) as e:
        raise DeliveryError(f"provider unreachable: {e}", retryable=True) from e
    if 400 <= result.status < 500:
        raise DeliveryError(f"provider rejected the message ({result.status}): {result.body}", retryable=False)
    if result.status >= 500:
        raise DeliveryError(f"provider error {result.status}", retryable=True)
    return result.body


class TextwireClient:
    """SMS through Textwire (https://api.textwire.example/v1). Textwire returns 429 when we exceed our send rate."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.textwire.example/v1"):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url

    def send(self, to: str, text: str) -> str:
        return _send(self._transport, f"{self._base_url}/messages", self._api_key, {"to": to, "body": text}, 5.0)["sid"]


class PostboxClient:
    """Email through Postbox (https://api.postbox.example/v1)."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.postbox.example/v1"):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url

    def send(self, to: str, subject: str, text: str) -> str:
        body = _send(self._transport, f"{self._base_url}/messages", self._api_key,
                     {"to": to, "subject": subject, "text": text, "from": "alerts@markets.example"}, 5.0)
        return body["message_id"]
