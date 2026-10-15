from datetime import date
from decimal import Decimal
from typing import List

from .earning import miles_for_fare
from .models import InsufficientMiles, Lot, Member

EXPIRY_YEARS = 2


class MilesAccount:
    def __init__(self, member: Member):
        self.member = member
        self.lots: List[Lot] = []

    def earn(self, fare: Decimal, on: date) -> Lot:
        miles = miles_for_fare(Decimal(fare), self.member.tier)
        lot = Lot(earned_on=on, miles=miles, remaining=miles)
        self.lots.append(lot)
        return lot

    def expires_on(self, lot: Lot) -> date:
        return lot.earned_on.replace(year=lot.earned_on.year + EXPIRY_YEARS)

    def _usable(self, lot: Lot, as_of: date) -> bool:
        return lot.remaining > 0 and as_of <= self.expires_on(lot)

    def balance(self, as_of: date) -> int:
        return sum(lot.remaining for lot in self.lots if self._usable(lot, as_of))

    def redeem(self, miles: int, on: date) -> None:
        if miles <= 0:
            raise ValueError("redeem a positive number of miles")
        usable = sorted((l for l in self.lots if self._usable(l, on)),
                        key=lambda l: l.earned_on, reverse=True)
        still_needed = miles
        for lot in usable:
            take = min(lot.remaining, still_needed)
            lot.remaining -= take
            still_needed -= take
            if still_needed == 0:
                return
        raise InsufficientMiles(f"short by {still_needed} miles")
