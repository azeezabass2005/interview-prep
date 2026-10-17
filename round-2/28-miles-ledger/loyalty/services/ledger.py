from datetime import date
from typing import List

from ..config import EXPIRY_YEARS
from ..errors import InsufficientMiles
from ..models import Lot
from ..store import InMemoryStore
from .status import StatusService


def anniversary(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


class Ledger:
    def __init__(self, store: InMemoryStore, status: StatusService):
        self._store = store
        self._status = status

    def usable(self, lot: Lot, on: date, platinum: bool) -> bool:
        if lot.remaining <= 0:
            return False
        return platinum or on <= anniversary(lot.dated, EXPIRY_YEARS)

    def usable_lots(self, member_id: str, on: date) -> List[Lot]:
        platinum = self._status.tier(member_id, on) == "PLATINUM"
        return [l for l in self._store.lots_for(member_id) if self.usable(l, on, platinum)]

    def balance(self, member_id: str, on: date) -> int:
        return sum(l.remaining for l in self.usable_lots(member_id, on))

    def spend(self, member_id: str, miles: int, on: date) -> None:
        if miles <= 0:
            raise ValueError("miles must be positive")
        if self.balance(member_id, on) < miles:
            raise InsufficientMiles(f"{member_id} has fewer than {miles} usable miles")
        needed = miles
        for lot in sorted(self.usable_lots(member_id, on), key=lambda l: (l.dated, l.lot_id), reverse=True):
            take = min(lot.remaining, needed)
            lot.remaining -= take
            needed -= take
            if needed == 0:
                return
