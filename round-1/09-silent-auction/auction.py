from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Optional

BANDS = [(Decimal("500"), Decimal("25")), (Decimal("100"), Decimal("10")), (Decimal("0"), Decimal("5"))]
SOFT_CLOSE = timedelta(minutes=5)
PREMIUM = Decimal("0.10")
CENT = Decimal("0.01")


class AuctionError(Exception):
    pass


@dataclass
class Item:
    item_id: str
    start: Decimal
    closes_at: datetime
    reserve: Optional[Decimal] = None
    maxes: Dict[str, tuple] = field(default_factory=dict)
    closed: bool = False


def increment(price):
    for floor, step in BANDS:
        if price > floor:
            return step
    return BANDS[-1][1]


class SilentAuction:
    def __init__(self):
        self.items = {}
        self._seq = 0

    def add_item(self, item_id, start, closes_at, reserve=None):
        reserve = Decimal(str(reserve)) if reserve is not None else None
        self.items[item_id] = Item(item_id, Decimal(str(start)), closes_at, reserve)

    def _item(self, item_id):
        item = self.items.get(item_id)
        if item is None:
            raise AuctionError("unknown item")
        return item

    def _ranked(self, item):
        return sorted(item.maxes.items(), key=lambda kv: (-kv[1][0], -kv[1][1]))

    def leader(self, item_id):
        ranked = self._ranked(self._item(item_id))
        return ranked[0][0] if ranked else None

    def price(self, item_id):
        item = self._item(item_id)
        ranked = self._ranked(item)
        if len(ranked) < 2:
            return item.start
        second = ranked[1][1][0]
        return second + increment(second)

    def bid(self, item_id, bidder, max_amount, at):
        item = self._item(item_id)
        max_amount = Decimal(str(max_amount))
        if item.closed or at >= item.closes_at:
            raise AuctionError("bidding is closed")
        if not item.maxes:
            minimum = item.start
        elif bidder == self.leader(item_id):
            minimum = item.maxes[bidder][0] + CENT
        else:
            current = self.price(item_id)
            minimum = current + increment(current)
        if max_amount < minimum:
            raise AuctionError(f"bid at least {minimum}")
        self._seq += 1
        item.maxes[bidder] = (max_amount, self._seq)
        if item.closes_at - at <= SOFT_CLOSE:
            item.closes_at = item.closes_at + SOFT_CLOSE
        return self.price(item_id)

    def close(self, item_id, at):
        item = self._item(item_id)
        if at < item.closes_at:
            raise AuctionError("auction still running")
        item.closed = True
        winner = self.leader(item_id)
        if winner is None:
            return None
        price = self.price(item_id)
        premium = (price * PREMIUM).quantize(CENT, rounding=ROUND_HALF_UP)
        return {"winner": winner, "price": price, "premium": premium, "total": price + premium}
