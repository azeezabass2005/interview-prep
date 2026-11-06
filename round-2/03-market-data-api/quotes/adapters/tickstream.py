from urllib.parse import urlencode

from ..errors import UpstreamError
from .transport import TransportError, TransportTimeout


class TickstreamClient:
    """Tickstream is our real-time price vendor (https://api.tickstream.example/v2). Billed per request."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.tickstream.example/v2", timeout: float = 2.0):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self._base_url}{path}?{urlencode(params)}"
        try:
            result = self._transport.send("GET", url, {"X-Api-Key": self._api_key}, None, self._timeout)
        except (TransportTimeout, TransportError) as e:
            raise UpstreamError("price vendor unreachable") from e
        if result.status != 200:
            raise UpstreamError(f"price vendor returned {result.status}")
        return result.body

    def latest(self, symbols: list[str]) -> dict[str, dict]:
        """{symbol: {"price": float, "currency": str, "ts": iso}} for each symbol Tickstream knows."""
        body = self._get("/quotes", {"symbols": ",".join(symbols)})
        return {q["symbol"]: q for q in body.get("quotes", [])}

    def fx_rate(self, base: str, quote: str) -> float:
        body = self._get("/fx", {"pair": f"{base}{quote}"})
        return float(body["rate"])
