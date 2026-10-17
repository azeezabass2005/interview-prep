from datetime import date

from ..config import VOLUME_DISCOUNT_FROM, VOLUME_DISCOUNT_RATE
from ..errors import NotFound
from ..models import ACTIVE, Statement, StatementLine
from ..money import ZERO, half_up
from ..store import InMemoryStore
from .commission import commission_for
from .regulatory import regulatory_fee


def month_bounds(year: int, month: int):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


class StatementService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def trades_in_month(self, account_id: str, year: int, month: int):
        start, end = month_bounds(year, month)
        trades = [t for t in self._store.trades_for(account_id) if start <= t.executed_at.date() <= end]
        return sorted(trades, key=lambda t: (t.executed_at, t.trade_id))

    def build(self, account_id: str, year: int, month: int) -> Statement:
        if self._store.account(account_id) is None:
            raise NotFound(f"account {account_id}")
        statement = Statement(account_id, year, month)
        for number, trade in enumerate(self.trades_in_month(account_id, year, month), start=1):
            if trade.status != ACTIVE:
                continue
            commission = commission_for(trade)
            discount = half_up(commission * VOLUME_DISCOUNT_RATE) if number >= VOLUME_DISCOUNT_FROM else ZERO
            statement.lines.append(StatementLine(trade.trade_id, commission, discount, regulatory_fee(trade)))
        return statement
