FIXES = [
    ("shipping/services/weights.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_CEILING, Decimal"),
    ("shipping/services/weights.py", "    return pkg.length * pkg.width * pkg.height / CARRIERS[carrier][\"divisor\"]",
     "    l, w, h = (d.to_integral_value(rounding=ROUND_CEILING) for d in (pkg.length, pkg.width, pkg.height))\n"
     "    return l * w * h / CARRIERS[carrier][\"divisor\"]"),
    ("shipping/services/weights.py", "rounding=ROUND_HALF_UP)))", "rounding=ROUND_CEILING)))"),
    ("shipping/services/rating.py", "fuel = cents((base + oversize + residential_fee) * CARRIERS", "fuel = cents((base + oversize) * CARRIERS"),
    ("shipping/services/checkout.py", "    if subtotal >= FREE_THRESHOLD and", "    if subtotal - discount >= FREE_THRESHOLD and"),
    ("shipping/services/estimate.py", "ordered_at.hour > CUTOFF_HOUR", "ordered_at.hour >= CUTOFF_HOUR"),
]
