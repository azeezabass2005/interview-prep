from ..errors import Rejected
from ..store import InMemoryStore
from .bidding import BiddingService
from .pricing import standing


class ClosingService:
    def __init__(self, store: InMemoryStore, bidding: BiddingService, clock):
        self._store = store
        self._bidding = bidding
        self._clock = clock

    def close(self, lot_id: str):
        lot = self._bidding.lot(lot_id)
        if lot.closed:
            raise Rejected("already closed")
        if self._clock.now() < lot.closes_at:
            raise Rejected("lot is still open")
        winner, price = standing(lot, self._store.bids_for(lot_id))
        lot.closed = True
        if winner is not None and (lot.reserve is None or price >= lot.reserve):
            lot.winner, lot.hammer = winner, price
        return lot
