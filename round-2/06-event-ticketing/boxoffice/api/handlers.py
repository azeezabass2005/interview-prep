from dataclasses import dataclass, field

from ..errors import BoxOfficeError
from ..services.checkout import CheckoutService
from ..services.refunds import RefundService
from ..services.seating import SeatService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class BoxOfficeApi:
    def __init__(self, seats: SeatService, checkout: CheckoutService, refunds: RefundService):
        self._seats = seats
        self._checkout = checkout
        self._refunds = refunds

    def _run(self, fn):
        try:
            return fn()
        except BoxOfficeError as e:
            return Response(e.status, {"error": str(e)})

    def post_hold(self, customer: str, event_id: str, body: dict) -> Response:
        def go():
            self._seats.hold(event_id, body.get("seats", []), customer)
            return Response(200, {"held": body["seats"]})
        return self._run(go)

    def post_purchase(self, customer: str, event_id: str, body: dict) -> Response:
        def go():
            o = self._checkout.purchase(customer, event_id, body.get("seats", []))
            return Response(201, {"order_id": o.order_id, "face_total_cents": o.face_total_cents,
                                  "fee_total_cents": o.fee_total_cents, "total_cents": o.total_cents})
        return self._run(go)

    def post_refund(self, order_id: str) -> Response:
        return self._run(lambda: Response(200, {"refunded_cents": self._refunds.refund(order_id)}))

    def get_available(self, event_id: str) -> Response:
        return Response(200, {"seats": self._seats.available(event_id)})
