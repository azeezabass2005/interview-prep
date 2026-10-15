import math
from decimal import Decimal
from typing import Dict, List

from .models import Portfolio, Trade

CASH_BUFFER = Decimal("0.02")
BAND = Decimal("0.05")
MIN_TRADE_VALUE = Decimal("100")


def target_values(portfolio: Portfolio, targets: Dict[str, Decimal]) -> Dict[str, Decimal]:
    if abs(sum(targets.values()) - 1) > Decimal("0.0001"):
        raise ValueError("target weights must sum to 100%")
    investable = portfolio.total_value()
    return {symbol: investable * weight for symbol, weight in targets.items()}


def trade_quantity(target_value: Decimal, current_value: Decimal, price: Decimal) -> int:
    return math.floor((target_value - current_value) / price)


def plan(portfolio: Portfolio, targets: Dict[str, Decimal]) -> List[Trade]:
    total = portfolio.total_value()
    buffer = total * CASH_BUFFER
    cash = portfolio.cash
    trades: List[Trade] = []

    for symbol, target in target_values(portfolio, targets).items():
        holding = portfolio.holdings[symbol]
        diff = target - holding.value
        if abs(diff) <= BAND * target:
            continue
        qty = trade_quantity(target, holding.value, holding.price)
        if qty > 0:
            affordable = math.floor(max(cash - buffer, Decimal(0)) / holding.price)
            qty = min(qty, affordable)
        if qty == 0 or abs(qty) * holding.price < MIN_TRADE_VALUE:
            continue
        cash -= qty * holding.price
        trades.append(Trade("BUY" if qty > 0 else "SELL", symbol, abs(qty)))
    return trades
