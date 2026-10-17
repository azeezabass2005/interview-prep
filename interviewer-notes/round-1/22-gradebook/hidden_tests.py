import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from gradebook import Gradebook

DUE = datetime(2026, 3, 1, 23, 59)
LATER = datetime(2026, 4, 1)


class HiddenGradebook(unittest.TestCase):
    def test_B1_started_day_counts(self):
        g = Gradebook()
        g.add_assignment("h1", "HOMEWORK", 10, DUE)
        g.submit("h1", "ana", 10, DUE + timedelta(minutes=31))
        self.assertEqual(g.category_percent("ana", "HOMEWORK", LATER), Decimal("90.00"))

    def test_B2_excused_is_ignored(self):
        g = Gradebook()
        g.add_assignment("q1", "QUIZ", 10, DUE)
        g.add_assignment("q2", "QUIZ", 10, DUE)
        g.submit("q1", "ana", 10, DUE)
        g.excuse("q2", "ana")
        self.assertEqual(g.category_percent("ana", "QUIZ", LATER), Decimal("100.00"))

    def test_B3_drop_lowest_percentage(self):
        g = Gradebook()
        g.add_assignment("h1", "HOMEWORK", 10, DUE)
        g.add_assignment("h2", "HOMEWORK", 20, DUE)
        g.submit("h1", "ana", 8, DUE)
        g.submit("h2", "ana", 15, DUE)
        self.assertEqual(g.category_percent("ana", "HOMEWORK", LATER), Decimal("80.00"))

    def test_B4_weights_rescaled(self):
        g = Gradebook()
        g.add_assignment("e1", "EXAM", 100, DUE)
        g.submit("e1", "ana", 85, DUE)
        self.assertEqual(g.final("ana", LATER), (Decimal("85.00"), "B"))

    def test_B5_ninety_is_an_a(self):
        g = Gradebook()
        for aid, cat, possible, score in (("h1", "HOMEWORK", 10, 9), ("q1", "QUIZ", 10, 9), ("e1", "EXAM", 100, 90)):
            g.add_assignment(aid, cat, possible, DUE)
            g.submit(aid, "ana", score, DUE)
        self.assertEqual(g.final("ana", LATER), (Decimal("90.00"), "A"))
