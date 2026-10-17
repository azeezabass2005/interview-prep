FIXES = [
    ("payroll.py", "        if hours >= BREAK_AFTER:", "        if hours > BREAK_AFTER:"),
    ("payroll.py", "            overtime = max(hours - DAILY_REGULAR, Decimal(0))\n            double = Decimal(0)",
     "            overtime = min(max(hours - DAILY_REGULAR, Decimal(0)), DAILY_DOUBLE - DAILY_REGULAR)\n            double = max(hours - DAILY_DOUBLE, Decimal(0))"),
    ("payroll.py", "            weekly_hours += hours\n", "            weekly_hours += regular\n"),
    ("payroll.py", "        return history[-1][1]",
     "        current = [(when, rate) for when, rate in history if when <= day]\n        if not current:\n            raise PayrollError(f\"no rate for {employee} on {day}\")\n        return max(current, key=lambda r: r[0])[1]"),
    ("payroll.py", "            day = s.end.date()", "            day = s.start.date()"),
]
