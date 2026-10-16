from datetime import date

from .errors import BondError
from .services.booking import BookingService


class BondApi:
    def __init__(self, booking: BookingService, calendar):
        self._booking = booking
        self._calendar = calendar

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except BondError as exc:
            return exc.status, {"error": str(exc)}

    def load_bond(self, body: dict):
        return self._call(lambda: {"bond_id": self._booking.load_bond(body["bond_id"], body["coupon"], body["frequency"],
                                                                     date.fromisoformat(body["maturity"]),
                                                                     body.get("day_count", "30/360")).bond_id}, 201)

    def add_holiday(self, day: str):
        self._calendar.add_holiday(date.fromisoformat(day))
        return 200, {"holiday": day}

    def book(self, body: dict):
        def go():
            t = self._booking.book(body["trade_id"], body["bond_id"], body.get("side", "BUY"), body["face"],
                                   body["price"], date.fromisoformat(body["trade_date"]))
            return {"settle_date": t.settle_date.isoformat(), "accrued": str(t.accrued),
                    "settlement_amount": str(t.settlement_amount)}
        return self._call(go, 201)
