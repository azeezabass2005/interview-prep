from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from ..config import SOFT_CLOSE_SECONDS
from ..errors import NotFound, Rejected
from ..models import Bid, Bidder, Lot
from ..store import InMemoryStore
from .pricing import standing


class BiddingService:
    def __init__(self, store: InMemoryStore, clock):
        self._store = store
        self._clock = clock

    def register(self, paddle: int, name: str) -> Bidder:
        if self._store.bidder(paddle):
            raise Rejected(f"paddle {paddle} taken")
        bidder = Bidder(paddle, name)
        self._store.add_bidder(bidder)
        return bidder

    def add_lot(self, lot: Lot) -> Lot:
        if self._store.lot(lot.lot_id):
            raise Rejected(f"lot {lot.lot_id} exists")
        self._store.add_lot(lot)
        return lot

    def lot(self, lot_id: str) -> Lot:
        lot = self._store.lot(lot_id)
        if lot is None:
            raise NotFound(f"lot {lot_id}")
        return lot

    def bid(self, lot_id: str, paddle: int, maximum) -> Bid:
        lot = self.lot(lot_id)
        if self._store.bidder(paddle) is None:
            raise NotFound(f"paddle {paddle}")
        try:
            maximum = Decimal(str(maximum))
        except InvalidOperation:
            raise Rejected("bid must be a number")
        now = self._clock.now()
        if lot.closed or now >= lot.closes_at:
            raise Rejected("lot is closed")
        own = [b.maximum for b in self._store.bids_for(lot_id) if b.paddle == paddle]
        if own and maximum <= max(own):
            raise Rejected("new maximum must be higher than your current maximum")
        if maximum < lot.opening:
            raise Rejected("bid below opening price")
        bid = Bid(lot_id, paddle, maximum, now, self._store.next_seq())
        self._store.add_bid(bid)
        if lot.closes_at - now <= timedelta(seconds=SOFT_CLOSE_SECONDS):
            lot.closes_at = lot.closes_at + timedelta(seconds=SOFT_CLOSE_SECONDS)
        return bid

    def current(self, lot_id: str):
        lot = self.lot(lot_id)
        return standing(lot, self._store.bids_for(lot_id))
