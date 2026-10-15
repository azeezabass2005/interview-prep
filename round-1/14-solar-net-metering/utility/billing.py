from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from .models import Bill, Reading
from .tariff import FIXED_CHARGE, TAX_RATE, TIERS

CENT = Decimal("0.01")


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def tiered_energy_charge(kwh: int) -> Decimal:
    charge = Decimal("0")
    lower = 0
    for upper, rate in TIERS:
        top = kwh if upper is None else min(kwh, upper)
        if top > lower:
            charge += (top - lower) * rate
        if upper is None or kwh <= upper:
            break
        lower = upper
    return charge


class SolarAccount:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.bank_kwh = 0
        self.last_billed = None

    def bill(self, reading: Reading) -> Bill:
        net = reading.consumed_kwh - reading.exported_kwh
        if net < 0:
            self.bank_kwh += -net
            billable = 0
        else:
            billable = net

        energy = tiered_energy_charge(reading.consumed_kwh if net > 0 else 0)
        if billable > 0 and self.bank_kwh > 0:
            used = min(self.bank_kwh, billable)
            energy -= used * TIERS[0][1]
            billable -= used

        energy = cents(energy)
        tax = cents((energy + FIXED_CHARGE) * TAX_RATE)
        self.last_billed = reading.month
        return Bill(reading.month, billable, energy, tax, FIXED_CHARGE, energy + tax + FIXED_CHARGE)
