import unittest

from payroll.app import build_app


def gross(*shifts, rate_changes=()):
    api = build_app()
    api.hire("w", "Wes", "20", "2026-01-01")
    for rate, effective in rate_changes:
        api.change_rate("w", rate, effective)
    for start, end, break_taken in shifts:
        api.clock("w", {"start": start, "end": end, "break_taken": break_taken})
    return api.stub("w", "2026-03-02")[1]["gross"]


class HiddenPayroll(unittest.TestCase):
    def test_B1_double_time_not_also_overtime(self):
        self.assertEqual(gross(("2026-03-02T06:00", "2026-03-02T20:00", True)), "360.00")

    def test_B2_weekly_overtime_on_regular_hours(self):
        days = [(f"2026-03-0{d}T08:00", f"2026-03-0{d}T18:00", True) for d in range(2, 7)]
        self.assertEqual(gross(*days), "1100.00")

    def test_B3_overnight_shift_on_start_day(self):
        self.assertEqual(gross(("2026-03-02T20:00", "2026-03-03T06:00", True),
                               ("2026-03-03T08:00", "2026-03-03T16:00", True)), "380.00")

    def test_B4_exactly_six_hours_no_deduction(self):
        self.assertEqual(gross(("2026-03-02T09:00", "2026-03-02T15:00", False)), "120.00")

    def test_B5_rate_in_effect_on_shift_day(self):
        self.assertEqual(gross(("2026-03-02T09:00", "2026-03-02T17:00", True),
                               ("2026-03-04T09:00", "2026-03-04T17:00", True),
                               rate_changes=[("25", "2026-03-04")]), "360.00")
