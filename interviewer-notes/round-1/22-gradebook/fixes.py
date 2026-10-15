FIXES = [
    ("grades/compute.py", "from decimal import Decimal", "from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal"),
    ("grades/compute.py", "        days = int(item.days_late)",
     "        days = int(item.days_late.to_integral_value(rounding=ROUND_CEILING))"),
    ("grades/compute.py", "for i in items if i.category == category]", "for i in items if i.category == category and not i.excused]"),
    ("grades/compute.py", "rows.remove(min(rows, key=lambda r: r[0]))", "rows.remove(min(rows, key=lambda r: r[0] / r[1]))"),
    ("grades/compute.py", "    if pct[\"midterm\"] > pct[\"final\"]:\n        pct[\"final\"] = pct[\"midterm\"]",
     "    if pct[\"final\"] > pct[\"midterm\"]:\n        pct[\"midterm\"] = pct[\"final\"]"),
    ("grades/compute.py", "def letter_for(percent: Decimal) -> str:\n",
     "def letter_for(percent: Decimal) -> str:\n    percent = percent.quantize(Decimal(\"0.1\"), rounding=ROUND_HALF_UP)\n"),
]
