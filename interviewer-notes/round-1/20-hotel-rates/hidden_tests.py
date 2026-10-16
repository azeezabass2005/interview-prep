import unittest
from datetime import datetime

from hotel.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


def app(now=datetime(2026, 5, 1, 9, 0)):
    return build_app(FakeClock(now))[0]


def stay(room, check_in, check_out, **kw):
    body = {"room_type": room, "check_in": check_in, "check_out": check_out}
    body.update(kw)
    return body


class HiddenHotel(unittest.TestCase):
    def test_B1_friday_and_saturday_nights(self):
        q = app().quote(stay("DELUXE", "2026-06-04", "2026-06-07"))[1]
        self.assertEqual(q["nightly"], ["220", "264.00", "264.00"])

    def test_B2_every_night_must_be_available(self):
        api = app()
        for guest in ("a", "b"):
            api.book(dict(stay("SUITE", "2026-06-03", "2026-06-04"), guest=guest))
        self.assertEqual(api.book(dict(stay("SUITE", "2026-06-02", "2026-06-04"), guest="c"))[0], 409)

    def test_B3_promo_applied_last(self):
        q = app().quote(stay("STANDARD", "2026-06-01", "2026-06-04", promo="SAVE50"))[1]
        self.assertEqual(q["room_total"], "377.50")

    def test_B4_city_fee_not_taxed(self):
        self.assertEqual(app().quote(stay("STANDARD", "2026-06-01", "2026-06-02"))[1]["total"], "175.63")

    def test_B5_refund_window_to_3pm(self):
        api = app(datetime(2026, 5, 28, 10, 0))
        booked = api.book(dict(stay("DELUXE", "2026-06-04", "2026-06-07"), guest="g"))[1]
        self.assertEqual(api.cancel(booked["reservation_id"])[1]["refund"], booked["total"])
