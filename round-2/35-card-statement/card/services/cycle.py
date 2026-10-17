from collections import defaultdict
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from ..config import (APR, DAYS_PER_YEAR, DUE_DAYS, LATE_FEE, MIN_PAYMENT_FLOOR, MIN_PAYMENT_RATE,
                      OVER_LIMIT_FEE)
from ..errors import CardError, NotFound
from ..models import PAYMENT, Account, Statement
from ..store import InMemoryStore
from .posting import apply

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class CycleService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def _paid_by(self, account: Account, start: date, end: date) -> Decimal:
        return sum((t.amount for t in account.txns if t.kind == PAYMENT and start <= t.posted_on < end), ZERO)

    def close(self, account_id: str, close_date: date) -> Statement:
        account = self._store.account(account_id)
        if account is None:
            raise NotFound(account_id)
        previous = account.last_statement
        start = previous.cycle_end + timedelta(days=1) if previous else account.opened_on
        if close_date < start:
            raise CardError("close date before cycle start")
        days = (close_date - start).days + 1
        balances = dict(previous.balances) if previous else {"purchase": ZERO, "cash": ZERO}
        by_day = defaultdict(list)
        for txn in account.txns:
            if start <= txn.posted_on <= close_date:
                by_day[txn.posted_on].append(txn)
        daily_sum = {"purchase": ZERO, "cash": ZERO}
        over_limit = False
        for offset in range(days):
            day = start + timedelta(days=offset)
            for txn in by_day.get(day, []):
                apply(txn, balances)
            for bucket in daily_sum:
                daily_sum[bucket] += max(balances[bucket], ZERO)
            if balances["purchase"] + balances["cash"] > account.credit_limit:
                over_limit = True

        grace = False
        fees = ZERO
        if previous:
            paid = self._paid_by(account, start, previous.due_date)
            grace = paid >= previous.new_balance
            if paid < previous.minimum_due:
                fees += LATE_FEE
        if over_limit:
            fees += OVER_LIMIT_FEE

        interest = {}
        for bucket, apr in APR.items():
            if grace:
                interest[bucket] = ZERO
            else:
                interest[bucket] = cents(daily_sum[bucket] / 30 * apr / DAYS_PER_YEAR * days)
            balances[bucket] += interest[bucket]
        balances["purchase"] += fees

        new_balance = balances["purchase"] + balances["cash"]
        total_interest = sum(interest.values(), ZERO)
        minimum = max(MIN_PAYMENT_FLOOR, cents(new_balance * MIN_PAYMENT_RATE) + total_interest + fees)
        if new_balance < MIN_PAYMENT_FLOOR:
            minimum = max(new_balance, ZERO)
        statement = Statement(start, close_date, days, interest, fees, dict(balances), new_balance, minimum,
                              close_date + timedelta(days=DUE_DAYS))
        account.statements.append(statement)
        return statement
