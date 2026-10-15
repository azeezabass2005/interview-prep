FIXES = [
    ("hotel/pricing.py", "if night.weekday() in (5, 6):", "if night.weekday() in (4, 5):"),
    ("hotel/pricing.py", "if nights > LOS_LONG[0]:", "if nights >= LOS_LONG[0]:"),
    ("hotel/pricing.py",
     "    after_promo = subtotal - promo\n    los = cents(after_promo * los_discount_rate(nights))\n    room_total = after_promo - los\n",
     "    los = cents(subtotal * los_discount_rate(nights))\n    room_total = subtotal - los - promo\n"),
    ("hotel/pricing.py", "tax = cents((room_total + city_fee) * TAX_RATE)", "tax = cents(room_total * TAX_RATE)"),
    ("hotel/cancellation.py", "check_in = datetime(q.check_in.year, q.check_in.month, q.check_in.day)",
     "check_in = datetime(q.check_in.year, q.check_in.month, q.check_in.day, CHECK_IN_HOUR)"),
    ("hotel/cancellation.py", "from .rates import FULL_REFUND_HOURS,", "from .rates import CHECK_IN_HOUR, FULL_REFUND_HOURS,"),
]
