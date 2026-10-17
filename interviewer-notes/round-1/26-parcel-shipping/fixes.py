FIXES = [
    ("shipping.py", "    return Decimal(round(weight * 2)) / 2", "    return Decimal(math.ceil(weight * 2)) / 2"),
    ("shipping.py", "    charge = c[\"base\"] + c[\"per_kg\"][zone] * billable_weight(parcel)\n",
     "    charge = c[\"base\"] + c[\"per_kg\"][zone] * billable_weight(parcel)\n    charge += charge * FUEL\n"),
    ("shipping.py", "        charge += RESIDENTIAL\n    charge += charge * FUEL\n", "        charge += RESIDENTIAL\n"),
    ("shipping.py", "    if placed_at.time() >= CUTOFF or d.weekday() >= 5:", "    if placed_at.time() > CUTOFF or d.weekday() >= 5:"),
    ("shipping.py", "    return ship_date(placed_at) + timedelta(days=CARRIERS[carrier][\"days\"][zone])",
     "    d = ship_date(placed_at)\n    for _ in range(CARRIERS[carrier][\"days\"][zone]):\n        d = _next_business_day(d)\n    return d"),
    ("shipping.py", "    if Decimal(str(order_total)) >= FREE_THRESHOLD:\n        return {\"carrier\": \"BUDGET\", \"price\": Decimal(\"0.00\"), \"delivery\": delivery_date(\"BUDGET\", zone, placed_at)}",
     "    budget_when = delivery_date(\"BUDGET\", zone, placed_at)\n    if Decimal(str(order_total)) >= FREE_THRESHOLD and (deadline is None or budget_when <= deadline):\n        return {\"carrier\": \"BUDGET\", \"price\": Decimal(\"0.00\"), \"delivery\": budget_when}"),
]
