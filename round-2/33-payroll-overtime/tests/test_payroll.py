import unittest

from payroll.app import build_app


class TestPayroll(unittest.TestCase):
    def test_single_regular_day(self):
        api = build_app()
        api.hire("w1", "Wes", "20", "2026-01-01")
        api.clock("w1", {"start": "2026-03-02T09:00", "end": "2026-03-02T17:00", "break_taken": True})
        status, stub = api.stub("w1", "2026-03-02")
        self.assertEqual(status, 200)
        self.assertEqual(stub["gross"], "160.00")


if __name__ == "__main__":
    unittest.main()
