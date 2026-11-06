import json

from .transport import TransportError, TransportTimeout


class ScanlyError(Exception):
    def __init__(self, message: str, retryable: bool):
        super().__init__(message)
        self.retryable = retryable


class ScanlyClient:
    """Receipt OCR from Scanly (https://api.scanly.example/v2). Returns the total it reads off the receipt."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.scanly.example/v2"):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url

    def read_total(self, image_b64: str) -> str:
        try:
            result = self._transport.send("POST", f"{self._base_url}/receipts", {"X-Api-Key": self._api_key},
                                          json.dumps({"image": image_b64}).encode(), 10.0)
        except (TransportTimeout, TransportError) as e:
            raise ScanlyError(str(e), retryable=True) from e
        if result.status == 422:
            raise ScanlyError(result.body.get("error", "unreadable receipt"), retryable=False)
        if result.status != 200:
            raise ScanlyError(f"scanly returned {result.status}", retryable=True)
        return str(result.body["total"])
