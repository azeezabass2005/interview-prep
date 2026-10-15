from dataclasses import dataclass, field

from ..errors import StockError
from ..repositories.skus import SkuRepository
from ..services.availability import AvailabilityService
from ..services.checkout import CheckoutService
from ..services.reports import low_stock
from ..services.reservations import ReservationService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class InventoryApi:
    def __init__(self, db, clock):
        self._skus = SkuRepository(db)
        self._availability = AvailabilityService(self._skus)
        self._reservations = ReservationService(db, clock)
        self._checkout = CheckoutService(db, clock)

    def _run(self, fn):
        try:
            return fn()
        except StockError as e:
            return Response(e.status, {"error": str(e)})

    def get_availability(self, sku: str) -> Response:
        return self._run(lambda: Response(200, {"sku": sku, "available": self._availability.available(sku)}))

    def post_reservation(self, cart_id: str, body: dict) -> Response:
        def go():
            self._reservations.reserve(cart_id, body["sku"], body["qty"])
            return Response(201, {"cart_id": cart_id})
        return self._run(go)

    def post_checkout(self, cart_id: str) -> Response:
        return self._run(lambda: Response(200, {"lines": self._checkout.confirm(cart_id)}))

    def get_low_stock(self) -> Response:
        return Response(200, {"items": low_stock(self._skus)})
