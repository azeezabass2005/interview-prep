FIXES = [
    ("tips.py", "        return ((t[\"cash\"] + t[\"card\"]) * (1 - CARD_FEE)).quantize(CENT, rounding=ROUND_HALF_UP)",
     "        return t[\"cash\"] + t[\"card\"] - (t[\"card\"] * CARD_FEE).quantize(CENT, rounding=ROUND_HALF_UP)"),
    ("tips.py", "            if w.day == day and w.hours > MIN_HOURS:\n                points[w.employee] += w.hours * WEIGHTS.get(w.role, Decimal(\"1.0\"))",
     "            if w.day == day and w.service == service and w.hours >= MIN_HOURS and w.role in WEIGHTS:\n                points[w.employee] += w.hours * WEIGHTS[w.role]"),
    ("tips.py", "        for employee in sorted(points)[:leftover]:", "        for employee in sorted(points, key=lambda e: (-points[e], e))[:leftover]:"),
]
