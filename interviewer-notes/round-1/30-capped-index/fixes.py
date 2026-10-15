FIXES = [
    ("index/weights.py", "    return (s.free_float > MIN_FREE_FLOAT", "    return (s.free_float >= MIN_FREE_FLOAT"),
    ("index/weights.py", "def float_adjusted_cap(s: Security) -> Decimal:\n    return s.shares * s.price",
     "def float_adjusted_cap(s: Security) -> Decimal:\n    return s.shares * s.free_float * s.price"),
    ("index/weights.py",
     """    w = dict(weights)
    over: List[str] = [t for t, v in w.items() if v > cap]
    excess = sum((w[t] - cap for t in over), Decimal(0))
    for t in over:
        w[t] = cap
    under = [t for t in w if t not in over]
    for t in under:
        w[t] += excess / len(under)
    return w""",
     """    w = dict(weights)
    capped: List[str] = []
    while True:
        over = [t for t, v in w.items() if v > cap]
        if not over:
            return w
        excess = sum((w[t] - cap for t in over), Decimal(0))
        for t in over:
            w[t] = cap
        capped.extend(over)
        under = [t for t in w if t not in capped]
        under_total = sum((w[t] for t in under), Decimal(0))
        for t in under:
            w[t] += excess * w[t] / under_total"""),
    ("index/weights.py",
     "    return {t: (v * HUNDRED).quantize(PLACES, rounding=ROUND_HALF_UP) for t, v in capped.items()}",
     "    published = {t: (v * HUNDRED).quantize(PLACES, rounding=ROUND_HALF_UP) for t, v in capped.items()}\n"
     "    if published:\n"
     "        residue = HUNDRED - sum(published.values())\n"
     "        uncapped = [t for t, v in capped.items() if v < cap] or list(published)\n"
     "        target = sorted(uncapped, key=lambda t: (-published[t], t))[0]\n"
     "        published[target] += residue\n"
     "    return published"),
]
