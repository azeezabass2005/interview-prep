import unittest
from decimal import Decimal

from library.app import build_app


def world():
    api, store = build_app()
    api.setup({"MAIN": []}, {"b1": ("BOOK", "MAIN"), "d1": ("DVD", "MAIN")}, ["ann", "bob"])
    return api, store


class HiddenLibrary(unittest.TestCase):
    def test_B1_sundays_closed(self):
        api, _ = world()
        api.checkout("ann", "d1", "2026-03-02")
        self.assertEqual(api.check_in("d1", "2026-03-16")[1]["fine"], "6.00")

    def test_B2_grace_forgives_one_day_only(self):
        api, _ = world()
        api.checkout("ann", "b1", "2026-03-02")
        self.assertEqual(api.check_in("b1", "2026-03-25")[1]["fine"], "0.50")

    def test_B3_renewal_from_due_date(self):
        api, _ = world()
        api.checkout("ann", "b1", "2026-03-02")
        self.assertEqual(api.renew("b1", "2026-03-10")[1]["due"], "2026-04-13")

    def test_B4_no_renewal_with_holds(self):
        api, _ = world()
        api.checkout("ann", "b1", "2026-03-02")
        api.hold("bob", "b1")
        self.assertEqual(api.renew("b1", "2026-03-10")[0], 409)

    def test_B5_blocked_at_ten_dollars(self):
        api, store = world()
        store.patrons["ann"].balance = Decimal("10.00")
        self.assertEqual(api.checkout("ann", "b1", "2026-03-02")[0], 409)
