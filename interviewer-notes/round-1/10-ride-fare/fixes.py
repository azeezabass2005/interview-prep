FIXES = [
    ("fare/calculator.py", "    return duration_seconds // 60", "    return -(-duration_seconds // 60)"),
    ("fare/calculator.py",
     """        surge = self._surge_feed.multiplier(trip.zone)
        fare = (metered_subtotal(trip) + BOOKING_FEE) * surge
        fare = fare + trip.tolls
        fare = max(fare, MINIMUM_FARE)
""",
     """        surge = min(trip.quoted_surge, SURGE_CAP)
        fare = metered_subtotal(trip) * surge + BOOKING_FEE
        fare = max(fare, MINIMUM_FARE)
        fare = fare + trip.tolls
"""),
    ("fare/calculator.py", "MINIMUM_FARE, PER_MILE, PER_MINUTE", "MINIMUM_FARE, PER_MILE, PER_MINUTE, SURGE_CAP"),
    ("fare/cancellation.py", "from .rates import CANCEL_FEE, CANCEL_FREE_WINDOW_SECONDS",
     "from .rates import CANCEL_FEE, CANCEL_FREE_WINDOW_SECONDS, DRIVER_LATE_GRACE_SECONDS"),
    ("fare/cancellation.py", "        return Decimal(\"0.00\")\n    return CANCEL_FEE",
     "        return Decimal(\"0.00\")\n"
     "    if arrived_at is None and waited > eta_seconds + DRIVER_LATE_GRACE_SECONDS:\n"
     "        return Decimal(\"0.00\")\n"
     "    return CANCEL_FEE"),
]
