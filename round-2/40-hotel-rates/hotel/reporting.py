from datetime import date

from .config import ROOM_TYPES
from .services.availability import Availability
from .store import InMemoryStore


def occupancy(store: InMemoryStore, night: date) -> dict:
    availability = Availability(store)
    report = {}
    for room_type, (rooms, _) in ROOM_TYPES.items():
        left = availability.rooms_left(room_type, night)
        report[room_type] = {"sold": rooms - left, "rooms": rooms, "occupancy": f"{(rooms - left) / rooms:.0%}"}
    return report
