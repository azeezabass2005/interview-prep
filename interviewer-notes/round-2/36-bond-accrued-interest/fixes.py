FIXES = [
    ("bonds/daycount.py", "    if d2 == 31:\n", "    if d2 == 31 and d1 == 30:\n"),
    ("bonds/daycount.py", "Decimal((end - start).days) / 365", "Decimal((end - start).days) / 360"),
    ("bonds/calendar.py", "        return d.weekday() < 5\n", "        return d.weekday() < 5 and d not in self.holidays\n"),
    ("bonds/schedule.py", "from .calendar import shift_months", "from datetime import date as _date\n\nfrom .calendar import is_month_end, last_day, shift_months"),
    ("bonds/schedule.py", "        dates.append(shift_months(bond.maturity, -step * n))",
     "        d = shift_months(bond.maturity, -step * n)\n"
     "        if is_month_end(bond.maturity):\n            d = _date(d.year, d.month, last_day(d.year, d.month))\n"
     "        dates.append(d)"),
    ("bonds/schedule.py", "previous = max(d for d in dates if d < settle)", "previous = max(d for d in dates if d <= settle)"),
]
