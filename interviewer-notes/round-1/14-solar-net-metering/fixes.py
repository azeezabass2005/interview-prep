FIXES = [
    ("utility/billing.py", "from .tariff import FIXED_CHARGE, TAX_RATE, TIERS",
     "from .tariff import FIXED_CHARGE, TAX_RATE, TIERS, TRUE_UP_MONTH, TRUE_UP_RATE"),
    ("utility/billing.py",
     """        net = reading.consumed_kwh - reading.exported_kwh
""",
     """        if self.last_billed is not None and reading.month <= self.last_billed:
            raise ValueError("bills must be produced in month order")
        net = reading.consumed_kwh - reading.exported_kwh
"""),
    ("utility/billing.py",
     """        energy = tiered_energy_charge(reading.consumed_kwh if net > 0 else 0)
        if billable > 0 and self.bank_kwh > 0:
            used = min(self.bank_kwh, billable)
            energy -= used * TIERS[0][1]
            billable -= used

        energy = cents(energy)
        tax = cents((energy + FIXED_CHARGE) * TAX_RATE)
        self.last_billed = reading.month
        return Bill(reading.month, billable, energy, tax, FIXED_CHARGE, energy + tax + FIXED_CHARGE)""",
     """        if billable > 0 and self.bank_kwh > 0:
            used = min(self.bank_kwh, billable)
            self.bank_kwh -= used
            billable -= used
        energy = cents(tiered_energy_charge(billable))

        tax = cents(energy * TAX_RATE)
        payout = Decimal("0.00")
        if reading.month.month == TRUE_UP_MONTH:
            payout = cents(self.bank_kwh * TRUE_UP_RATE)
            self.bank_kwh = 0
        self.last_billed = reading.month
        return Bill(reading.month, billable, energy, tax, FIXED_CHARGE, energy + tax + FIXED_CHARGE, payout)"""),
]
