FIXES = [
    ("bonds.py", "        return d.weekday() < 5", "        return d.weekday() < 5 and d not in self.holidays"),
    ("bonds.py", "    d1, d2 = start.day, end.day\n", "    d1, d2 = start.day, end.day\n    if d1 == 31:\n        d1 = 30\n"),
    ("bonds.py", "        basis = 360 if self.convention == \"30/360\" else 365", "        basis = 360"),
    ("bonds.py", "if d < settle)", "if d <= settle)"),
    ("bonds.py", "        dates, current = [], self.maturity\n        while current > start:\n            dates.append(current)\n            current = add_months(current, -step)\n        dates.append(current)",
     "        dates, k = [], 0\n        while True:\n            current = add_months(self.maturity, -step * k)\n            dates.append(current)\n            if current <= start:\n                break\n            k += 1"),
]
