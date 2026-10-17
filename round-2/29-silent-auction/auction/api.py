from datetime import datetime
from decimal import Decimal

from .errors import AuctionError
from .models import Lot
from .services.bidding import BiddingService
from .services.closing import ClosingService
from .services.invoices import build_invoices
from .store import InMemoryStore


class AuctionApi:
    def __init__(self, store: InMemoryStore, bidding: BiddingService, closing: ClosingService):
        self._store = store
        self._bidding = bidding
        self._closing = closing

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except AuctionError as exc:
            return exc.status, {"error": str(exc)}

    def add_lot(self, body: dict):
        def go():
            lot = Lot(body["lot_id"], body.get("title", ""), Decimal(str(body["opening"])), Decimal(str(body["fmv"])),
                      datetime.fromisoformat(body["closes_at"]),
                      Decimal(str(body["reserve"])) if body.get("reserve") is not None else None)
            return {"lot_id": self._bidding.add_lot(lot).lot_id}
        return self._call(go, 201)

    def register(self, paddle: int, name: str):
        return self._call(lambda: {"paddle": self._bidding.register(paddle, name).paddle}, 201)

    def bid(self, lot_id: str, paddle: int, maximum):
        def go():
            self._bidding.bid(lot_id, paddle, maximum)
            winner, price = self._bidding.current(lot_id)
            lot = self._bidding.lot(lot_id)
            return {"leader": winner, "price": str(price), "closes_at": lot.closes_at.isoformat()}
        return self._call(go, 201)

    def close(self, lot_id: str):
        def go():
            lot = self._closing.close(lot_id)
            return {"winner": lot.winner, "hammer": str(lot.hammer) if lot.hammer is not None else None}
        return self._call(go)

    def invoices(self):
        return self._call(lambda: {str(p): {"total": str(inv.total),
                                            "lines": [{"lot": l.lot_id, "hammer": str(l.hammer), "premium": str(l.premium),
                                                       "deductible": str(l.deductible)} for l in inv.lines]}
                                   for p, inv in build_invoices(self._store).items()})
