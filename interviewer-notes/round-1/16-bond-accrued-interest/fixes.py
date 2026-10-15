FIXES = [
    ("bond/daycount.py", "    if d2 == 31:\n", "    if d2 == 31 and d1 == 30:\n"),
    ("bond/calendar.py",
     "def add_months(d: date, months: int) -> date:\n",
     "def add_months(d: date, months: int, end_of_month: bool = False) -> date:\n"),
    ("bond/calendar.py",
     "    return date(year, month, min(d.day, last_day_of_month(year, month)))",
     "    if end_of_month:\n        return date(year, month, last_day_of_month(year, month))\n"
     "    return date(year, month, min(d.day, last_day_of_month(year, month)))"),
    ("bond/calendar.py", "    return d + timedelta(days=days)",
     "    while days > 0:\n        d += timedelta(days=1)\n        if d.weekday() < 5:\n            days -= 1\n    return d"),
    ("bond/schedule.py", "from .calendar import add_months", "from .calendar import add_months, is_month_end"),
    ("bond/schedule.py", "dates.append(add_months(bond.maturity, -step * n))",
     "dates.append(add_months(bond.maturity, -step * n, end_of_month=is_month_end(bond.maturity)))"),
    ("bond/schedule.py", "previous = max(d for d in dates if d < settle)", "previous = max(d for d in dates if d <= settle)"),
    ("bond/pricing.py", "    return Decimal(int(raw * 100)) / 100",
     "    return raw.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)"),
    ("bond/pricing.py", "from decimal import Decimal", "from decimal import ROUND_HALF_UP, Decimal"),
]
