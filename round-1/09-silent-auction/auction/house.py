import itertools
from typing import Dict, Optional

from .models import AuctionError, Bid, Lot, Result
from .pricing import settle


class AuctionHouse:
    def __init__(self):
        self._lots: Dict[str, Lot] = {}
        self._seq = itertools.count(1)

    def add_lot(self, lot_id: str, reserve_cents: Optional[int] = None) -> Lot:
        if lot_id in self._lots:
            raise AuctionError(f"duplicate lot {lot_id}")
        lot = Lot(lot_id, reserve_cents)
        self._lots[lot_id] = lot
        return lot

    def place_bid(self, lot_id: str, bidder: str, amount_cents: int) -> Bid:
        lot = self._lots[lot_id]
        if amount_cents <= 0:
            raise AuctionError("bid must be positive")
        bid = Bid(bidder, amount_cents, next(self._seq))
        lot.bids.append(bid)
        return bid

    def close(self, lot_id: str) -> Optional[Result]:
        lot = self._lots[lot_id]
        lot.closed = True
        return settle(lot)
