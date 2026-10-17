FIXES = [
    ("rebalance.py", "        if self.drift(account, model) < DRIFT_BAND:", "        if self.drift(account, model) <= DRIFT_BAND:"),
    ("rebalance.py", "        investable = self.total(account) - restricted_value\n",
     "        investable = (self.total(account) - restricted_value) * (1 - CASH_BUFFER)\n"),
    ("rebalance.py", "        weights = {t: w for t, w in model.items() if t not in account.restricted}\n",
     "        weights = {t: w for t, w in model.items() if t not in account.restricted}\n"
     "        scale = sum(weights.values())\n"
     "        weights = {t: w / scale for t, w in weights.items()}\n"),
    ("rebalance.py", "            shares = math.floor(diff / self.prices[ticker])", "            shares = int(diff / self.prices[ticker])"),
    ("rebalance.py", "        return trades", "        return sorted(trades, key=lambda t: (t[1] != \"SELL\", t[0]))"),
]
