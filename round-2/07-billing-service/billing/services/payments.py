import hmac

from ..clock import iso
from ..errors import NotFound, Unauthorized


class PaymentWebhooks:
    """Paygate (our card processor) calls us when an invoice payment succeeds. Paygate delivers each event at least once and
    retries until we answer 2xx, so the same event can arrive more than once."""

    def __init__(self, secret: str, invoices, payments, clock, ids, logger):
        self._secret = secret
        self._invoices = invoices
        self._payments = payments
        self._clock = clock
        self._ids = ids
        self._logger = logger

    def handle(self, secret_header: str | None, event: dict) -> None:
        if not secret_header or not hmac.compare_digest(secret_header, self._secret):
            raise Unauthorized("bad webhook secret")
        if event.get("type") != "payment.succeeded":
            return
        data = event.get("data", {})
        invoice = self._invoices.get(str(data.get("invoice_id", "")))
        if invoice is None:
            raise NotFound("unknown invoice")
        self._payments.add(self._ids.new("pmt"), invoice["id"], str(data["payment_id"]), int(data["amount_cents"]),
                           iso(self._clock.now()))
        if self._payments.paid_total(invoice["id"]) >= invoice["total_cents"]:
            self._invoices.set_status(invoice["id"], "paid")
        self._logger.info("payment_recorded", invoice_id=invoice["id"], payment_id=data["payment_id"])
