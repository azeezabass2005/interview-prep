from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from .models import Trade


class TradeTape:
    def __init__(self):
        self.trades: List[Trade] = []
        self._notional: Dict[str, int] = defaultdict(int)
        self._volume: Dict[str, int] = defaultdict(int)

    def publish(self, trade: Trade) -> None:
        self.trades.append(trade)
        self._notional[trade.symbol] += trade.price * trade.quantity
        self._volume[trade.symbol] += trade.quantity

    def last_price(self, symbol: str):
        for trade in reversed(self.trades):
            if trade.symbol == symbol:
                return trade.price
        return None

    def vwap(self, symbol: str):
        if not self._volume[symbol]:
            return None
        value = Decimal(self._notional[symbol]) / Decimal(self._volume[symbol])
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
