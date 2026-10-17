FIXES = [
    ("tips/services/pools.py", "    gross = declaration.card + declaration.cash\n    return (gross * (1 - CARD_FEE_RATE))",
     "    return (declaration.card * (1 - CARD_FEE_RATE) + declaration.cash)"),
    ("tips/services/pools.py", "from ..config import CARD_FEE_RATE, MIN_HOURS, ROLE_POINTS",
     "from ..config import CARD_FEE_RATE, INELIGIBLE_ROLES, MIN_HOURS, ROLE_POINTS"),
    ("tips/services/pools.py", "        h = hours_in_service(shift, day, service)\n",
     "        if shift.role in INELIGIBLE_ROLES:\n            continue\n        h = hours_in_service(shift, day, service)\n"),
    ("tips/services/pools.py", "        weight[shift.employee] = ROLE_POINTS[shift.role] * h",
     "        weight[shift.employee] = weight.get(shift.employee, Decimal(0)) + ROLE_POINTS[shift.role] * h"),
    ("tips/services/pools.py", "if hours[name] > MIN_HOURS}", "if hours[name] >= MIN_HOURS}"),
    ("tips/services/periods.py",
     "    if not (start <= shift.start < end):\n        return Decimal(0)\n    minutes = int((shift.end - shift.start).total_seconds() // 60)",
     "    overlap = (min(shift.end, end) - max(shift.start, start)).total_seconds()\n"
     "    if overlap <= 0:\n        return Decimal(0)\n    minutes = int(overlap // 60)"),
]
