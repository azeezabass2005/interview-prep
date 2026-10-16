from datetime import date
from decimal import Decimal
from typing import List, Tuple

from ..errors import PnlError
from ..models import Fill, Lot, Split


def apply_splits(lots: List[Lot], splits: List[Split], as_of: date) -> None:
    for split in splits:
        if split.effective > as_of:
            continue
        for lot in lots:
            if lot.opened >= split.effective:
                lot.quantity *= split.ratio
                lot.cost /= split.ratio


def build_lots(fills: List[Fill], splits: List[Split]) -> Tuple[List[Lot], Decimal]:
    lots: List[Lot] = []
    realized = Decimal("0")
    applied = set()
    for fill in fills:
        due = [s for s in splits if s.effective <= fill.trade_date and s.effective not in applied]
        apply_splits(lots, due, fill.trade_date)
        applied.update(s.effective for s in due)
        if fill.side == "BUY":
            lots.append(Lot(fill.trade_date, fill.quantity, fill.price))
            continue
        open_qty = sum((l.quantity for l in lots), Decimal("0"))
        if fill.quantity > open_qty:
            raise PnlError("short selling is not supported")
        average_cost = sum((l.quantity * l.cost for l in lots), Decimal("0")) / open_qty
        realized += (fill.price - average_cost) * fill.quantity
        remaining = fill.quantity
        while remaining > 0:
            lot = lots[0]
            take = min(lot.quantity, remaining)
            lot.quantity -= take
            remaining -= take
            if lot.quantity == 0:
                lots.pop(0)
    remaining_splits = [s for s in splits if s.effective not in applied]
    return lots, realized, remaining_splits
