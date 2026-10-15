import unittest
from decimal import Decimal as D

from grades.compute import adjusted_points, category_percent, course_percent, letter_for
from tests.helpers import full_marks_except, item


class HiddenGrades(unittest.TestCase):
    def test_B1_drop_lowest_percentage(self):
        items = [item("homework", "a", 8, 10), item("homework", "b", 15, 20), item("homework", "c", 18, 20)]
        self.assertEqual(round(category_percent(items, "homework"), 2), D("86.67"))

    def test_B2_partial_day_counts_as_full_day(self):
        self.assertEqual(adjusted_points(item("homework", "a", 10, 10, days_late=1.5)), D("8"))

    def test_B3_final_replaces_midterm(self):
        items = full_marks_except(midterm=[item("midterm", "mid", 60, 100)],
                                  final=[item("final", "fin", 90, 100)])
        self.assertEqual(course_percent(items), D("95"))

    def test_B4_round_before_letter(self):
        self.assertEqual(letter_for(D("89.95")), "A")

    def test_B5_excused_items_removed(self):
        items = [item("quiz", "q1", 10, 10), item("quiz", "q2", None, 10, excused=True)]
        self.assertEqual(category_percent(items, "quiz"), D("100"))
