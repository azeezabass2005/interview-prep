FIXES = [
    ("hotel/services/pricing.py", "if n.weekday() in (5, 6) else", "if n.weekday() in (4, 5) else"),
    ("hotel/services/pricing.py",
     """    after_promo = subtotal - promo_amount
    los = cents(after_promo * los_rate(len(rates)))
    plan_discount = cents((after_promo - los) * NON_REFUNDABLE_DISCOUNT) if plan == NON_REFUNDABLE else Decimal("0")
    room_total = max(after_promo - los - plan_discount, Decimal("0"))""",
     """    los = cents(subtotal * los_rate(len(rates)))
    plan_discount = cents((subtotal - los) * NON_REFUNDABLE_DISCOUNT) if plan == NON_REFUNDABLE else Decimal("0")
    room_total = max(subtotal - los - plan_discount - promo_amount, Decimal("0"))"""),
    ("hotel/services/pricing.py", "tax = cents((room_total + city_fee) * TAX_RATE)", "tax = cents(room_total * TAX_RATE)"),
    ("hotel/services/availability.py", "        return self.rooms_left(room_type, nights(check_in, check_out)[0]) > 0",
     "        return all(self.rooms_left(room_type, n) > 0 for n in nights(check_in, check_out))"),
    ("hotel/services/reservations.py", "check_in = datetime(r.check_in.year, r.check_in.month, r.check_in.day)",
     "check_in = datetime(r.check_in.year, r.check_in.month, r.check_in.day, CHECK_IN_HOUR)"),
]
