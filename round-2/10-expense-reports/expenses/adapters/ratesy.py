from urllib.parse import urlencode

from ..errors import UpstreamError
from .transport import TransportError, TransportTimeout


class RatesyClient:
    """Historical FX rates from Ratesy (https://api.ratesy.example/v1): the rate on a given date."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.ratesy.example/v1"):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url

    def rate(self, base: str, quote: str, on_date: str) -> float:
        url = f"{self._base_url}/historical?{urlencode({'date': on_date, 'base': base, 'symbols': quote})}"
        try:
            result = self._transport.send("GET", url, {"X-Api-Key": self._api_key}, None, 3.0)
        except (TransportTimeout, TransportError) as e:
            raise UpstreamError("FX rates unavailable, try again shortly") from e
        if result.status != 200:
            raise UpstreamError(f"FX rates unavailable ({result.status})")
        return float(result.body["rates"][quote])
