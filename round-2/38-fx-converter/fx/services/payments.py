import uuid
from decimal import Decimal

from ..config import CANCEL_WINDOW, DAILY_LIMIT_USD, QUOTE_TTL
from ..errors import NotFound, Rejected
from ..models import BOOKED, CANCELLED, Payment
from ..store import InMemoryStore


class PaymentService:
    def __init__(self, store: InMemoryStore, clock):
        self._store = store
        self._clock = clock

    def booked_today(self, customer: str) -> Decimal:
        today = self._clock.now().date()
        total = Decimal(0)
        for payment_id in self._store.payments_by_customer[customer]:
            payment = self._store.payments[payment_id]
            if payment.booked_at.date() == today:
                total += self._store.quotes[payment.quote_id].usd_equivalent
        return total

    def book(self, quote_id: str) -> Payment:
        quote = self._store.quotes.get(quote_id)
        if quote is None:
            raise NotFound(quote_id)
        if quote.booked:
            raise Rejected("quote already booked")
        if self.booked_today(quote.customer) + quote.usd_equivalent > DAILY_LIMIT_USD:
            raise Rejected("daily limit exceeded")
        quote.booked = True
        payment = Payment(f"p-{uuid.uuid4().hex[:8]}", quote_id, quote.customer, self._clock.now())
        self._store.payments[payment.payment_id] = payment
        self._store.payments_by_customer[quote.customer].append(payment.payment_id)
        return payment

    def cancel(self, payment_id: str) -> Payment:
        payment = self._store.payments.get(payment_id)
        if payment is None:
            raise NotFound(payment_id)
        if payment.status != BOOKED or self._clock.now() - payment.booked_at > CANCEL_WINDOW:
            raise Rejected("payment can no longer be cancelled")
        payment.status = CANCELLED
        return payment
