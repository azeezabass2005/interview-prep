from ..adapters.paystream import PaystreamDeclined
from ..auth import Principal
from ..clock import iso
from ..errors import Conflict, NotFound, ValidationError
from ..models import Payment, Refund
from ..money import to_minor

MAX_DESCRIPTION = 140


class PaymentService:
    def __init__(self, payments, refunds, paystream, clock, ids, logger, metrics):
        self._payments = payments
        self._refunds = refunds
        self._paystream = paystream
        self._clock = clock
        self._ids = ids
        self._logger = logger
        self._metrics = metrics

    def create(self, principal: Principal, idempotency_key: str | None, data: dict) -> tuple[Payment, bool]:
        """Returns (payment, created). A repeated Idempotency-Key returns the original payment."""
        if not idempotency_key:
            raise ValidationError("Idempotency-Key header is required")
        existing = self._payments.by_key(principal.org_id, idempotency_key)
        if existing is not None:
            return existing, False
        currency = str(data.get("currency", "")).upper()
        amount_minor = to_minor(str(data.get("amount", "")), currency)
        card_token = str(data.get("card_token", ""))
        if not card_token.startswith("tok_card_"):
            raise ValidationError("card_token must be a Paystream card token")
        description = str(data.get("description", ""))[:MAX_DESCRIPTION]
        now = iso(self._clock.now())
        payment = Payment(self._ids.new("pay"), principal.org_id, idempotency_key, amount_minor, currency, description,
                          "processing", None, None, now, now)
        self._payments.insert(payment)
        try:
            charge = self._paystream.create_charge(payment.id, amount_minor, currency, card_token, description)
        except PaystreamDeclined as e:
            self._payments.update(payment.id, iso(self._clock.now()), status="failed", failure_code=e.code)
            self._metrics.increment("payments_total", status="failed", currency=currency)
            return self._payments.get(principal.org_id, payment.id), True
        status = "captured" if charge.get("status") == "succeeded" else "pending"
        self._payments.update(payment.id, iso(self._clock.now()), status=status, psp_charge_id=charge["id"])
        self._metrics.increment("payments_total", status=status, currency=currency)
        self._logger.info("payment_created", payment_id=payment.id, merchant_id=principal.org_id, status=status)
        return self._payments.get(principal.org_id, payment.id), True

    def get(self, principal: Principal, payment_id: str) -> Payment:
        payment = self._payments.get(principal.org_id, payment_id)
        if payment is None:
            raise NotFound("payment not found")
        return payment

    def list(self, principal: Principal, status: str | None, limit: int) -> list[Payment]:
        return self._payments.list(principal.org_id, status, min(max(limit, 1), 100))

    def refund(self, principal: Principal, payment_id: str, amount: str | None) -> Refund:
        payment = self.get(principal, payment_id)
        if payment.status != "captured":
            raise Conflict(f"only captured payments can be refunded (this one is {payment.status})")
        amount_minor = payment.amount_minor if amount is None else to_minor(amount, payment.currency)
        remaining = payment.amount_minor - self._refunds.refunded_total(payment.id)
        if amount_minor > remaining:
            raise ValidationError(f"refund exceeds the refundable amount ({remaining} minor units left)")
        refund = Refund(self._ids.new("re"), payment.id, amount_minor, "pending", None, iso(self._clock.now()))
        result = self._paystream.create_refund(refund.id, payment.psp_charge_id, amount_minor)
        refund.psp_refund_id = result["id"]
        refund.status = "succeeded" if result.get("status") == "succeeded" else "pending"
        self._refunds.insert(refund)
        return refund

    def refunds(self, principal: Principal, payment_id: str) -> list[Refund]:
        return self._refunds.for_payment(self.get(principal, payment_id).id)
