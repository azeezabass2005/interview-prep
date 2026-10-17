import unittest
from decimal import Decimal

from gradebook.app import build_app
from gradebook.services.grading import category_percent

DUE = "2026-03-01T23:59"


def course(*items):
    """items: (id, category, max, points or None, submitted_at)"""
    api, store = build_app()
    api.create("C", ["ana"])
    for aid, cat, max_points, points, at in items:
        api.assignment("C", {"id": aid, "category": cat, "max_points": max_points, "due": DUE})
        if points is not None:
            api.submit("C", "ana", aid, at or "2026-03-01T12:00")
            api.grade("C", "ana", aid, points)
    return api, store


FULL = [("q", "QUIZ", 10, 10, None), ("hw", "HOMEWORK", 10, 10, None)]


class HiddenGradebook(unittest.TestCase):
    def test_B1_drop_lowest_percentage(self):
        _, store = course(("a", "HOMEWORK", 10, 8, None), ("b", "HOMEWORK", 20, 15, None), ("c", "HOMEWORK", 20, 18, None))
        self.assertEqual(round(category_percent(store.course("C"), "ana", "HOMEWORK"), 2), Decimal("86.67"))

    def test_B2_started_late_days(self):
        _, store = course(("a", "HOMEWORK", 10, 10, "2026-03-03T00:59"))
        self.assertEqual(category_percent(store.course("C"), "ana", "HOMEWORK"), Decimal("80"))

    def test_B3_final_replaces_midterm(self):
        api, _ = course(*FULL, ("m", "MIDTERM", 100, 60, None), ("f", "FINAL", 100, 90, None))
        self.assertEqual(api.report("C", "ana")[1]["percent"], "95.00")

    def test_B4_rounded_before_letter(self):
        api, _ = course(*FULL, ("m", "MIDTERM", 100, "79.9", None), ("f", "FINAL", 100, "79.9", None))
        self.assertEqual(api.report("C", "ana")[1]["letter"], "A")

    def test_B5_excused_removed(self):
        api, store = course(("q1", "QUIZ", 10, 10, None), ("q2", "QUIZ", 10, None, None))
        api.excuse("C", "ana", "q2")
        self.assertEqual(category_percent(store.course("C"), "ana", "QUIZ"), Decimal("100"))
