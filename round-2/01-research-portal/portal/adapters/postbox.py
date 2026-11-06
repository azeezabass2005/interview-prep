import json

from .transport import TransportError, TransportTimeout


class EmailError(Exception):
    def __init__(self, message: str, retryable: bool):
        super().__init__(message)
        self.retryable = retryable


class PostboxClient:
    """Client for Postbox, the transactional email provider (https://api.postbox.example/v1)."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.postbox.example/v1", timeout: float = 5.0):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    def send(self, to: str, subject: str, html: str) -> str:
        body = json.dumps({"to": to, "subject": subject, "html": html, "from": "research@portal.example"}).encode()
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        try:
            result = self._transport.send("POST", f"{self._base_url}/messages", headers, body, self._timeout)
        except (TransportTimeout, TransportError) as e:
            raise EmailError(f"postbox unreachable: {e}", retryable=True) from e
        if result.status >= 500 or result.status == 429:
            raise EmailError(f"postbox returned {result.status}", retryable=True)
        if result.status >= 400:
            raise EmailError(f"postbox rejected the message: {result.body}", retryable=False)
        return result.body.get("message_id", "")
