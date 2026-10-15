FIXES = [
    ("pnl/services/lots.py", "            if lot.opened >= split.effective:", "            if lot.opened < split.effective:"),
    ("pnl/services/lots.py",
     """        average_cost = sum((l.quantity * l.cost for l in lots), Decimal("0")) / open_qty
        realized += (fill.price - average_cost) * fill.quantity
        remaining = fill.quantity
        while remaining > 0:
            lot = lots[0]
            take = min(lot.quantity, remaining)
            lot.quantity -= take""",
     """        remaining = fill.quantity
        while remaining > 0:
            lot = lots[0]
            take = min(lot.quantity, remaining)
            realized += (fill.price - lot.cost) * take
            lot.quantity -= take"""),
    ("pnl/repositories/market.py",
     "\"SELECT close FROM prices WHERE security = ? AND price_date <= ? ORDER BY price_date LIMIT 1\"",
     "\"SELECT close FROM prices WHERE security = ? AND price_date <= ? ORDER BY price_date DESC LIMIT 1\""),
    ("pnl/services/pnl.py",
     "            total += row[\"realized\"] + row[\"unrealized\"]",
     "            total += self._fx.to_usd(row[\"realized\"] + row[\"unrealized\"], row[\"currency\"], as_of)"),
]
