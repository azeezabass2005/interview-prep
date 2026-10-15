from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict

from .models import CASH, PAYMENT, PURCHASE, Cycle, Statement, Txn
from .rates import (APR, CASH_FEE_MIN, CASH_FEE_RATE, DAYS_PER_YEAR, MIN_PAYMENT_FLOOR,
                    MIN_PAYMENT_PERCENT, STANDARD_CYCLE_DAYS)

CENT = Decimal("0.01")
PAYMENT_ORDER = ["purchase", "cash"]


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def cash_advance_fee(amount: Decimal) -> Decimal:
    return cents(min(amount * CASH_FEE_RATE, CASH_FEE_MIN))


def _apply(txn: Txn, balances: Dict[str, Decimal]) -> None:
    if txn.kind == PURCHASE:
        balances["purchase"] += txn.amount
    elif txn.kind == CASH:
        balances["cash"] += txn.amount + cash_advance_fee(txn.amount)
    elif txn.kind == PAYMENT:
        remaining = txn.amount
        for bucket in PAYMENT_ORDER:
            applied = min(remaining, max(balances[bucket], Decimal("0")))
            balances[bucket] -= applied
            remaining -= applied
        balances["purchase"] -= remaining  # overpayment becomes a credit
    else:
        raise ValueError(f"unknown transaction kind {txn.kind}")


def build_statement(cycle: Cycle) -> Statement:
    balances = {"purchase": cycle.start_purchase, "cash": cycle.start_cash}
    daily_sum = {"purchase": Decimal("0"), "cash": Decimal("0")}
    by_day = defaultdict(list)
    for txn in cycle.txns:
        by_day[txn.day].append(txn)

    for day in range(cycle.days):
        for txn in by_day.get(day, []):
            _apply(txn, balances)
        for bucket, balance in balances.items():
            daily_sum[bucket] += max(balance, Decimal("0"))

    interest = {}
    for bucket in balances:
        average = daily_sum[bucket] / STANDARD_CYCLE_DAYS
        if cycle.paid_in_full_last_cycle:
            interest[bucket] = Decimal("0.00")
        else:
            interest[bucket] = cents(average * APR[bucket] / DAYS_PER_YEAR * cycle.days)

    total_interest = interest["purchase"] + interest["cash"]
    new_balance = balances["purchase"] + balances["cash"] + total_interest
    minimum = max(MIN_PAYMENT_FLOOR, cents(new_balance * MIN_PAYMENT_PERCENT) + total_interest)
    return Statement(balances["purchase"], balances["cash"], interest["purchase"], interest["cash"],
                     new_balance, minimum)
