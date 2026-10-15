import unittest
from decimal import Decimal as D

from grades.compute import category_percent, course_percent, letter_for
from tests.helpers import full_marks_except, item


class TestCategories(unittest.TestCase):
    def test_homework_drop_equal_max(self):
        items = [item("homework", "a", 5, 10), item("homework", "b", 9, 10), item("homework", "c", 7, 10)]
        self.assertEqual(category_percent(items, "homework"), D("80"))

    def test_missing_counts_zero(self):
        items = [item("quiz", "q1", 10, 10), item("quiz", "q2", None, 10)]
        self.assertEqual(category_percent(items, "quiz"), D("50"))

    def test_quiz_average_of_percentages(self):
        items = [item("quiz", "q1", 5, 10), item("quiz", "q2", 20, 20)]
        self.assertEqual(category_percent(items, "quiz"), D("75"))


class TestCourse(unittest.TestCase):
    def test_perfect_course(self):
        self.assertEqual(course_percent(full_marks_except()), D("100"))

    def test_letters(self):
        self.assertEqual(letter_for(D("90")), "A")
        self.assertEqual(letter_for(D("79")), "C")
        self.assertEqual(letter_for(D("12")), "F")


if __name__ == "__main__":
    unittest.main()
