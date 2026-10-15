FIXES = [
    ("ship/parcel.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_CEILING, Decimal"),
    ("ship/parcel.py", "    return pkg.length * pkg.width * pkg.height / DIM_DIVISOR",
     "    l, w, h = (d.to_integral_value(rounding=ROUND_CEILING) for d in (pkg.length, pkg.width, pkg.height))\n"
     "    return l * w * h / DIM_DIVISOR"),
    ("ship/parcel.py", "heavier.quantize(Decimal(\"1\"), rounding=ROUND_HALF_UP)", "heavier.quantize(Decimal(\"1\"), rounding=ROUND_CEILING)"),
    ("ship/quote.py", "pkg.longest_side >= OVERSIZE_LENGTH", "pkg.longest_side > OVERSIZE_LENGTH"),
    ("ship/quote.py", "fuel = cents((base + oversize + residential_fee) * FUEL_RATE)", "fuel = cents((base + oversize) * FUEL_RATE)"),
    ("ship/quote.py", "    if subtotal >= FREE_SHIPPING_THRESHOLD:",
     "    if subtotal - discount >= FREE_SHIPPING_THRESHOLD and zone <= FREE_SHIPPING_MAX_ZONE:"),
    ("ship/quote.py", "from .rates import (FREE_SHIPPING_THRESHOLD,", "from .rates import (FREE_SHIPPING_MAX_ZONE, FREE_SHIPPING_THRESHOLD,"),
]
