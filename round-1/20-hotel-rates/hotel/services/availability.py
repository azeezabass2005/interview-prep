from datetime import date

from ..config import ROOM_TYPES
from ..store import InMemoryStore
from .pricing import nights


class Availability:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def rooms_left(self, room_type: str, night: date) -> int:
        taken = sum(1 for r in self._store.active(room_type) if r.check_in <= night < r.check_out)
        return ROOM_TYPES[room_type][0] - taken

    def available(self, room_type: str, check_in: date, check_out: date) -> bool:
        return self.rooms_left(room_type, nights(check_in, check_out)[0]) > 0
