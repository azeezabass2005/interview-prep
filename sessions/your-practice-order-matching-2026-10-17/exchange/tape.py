from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from .models import Trade


class TradeTape:
    def __init__(self):
        # Initialize trade history and per-symbol notional and volume totals.
        self.trades: List[Trade] = []
        self._notional: Dict[str, int] = defaultdict(int)
        self._volume: Dict[str, int] = defaultdict(int)

    def publish(self, trade: Trade) -> None:
        # Record a trade and update its symbol's notional and traded volume.
        self.trades.append(trade)
        self._notional[trade.symbol] += trade.price * trade.quantity
        self._volume[trade.symbol] += trade.quantity

    def last_price(self, symbol: str):
        # Return the symbol's most recent trade price, or None if it has no trades.
        for trade in reversed(self.trades):
            if trade.symbol == symbol:
                return trade.price
        return None

    def vwap(self, symbol: str):
        # Return the symbol's volume-weighted average price rounded to two decimal places.
        if not self._volume[symbol]:
            return None
        value = Decimal(self._notional[symbol]) / Decimal(self._volume[symbol])
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
