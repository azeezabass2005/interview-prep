FIXES = [
    ("gradebook.py", "        days_late = (at - a.due) // timedelta(days=1)", "        days_late = -(-(at - a.due) // timedelta(days=1))"),
    ("gradebook.py", "                items.append((Decimal(\"0\"), a.possible))\n                continue", "                continue"),
    ("gradebook.py", "key=lambda i: i[0]))", "key=lambda i: i[0] / i[1]))"),
    ("gradebook.py", "        total, weights = Decimal(\"0\"), sum(WEIGHTS.values())", "        total, weights = Decimal(\"0\"), Decimal(\"0\")"),
    ("gradebook.py", "                total += weight * pct", "                total += weight * pct\n                weights += weight"),
    ("gradebook.py", "if percent > cut)", "if percent >= cut)"),
]
