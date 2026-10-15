from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict

from ..db import Database
from ..errors import PnlError
from ..repositories.market import FillRepository, FxRepository, PriceRepository, SplitRepository
from .fx import FxService
from .lots import apply_splits, build_lots

CENT = Decimal("0.01")


class PnlService:
    def __init__(self, db: Database):
        self._fills = FillRepository(db)
        self._prices = PriceRepository(db)
        self._splits = SplitRepository(db)
        self._fx = FxService(FxRepository(db))

    def position_pnl(self, book: str, as_of: date) -> Dict[str, dict]:
        by_security = defaultdict(list)
        for fill in self._fills.for_book(book, as_of):
            by_security[fill.security].append(fill)
        result = {}
        for security, fills in by_security.items():
            lots, realized, pending_splits = build_lots(fills, self._splits.for_security(security, as_of))
            apply_splits(lots, pending_splits, as_of)
            price = self._prices.close_on_or_before(security, as_of)
            if price is None and lots:
                raise PnlError(f"no price for {security}")
            unrealized = sum(((price - l.cost) * l.quantity for l in lots), Decimal("0"))
            result[security] = {"currency": fills[0].currency,
                                "quantity": sum((l.quantity for l in lots), Decimal("0")),
                                "realized": realized.quantize(CENT, rounding=ROUND_HALF_UP),
                                "unrealized": unrealized.quantize(CENT, rounding=ROUND_HALF_UP)}
        return result

    def book_total_usd(self, book: str, as_of: date) -> Decimal:
        total = Decimal("0")
        for row in self.position_pnl(book, as_of).values():
            total += row["realized"] + row["unrealized"]
        return total.quantize(CENT, rounding=ROUND_HALF_UP)
