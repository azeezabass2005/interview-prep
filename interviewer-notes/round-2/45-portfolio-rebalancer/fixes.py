FIXES = [
    ("robo/services/targets.py", "    return {s: w for s, w in model.weights.items() if s not in restricted}",
     "    kept = {s: w for s, w in model.weights.items() if s not in restricted}\n"
     "    total = sum(kept.values(), Decimal(0))\n"
     "    return {s: w / total for s, w in kept.items()} if total else {}"),
    ("robo/services/targets.py", "    investable = total_value(account, prices)\n", "    investable = total_value(account, prices) * (1 - CASH_BUFFER)\n"),
    ("robo/services/planner.py", "    return math.floor((target - current) / price)", "    return int((target - current) / price)"),
    ("robo/services/planner.py",
     """    for symbol, target in sorted(target_values(account, model, prices).items()):
        price = prices.get(symbol)
        current = account.holdings.get(symbol, 0) * price
        diff = target - current
        restricted = symbol in account.restricted
        if not restricted and abs(diff) <= BAND * target:
            continue
""",
     """    candidates = []
    for symbol, target in sorted(target_values(account, model, prices).items()):
        price = prices.get(symbol)
        current = account.holdings.get(symbol, 0) * price
        diff = target - current
        restricted = symbol in account.restricted
        if not restricted and abs(diff) <= BAND * total:
            continue
        candidates.append((symbol, target, price, current, diff))
    sells = [c for c in candidates if c[4] < 0]
    buys = sorted((c for c in candidates if c[4] > 0), key=lambda c: (-c[4], c[0]))
    for symbol, target, price, current, diff in sells + buys:
"""),
]
