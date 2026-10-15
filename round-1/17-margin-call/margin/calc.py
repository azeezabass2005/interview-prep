from decimal import ROUND_HALF_UP, Decimal
from typing import Dict

from .models import (CALL_ROUNDING, CONCENTRATED_HAIRCUT, CONCENTRATION_LIMIT, HAIRCUTS,
                     SHORT_REQUIREMENT, Account)

ZERO = Decimal("0")


def haircuts(account: Account) -> Dict[str, Decimal]:
    """Effective haircut per long position symbol."""
    base_value = sum((p.market_value for p in account.positions), ZERO)
    result = {}
    for p in account.positions:
        if not p.is_long:
            continue
        haircut = HAIRCUTS[p.asset_class]
        if base_value > 0 and p.market_value / base_value >= CONCENTRATION_LIMIT:
            haircut = max(haircut, CONCENTRATED_HAIRCUT)
        result[p.symbol] = haircut
    return result


def collateral(account: Account) -> Decimal:
    cuts = haircuts(account)
    return sum((p.market_value * (1 - cuts[p.symbol]) for p in account.positions if p.is_long), ZERO)


def requirement(account: Account) -> Decimal:
    loan = max(-account.cash, ZERO)
    shorts = sum((abs(p.market_value) * SHORT_REQUIREMENT for p in account.positions if not p.is_long), ZERO)
    return loan + shorts


def excess(account: Account) -> Decimal:
    return collateral(account) - requirement(account)


def margin_call(account: Account) -> Decimal:
    shortfall = -excess(account)
    if shortfall <= 0:
        return ZERO
    return (shortfall / CALL_ROUNDING).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * CALL_ROUNDING
