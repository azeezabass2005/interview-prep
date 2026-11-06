from ..http import Request, Response
from ..models import Payment, Refund
from ..money import to_major


def payment_json(p: Payment) -> dict:
    return {"id": p.id, "amount": to_major(p.amount_minor, p.currency), "amount_minor": p.amount_minor, "currency": p.currency,
            "description": p.description, "status": p.status, "failure_code": p.failure_code, "created_at": p.created_at}


def refund_json(r: Refund, currency: str) -> dict:
    return {"id": r.id, "payment_id": r.payment_id, "amount": to_major(r.amount_minor, currency), "status": r.status}


class Handlers:
    def __init__(self, payments, webhooks):
        self._payments = payments
        self._webhooks = webhooks

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.post("/payments", self.create)
        router.get("/payments", self.list)
        router.get("/payments/{payment_id}", self.get)
        router.post("/payments/{payment_id}/refunds", self.refund)
        router.get("/payments/{payment_id}/refunds", self.refunds)
        router.post("/webhooks/paystream", self.webhook)

    def create(self, request: Request) -> Response:
        payment, created = self._payments.create(request.principal, request.headers.get("Idempotency-Key"), request.json())
        return Response(201 if created else 200, payment_json(payment))

    def list(self, request: Request) -> Response:
        items = self._payments.list(request.principal, request.query.get("status"), int(request.query.get("limit", 50)))
        return Response(200, {"items": [payment_json(p) for p in items]})

    def get(self, request: Request) -> Response:
        return Response(200, payment_json(self._payments.get(request.principal, request.params["payment_id"])))

    def refund(self, request: Request) -> Response:
        payment = self._payments.get(request.principal, request.params["payment_id"])
        amount = request.json().get("amount")
        refund = self._payments.refund(request.principal, payment.id, None if amount is None else str(amount))
        return Response(201, refund_json(refund, payment.currency))

    def refunds(self, request: Request) -> Response:
        payment = self._payments.get(request.principal, request.params["payment_id"])
        return Response(200, {"items": [refund_json(r, payment.currency)
                                        for r in self._payments.refunds(request.principal, payment.id)]})

    def webhook(self, request: Request) -> Response:
        self._webhooks.handle(request.headers.get("Paystream-Signature"), request.body)
        return Response(200, {"received": True})
