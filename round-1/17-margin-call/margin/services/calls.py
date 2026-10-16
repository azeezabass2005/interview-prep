from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from ..config import CALL_ROUNDING
from ..errors import NotFound
from ..models import MET, Call, Deposit
from ..store import InMemoryStore
from .valuation import Valuation


def round_call(shortfall: Decimal) -> Decimal:
    return (shortfall / CALL_ROUNDING).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * CALL_ROUNDING


class CallService:
    def __init__(self, store: InMemoryStore, valuation: Valuation):
        self._store = store
        self._valuation = valuation

    def deposit(self, account_id: str, on: date, amount) -> Deposit:
        account = self._store.account(account_id)
        if account is None:
            raise NotFound(account_id)
        d = Deposit(account_id, on, Decimal(str(amount)))
        account.cash += d.amount
        self._store.deposits[account_id].append(d)
        self._check_met(account_id)
        return d

    def _check_met(self, account_id: str) -> None:
        call = self._store.open_call(account_id)
        if call is None:
            return
        deposited = sum((d.amount for d in self._store.deposits[account_id]), Decimal("0"))
        if deposited >= call.amount:
            call.status = MET

    def run(self, account_id: str, run_date: date) -> Optional[Call]:
        account = self._store.account(account_id)
        if account is None:
            raise NotFound(account_id)
        excess = self._valuation.summary(account, run_date)["excess"]
        call = self._store.open_call(account_id)
        if excess >= 0:
            if call:
                call.status = MET
            return None
        if call:
            return call
        call = Call(account_id, run_date, round_call(-excess))
        self._store.calls[account_id].append(call)
        return call
