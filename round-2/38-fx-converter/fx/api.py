from .errors import FxError
from .services.payments import PaymentService
from .services.quotes import QuoteService
from .services.rates import RateBook


class FxApi:
    def __init__(self, rates: RateBook, quotes: QuoteService, payments: PaymentService):
        self._rates = rates
        self._quotes = quotes
        self._payments = payments

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except FxError as exc:
            return exc.status, {"error": str(exc)}

    def publish(self, pair: str, rate):
        def go():
            self._rates.publish(pair, rate)
            return {"pair": pair}
        return self._call(go, 201)

    def quote(self, body: dict):
        def go():
            q = self._quotes.quote(body["customer"], body["source"], body["amount"], body["target"])
            return {"quote_id": q.quote_id, "target_amount": str(q.target_amount), "spread": str(q.spread),
                    "usd_equivalent": str(q.usd_equivalent)}
        return self._call(go, 201)

    def book(self, quote_id: str):
        return self._call(lambda: {"payment_id": self._payments.book(quote_id).payment_id}, 201)

    def cancel(self, payment_id: str):
        return self._call(lambda: {"status": self._payments.cancel(payment_id).status})
