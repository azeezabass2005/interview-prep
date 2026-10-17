from typing import Dict, List

from .models import CONFIRMED, Reservation


class InMemoryStore:
    def __init__(self):
        self.reservations: Dict[str, Reservation] = {}

    def active(self, room_type: str) -> List[Reservation]:
        return [r for r in self.reservations.values() if r.room_type == room_type and r.status == CONFIRMED]
