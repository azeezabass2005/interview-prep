FIXES = [
    ("payroll/services/overtime.py", "    overtime = max(hours - DAILY_REGULAR, ZERO)", "    overtime = max(min(hours, DAILY_DOUBLE_AFTER) - DAILY_REGULAR, ZERO)"),
    ("payroll/services/overtime.py", "    total_hours = sum((d.hours for d in days), ZERO)\n    excess = max(total_hours - WEEKLY_REGULAR, ZERO)",
     "    excess = max(sum((r[1] for r in rows), ZERO) - WEEKLY_REGULAR, ZERO)"),
    ("payroll/services/timesheets.py", "hours[shift.end.date()] += shift_hours(shift)", "hours[shift.start.date()] += shift_hours(shift)"),
    ("payroll/services/timesheets.py", "hours >= MEAL_BREAK_AFTER:", "hours > MEAL_BREAK_AFTER:"),
    ("payroll/services/rates.py", "    latest = max(worker.rates, key=lambda r: r.effective)", "    latest = max(applicable, key=lambda r: r.effective)"),
]
