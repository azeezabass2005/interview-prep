import unittest

from gradebook.app import build_app


class TestGradebook(unittest.TestCase):
    def test_perfect_student(self):
        api, _ = build_app()
        api.create("CS101", ["ana"])
        for aid, cat in (("hw1", "HOMEWORK"), ("q1", "QUIZ"), ("mid", "MIDTERM"), ("fin", "FINAL")):
            api.assignment("CS101", {"id": aid, "category": cat, "max_points": 10, "due": "2026-03-01T23:59"})
            api.submit("CS101", "ana", aid, "2026-03-01T12:00")
            api.grade("CS101", "ana", aid, 10)
        self.assertEqual(api.report("CS101", "ana")[1]["letter"], "A")


if __name__ == "__main__":
    unittest.main()
