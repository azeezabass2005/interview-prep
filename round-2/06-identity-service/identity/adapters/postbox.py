import json

from .transport import TransportError, TransportTimeout


class EmailError(Exception):
    pass


class PostboxClient:
    """Transactional email through Postbox (https://api.postbox.example/v1)."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.postbox.example/v1"):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url

    def send(self, to: str, subject: str, text: str) -> None:
        payload = json.dumps({"to": to, "subject": subject, "text": text, "from": "accounts@markets.example"}).encode()
        try:
            result = self._transport.send("POST", f"{self._base_url}/messages",
                                          {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                                          payload, 5.0)
        except (TransportTimeout, TransportError) as e:
            raise EmailError(str(e)) from e
        if result.status >= 300:
            raise EmailError(f"postbox returned {result.status}")
