FIXES = [
    ("leaderboard.py", "(-self.return_pct(p.name), -p.trades, p.joined_at)", "(-self.return_pct(p.name), p.trades, p.joined_at)"),
    ("leaderboard.py", "        return p.cash + sum((q * p.trade_prices[s] for s, q in p.positions.items()), Decimal(\"0\"))",
     "        return p.cash + sum((q * self.prices.get(s, p.trade_prices[s]) for s, q in p.positions.items()), Decimal(\"0\"))"),
    ("leaderboard.py", "if p.trades > MIN_TRADES]", "if p.trades >= MIN_TRADES and not p.disqualified]"),
    ("leaderboard.py", "        return rows[n * size:(n + 1) * size]", "        return rows[(n - 1) * size:n * size]"),
]
