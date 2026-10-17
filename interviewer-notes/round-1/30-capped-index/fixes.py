FIXES = [
    ("capped.py", """    w = dict(weights)
    over = [t for t, v in w.items() if v > cap]
    excess = sum((w[t] - cap for t in over), Decimal(0))
    for t in over:
        w[t] = cap
    rest = {t: v for t, v in w.items() if t not in over}
    base = sum(rest.values())
    for t, v in rest.items():
        w[t] = v + excess * v / base
    return w""", """    w, capped = dict(weights), set()
    while True:
        over = [t for t, v in w.items() if v > cap]
        if not over:
            return w
        excess = sum((w[t] - cap for t in over), Decimal(0))
        for t in over:
            w[t] = cap
        capped.update(over)
        rest = {t: v for t, v in w.items() if t not in capped}
        base = sum(rest.values())
        for t, v in rest.items():
            w[t] = v + excess * v / base"""),
    ("capped.py", "from decimal import ROUND_DOWN, Decimal", "from decimal import ROUND_HALF_UP, Decimal"),
    ("capped.py", "rounding=ROUND_DOWN)", "rounding=ROUND_HALF_UP)"),
    ("capped.py", "    caps = {s.ticker: s.shares * s.price for s in stocks}", "    caps = {s.ticker: s.shares * s.free_float * s.price for s in stocks}"),
    ("capped.py", "        target = sorted(published, key=lambda t: (-published[t], t))[0]",
     "        uncapped = [t for t in published if weights[t] < cap] or list(published)\n        target = sorted(uncapped, key=lambda t: (-published[t], t))[0]"),
    ("capped.py", "    return sum((abs(new[t] - old.get(t, Decimal(0))) for t in new), Decimal(0)) / 2",
     "    names = set(old) | set(new)\n    return sum((abs(new.get(t, Decimal(0)) - old.get(t, Decimal(0))) for t in names), Decimal(0)) / 2"),
]
