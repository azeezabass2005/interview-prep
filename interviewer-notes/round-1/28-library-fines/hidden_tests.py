import unittest
from datetime import date
from decimal import Decimal

from library import Library


def lib():
    l = Library()
    for item, kind in (("b1", "BOOK"), ("d1", "DVD")) + tuple((f"x{i}", "BOOK") for i in range(6)):
        l.add_item(item, kind)
    for p in ("ana", "bob", "cat"):
        l.add_patron(p)
    return l


class HiddenLibrary(unittest.TestCase):
    def test_B1_sunday_due_date_moves_to_monday(self):
        self.assertEqual(lib().checkout("ana", "d1", date(2026, 3, 5)).due, date(2026, 3, 9))

    def test_B2_fine_is_capped(self):
        l = lib()
        l.checkout("ana", "d1", date(2026, 3, 5))
        self.assertEqual(l.check_in("d1", date(2026, 4, 20)), Decimal("15.00"))

    def test_B3_renewal_from_due_date(self):
        l = lib()
        l.checkout("ana", "b1", date(2026, 3, 2))
        self.assertEqual(l.renew("b1", date(2026, 3, 10)).due, date(2026, 4, 13))

    def test_B4_holds_first_come_first_served(self):
        l = lib()
        l.checkout("ana", "b1", date(2026, 3, 2))
        l.place_hold("bob", "b1")
        l.place_hold("cat", "b1")
        l.check_in("b1", date(2026, 3, 9))
        self.assertEqual(l.hold_shelf["b1"], "bob")

    def test_B5_returned_items_do_not_count_toward_limit(self):
        l = lib()
        for i in range(5):
            l.checkout("ana", f"x{i}", date(2026, 3, 2))
        l.check_in("x0", date(2026, 3, 3))
        self.assertEqual(l.checkout("ana", "x5", date(2026, 3, 3)).item, "x5")
