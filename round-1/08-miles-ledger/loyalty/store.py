import itertools
from collections import defaultdict
from typing import Dict, List, Optional

from .models import Flight, Lot, Member


class InMemoryStore:
    def __init__(self):
        self.members: Dict[str, Member] = {}
        self.flights: Dict[str, Flight] = {}
        self.lots: Dict[str, List[Lot]] = defaultdict(list)
        self.qualifying: Dict[tuple, int] = defaultdict(int)
        self._lot_ids = itertools.count(1)

    def add_member(self, member: Member) -> None:
        self.members[member.member_id] = member

    def member(self, member_id: str) -> Optional[Member]:
        return self.members.get(member_id)

    def add_flight(self, flight: Flight) -> None:
        self.flights[flight.flight_id] = flight

    def flight(self, flight_id: str) -> Optional[Flight]:
        return self.flights.get(flight_id)

    def add_lot(self, member_id: str, dated, miles: int, source: str, flight_id=None) -> Lot:
        lot = Lot(next(self._lot_ids), member_id, dated, miles, miles, source, flight_id)
        self.lots[member_id].append(lot)
        return lot

    def lots_for(self, member_id: str) -> List[Lot]:
        return list(self.lots.get(member_id, []))

    def add_qualifying(self, member_id: str, year: int, miles: int) -> None:
        self.qualifying[(member_id, year)] += miles

    def qualifying_miles(self, member_id: str, year: int) -> int:
        return self.qualifying.get((member_id, year), 0)
