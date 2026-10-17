from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List

from ..config import CONCENTRATED_HAIRCUT, CONCENTRATION_LIMIT, HAIRCUTS, SHORT_ADD_ON, STALE_SURCHARGE
from ..models import Account, Line
from ..store import InMemoryStore
from .prices import PriceService

ZERO = Decimal("0")


class Valuation:
    def __init__(self, store: InMemoryStore, prices: PriceService):
        self._store = store
        self._prices = prices

    def lines(self, account: Account, run_date: date) -> List[Line]:
        raw = []
        for symbol, qty in sorted(account.positions.items()):
            if qty == 0:
                continue
            price = self._prices.latest(symbol, run_date)
            raw.append((symbol, qty, price))
        base = sum((qty * p.price for _, qty, p in raw), ZERO)
        lines = []
        for symbol, qty, p in raw:
            mv = qty * p.price
            haircut = None
            if qty > 0:
                haircut = HAIRCUTS[self._store.securities[symbol]]
                if p.on < run_date - timedelta(days=1):
                    haircut += STALE_SURCHARGE
                if base > 0 and mv / base > CONCENTRATION_LIMIT:
                    haircut = max(haircut, CONCENTRATED_HAIRCUT)
            lines.append(Line(symbol, qty, p.price, mv, haircut))
        return lines

    def summary(self, account: Account, run_date: date) -> Dict[str, Decimal]:
        lines = self.lines(account, run_date)
        collateral = sum((l.market_value * (1 - l.haircut) for l in lines if l.quantity > 0), ZERO)
        collateral += max(account.cash, ZERO)
        requirement = max(-account.cash, ZERO)
        requirement += sum((abs(l.market_value) * SHORT_ADD_ON for l in lines if l.quantity < 0), ZERO)
        return {"collateral": collateral, "requirement": requirement, "excess": collateral - requirement}
