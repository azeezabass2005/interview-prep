import json
import uuid

from .transport import TransportError, TransportTimeout

MAX_ATTEMPTS = 3


class PaystreamDeclined(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class PaystreamUnavailable(Exception):
    pass


class PaystreamClient:
    """Paystream is our card processor (https://api.paystream.example). Charges and refunds go through it; results come back
    synchronously when possible and as webhooks otherwise. Paystream de-duplicates requests by their Idempotency-Key header
    for 24 hours."""

    def __init__(self, transport, secret_key: str, base_url: str = "https://api.paystream.example/v1", timeout: float = 8.0):
        self._transport = transport
        self._secret_key = secret_key
        self._base_url = base_url
        self._timeout = timeout

    def _post(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode()
        last = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            headers = {
                "Authorization": f"Bearer {self._secret_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": str(uuid.uuid4()),
            }
            try:
                result = self._transport.send("POST", f"{self._base_url}{path}", headers, body, self._timeout)
            except (TransportTimeout, TransportError) as e:
                last = e
                continue
            if result.status >= 400:
                last = result
                continue
            return result.body
        if last is not None and not isinstance(last, Exception) and last.status < 500:
            error = last.body.get("error", {})
            raise PaystreamDeclined(error.get("code", "declined"), error.get("message", "card declined"))
        raise PaystreamUnavailable(f"paystream unavailable after {MAX_ATTEMPTS} attempts: {last}")

    def create_charge(self, payment_id: str, amount_minor: int, currency: str, card_token: str, description: str) -> dict:
        return self._post("/charges", {"amount": amount_minor, "currency": currency.lower(), "source": card_token,
                                       "description": description, "metadata": {"payment_id": payment_id}})

    def create_refund(self, refund_id: str, charge_id: str, amount_minor: int) -> dict:
        return self._post("/refunds", {"charge": charge_id, "amount": amount_minor, "metadata": {"refund_id": refund_id}})
