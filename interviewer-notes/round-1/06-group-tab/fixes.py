FIXES = [
    ("tab/allocation.py",
     "    return {name: amount * weight // total_weight for name, weight in weights.items()}",
     "    shares = {name: amount * weight // total_weight for name, weight in weights.items()}\n"
     "    leftover = amount - sum(shares.values())\n"
     "    for name in sorted(shares)[:leftover]:\n"
     "        shares[name] += 1\n"
     "    return shares"),
    ("tab/calculator.py",
     "    tax = _round_cents(subtotal * TAX_RATE)\n    discounted = subtotal - bill.coupon_cents\n",
     "    discounted = subtotal - bill.coupon_cents\n    tax = _round_cents(discounted * TAX_RATE)\n"),
    ("tab/calculator.py", "if party_size > AUTO_GRATUITY_PARTY_SIZE", "if party_size >= AUTO_GRATUITY_PARTY_SIZE"),
    ("tab/calculator.py", "tip = _round_cents(Decimal(discounted + tax) * tip_percent / 100)",
     "tip = _round_cents(Decimal(discounted) * tip_percent / 100)"),
    ("tab/calculator.py", "        for person, amount in sorted(breakdown.shares.items())\n",
     "        for person, amount in sorted(breakdown.shares.items())\n        if person != bill.payer\n"),
]
