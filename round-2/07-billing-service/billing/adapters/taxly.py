import json

from .transport import TransportError, TransportTimeout


class TaxUnavailable(Exception):
    pass


class TaxlyClient:
    """Sales tax / VAT from Taxly (https://api.taxly.example/v3). Taxly is slow at month start; calls time out after 3 s."""

    def __init__(self, transport, api_key: str, base_url: str = "https://api.taxly.example/v3"):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url

    def tax_for(self, country: str, amount_cents: int) -> int:
        body = json.dumps({"country": country, "amount": amount_cents, "currency": "usd", "product": "saas"}).encode()
        try:
            result = self._transport.send("POST", f"{self._base_url}/calculate",
                                          {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                                          body, 3.0)
        except (TransportTimeout, TransportError) as e:
            raise TaxUnavailable(str(e)) from e
        if result.status != 200:
            raise TaxUnavailable(f"taxly returned {result.status}")
        return int(result.body["tax_amount"])
