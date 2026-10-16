from datetime import date

from .errors import HotelError
from .services.pricing import price
from .services.reservations import ReservationService


class HotelApi:
    def __init__(self, reservations: ReservationService):
        self._reservations = reservations

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except HotelError as exc:
            return exc.status, {"error": str(exc)}

    def quote(self, body: dict):
        def go():
            q = price(body["room_type"], date.fromisoformat(body["check_in"]), date.fromisoformat(body["check_out"]),
                      body.get("plan", "FLEXIBLE"), body.get("promo"))
            return {"nightly": [str(n) for n in q.nightly], "room_total": str(q.room_total), "tax": str(q.tax),
                    "total": str(q.total)}
        return self._call(go)

    def book(self, body: dict):
        def go():
            r = self._reservations.book(body["guest"], body["room_type"], date.fromisoformat(body["check_in"]),
                                        date.fromisoformat(body["check_out"]), body.get("plan", "FLEXIBLE"), body.get("promo"))
            return {"reservation_id": r.reservation_id, "total": str(r.quote.total)}
        return self._call(go, 201)

    def cancel(self, reservation_id: str):
        return self._call(lambda: {"refund": str(self._reservations.cancel(reservation_id).refund)})
