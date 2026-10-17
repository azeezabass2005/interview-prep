from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Dict

from ..config import APR, CASH_FEE_MIN, CASH_FEE_RATE
from ..errors import CardError, NotFound
from ..models import CASH, FEE, PAYMENT, PURCHASE, REFUND, Account, Txn
from ..store import InMemoryStore

CENT = Decimal("0.01")
KINDS = (PURCHASE, REFUND, CASH, PAYMENT)
PAYMENT_ORDER = sorted(APR, key=APR.get)


def cash_fee(amount: Decimal) -> Decimal:
    return min(amount * CASH_FEE_RATE, CASH_FEE_MIN).quantize(CENT, rounding=ROUND_HALF_UP)


def apply(txn: Txn, balances: Dict[str, Decimal]) -> None:
    if txn.kind == PURCHASE or txn.kind == FEE:
        balances["purchase"] += txn.amount
    elif txn.kind == REFUND:
        balances["purchase"] -= txn.amount
    elif txn.kind == CASH:
        balances["cash"] += txn.amount + cash_fee(txn.amount)
    elif txn.kind == PAYMENT:
        remaining = txn.amount
        for bucket in PAYMENT_ORDER:
            applied = min(remaining, max(balances[bucket], Decimal("0")))
            balances[bucket] -= applied
            remaining -= applied
        balances["purchase"] -= remaining


class PostingService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def open(self, account_id: str, credit_limit, opened_on: date) -> Account:
        account = Account(account_id, Decimal(str(credit_limit)), opened_on)
        self._store.accounts[account_id] = account
        return account

    def post(self, account_id: str, posted_on: date, kind: str, amount) -> Txn:
        account = self._store.account(account_id)
        if account is None:
            raise NotFound(account_id)
        if kind not in KINDS:
            raise CardError(f"unknown kind {kind}")
        try:
            amount = Decimal(str(amount))
        except InvalidOperation:
            raise CardError("amount must be a number")
        if amount <= 0:
            raise CardError("amount must be positive")
        last = account.last_statement
        if last and posted_on <= last.cycle_end:
            raise CardError("cannot post into a closed cycle")
        txn = Txn(posted_on, kind, amount)
        account.txns.append(txn)
        return txn
