FIXES = [
    ("fares.py", "        fare = money(max(raw, MIN_FARE) * self.current_surge)", "        fare = money(max(raw * trip.surge, MIN_FARE))"),
    ("fares.py", "        return money(minutes * WAIT_PER_MIN) if minutes > FREE_WAIT_MIN",
     "        return money((minutes - FREE_WAIT_MIN) * WAIT_PER_MIN) if minutes > FREE_WAIT_MIN"),
    ("fares.py", "        discount = money((fare + waiting) * trip.promo_pct)", "        discount = min(money((fare + waiting) * trip.promo_pct), MAX_DISCOUNT)"),
    ("fares.py", "        payout = money((fare + waiting - discount) * DRIVER_SHARE)", "        payout = money((fare + waiting) * DRIVER_SHARE)"),
]
