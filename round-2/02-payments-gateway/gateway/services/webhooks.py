from ..adapters import webhooks
from ..clock import iso


class WebhookService:
    """Applies Paystream events. Paystream retries a webhook until we answer 2xx, so handling must be idempotent."""

    def __init__(self, secret: str, payments, refunds, events, clock, logger):
        self._secret = secret
        self._payments = payments
        self._refunds = refunds
        self._events = events
        self._clock = clock
        self._logger = logger

    def handle(self, signature_header: str | None, body: bytes) -> None:
        event = webhooks.verify(self._secret, signature_header, body, int(self._clock.now().timestamp()))
        if not self._events.record(event["id"], event["type"], iso(self._clock.now())):
            return
        data = event.get("data", {})
        now = iso(self._clock.now())
        if event["type"] in ("charge.succeeded", "charge.failed"):
            payment = self._payments.by_charge(data.get("id", ""))
            if payment is None:
                self._logger.warning("webhook_unknown_charge", charge_id=data.get("id"))
                return
            if event["type"] == "charge.succeeded":
                self._payments.update(payment.id, now, status="captured")
            else:
                self._payments.update(payment.id, now, status="failed", failure_code=data.get("failure_code", "declined"))
        elif event["type"] == "refund.succeeded":
            self._refunds.set_status(data.get("id", ""), "succeeded")
        self._logger.info("webhook_applied", event_id=event["id"], type=event["type"])
