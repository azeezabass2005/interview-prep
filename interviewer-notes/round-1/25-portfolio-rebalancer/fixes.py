FIXES = [
    ("rebalance/engine.py", "    investable = portfolio.total_value()\n",
     "    investable = portfolio.total_value() * (1 - CASH_BUFFER)\n"),
    ("rebalance/engine.py", "    return math.floor((target_value - current_value) / price)",
     "    return int((target_value - current_value) / price)"),
    ("rebalance/engine.py",
     """    for symbol, target in target_values(portfolio, targets).items():
        holding = portfolio.holdings[symbol]
        diff = target - holding.value
        if abs(diff) <= BAND * target:
            continue
""",
     """    candidates = []
    for symbol, target in target_values(portfolio, targets).items():
        holding = portfolio.holdings[symbol]
        diff = target - holding.value
        if abs(diff) <= BAND * total:
            continue
        candidates.append((symbol, target, holding, diff))
    sells = [c for c in candidates if c[3] < 0]
    buys = sorted((c for c in candidates if c[3] > 0), key=lambda c: (-c[3], c[0]))

    for symbol, target, holding, diff in sells + buys:
"""),
]
