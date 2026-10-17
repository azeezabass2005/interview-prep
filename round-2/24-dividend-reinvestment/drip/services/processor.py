from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import List

from ..config import CENT, FEE_CAP_RATE, REINVEST_FEE, SHARE_UNIT
from ..errors import NotFound
from ..models import Account, DividendEvent, Movement, Payment
from ..register import ShareRegister
from ..store import InMemoryStore
from .enrolment import EnrolmentService
from .withholding import withholding

ZERO = Decimal("0")


class DividendProcessor:
    def __init__(self, store: InMemoryStore, register: ShareRegister, enrolment: EnrolmentService):
        self._store = store
        self._register = register
        self._enrolment = enrolment

    def process(self, event_id: str) -> List[Payment]:
        event = self._store.events.get(event_id)
        if event is None:
            raise NotFound(f"event {event_id}")
        payments = []
        holdings = self._register.holdings(event.security, event.pay_date)
        for account_id, shares in sorted(holdings.items()):
            if shares <= 0:
                continue
            account = self._store.account(account_id)
            gross = (shares * event.per_share).quantize(CENT, rounding=ROUND_DOWN)
            tax = withholding(account, gross)
            if self._enrolment.currently_enrolled(account_id, event.security):
                payments.append(self._reinvest(account, event, gross, tax))
            else:
                payments.append(Payment(event.event_id, account_id, gross, tax, ZERO, gross - tax, ZERO, ZERO))
        self._store.save_payments(event.event_id, payments)
        return payments

    def _reinvest(self, account: Account, event: DividendEvent, gross: Decimal, tax: Decimal) -> Payment:
        net = gross - tax
        fee = min(REINVEST_FEE, (gross * FEE_CAP_RATE).quantize(CENT, rounding=ROUND_HALF_UP))
        investable = net - fee
        shares = (investable / event.reinvest_price).quantize(SHARE_UNIT, rounding=ROUND_DOWN)
        leftover = investable - shares * event.reinvest_price
        self._store.set_leftover(account.account_id, event.security, leftover)
        if shares > 0:
            self._register.record(Movement(account.account_id, event.security, event.pay_date, shares, "DRIP"))
        return Payment(event.event_id, account.account_id, gross, tax, fee, ZERO, shares, leftover)
