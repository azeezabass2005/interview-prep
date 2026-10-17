import itertools
from collections import defaultdict
from typing import Dict, List, Optional

from .models import Bid, Bidder, Lot


class InMemoryStore:
    def __init__(self):
        self.lots: Dict[str, Lot] = {}
        self.bidders: Dict[int, Bidder] = {}
        self.bids: Dict[str, List[Bid]] = defaultdict(list)
        self._seq = itertools.count(1)

    def next_seq(self) -> int:
        return next(self._seq)

    def add_lot(self, lot: Lot) -> None:
        self.lots[lot.lot_id] = lot

    def lot(self, lot_id: str) -> Optional[Lot]:
        return self.lots.get(lot_id)

    def add_bidder(self, bidder: Bidder) -> None:
        self.bidders[bidder.paddle] = bidder

    def bidder(self, paddle: int) -> Optional[Bidder]:
        return self.bidders.get(paddle)

    def add_bid(self, bid: Bid) -> None:
        self.bids[bid.lot_id].append(bid)

    def bids_for(self, lot_id: str) -> List[Bid]:
        return list(self.bids.get(lot_id, []))
