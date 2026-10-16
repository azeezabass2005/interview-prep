FIXES = [
    ("indexing/services/eligibility.py", "    return (s.free_float > MIN_FREE_FLOAT", "    return (s.free_float >= MIN_FREE_FLOAT"),
    ("indexing/services/eligibility.py", "(on - s.listed_on).days > MIN_LISTED_DAYS)", "(on - s.listed_on).days >= MIN_LISTED_DAYS)"),
    ("indexing/services/weighting.py", "def float_cap(s: Security) -> Decimal:\n    return s.shares * s.price",
     "def float_cap(s: Security) -> Decimal:\n    return s.shares * s.free_float * s.price"),
    ("indexing/services/weighting.py",
     """    w = dict(weights)
    over = [t for t, v in w.items() if v > cap]
    excess = sum((w[t] - cap for t in over), Decimal(0))
    for t in over:
        w[t] = cap
    under = [t for t in w if t not in over]
    for t in under:
        w[t] += excess / len(under)
    return w""",
     """    w = dict(weights)
    capped = set()
    while True:
        over = [t for t, v in w.items() if v > cap]
        if not over:
            return w
        excess = sum((w[t] - cap for t in over), Decimal(0))
        for t in over:
            w[t] = cap
        capped.update(over)
        under = [t for t in w if t not in capped]
        base = sum((w[t] for t in under), Decimal(0))
        for t in under:
            w[t] += excess * w[t] / base"""),
]
