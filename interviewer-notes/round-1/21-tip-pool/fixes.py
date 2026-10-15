FIXES = [
    ("tips/pool.py", "from .policy import CARD_FEE_RATE, MIN_HOURS, ROLE_POINTS",
     "from .policy import CARD_FEE_RATE, INELIGIBLE_ROLES, MIN_HOURS, ROLE_POINTS"),
    ("tips/pool.py",
     "    gross = tips.card + tips.cash\n    return (gross * (1 - CARD_FEE_RATE)).quantize(CENT, rounding=ROUND_HALF_UP)",
     "    return (tips.card * (1 - CARD_FEE_RATE) + tips.cash).quantize(CENT, rounding=ROUND_HALF_UP)"),
    ("tips/pool.py",
     "        hours[shift.employee] += shift.hours\n        weight[shift.employee] = ROLE_POINTS[shift.role] * shift.hours\n"
     "    return {name: w for name, w in weight.items() if hours[name] > MIN_HOURS}",
     "        if shift.role in INELIGIBLE_ROLES:\n            continue\n"
     "        hours[shift.employee] += shift.hours\n"
     "        weight[shift.employee] = weight.get(shift.employee, 0) + ROLE_POINTS[shift.role] * shift.hours\n"
     "    return {name: w for name, w in weight.items() if hours[name] >= MIN_HOURS}"),
    ("tips/pool.py", "    for name in sorted(shares)[:leftover_cents]:",
     "    by_remainder = sorted(shares, key=lambda n: (-(exact[n] - shares[n]), n))\n"
     "    for name in by_remainder[:leftover_cents]:"),
]
