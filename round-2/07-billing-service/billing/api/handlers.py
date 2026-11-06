from ..errors import NotFound, ValidationError
from ..http import Request, Response


def invoice_json(row, lines=None, payments=None) -> dict:
    body = {k: row[k] for k in ("id", "customer_id", "period", "subtotal_cents", "tax_cents", "total_cents", "status",
                                "created_at")}
    if lines is not None:
        body["lines"] = [{"description": l["description"], "amount_cents": l["amount_cents"]} for l in lines]
    if payments is not None:
        body["payments"] = [{"id": p["id"], "amount_cents": p["amount_cents"], "received_at": p["received_at"]} for p in payments]
    return body


class Handlers:
    def __init__(self, seats, usage, invoices, payments, webhooks, ids):
        self._seats = seats
        self._usage = usage
        self._invoices = invoices
        self._payments = payments
        self._webhooks = webhooks
        self._ids = ids

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.post("/seats", self.change_seats)
        router.post("/internal/usage", self.usage)
        router.get("/invoices", self.list_invoices)
        router.get("/invoices/{invoice_id}", self.get_invoice)
        router.post("/webhooks/paygate", self.webhook)

    def change_seats(self, request: Request) -> Response:
        request.principal.require_role("billing_admin")
        try:
            seats = int(request.json()["seats"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValidationError("seats must be an integer") from e
        return Response(200, self._seats.change(request.principal.org_id, seats))

    def usage(self, request: Request) -> Response:
        request.principal.require_role("metering")
        data = request.json()
        self._usage.record(str(data["event_id"]), str(data["customer_id"]), int(data["quantity"]), str(data["occurred_at"]))
        return Response(202, {"accepted": True})

    def list_invoices(self, request: Request) -> Response:
        return Response(200, {"invoices": [invoice_json(r) for r in self._invoices.for_customer(request.principal.org_id)]})

    def get_invoice(self, request: Request) -> Response:
        row = self._invoices.get(request.params["invoice_id"])
        if row is None or row["customer_id"] != request.principal.org_id:
            raise NotFound("invoice not found")
        return Response(200, invoice_json(row, self._invoices.lines(row["id"]), self._payments.for_invoice(row["id"])))

    def webhook(self, request: Request) -> Response:
        self._webhooks.handle(request.headers.get("X-Paygate-Secret"), request.json())
        return Response(200, {"received": True})
