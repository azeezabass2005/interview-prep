FIXES = [
    ("gradebook/services/grading.py", "rows.remove(min(rows, key=lambda r: r[0]))", "rows.remove(min(rows, key=lambda r: r[0] / r[1]))"),
    ("gradebook/services/grading.py", "        if a.category != category:\n            continue\n",
     "        if a.category != category or (student, a.assignment_id) in course.excused:\n            continue\n"),
    ("gradebook/services/grading.py", "pct[\"MIDTERM\"] > pct[\"FINAL\"]:\n        pct[\"FINAL\"] = pct[\"MIDTERM\"]",
     "pct[\"FINAL\"] > pct[\"MIDTERM\"]:\n        pct[\"MIDTERM\"] = pct[\"FINAL\"]"),
    ("gradebook/services/grading.py", "def letter(percent: Decimal) -> str:\n",
     "def letter(percent: Decimal) -> str:\n    from decimal import ROUND_HALF_UP\n    percent = percent.quantize(Decimal(\"0.1\"), rounding=ROUND_HALF_UP)\n"),
    ("gradebook/services/late.py", "    return int((submitted_at - due).total_seconds() // 86400)",
     "    return int(-(-(submitted_at - due).total_seconds() // 86400))"),
]
