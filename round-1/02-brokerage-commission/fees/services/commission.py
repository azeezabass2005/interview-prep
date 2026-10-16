from decimal import Decimal

from ..config import (EQUITY_MAX, EQUITY_MIN, EQUITY_TIERS, OPTION_MIN, OPTION_MULTIPLIER,
                      OPTION_PER_CONTRACT)
from ..models import EQUITY, OPTION, Trade
from ..money import clamp, half_up


def notional(trade: Trade) -> Decimal:
    if trade.asset_class == OPTION:
        return trade.price * trade.quantity * OPTION_MULTIPLIER
    return trade.price * trade.quantity


def tiered_equity_commission(amount: Decimal) -> Decimal:
    for upper, rate in EQUITY_TIERS:
        if upper is None or amount <= upper:
            return amount * rate
    raise AssertionError("tier table must end with an unbounded band")


def equity_commission(amount: Decimal) -> Decimal:
    return clamp(half_up(tiered_equity_commission(amount)), EQUITY_MIN, EQUITY_MAX)


def option_commission(contracts: int) -> Decimal:
    return clamp(half_up(OPTION_PER_CONTRACT * contracts), OPTION_MIN, EQUITY_MAX)


def commission_for(trade: Trade) -> Decimal:
    if trade.asset_class == EQUITY:
        return equity_commission(notional(trade))
    if trade.asset_class == OPTION:
        return option_commission(trade.quantity)
    raise ValueError(f"unknown asset class {trade.asset_class}")
