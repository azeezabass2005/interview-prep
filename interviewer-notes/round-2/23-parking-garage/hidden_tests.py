import unittest
from datetime import date, datetime

from garage.app import build_app


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current


def stay(entry, exit, plate="AB12CDE", pass_holder=False):
    clock = FakeClock(entry)
    api, _ = build_app(clock)
    if pass_holder:
        api.issue_pass({"plate": plate, "holder": "Pat", "valid_from": "2026-01-01", "valid_to": "2026-12-31"})
    _, t = api.enter(plate)
    clock.current = exit
    return api.exit(t["ticket_id"])[1]["charge_cents"]


class HiddenGarage(unittest.TestCase):
    def test_B1_cap_per_24_hours(self):
        self.assertEqual(stay(datetime(2026, 3, 2, 10), datetime(2026, 3, 3, 12)), 3200)

    def test_B2_fifteen_minutes_free(self):
        self.assertEqual(stay(datetime(2026, 3, 3, 10), datetime(2026, 3, 3, 10, 15)), 0)

    def test_B3_nine_oclock_too_late_for_early_bird(self):
        self.assertEqual(stay(datetime(2026, 3, 3, 9), datetime(2026, 3, 3, 17)), 2400)
        self.assertEqual(stay(datetime(2026, 3, 3, 8, 59), datetime(2026, 3, 3, 17)), 1200)

    def test_B4_public_cars_cannot_use_reserved_spaces(self):
        clock = FakeClock(datetime(2026, 3, 3, 10))
        api, _ = build_app(clock)
        for i in range(200):
            self.assertEqual(api.enter(f"PUB{i}")[0], 201)
        self.assertEqual(api.enter("PUB200")[0], 409)
        api.issue_pass({"plate": "PASS1", "holder": "Pat", "valid_from": "2026-01-01", "valid_to": "2026-12-31"})
        self.assertEqual(api.enter("PASS1")[0], 201)

    def test_B5_pass_uses_entry_day(self):
        self.assertEqual(stay(datetime(2026, 3, 6, 18), datetime(2026, 3, 7, 11), pass_holder=True), 0)
        self.assertGreater(stay(datetime(2026, 3, 8, 18), datetime(2026, 3, 9, 8), pass_holder=True), 0)
