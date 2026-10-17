import math
from decimal import Decimal
from typing import List

from ..models import Account, Model, Trade
from .prices import PriceService
from .targets import CASH_BUFFER, target_values, total_value

BAND = Decimal("0.05")
MIN_TRADE = Decimal("100")


def quantity(target: Decimal, current: Decimal, price: Decimal) -> int:
    return math.floor((target - current) / price)


def plan(account: Account, model: Model, prices: PriceService) -> List[Trade]:
    total = total_value(account, prices)
    buffer = total * CASH_BUFFER
    cash = account.cash
    trades: List[Trade] = []
    for symbol, target in sorted(target_values(account, model, prices).items()):
        price = prices.get(symbol)
        current = account.holdings.get(symbol, 0) * price
        diff = target - current
        restricted = symbol in account.restricted
        if not restricted and abs(diff) <= BAND * target:
            continue
        qty = quantity(target, current, price)
        if qty > 0:
            qty = min(qty, math.floor(max(cash - buffer, Decimal(0)) / price))
        if qty == 0 or abs(qty) * price < MIN_TRADE:
            continue
        cash -= qty * price
        trades.append(Trade("BUY" if qty > 0 else "SELL", symbol, abs(qty)))
    return trades
