import unittest
from datetime import datetime
from decimal import Decimal

from gradebook import Gradebook

DUE = datetime(2026, 3, 1, 23, 59)


class TestGradebook(unittest.TestCase):
    def test_on_time_quiz(self):
        g = Gradebook()
        g.add_assignment("q1", "QUIZ", 10, DUE)
        g.submit("q1", "ana", 7, DUE)
        self.assertEqual(g.category_percent("ana", "QUIZ", DUE), Decimal("70.00"))


if __name__ == "__main__":
    unittest.main()
