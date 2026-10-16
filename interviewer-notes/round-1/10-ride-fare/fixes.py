FIXES = [
    ("rides/services/fare.py", "    return int(seconds // 60)", "    return int(-(-seconds // 60))"),
    ("rides/services/fare.py", "    return cents(wait_minutes * WAIT_PER_MINUTE)", "    return cents((wait_minutes - FREE_WAIT_MINUTES) * WAIT_PER_MINUTE)"),
    ("rides/services/fare.py", "discount = min(cents((subtotal + tolls) * PROMOS[promo]), PROMO_MAX)",
     "discount = min(cents(subtotal * PROMOS[promo]), PROMO_MAX)"),
    ("rides/services/trips.py", "self._surge.current(trip.zone), trip.tolls, trip.promo)", "trip.locked_surge, trip.tolls, trip.promo)"),
    ("rides/services/trips.py", "cents((trip.fare - trip.tolls) * DRIVER_SHARE)", "cents((trip.fare - BOOKING_FEE - trip.tolls) * DRIVER_SHARE)"),
]
